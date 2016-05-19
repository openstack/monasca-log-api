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

import falcon
import itertools

from monasca_common.kafka import producer
from monasca_common.rest import utils as rest_utils
from oslo_config import cfg
from oslo_log import log

from monasca_log_api.reference.common import validation

LOG = log.getLogger(__name__)
CONF = cfg.CONF

log_publisher_opts = [
    cfg.StrOpt('kafka_url',
               required=True,
               help='Url to kafka server'),
    cfg.MultiStrOpt('topics',
                    default=['logs'],
                    help='Consumer topics')
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

    # TODO(trebskit) caching of computed keys should be done
    # TODO(trebskit) cache should have expires_at_like functionality
    @staticmethod
    def _build_key(tenant_it, obj=None):
        """Message key builder

        Builds message key using tenant_id and dimensions (only values).
        Used values are concatenated with ':' character for readability.

        :param str tenant_it: tenant id
        :param dict obj: log instance
        :return: key
        :rtype: str
        """

        if obj is None:
            obj = {}
        if not (tenant_it or obj):
            return ''

        str_list = [str(tenant_it)]

        dims = obj.get('dimensions', None)
        if dims:
            sorted_dims = sorted(dims)
            for name in sorted_dims:
                str_list.append(dims[name])

        return ':'.join(filter(None, str_list))

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

    def send_message(self, messages):
        """Sends message to each configured topic.

        Note:
            Falsy messages (i.e. empty) are not shipped to kafka

        See also
            :py:class:`monasca_log_api.common.model.Envelope'
            :py:meth:`._is_message_valid'
            :py:meth:`._build_key'

        :param dict|list messages: instance (or instances) of log envelope
        """

        if not messages:
            return
        if not isinstance(messages, list):
            messages = [messages]

        buckets = {}
        sent_counter = 0
        to_sent_counter = len(messages)

        LOG.debug('About to publish %d messages to %s topics',
                  to_sent_counter, self._topics)

        try:
            for message in messages:
                if not self._is_message_valid(message):
                    raise InvalidMessageException()

                key = self._build_key(message['meta']['tenantId'],
                                      message['log'])
                msg = rest_utils.as_json(message).encode('utf8')

                validation.validate_envelope_size(msg)

                if key not in buckets:
                    buckets[key] = []

                buckets[key].append(msg)

            all_keys = buckets.keys()
            LOG.debug('Publishing %d buckets of messages', len(all_keys))

            topic_to_key = itertools.product(self._topics, all_keys)
            for topic, key in topic_to_key:

                bucket = buckets.get(key)  # array of messages for the same key
                if not bucket:
                    LOG.warn('Empty bucket spotted, continue...')
                    continue
                try:
                    self._kafka_publisher.publish(topic, bucket, key)
                except Exception as ex:
                    raise falcon.HTTPServiceUnavailable('Service unavailable',
                                                        ex.message, 60)

                LOG.debug('Sent %d messages (topics=%s,key=%s)',
                          len(bucket), topic, key)

                # keep on track how many msgs have been sent
                sent_counter += len(bucket)
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
