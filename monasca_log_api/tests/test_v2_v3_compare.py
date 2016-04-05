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

from falcon import testing
import mock
import ujson as json

from monasca_log_api.api import headers
from monasca_log_api.api import logs_api
from monasca_log_api.reference.v2 import logs as v2_logs
from monasca_log_api.reference.v3 import logs as v3_logs

from monasca_log_api.reference.common import model


class SameV2V3Output(testing.TestBase):
    @mock.patch('monasca_log_api.reference.common.log_publisher.LogPublisher')
    def test_send_identical_messages(self, publisher):
        # mocks only log publisher, so the last component that actually
        # sends data to kafka
        # case is to verify if publisher was called with same arguments
        # for both cases

        v2 = v2_logs.Logs()
        v3 = v3_logs.Logs()

        v2._kafka_publisher = publisher
        v3._log_publisher = publisher

        component = 'monasca-log-api'
        service = 'laas'
        hostname = 'kornik'
        tenant_id = 'ironMan'

        v2_dimensions = 'hostname:%s,service:%s' % (hostname, service)
        v3_dimensions = {
            'hostname': hostname,
            'component': component,
            'service': service
        }

        v2_body = {
            'message': 'test'
        }

        v3_body = {
            'logs': [
                {
                    'message': 'test',
                    'dimensions': v3_dimensions
                }
            ]
        }

        self.api.add_route('/v2.0', v2)
        self.api.add_route('/v3.0', v3)

        self.simulate_request(
            '/v2.0',
            method='POST',
            headers={
                headers.X_ROLES.name: logs_api.MONITORING_DELEGATE_ROLE,
                headers.X_DIMENSIONS.name: v2_dimensions,
                headers.X_APPLICATION_TYPE.name: component,
                headers.X_TENANT_ID.name: tenant_id,
                'Content-Type': 'application/json',
                'Content-Length': '100'
            },
            body=json.dumps(v2_body)
        )

        self.simulate_request(
            '/v3.0',
            method='POST',
            headers={
                headers.X_ROLES.name: logs_api.MONITORING_DELEGATE_ROLE,
                headers.X_TENANT_ID.name: tenant_id,
                'Content-Type': 'application/json',
                'Content-Length': '100'
            },
            body=json.dumps(v3_body)
        )

        self.assertEqual(2, publisher.call_count)

        # in v2 send_messages is called with single envelope
        v2_send_msg_arg = publisher.method_calls[0][1][0]

        # in v3 it is always called with list of envelopes
        v3_send_msg_arg = publisher.method_calls[1][1][0][0]

        self.maxDiff = None

        # at this point we know that both args should be identical
        self.assertEqual(type(v2_send_msg_arg), type(v3_send_msg_arg))
        self.assertIsInstance(v3_send_msg_arg, model.Envelope)
        self.assertDictEqual(v2_send_msg_arg, v3_send_msg_arg)
