# Copyright 2015-2017 FUJITSU LIMITED
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

from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from testtools import matchers

from monasca_log_api_tempest.tests import base

_RETRY_COUNT = 15
_RETRY_WAIT = 2


class TestSingleLog(base.BaseLogsTestCase):
    def _run_and_wait(self, key, data, version,
                      content_type='application/json',
                      headers=None, fields=None):

        headers = base._get_headers(headers, content_type)

        def wait():
            return self.logs_search_client.count_search_messages(key,
                                                                 headers) > 0

        self.assertEqual(0, self.logs_search_client.count_search_messages(key,
                                                                          headers),
                         'Find log message in elasticsearch: {0}'.format(key))

        headers = base._get_headers(headers, content_type)
        data = base._get_data(data, content_type, version=version)

        client = self.logs_clients[version]
        response, _ = client.send_single_log(data, headers, fields)
        self.assertEqual(204, response.status)

        test_utils.call_until_true(wait, _RETRY_COUNT * _RETRY_WAIT,
                                   _RETRY_WAIT)
        response = self.logs_search_client.search_messages(key, headers)
        self.assertEqual(1, len(response))

        return response

    @decorators.attr(type="gate")
    def test_small_message(self):
        for ver in self.logs_clients:
            self._run_and_wait(*base.generate_small_message(), version=ver)

    @decorators.attr(type="gate")
    def test_medium_message(self):
        for ver in self.logs_clients:
            self._run_and_wait(*base.generate_medium_message(), version=ver)

    @decorators.attr(type="gate")
    def test_big_message(self):
        for ver in self.logs_clients:
            self._run_and_wait(*base.generate_large_message(), version=ver)

    @decorators.attr(type="gate")
    def test_small_message_multiline(self):
        for ver in self.logs_clients:
            sid, message = base.generate_small_message()
            self._run_and_wait(sid, message.replace(' ', '\n'), version=ver)

    @decorators.attr(type="gate")
    def test_medium_message_multiline(self):
        for ver in self.logs_clients:
            sid, message = base.generate_medium_message()
            self._run_and_wait(sid, message.replace(' ', '\n'), version=ver)

    @decorators.attr(type="gate")
    def test_big_message_multiline(self):
        for ver in self.logs_clients:
            sid, message = base.generate_large_message()
            self._run_and_wait(sid, message.replace(' ', '\n'), version=ver)

    @decorators.attr(type="gate")
    def test_send_header_application_type(self):
        sid, message = base.generate_unique_message()
        headers = {'X-Application-Type': 'application-type-test'}
        response = self._run_and_wait(sid, message, headers=headers,
                                      version="v2")
        self.assertEqual('application-type-test',
                         response[0]['_source']['component'])

    @decorators.attr(type="gate")
    def test_send_header_dimensions(self):
        sid, message = base.generate_unique_message()
        headers = {'X-Dimensions':
                       'server:WebServer01,environment:production'}
        response = self._run_and_wait(sid, message, headers=headers,
                                      version="v2")
        self.assertEqual('production', response[0]['_source']['environment'])
        self.assertEqual('WebServer01', response[0]['_source']['server'])

    @decorators.attr(type="gate")
    def test_send_cross_tenant(self):
        sid, message = base.generate_small_message()
        headers = {'X-Roles': 'admin, monitoring-delegate'}
        cross_tennant_id = '2106b2c8da0eecdb3df4ea84a0b5624b'
        fields = {'tenant_id': cross_tennant_id}
        response = self._run_and_wait(sid, message, version="v3",
                                      headers=headers, fields=fields)
        self.assertThat(response[0]['_source']['tenant'],
                        matchers.StartsWith(cross_tennant_id))

    # TODO(trebski) following test not passing - failed to retrieve
    # big message from elasticsearch

    # @decorators.attr(type='gate')
    # def test_should_truncate_big_message(self):
    #     message_size = base._get_message_size(0.9999)
    #     sid, message = base.generate_unique_message(size=message_size)
    #
    #     headers = base._get_headers(self.logs_clients.get_headers())
    #     response = self._run_and_wait(sid, message, headers=headers)
    #
    #     self.assertTrue(False, 'API should respond with 500')
