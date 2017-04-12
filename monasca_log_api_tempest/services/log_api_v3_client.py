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

from oslo_serialization import jsonutils as json
from six.moves.urllib.parse import urlencode
from tempest.lib.common import rest_client


class LogApiV3Client(rest_client.RestClient):

    _uri = "/logs"

    def __init__(self, auth_provider, service, region):
        super(LogApiV3Client, self).__init__(
            auth_provider,
            service,
            region
        )

    def get_version(self):
        resp, response_body = self.send_request('GET', '/')
        return resp, response_body

    def send_single_log(self, log, headers=None, fields=None):
        default_headers = {
            'X-Tenant-Id': 'b4265b0a48ae4fd3bdcee0ad8c2b6012',
            'X-Roles': 'admin',
        }
        default_headers.update(headers)
        msg = json.dumps(log)
        uri = LogApiV3Client._uri

        if fields:
            uri += '?' + urlencode(fields)

        resp, body = self.post(uri, msg, default_headers)

        return resp, body

    def custom_request(self, method, headers=None, body=None):
        self.request(method=method, url=LogApiV3Client._uri, headers=headers, body=body)
