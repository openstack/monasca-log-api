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

from tempest.lib import decorators
from tempest.lib import exceptions

from monasca_log_api_tempest.tests import base


class TestLogApiConstraints(base.BaseLogsTestCase):
    @decorators.attr(type='gate')
    def test_should_reject_if_body_is_empty(self):
        headers = base._get_headers()
        for cli in self.logs_clients.itervalues():
            try:
                cli.custom_request('POST', headers, None)
            except exceptions.UnprocessableEntity as urc:
                # depending on the actual server (for example gunicorn vs mod_wsgi)
                # monasca-log-api may return a different error code
                self.assertTrue(urc.resp.status in [411, 422])
                return

            self.assertTrue(False, 'API should respond with an error')

    @decorators.attr(type='gate')
    def test_should_reject_if_content_type_missing(self):
        headers = base._get_headers(content_type='')
        for cli in self.logs_clients.itervalues():
            try:
                cli.custom_request('POST', headers, '{}')
            except exceptions.BadRequest as urc:
                self.assertEqual(400, urc.resp.status)
                return

            self.assertTrue(False, 'API should respond with 400')

    @decorators.attr(type='gate')
    def test_should_reject_if_wrong_content_type(self):
        headers = base._get_headers(content_type='video/3gpp')
        for cli in self.logs_clients.itervalues():
            try:
                cli.custom_request('POST', headers, '{}')
            except exceptions.InvalidContentType as urc:
                self.assertEqual(415, urc.resp.status)
                return

            self.assertTrue(False, 'API should respond with 400')

    @decorators.attr(type='gate')
    def test_should_reject_too_big_message(self):
        _, message = base.generate_rejectable_message()
        headers = base._get_headers(self.logs_clients["v3"].get_headers())
        # Add 'Connection: Keep-Alive' to send large message before
        # connection is closed by client. In class ClosingHttp is added
        # header 'connection:close' (which will cause closing socket before sending whole message).
        # Data are send in small TCP packages.
        # Without this header set to Keep-Alive Tempest lib will try to retry connection and finally
        # raise ProtocolError.
        headers.update({'Connection': 'Keep-Alive'})
        for ver, cli in self.logs_clients.items():
            data = base._get_data(message, version=ver)
            try:
                cli.send_single_log(data, headers)
            except exceptions.OverLimit as urc:
                self.assertEqual(413, urc.resp.status)
                return

            self.assertTrue(False, 'API should respond with 413')

    @decorators.attr(type='gate')
    def test_should_reject_too_big_message_multiline(self):
        _, message = base.generate_rejectable_message()
        message = message.replace(' ', '\n')
        headers = base._get_headers(self.logs_clients["v3"].get_headers())
        # Add Connection: Keep-Alive to send large message before
        # connection is closed by cli. In class ClosingHttp is added
        # header connection:close (which will cause closing socket before sending whole message).
        # Data are send in small TCP packages.
        # Without this header set to Keep-Alive Tempest lib will try to retry connection and finally
        # raise ProtocolError.
        headers.update({'Connection': 'Keep-Alive'})
        for ver, cli in self.logs_clients.items():
            data = base._get_data(message, version=ver)
            try:
                cli.send_single_log(data, headers)
            except exceptions.OverLimit as urc:
                self.assertEqual(413, urc.resp.status)
                return

            self.assertTrue(False, 'API should respond with 413')
