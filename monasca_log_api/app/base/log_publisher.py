# Copyright 2015 kornicameister@gmail.com
# Copyright 2016-2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import falcon
from monasca_common.kafka import producer
from monasca_common.rest import utils as rest_utils
from oslo_log import log
from oslo_utils import encodeutils

from monasca_log_api.app.base import model
from monasca_log_api import conf
from monasca_log_api.monitoring import client
from monasca_log_api.monitoring import metrics

LOG = log.getLogger(__name__)
CONF = conf.CONF

_RETRY_AFTER = 60
_TIMESTAMP_KEY_SIZE = len(
    bytearray(str(int(time.time() * 1000)).encode('utf-8')))
_TRUNCATED_PROPERTY_SIZE = len(
    bytearray('"truncated": true'.encode('utf-8')))
_KAFKA_META_DATA_SIZE = 32
_TRUNCATION_SAFE_OFFSET = 1


class InvalidMessageException(Exception):
    pass


class LogPublisher(object):
    """Publishes log data to Kafka

    LogPublisher is able to send single message to multiple configured topic.
    It uses following configuration written in conf file ::

        [log_publisher]
        topics = 'logs'
        kafka_url = 'localhost:8900'

    Note:
        Uses :py:class:`monasca_common.kafka.producer.KafkaProducer`
        to ship logs to kafka. For more details
        see `monasca_common`_ github repository.

    .. _monasca_common: https://github.com/openstack/monasca-common

    """

    def __init__(self):
        self._topics = CONF.log_publisher.topics
        self.max_message_size = CONF.log_publisher.max_message_size

        self._kafka_publisher = producer.KafkaProducer(
            url=CONF.log_publisher.kafka_url
        )
        if CONF.monitoring.enable:
            self._statsd = client.get_client()

            # setup counter, gauges etc
            self._logs_published_counter = self._statsd.get_counter(
                metrics.LOGS_PUBLISHED_METRIC
            )
            self._publish_time_ms = self._statsd.get_timer(
                metrics.LOGS_PUBLISH_TIME_METRIC
            )
            self._logs_lost_counter = self._statsd.get_counter(
                metrics.LOGS_PUBLISHED_LOST_METRIC
            )
            self._logs_truncated_gauge = self._statsd.get_gauge(
                metrics.LOGS_TRUNCATED_METRIC
            )

        LOG.info('Initializing LogPublisher <%s>', self)

    def send_message(self, messages):
        """Sends message to each configured topic.

        Note:
            Falsy messages (i.e. empty) are not shipped to kafka

        See also
            * :py:class:`monasca_log_api.common.model.Envelope`
            * :py:meth:`._is_message_valid`

        :param dict|list messages: instance (or instances) of log envelope
        """

        if not messages:
            return
        if not isinstance(messages, list):
            messages = [messages]

        sent_counter = 0
        num_of_msgs = len(messages)

        LOG.debug('About to publish %d messages to %s topics',
                  num_of_msgs, self._topics)

        try:
            send_messages = []

            for message in messages:
                msg = self._transform_message(message)
                send_messages.append(msg)
            if CONF.monitoring.enable:
                with self._publish_time_ms.time(name=None):
                    self._publish(send_messages)
            else:
                self._publish(send_messages)

            sent_counter = len(send_messages)
        except Exception as ex:
            LOG.exception('Failure in publishing messages to kafka')
            raise ex
        finally:
            self._after_publish(sent_counter, num_of_msgs)

    def _transform_message(self, message):
        """Transforms message into JSON.

        Method executes transformation operation for
        single element. Operation is set of following
        operations:

        * checking if message is valid
            (:py:func:`.LogPublisher._is_message_valid`)
        * truncating message if necessary
            (:py:func:`.LogPublisher._truncate`)

        :param model.Envelope message: instance of message
        :return: serialized message
        :rtype: str
        """
        if not self._is_message_valid(message):
            raise InvalidMessageException()
        truncated = self._truncate(message)
        return encodeutils.safe_encode(truncated, incoming='utf-8')

    def _truncate(self, envelope):
        """Truncates the message if needed.

        Each message send to kafka is verified.
        Method checks if message serialized to json
        exceeds maximum allowed size that can be posted to kafka
        queue. If so, method truncates message property of the log
        by difference between message and allowed size.

        :param Envelope envelope: original envelope
        :return: serialized message
        :rtype: str
        """

        msg_str = model.serialize_envelope(envelope)
        envelope_size = ((len(bytearray(msg_str, 'utf-8', 'replace')) +
                          _TIMESTAMP_KEY_SIZE +
                          _KAFKA_META_DATA_SIZE)
                         if msg_str is not None else -1)

        diff_size = ((envelope_size - self.max_message_size) +
                     _TRUNCATION_SAFE_OFFSET)

        if diff_size > 1:
            truncated_by = diff_size + _TRUNCATED_PROPERTY_SIZE

            LOG.warning(('Detected message that exceeds %d bytes,'
                         'message will be truncated by %d bytes'),
                        self.max_message_size,
                        truncated_by)

            log_msg = envelope['log']['message']
            truncated_log_msg = log_msg[:-truncated_by]

            envelope['log']['truncated'] = True
            envelope['log']['message'] = truncated_log_msg
            if CONF.monitoring.enable:
                self._logs_truncated_gauge.send(name=None, value=truncated_by)

            msg_str = rest_utils.as_json(envelope)
        else:
            if CONF.monitoring.enable:
                self._logs_truncated_gauge.send(name=None, value=0)

        return msg_str

    def _publish(self, messages):
        """Publishes messages to kafka.

        :param list messages: list of messages
        """
        num_of_msg = len(messages)

        LOG.debug('Publishing %d messages', num_of_msg)

        try:
            for topic in self._topics:
                self._kafka_publisher.publish(
                    topic,
                    messages
                )
                LOG.debug('Sent %d messages to topic %s', num_of_msg, topic)
        except Exception as ex:
            raise falcon.HTTPServiceUnavailable('Service unavailable',
                                                str(ex), 60)

    @staticmethod
    def _is_message_valid(message):
        """Validates message before sending.

        Methods checks if message is :py:class:`model.Envelope`.
        By being instance of this class it is ensured that all required
        keys are found and they will have their values.

        """
        return message and isinstance(message, model.Envelope)

    def _after_publish(self, send_count, to_send_count):
        """Executed after publishing to sent metrics.

        :param int send_count: how many messages have been sent
        :param int to_send_count: how many messages should be sent

        """

        failed_to_send = to_send_count - send_count

        if failed_to_send == 0:
            LOG.debug('Successfully published all [%d] messages',
                      send_count)
        else:
            error_str = ('Failed to send all messages, %d '
                         'messages out of %d have not been published')
            LOG.error(error_str, failed_to_send, to_send_count)
        if CONF.monitoring.enable:
            self._logs_published_counter.increment(value=send_count)
            self._logs_lost_counter.increment(value=failed_to_send)
