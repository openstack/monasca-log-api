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
import mock
import simplejson

from monasca_log_api.publisher import exceptions
from monasca_log_api.tests import base
from monasca_log_api.v1.common import log_publisher
from monasca_log_api.v1.common import service


class TestBuildKey(unittest.TestCase):
    def test_should_return_empty_for_none_params(self):
        self.assertFalse(log_publisher.LogPublisher._build_key(None, None))

    def test_should_return_tenant_id_for_tenant_id_defined_1(self):
        tenant_id = 'monasca'
        self.assertEqual(
            tenant_id,
            log_publisher.LogPublisher._build_key(tenant_id, None)
        )

    def test_should_return_tenant_id_for_tenant_id_defined_2(self):
        tenant_id = 'monasca'
        self.assertEqual(tenant_id,
                         log_publisher.LogPublisher._build_key(tenant_id, {}))

    def test_should_return_ok_key_1(self):
        # Evaluates if key matches value for defined tenant_id and
        # application_type
        tenant_id = 'monasca'
        application_type = 'monasca-log-api'
        log_object = {
            'application_type': application_type
        }
        expected_key = tenant_id + application_type

        self.assertEqual(expected_key,
                         log_publisher.LogPublisher._build_key(tenant_id,
                                                               log_object))

    def test_should_return_ok_key_2(self):
        # Evaluates if key matches value for defined tenant_id and
        # application_type and single dimension
        tenant_id = 'monasca'
        application_type = 'monasca-log-api'
        dimension = service.Dimension('cpu_time', 50)
        log_object = {
            'application_type': application_type,
            'dimensions': [dimension]
        }
        expected_key = tenant_id + application_type + dimension.name + str(
            dimension.value)

        self.assertEqual(expected_key,
                         log_publisher.LogPublisher._build_key(tenant_id,
                                                               log_object))

    def test_should_return_ok_key_3(self):
        # Evaluates if key matches value for defined tenant_id and
        # application_type and two dimensions dimensions given unsorted
        tenant_id = 'monasca'
        application_type = 'monasca-log-api'
        dimension_1 = service.Dimension('disk_usage', 50)
        dimension_2 = service.Dimension('cpu_time', 50)
        log_object = {
            'application_type': application_type,
            'dimensions': [dimension_1, dimension_2]
        }
        expected_key = ''.join([tenant_id, application_type, dimension_2.name,
                                str(dimension_2.value), dimension_1.name,
                                str(dimension_1.value)])

        self.assertEqual(expected_key,
                         log_publisher.LogPublisher._build_key(tenant_id,
                                                               log_object))


class TestSendMessage(testing.TestBase):
    def setUp(self):
        self.conf = base.mock_config(self)
        return super(TestSendMessage, self).setUp()

    def test_should_not_send_empty_message(self):
        instance = log_publisher.LogPublisher()
        instance._kafka_publisher.send_message = mock.Mock()

        instance.send_message({})

        self.assertFalse(instance._kafka_publisher.send_message.called)

    def test_should_raise_exception(self):
        instance = log_publisher.LogPublisher()
        instance._kafka_publisher.send_message = mock.Mock(
            side_effect=[exceptions.MessageQueueException(1, 1)]
        )

        msg = {
            'log': {
                'message': 1
            },
            'meta': {
                'tenantId': 1
            }
        }
        self.assertRaises(exceptions.MessageQueueException,
                          instance.send_message, msg)

    def test_should_send_message(self):
        instance = log_publisher.LogPublisher()
        instance._kafka_publisher.send_message = mock.Mock(name='send_message',
                                                           return_value={})
        instance._build_key = mock.Mock(name='_build_key',
                                        return_value='some_key')
        msg = {
            'log': {
                'message': 1,
                'application_type': 'monasca_log_api',
                'dimensions': [service.Dimension('disk_usage', 50),
                               service.Dimension('cpu_time', 50)]
            },
            'meta': {
                'tenantId': 1
            }
        }

        instance.send_message(msg)

        instance._kafka_publisher.send_message.assert_called_once_with(
            self.conf.conf.log_publisher.topics[0],
            'some_key',
            simplejson.dumps(msg))

    def test_should_send_message_multiple_topics(self):
        topics = ['logs', 'analyzer', 'tester']
        self.conf.config(topics=topics, group='log_publisher')

        instance = log_publisher.LogPublisher()
        instance._kafka_publisher.send_message = mock.Mock(name='send_message',
                                                           return_value={})
        instance._build_key = mock.Mock(name='_build_key',
                                        return_value='some_key')
        msg = {
            'log': {
                'message': 1,
                'application_type': 'monasca_log_api',
                'dimensions': [service.Dimension('disk_usage', 50),
                               service.Dimension('cpu_time', 50)]
            },
            'meta': {
                'tenantId': 1
            }
        }
        json_msg = simplejson.dumps(msg)

        instance.send_message(msg)

        self.assertEqual(len(topics),
                         instance._kafka_publisher.send_message.call_count)
        for topic in topics:
            instance._kafka_publisher.send_message.assert_any_call(
                topic,
                'some_key',
                json_msg)
