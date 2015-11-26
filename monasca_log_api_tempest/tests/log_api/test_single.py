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

from tempest import test

from monasca_log_api_tempest.tests import base

_RETRY_COUNT = 15
_RETRY_WAIT = 2


class TestSingleLog(base.BaseLogsTestCase):
    def _run_and_wait(self, key, data, content_type='application/json',
                      headers=None):
        def wait():
            return self.logs_search_client.count_search_messages(key) > 0

        self.assertEqual(0, self.logs_search_client.count_search_messages(key),
                         'Find log message in elasticsearch: {0}'.format(key))

        headers = base._get_headers(headers, content_type)
        data = base._get_data(data, content_type)

        response, _ = self.logs_client.send_single_log(data, headers)
        self.assertEqual(204, response.status)

        test.call_until_true(wait, _RETRY_COUNT, _RETRY_WAIT)
        response = self.logs_search_client.search_messages(key)
        self.assertEqual(1, len(response))

        return response

    @test.attr(type="gate")
    def test_small_message(self):
        self._run_and_wait(*base.generate_small_message())

    @test.attr(type="gate")
    def test_medium_message(self):
        self._run_and_wait(*base.generate_medium_message())

    @test.attr(type="gate")
    def test_big_message(self):
        self._run_and_wait(*base.generate_large_message())

    @test.attr(type="gate")
    def test_small_message_multiline(self):
        sid, message = base.generate_small_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @test.attr(type="gate")
    def test_medium_message_multiline(self):
        sid, message = base.generate_medium_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @test.attr(type="gate")
    def test_big_message_multiline(self):
        sid, message = base.generate_large_message()
        self._run_and_wait(sid, message.replace(' ', '\n'))

    @test.attr(type="gate")
    def test_send_header_application_type(self):
        sid, message = base.generate_unique_message()
        headers = {'X-Application-Type': 'application-type-test'}
        response = self._run_and_wait(sid, message, headers=headers)
        self.assertEqual('application-type-test',
                         response[0]['_source']['application_type'])

    @test.attr(type="gate")
    def test_send_header_dimensions(self):
        sid, message = base.generate_unique_message()
        headers = {'X-Dimensions': 'server:WebServer01,environment:production'}
        response = self._run_and_wait(sid, message, headers=headers)
        self.assertEqual('production', response[0]['_source']['environment'])
        self.assertEqual('WebServer01', response[0]['_source']['server'])
