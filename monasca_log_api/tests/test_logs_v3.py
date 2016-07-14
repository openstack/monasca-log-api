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

import random
import string
import unittest

from falcon import testing
import mock
import ujson as json

from monasca_log_api.api import exceptions as log_api_exceptions
from monasca_log_api.api import headers
from monasca_log_api.api import logs_api
from monasca_log_api.reference.v3 import logs


ENDPOINT = '/logs'
TENANT_ID = 'bob'


def _init_resource(test):
    resource = logs.Logs()
    test.api.add_route(ENDPOINT, resource)
    return resource


def _generate_unique_message(size):
    letters = string.ascii_lowercase

    def rand(amount, space=True):
        space = ' ' if space else ''
        return ''.join((random.choice(letters + space) for _ in range(amount)))

    return rand(size)


def _generate_v3_payload(log_count):
    v3_logs = [{
                   'message': _generate_unique_message(100),
                   'dimensions': {
                       'hostname': 'host_%d' % it,
                       'component': 'component_%d' % it,
                       'service': 'service_%d' % it
                   }
               } for it in xrange(log_count)]
    v3_body = {
        'dimensions': {
            'origin': __name__
        },
        'logs': v3_logs
    }

    return v3_body, v3_logs


class TestLogsVersion(unittest.TestCase):
    @mock.patch('monasca_log_api.reference.v3.logs.log_publisher'
                '.LogPublisher')
    def test_should_return_v3_as_version(self, _):
        logs_resource = logs.Logs()
        self.assertEqual('v3.0', logs_resource.version)


class TestLogsMonitoring(testing.TestBase):

    @mock.patch('monasca_log_api.reference.common.log_publisher.LogPublisher')
    def test_monitor_bulk_rejected(self, _):
        resource = _init_resource(self)

        resource._logs_in_counter = in_counter = mock.Mock()
        resource._logs_rejected_counter = rejected_counter = mock.Mock()
        resource._bulks_rejected_counter = bulk_counter = mock.Mock()
        resource._logs_size_gauge = size_gauge = mock.Mock()

        resource._get_logs = mock.Mock(
            side_effect=log_api_exceptions.HTTPUnprocessableEntity(''))

        log_count = 1
        v3_body, _ = _generate_v3_payload(log_count)
        payload = json.dumps(v3_body)
        content_length = len(payload)

        self.simulate_request(
            ENDPOINT,
            method='POST',
            headers={
                headers.X_ROLES.name: logs_api.MONITORING_DELEGATE_ROLE,
                headers.X_TENANT_ID.name: TENANT_ID,
                'Content-Type': 'application/json',
                'Content-Length': str(content_length)
            },
            body=payload
        )

        self.assertEqual(1, bulk_counter.increment.call_count)
        self.assertEqual(0, in_counter.increment.call_count)
        self.assertEqual(0, rejected_counter.increment.call_count)
        self.assertEqual(0, size_gauge.send.call_count)

    @mock.patch('monasca_log_api.reference.common.log_publisher.LogPublisher')
    def test_monitor_not_all_logs_ok(self, _):
        resource = _init_resource(self)

        resource._logs_in_counter = in_counter = mock.Mock()
        resource._logs_rejected_counter = rejected_counter = mock.Mock()
        resource._bulks_rejected_counter = bulk_counter = mock.Mock()
        resource._logs_size_gauge = size_gauge = mock.Mock()

        log_count = 5
        reject_logs = 1
        v3_body, _ = _generate_v3_payload(log_count)
        payload = json.dumps(v3_body)
        content_length = len(payload)

        side_effects = [{} for __ in xrange(log_count - reject_logs)]
        side_effects.append(log_api_exceptions.HTTPUnprocessableEntity(''))

        resource._get_dimensions = mock.Mock(side_effect=side_effects)

        self.simulate_request(
            ENDPOINT,
            method='POST',
            headers={
                headers.X_ROLES.name: logs_api.MONITORING_DELEGATE_ROLE,
                headers.X_TENANT_ID.name: TENANT_ID,
                'Content-Type': 'application/json',
                'Content-Length': str(content_length)
            },
            body=payload
        )

        self.assertEqual(1, bulk_counter.increment.call_count)
        self.assertEqual(0,
                         bulk_counter.increment.mock_calls[0][2]['value'])

        self.assertEqual(0, in_counter.increment.call_count)

        self.assertEqual(1, rejected_counter.increment.call_count)
        self.assertEqual(log_count,
                         rejected_counter.increment.mock_calls[0][2]['value'])

        self.assertEqual(1, size_gauge.send.call_count)
        self.assertEqual(content_length,
                         size_gauge.send.mock_calls[0][2]['value'])

    @mock.patch('monasca_log_api.reference.common.log_publisher.LogPublisher')
    def test_monitor_all_logs_ok(self, _):
        resource = _init_resource(self)

        resource._logs_in_counter = in_counter = mock.Mock()
        resource._logs_rejected_counter = rejected_counter = mock.Mock()
        resource._bulks_rejected_counter = bulk_counter = mock.Mock()
        resource._logs_size_gauge = size_gauge = mock.Mock()

        resource._send_logs = mock.Mock()

        log_count = 10

        v3_body, _ = _generate_v3_payload(log_count)

        payload = json.dumps(v3_body)
        content_length = len(payload)
        self.simulate_request(
            ENDPOINT,
            method='POST',
            headers={
                headers.X_ROLES.name: logs_api.MONITORING_DELEGATE_ROLE,
                headers.X_TENANT_ID.name: TENANT_ID,
                'Content-Type': 'application/json',
                'Content-Length': str(content_length)
            },
            body=payload
        )

        self.assertEqual(1, bulk_counter.increment.call_count)
        self.assertEqual(0,
                         bulk_counter.increment.mock_calls[0][2]['value'])

        self.assertEqual(1, in_counter.increment.call_count)
        self.assertEqual(log_count,
                         in_counter.increment.mock_calls[0][2]['value'])

        self.assertEqual(0, rejected_counter.increment.call_count)

        self.assertEqual(1, size_gauge.send.call_count)
        self.assertEqual(content_length,
                         size_gauge.send.mock_calls[0][2]['value'])
