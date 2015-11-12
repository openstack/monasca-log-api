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

import falcon
import mock
import simplejson

from monasca_log_api.api import rest_utils as ru


class RestUtilsTest(unittest.TestCase):

    @mock.patch('io.IOBase')
    def test_should_read_text_for_plain_text(self, payload):
        raw_msg = 'Hello World'
        msg = u''.join(raw_msg)

        payload.read.return_value = raw_msg

        self.assertEqual(msg, ru.read_body(payload, 'text/plain'))

    @mock.patch('io.IOBase')
    def test_should_read_json_for_application_json(self, payload):
        raw_msg = u'{"path":"/var/log/messages","message":"This is message"}'
        json_msg = simplejson.loads(raw_msg, encoding='utf-8')

        payload.read.return_value = raw_msg

        self.assertEqual(json_msg, ru.read_body(payload, 'application/json'))

    @mock.patch('io.IOBase')
    def test_should_fail_read_text_for_application_json(self, payload):
        with self.assertRaises(falcon.HTTPBadRequest) as context:
            raw_msg = 'Hello World'
            payload.read.return_value = raw_msg
            ru.read_body(payload, 'application/json')

        self.assertEqual(context.exception.title,
                         'Failed to read body as json')
