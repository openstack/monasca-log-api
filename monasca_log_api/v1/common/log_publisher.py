# Copyright 2015 kornicameister@gmail.com
# Copyright 2015 FUJITSU LIMITED
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

from oslo_config import cfg
from oslo_log import log
import simplejson

from monasca_log_api.publisher import kafka_publisher

LOG = log.getLogger(__name__)
CONF = cfg.CONF

log_publisher_opts = [
    cfg.MultiStrOpt('topics',
                    default=['logs'],
                    help='Target topic in kafka')
]
log_publisher_group = cfg.OptGroup(name='log_publisher', title='log_publisher')

cfg.CONF.register_group(log_publisher_group)
cfg.CONF.register_opts(log_publisher_opts, log_publisher_group)


class LogPublisher(object):
    def __init__(self):
        self._topics = CONF.log_publisher.topics
        self._kafka_publisher = kafka_publisher.KafkaPublisher()
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
        def comparator(a, b):
            """Comparator for dimensions

            :param a: dimension_a, tuple with properties name,value
            :param b: dimension_b, tuple with properties name,value
            :return: sorting result
            """
            if a.name == b.name:
                return (a.value > b.value) - (a.value < b.value)
            return (a.name > b.name) - (a.name < b.name)

        str_list = []

        if tenant_it:
            str_list.append(str(tenant_it))

        if obj:
            if 'application_type' in obj and obj['application_type']:
                str_list += obj['application_type']

            if 'dimensions' in obj and obj['dimensions']:
                dimensions = sorted(obj['dimensions'], cmp=comparator)
                for name, value in dimensions:
                    str_list += name
                    str_list += str(value)

        return ''.join(str_list)

    def send_message(self, message):
        if not message:
            return

        key = self._build_key(message['meta']['tenantId'], message['log'])
        msg = simplejson.dumps(message,
                               sort_keys=False,
                               ensure_ascii=False).encode('utf8')

        LOG.debug('Build key [%s] for message' % key)
        LOG.debug('Sending message {topics=%s,key=%s,message=%s}' %
                  (self._topics, key, msg))

        try:
            for topic in self._topics:
                self._kafka_publisher.send_message(topic, key, msg)
        except Exception as ex:
            LOG.error(ex.message)
            raise ex
