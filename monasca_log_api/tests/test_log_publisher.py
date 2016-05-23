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

import copy
import datetime
import random
import string
import ujson
import unittest

from falcon import testing
import mock

from monasca_log_api.reference.common import log_publisher
from monasca_log_api.tests import base

EPOCH_START = datetime.datetime(1970, 1, 1)


def _generate_unique_message(size):
    letters = string.ascii_lowercase

    def rand(amount, space=True):
        space = ' ' if space else ''
        return ''.join((random.choice(letters + space) for _ in range(amount)))

    return rand(size)


class TestSendMessage(testing.TestBase):
    def setUp(self):
        self.conf = base.mock_config(self)
        return super(TestSendMessage, self).setUp()

    @mock.patch('monasca_log_api.reference.common.log_publisher.producer'
                '.KafkaProducer')
    def test_should_not_send_empty_message(self, _):
        instance = log_publisher.LogPublisher()

        instance._kafka_publisher = mock.Mock()
        instance.send_message({})

        self.assertFalse(instance._kafka_publisher.publish.called)

    @unittest.expectedFailure
    def test_should_not_send_message_not_dict(self):
        instance = log_publisher.LogPublisher()
        not_dict_value = 123
        instance.send_message(not_dict_value)

    @mock.patch('monasca_log_api.reference.common.log_publisher.producer'
                '.KafkaProducer')
    def test_should_not_send_message_missing_keys(self, _):
        # checks every combination of missing keys
        # test does not rely on those keys having a value or not,
        # it simply assumes that values are set but important
        # message (i.e. envelope) properties are missing entirely
        # that's why there are two loops instead of three

        instance = log_publisher.LogPublisher()
        keys = ['log', 'creation_time', 'meta']

        for key_1 in keys:
            diff = keys[:]
            diff.remove(key_1)
            for key_2 in diff:
                message = {
                    key_1: random.randint(10, 20),
                    key_2: random.randint(30, 50)
                }
                self.assertRaises(log_publisher.InvalidMessageException,
                                  instance.send_message,
                                  message)

    @mock.patch('monasca_log_api.reference.common.log_publisher.producer'
                '.KafkaProducer')
    def test_should_not_send_message_missing_values(self, _):
        # original message assumes that every property has value
        # test modify each property one by one by removing that value
        # (i.e. creating false-like value)
        instance = log_publisher.LogPublisher()
        message = {
            'log': {
                'message': '11'
            },
            'creation_time': 123456,
            'meta': {
                'region': 'pl'
            }
        }

        for key in message:
            tmp_message = message
            tmp_message[key] = None
            self.assertRaises(log_publisher.InvalidMessageException,
                              instance.send_message,
                              tmp_message)

    @mock.patch('monasca_log_api.reference.common.log_publisher.producer'
                '.KafkaProducer')
    def test_should_send_message(self, kafka_producer):
        instance = log_publisher.LogPublisher()
        instance._kafka_publisher = kafka_producer
        instance.send_message({})

        creation_time = ((datetime.datetime.utcnow() - EPOCH_START)
                         .total_seconds())
        application_type = 'monasca-log-api'
        dimension_1_name = 'disk_usage'
        dimension_1_value = '50'
        dimension_2_name = 'cpu_time'
        dimension_2_value = '60'
        msg = {
            'log': {
                'message': 1,
                'application_type': application_type,
                'dimensions': {
                    dimension_1_name: dimension_1_value,
                    dimension_2_name: dimension_2_value
                }
            },
            'creation_time': creation_time,
            'meta': {
                'tenantId': 1
            }
        }

        instance.send_message(msg)

        instance._kafka_publisher.publish.assert_called_once_with(
            self.conf.conf.log_publisher.topics[0],
            [ujson.dumps(msg)])

    @mock.patch('monasca_log_api.reference.common.log_publisher.producer'
                '.KafkaProducer')
    def test_should_send_message_multiple_topics(self, _):
        topics = ['logs', 'analyzer', 'tester']
        self.conf.config(topics=topics,
                         max_message_size=5000,
                         group='log_publisher')

        instance = log_publisher.LogPublisher()
        instance._kafka_publisher = mock.Mock()
        instance.send_message({})

        creation_time = ((datetime.datetime.utcnow() - EPOCH_START)
                         .total_seconds())
        dimension_1_name = 'disk_usage'
        dimension_1_value = '50'
        dimension_2_name = 'cpu_time'
        dimension_2_value = '60'
        application_type = 'monasca-log-api'
        msg = {
            'log': {
                'message': 1,
                'application_type': application_type,
                'dimensions': {
                    dimension_1_name: dimension_1_value,
                    dimension_2_name: dimension_2_value
                }
            },
            'creation_time': creation_time,
            'meta': {
                'tenantId': 1
            }
        }
        json_msg = ujson.dumps(msg)

        instance.send_message(msg)

        self.assertEqual(len(topics),
                         instance._kafka_publisher.publish.call_count)
        for topic in topics:
            instance._kafka_publisher.publish.assert_any_call(
                topic,
                [json_msg])


class TestTruncation(testing.TestBase):
    EXTRA_CHARS_SIZE = len(bytearray(ujson.dumps({
        'log': {
            'message': None
        }
    }))) - 2

    def __init__(self, *args, **kwargs):
        super(TestTruncation, self).__init__(*args, **kwargs)
        self._conf = None

    def setUp(self):
        super(TestTruncation, self).setUp()
        self._conf = base.mock_config(self)

    @mock.patch(
        'monasca_log_api.reference.common.log_publisher.producer'
        '.KafkaProducer')
    def test_should_not_truncate_message_if_size_is_smaller(self, _):
        diff_size = random.randint(1, 100)
        self._run_truncate_test(log_size_factor=-diff_size,
                                truncate_by=0)

    @mock.patch(
        'monasca_log_api.reference.common.log_publisher.producer'
        '.KafkaProducer')
    def test_should_not_truncate_message_if_size_equal_to_max(self, _):
        self._run_truncate_test(log_size_factor=0,
                                truncate_by=0)

    @mock.patch(
        'monasca_log_api.reference.common.log_publisher.producer'
        '.KafkaProducer')
    def test_should_truncate_too_big_message(self, _):
        diff_size = random.randint(1, 100)
        max_size = 1000
        truncate_by = ((max_size -
                        (max_size - log_publisher._TRUNCATED_PROPERTY_SIZE)) +
                       log_publisher._TRUNCATION_SAFE_OFFSET + diff_size)
        self._run_truncate_test(max_message_size=1000,
                                log_size_factor=diff_size,
                                truncate_by=truncate_by)

    def _run_truncate_test(self,
                           max_message_size=1000,
                           log_size_factor=0,
                           truncate_by=0,
                           gen_fn=_generate_unique_message):

        log_size = (max_message_size -
                    TestTruncation.EXTRA_CHARS_SIZE -
                    log_publisher._KAFKA_META_DATA_SIZE -
                    log_publisher._TIMESTAMP_KEY_SIZE +
                    log_size_factor)

        expected_log_message_size = log_size - truncate_by

        self._conf.config(
            group='log_publisher',
            max_message_size=max_message_size
        )

        log_msg = gen_fn(log_size)
        envelope = {
            'log': {
                'message': log_msg
            }
        }

        instance = log_publisher.LogPublisher()

        envelope_copy = copy.deepcopy(envelope)
        json_envelope = instance._truncate(envelope_copy)

        parsed_envelope = ujson.loads(json_envelope)

        parsed_log_message = parsed_envelope['log']['message']
        parsed_log_message_len = len(parsed_log_message)

        if truncate_by > 0:
            self.assertNotEqual(envelope['log']['message'],
                                parsed_log_message)
        else:
            self.assertEqual(envelope['log']['message'],
                             parsed_log_message)

        self.assertEqual(expected_log_message_size, parsed_log_message_len)
