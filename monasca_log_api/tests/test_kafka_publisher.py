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

import unittest

from falcon import testing
from kafka import common
import mock

from monasca_log_api.publisher import exceptions
from monasca_log_api.publisher import kafka_publisher as publisher
from monasca_log_api.tests import base as base_test

TOPIC = 'test'


class MockKafkaClient(object):
    pass


class TestConfiguration(testing.TestBase):
    def setUp(self):
        self.conf = base_test.mock_config(self)
        self.instance = publisher.KafkaPublisher()
        super(TestConfiguration, self).setUp()

    def test_should_not_have_client_conf_at_begin(self):
        self.assertIsNone(self.instance._client_conf)

    def test_should_not_have_producer_conf_at_begin(self):
        self.assertIsNone(self.instance._producer_conf)

    def test_should_init_producer_conf(self):
        self.instance._get_producer_conf()
        self.assertIsNotNone(self.instance._producer_conf)

    def test_should_init_client_conf(self):
        self.instance._get_client_conf()
        self.assertIsNotNone(self.instance._client_conf)


class TestInitialization(testing.TestBase):
    def setUp(self):
        self.conf = base_test.mock_config(self)
        super(TestInitialization, self).setUp()

    def test_should_have_init_client_not_set(self):
        instance = publisher.KafkaPublisher()
        self.assertIsNone(instance._client)

    def test_should_have_init_producer_not_set(self):
        instance = publisher.KafkaPublisher()
        self.assertIsNone(instance._producer)

    @mock.patch('monasca_log_api.publisher.kafka_publisher.client.KafkaClient',
                side_effect=[common.KafkaUnavailableError])
    def test_client_should_fail_kafka_unavailable(self, kafka_client):
        instance = publisher.KafkaPublisher()
        self.assertRaises(
            common.KafkaUnavailableError,
            instance._init_client
        )

    @mock.patch('monasca_log_api.publisher.kafka_publisher.client.KafkaClient',
                side_effect=[common.LeaderNotAvailableError])
    def test_client_should_fail_leader_unavailable(self, kafka_client):
        instance = publisher.KafkaPublisher()
        self.assertRaises(
            common.LeaderNotAvailableError,
            instance._init_client
        )

    @mock.patch('monasca_log_api.publisher.kafka_publisher.client.KafkaClient',
                side_effect=[ValueError])
    def test_client_should_fail_other_error(self, kafka_client):
        instance = publisher.KafkaPublisher()
        self.assertRaises(
            ValueError,
            instance._init_client
        )

    @mock.patch('monasca_log_api.publisher.kafka_publisher.client.KafkaClient',
                autospec=True)
    def test_client_should_initialize(self, kafka_client):
        client_id = 'mock_client'
        timeout = 3600
        hosts = 'localhost:666'

        self.conf.config(
            client_id=client_id,
            timeout=timeout,
            host=hosts,
            group='kafka'
        )

        instance = publisher.KafkaPublisher()
        instance._init_client()

        self.assertIsNotNone(instance._client)
        kafka_client.assert_called_with(hosts, client_id, timeout)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                side_effect=[ValueError])
    def test_producer_should_fail_any_error(self, producer):
        instance = publisher.KafkaPublisher()
        instance._client = MockKafkaClient()
        instance._client_conf = {
            'host': 'localhost'
        }

        self.assertRaises(
            exceptions.PublisherInitException,
            instance._init_producer
        )

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_producer_should_initialize(self, producer):
        instance = publisher.KafkaPublisher()
        client = MockKafkaClient()

        instance._client = client
        instance._get_producer_conf = mock.Mock(return_value={})

        instance._init_producer()

        self.assertIsNotNone(instance._producer)
        self.assertTrue(producer.called)


class TestLogic(unittest.TestCase):
    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_not_call_producer_for_empty_key(self, producer):
        producer.send.return_value = None

        instance = publisher.KafkaPublisher()
        instance._producer = producer

        instance.send_message(TOPIC, None, 'msg')

        self.assertFalse(producer.send.called)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_not_call_producer_for_empty_message(self, producer):
        producer.send.return_value = None

        instance = publisher.KafkaPublisher()
        instance._producer = producer

        instance.send_message(TOPIC, 'key', None)

        self.assertFalse(producer.send.called)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_not_call_producer_for_empty_topic(self, producer):
        producer.send.return_value = None

        instance = publisher.KafkaPublisher()
        instance._producer = producer

        instance.send_message(None, 'key', 'msg')

        self.assertFalse(producer.send.called)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_fail_kafka_not_available(self, producer):
        producer.send.side_effect = [common.KafkaUnavailableError]

        instance = publisher.KafkaPublisher()
        instance._producer = producer
        instance._client = mock.Mock('client')

        with self.assertRaises(exceptions.MessageQueueException) as context:
            instance.send_message('a', 'b', 'c')

        self.assertEqual('Failed to post message to kafka',
                         context.exception.message)
        self.assertIsInstance(context.exception.caught,
                              common.KafkaUnavailableError)
        self.assertIsNone(instance._client)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_fail_leader_not_available(self, producer):
        producer.send.side_effect = [common.LeaderNotAvailableError]

        instance = publisher.KafkaPublisher()
        instance._producer = producer
        instance._client = mock.Mock('client')

        with self.assertRaises(exceptions.MessageQueueException) as context:
            instance.send_message('a', 'b', 'c')

        self.assertEqual('Failed to post message to kafka',
                         context.exception.message)
        self.assertIsInstance(context.exception.caught,
                              common.LeaderNotAvailableError)
        self.assertIsNone(instance._client)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_fail_any_error(self, producer):
        producer.send.side_effect = [Exception]

        instance = publisher.KafkaPublisher()
        instance._producer = producer

        with self.assertRaises(exceptions.MessageQueueException) as context:
            instance.send_message('a', 'b', 'c')

        self.assertEqual('Unknown error while sending message to kafka',
                         context.exception.message)
        self.assertIsInstance(context.exception.caught,
                              Exception)

    @mock.patch('monasca_log_api.publisher.kafka_publisher'
                '.producer.KeyedProducer',
                autospec=True)
    def test_should_send_message(self, producer):
        producer.send.return_value = None

        instance = publisher.KafkaPublisher()
        instance._producer = producer

        msg = 'msg'
        key = 'key'

        instance.send_message(TOPIC, key, msg)

        producer.send.assert_called_once_with(TOPIC, key, msg)
