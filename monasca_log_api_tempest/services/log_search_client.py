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
from tempest.common import service_client


class LogsSearchClient(service_client.ServiceClient):
    uri_prefix = "/elasticsearch"

    @staticmethod
    def deserialize(body):
        return json.loads(body.replace("\n", ""))

    @staticmethod
    def serialize(body):
        return json.dumps(body)

    def get_metadata(self):
        uri = "/"

        response, body = self.get(self._uri(uri))
        self.expected_success(200, response.status)

        if body:
            body = self.deserialize(body)
        return response, body

    def count_search_messages(self, message):
        return len(self.search_messages(message))

    def search_messages(self, message):
        uri = '_search'
        body = self.serialize(dict(
            query=dict(
                term=dict(message=message)
            )
        ))
        response, body = self.post(self._uri(uri), body)
        self.expected_success(200, response.status)
        body = self.deserialize(body)
        return body.get('hits', {}).get('hits', [])

    def _uri(self, url):
        return '{}/{}'.format(self.uri_prefix, url)
