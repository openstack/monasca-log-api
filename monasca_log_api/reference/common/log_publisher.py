# Copyright 2015 kornicameister@gmail.com
# Copyright 2016 FUJITSU LIMITED
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

from monasca_common.kafka import producer
from monasca_common.rest import utils as rest_utils
from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)
CONF = cfg.CONF

_MAX_MESSAGE_SIZE = 1048576
_RETRY_AFTER = 60
_TIMESTAMP_KEY_SIZE = len(
    bytearray(str(int(time.time() * 1000)).encode('utf-8')))
_TRUNCATED_PROPERTY_SIZE = len(
    bytearray('"truncated": true'.encode('utf-8')))
_KAFKA_META_DATA_SIZE = 32
_TRUNCATION_SAFE_OFFSET = 1

log_publisher_opts = [
    cfg.StrOpt('kafka_url',
               required=True,
               help='Url to kafka server'),
    cfg.MultiStrOpt('topics',
                    default=['logs'],
                    help='Consumer topics'),
    cfg.IntOpt('max_message_size',
               default=_MAX_MESSAGE_SIZE,
               required=True,
               help=('Message max size that can be sent '
                     'to kafka, default to %d bytes' % _MAX_MESSAGE_SIZE))
]

log_publisher_group = cfg.OptGroup(name='log_publisher', title='log_publisher')

cfg.CONF.register_group(log_publisher_group)
cfg.CONF.register_opts(log_publisher_opts, log_publisher_group)

ENVELOPE_SCHEMA = ['log', 'meta', 'creation_time']
"""Log envelope (i.e.) message keys"""


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
        self._kafka_publisher = producer.KafkaProducer(
            url=CONF.log_publisher.kafka_url
        )
        LOG.info('Initializing LogPublisher <%s>', self)

    @staticmethod
    def _is_message_valid(message):
        """Validates message before sending.

        Methods checks if message is :py:class:`dict`.
        If so dictionary is verified against having following keys:

        * meta
        * log
        * creation_time

        If keys are found, each key must have a valueH.

        If at least none of the conditions is met
        :py:class:`.InvalidMessageException` is raised

        :raises InvalidMessageException: if message does not comply to schema

        """
        if not isinstance(message, dict):
            return False

        for key in ENVELOPE_SCHEMA:
            if not (key in message and message.get(key)):
                return False

        return True

    def _truncate(self, envelope):
        """Truncates the message if needed.

        Each message send to kafka is verified.
        Method checks if message serialized to json
        exceeds maximum allowed size that can be posted to kafka
        queue. If so, method truncates message property of the log
        by difference between message and allowed size.

        :param Envelope envelope: envelope to check
        :return: truncated message if size is exceeded, otherwise message
                 is left unmodified
        """

        msg_str = rest_utils.as_json(envelope)

        max_size = CONF.log_publisher.max_message_size
        envelope_size = ((len(bytearray(msg_str)) +
                          _TIMESTAMP_KEY_SIZE +
                          _KAFKA_META_DATA_SIZE)
                         if msg_str is not None else -1)

        size_diff = (envelope_size - max_size) + _TRUNCATION_SAFE_OFFSET

        LOG.debug('_truncate(max_message_size=%d, message_size=%d, diff=%d)',
                  max_size, envelope_size, size_diff)

        if size_diff > 1:
            truncate_by = size_diff + _TRUNCATED_PROPERTY_SIZE

            LOG.warn(('Detected message that exceeds %d bytes,'
                      'message will be truncated by %d bytes'),
                     max_size,
                     truncate_by)

            log_msg = envelope['log']['message']
            truncated_log_msg = log_msg[:-truncate_by]

            envelope['log']['truncated'] = True
            envelope['log']['message'] = truncated_log_msg

            # will just transform message once again without truncation
            return rest_utils.as_json(envelope)

        return msg_str

    def send_message(self, messages):
        """Sends message to each configured topic.

        Note:
            Falsy messages (i.e. empty) are not shipped to kafka

        See also
            :py:class:`monasca_log_api.common.model.Envelope'
            :py:meth:`._is_message_valid'

        :param dict|list messages: instance (or instances) of log envelope
        """

        if not messages:
            return
        if not isinstance(messages, list):
            messages = [messages]

        sent_counter = 0
        to_sent_counter = len(messages)

        LOG.debug('About to publish %d messages to %s topics',
                  to_sent_counter, self._topics)

        try:
            send_messages = []
            for message in messages:
                if not self._is_message_valid(message):
                    raise InvalidMessageException()

                msg = self._truncate(message)
                send_messages.append(msg)

            for topic in self._topics:
                self._kafka_publisher.publish(topic, send_messages)

            sent_counter = to_sent_counter
        except Exception as ex:
            LOG.error('Failure in publishing messages to kafka')
            LOG.exception(ex)
            raise ex
        finally:
            if sent_counter == to_sent_counter:
                LOG.info('Successfully published all [%d] messages',
                         sent_counter)
            else:
                failed_to_send = to_sent_counter - sent_counter
                error_str = ('Failed to sent all messages, %d '
                             'messages out of %d have not been published')
                LOG.error(error_str, failed_to_send, to_sent_counter)
