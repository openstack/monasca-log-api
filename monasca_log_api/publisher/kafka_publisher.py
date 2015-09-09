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

import time

from kafka import client
from kafka import common
from kafka import conn
from kafka import producer
from kafka import protocol
from oslo_config import cfg
from oslo_log import log
import simport

from monasca_log_api.publisher import exceptions
from monasca_log_api.publisher import publisher

LOG = log.getLogger(__name__)
CONF = cfg.CONF

ACK_MAP = {
    'None': producer.KeyedProducer.ACK_NOT_REQUIRED,
    'Local': producer.KeyedProducer.ACK_AFTER_LOCAL_WRITE,
    'Server': producer.KeyedProducer.ACK_AFTER_CLUSTER_COMMIT
}

kafka_opts = [
    cfg.StrOpt('client_id',
               default=None,
               help='Client Id',
               required=True),
    cfg.IntOpt('timeout',
               default=conn.DEFAULT_SOCKET_TIMEOUT_SECONDS,
               help='Socket timeout'),
    cfg.StrOpt('host',
               default=None,
               help='List of hosts, comma delimited',
               required=True)
]
kafka_group = cfg.OptGroup(name='kafka', title='kafka')

kafka_producer_opts = [
    cfg.IntOpt('batch_send_every_n',
               default=None,
               help='Send every n items'),
    cfg.IntOpt('batch_send_every_t',
               default=None,
               help='Send every n seconds'),
    cfg.BoolOpt('async',
                default=False,
                help='Async communication'),
    cfg.StrOpt('reg_acks',
               default='None',
               help='Acknowledge options'),
    cfg.StrOpt('partitioner',
               default=None,
               help='Partitioner algorithm')
]
kafka_producer_group = cfg.OptGroup(name='kafka_producer',
                                    title='kafka_producer')

CONF.register_group(kafka_group)
CONF.register_opts(kafka_opts, kafka_group)

CONF.register_group(kafka_producer_group)
CONF.register_opts(kafka_producer_opts, kafka_producer_group)


class KafkaPublisher(publisher.Publisher):
    def __init__(self, max_retry=3, wait_time=None):
        self._producer_conf = None
        self._client_conf = None

        self._producer = None
        self._client = None

        self._max_retry = max_retry
        self._wait_time = wait_time

        LOG.info('Initializing KafkaPublisher <%s>' % self)

    def _get_client_conf(self):
        if self._client_conf:
            return self._client_conf

        client_conf = {
            'hosts': CONF.kafka.host,
            'client_id': CONF.kafka.client_id,
            'timeout': CONF.kafka.timeout
        }

        self._client_conf = client_conf

        return client_conf

    def _get_producer_conf(self):
        if self._producer_conf:
            return self._producer_conf

        batch_send_every_n = CONF.kafka_producer.batch_send_every_n
        batch_send_every_t = CONF.kafka_producer.batch_send_every_t
        partitioner = CONF.kafka_producer.partitioner

        producer_conf = {
            'codec': protocol.CODEC_GZIP,
            'batch_send': batch_send_every_n or batch_send_every_t,
            'async': CONF.kafka_producer.async,
            'reg_acks': ACK_MAP[CONF.kafka_producer.reg_acks]
        }
        if batch_send_every_t:
            producer_conf.update(
                {'batch_send_every_t': batch_send_every_t})
        if batch_send_every_n:
            producer_conf.update(
                {'batch_send_every_n': batch_send_every_n})
        if partitioner:
            partitioner = simport.load(partitioner)
            producer_conf.update({'partitioner': partitioner})

        self._producer_conf = producer_conf

        return producer_conf

    def _init_client(self):
        if self._client:
            self._client.close()
            self._producer = None
            self._client = None

        client_opts = self._get_client_conf()

        for i in range(self._max_retry):
            kafka_host = client_opts['hosts']
            try:
                self._client = client.KafkaClient(
                    client_opts['hosts'],
                    client_opts['client_id'],
                    client_opts['timeout']
                )
                if self._wait_time:
                    time.sleep(self._wait_time)
                break
            except common.KafkaUnavailableError as ex:
                LOG.error('Server is down at <host="%s">' % kafka_host)
                err = ex
            except common.LeaderNotAvailableError as ex:
                LOG.error('No leader at <host="%s">.' % kafka_host)
                err = ex
            except Exception as ex:
                LOG.error('Initialization failed at <host="%s">.' % kafka_host)
                err = ex

            if err:
                raise err

    def _init_producer(self):
        try:
            if not self._client:
                self._init_client()

            producer_opts = self._get_producer_conf()
            producer_opts.update({'client': self._client})

            self._producer = producer.KeyedProducer(*producer_opts)
            if self._wait_time:
                time.sleep(self._wait_time)
        except Exception as ex:
            self._producer = None
            LOG.exception(ex.message, exc_info=1)
            raise exceptions.PublisherInitException(
                message='KeyedProducer can not be created at <host="%s>"'
                        % self._client_conf['host'],
                caught=ex)

    def send_message(self, topic, key, message):
        if not message or not key or not topic:
            return
        try:
            if not self._producer:
                self._init_producer()

            return self._producer.send(topic, key, message)
        except (common.KafkaUnavailableError,
                common.LeaderNotAvailableError) as ex:
            self._client = None
            LOG.error(ex.message, exc_info=1)
            raise exceptions.MessageQueueException(
                message='Failed to post message to kafka',
                caught=ex
            )
        except Exception as ex:
            LOG.error(ex.message, exc_info=1)
            raise exceptions.MessageQueueException(
                message='Unknown error while sending message to kafka',
                caught=ex
            )

    # TODO(question) How to ensure that connection will be closed when program
    # stops ?
    def close(self):
        if self._client:
            self._producer = None
            self._client.close()

    def __repr__(self):
        return 'KafkaPublisher <host=%s>' % (
            self._client_conf['hosts'] if self._client_conf else None
        )
