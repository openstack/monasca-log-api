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

from monasca_common.kafka import producer
from monasca_common.rest import utils as rest_utils
from oslo_config import cfg
from oslo_log import log

from monasca_log_api.reference.v2.common import service

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
        self._kafka_publisher = None
        LOG.info('Initializing LogPublisher <%s>', self)

    @staticmethod
    def _build_key(tenant_it, obj):
        """Message key builder

        Builds message key using tenant_id and following details of
        log message:
        - application_type
        - dimensions
        :param tenant_it: tenant id
        :param obj: log instance
        :return: key
        """

        str_list = []

        if tenant_it:
            str_list.append(str(tenant_it))

        if obj:
            if 'application_type' in obj and obj['application_type']:
                str_list += obj['application_type']

            if 'dimensions' in obj and obj['dimensions']:
                dims = obj['dimensions']
                sorted_dims = sorted(dims)
                for name in sorted_dims:
                    str_list += name
                    str_list += str(dims[name])

        return ''.join(str_list)

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

    def _publisher(self):
        if not self._kafka_publisher:
            self._kafka_publisher = producer.KafkaProducer(
                url=CONF.log_publisher.kafka_url
            )
        return self._kafka_publisher

    def send_message(self, message):
        """Sends message to each configured topic.

        Prior to sending a message, unique key is being
        calculated for the given message using:

        * tenant id
        * application type
        * dimensions

        Note:
            Falsy messages (i.e. empty) are not shipped to kafka

        See :py:meth:`monasca_log_api.v2.common.service.LogCreator`
                    `.new_log_envelope`

        :param dict message: instance of log envelope
        """
        if not message:
            return
        if not self._is_message_valid(message):
            raise InvalidMessageException()

        key = self._build_key(message['meta']['tenantId'], message['log'])
        msg = rest_utils.as_json(message).encode('utf8')

        service.Validations.validate_envelope_size(msg)

        LOG.debug('Build key [%s] for message', key)
        LOG.debug('Sending message {topics=%s,key=%s,message=%s}',
                  self._topics, key, msg)

        try:
            for topic in self._topics:
                self._publisher().publish(topic, msg, key)
        except Exception as ex:
            LOG.error(ex.message)
            raise ex
