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

from tempest_lib import exceptions
from monasca_log_api_tempest.tests import base


class TestLogApiConstraints(base.BaseLogsTestCase):
    @test.attr(type='gate')
    def test_should_reject_if_content_length_missing(self):
        headers = base._get_headers()
        try:
            self.logs_client.custom_request('POST', headers, None)
        except exceptions.UnexpectedResponseCode as urc:
            self.assertIn('411', str(urc))  # Only possible way to detect that
            return

        self.assertTrue(False, 'API should respond with 411')

    @test.attr(type='gate')
    def test_should_reject_if_content_type_missing(self):
        headers = base._get_headers(content_type='')
        try:
            self.logs_client.custom_request('POST', headers, '{}')
        except exceptions.BadRequest as urc:
            self.assertEqual(400, urc.resp.status)
            return

        self.assertTrue(False, 'API should respond with 400')

    @test.attr(type='gate')
    def test_should_reject_if_wrong_content_type(self):
        headers = base._get_headers(content_type='video/3gpp')
        try:
            self.logs_client.custom_request('POST', headers, '{}')
        except exceptions.InvalidContentType as urc:
            self.assertEqual(415, urc.resp.status)
            return

        self.assertTrue(False, 'API should respond with 400')

    @test.attr(type='gate')
    def test_should_reject_too_big_message(self):
        _, message = base.generate_rejectable_message()
        headers = base._get_headers(self.logs_client.get_headers())
        try:
            self.logs_client.send_single_log(message, headers)
        except exceptions.OverLimit as urc:
            self.assertEqual(413, urc.resp.status)
            return

        self.assertTrue(False, 'API should respond with 413')

    @test.attr(type='gate')
    def test_should_reject_too_big_message_multiline(self):
        _, message = base.generate_rejectable_message()
        message = message.replace(' ', '\n')
        headers = base._get_headers(self.logs_client.get_headers())
        try:
            self.logs_client.send_single_log(message, headers)
        except exceptions.OverLimit as urc:
            self.assertEqual(413, urc.resp.status)
            return

        self.assertTrue(False, 'API should respond with 413')

    @test.attr(type='gate')
    def test_should_accept_message_but_reject_after_adding_metadata(self):
        _, message = base.generate_unique_message(
            size=base._get_message_size(0.9999))
        headers = base._get_headers(self.logs_client.get_headers())
        data = base._get_data(message)

        try:
            self.logs_client.send_single_log(data, headers)
        except exceptions.ServerFault as urc:
            self.assertEqual(500, urc.resp.status)
            msg = urc.resp_body.get('title', None)
            # in Java that is under message
            if msg is None:
                msg = urc.resp_body.get('message', None)
            self.assertIsNotNone(msg, 'Should get status message')
            self.assertEqual('Envelope size exceeded', msg)
            return

        self.assertTrue(False, 'API should respond with 500')
