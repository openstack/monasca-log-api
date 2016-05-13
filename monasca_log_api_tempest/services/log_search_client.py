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
from tempest.lib.common import rest_client


class LogsSearchClient(rest_client.RestClient):
    uri_prefix = "/elasticsearch"

    def __init__(self, auth_provider, service, region):
        super(LogsSearchClient, self).__init__(
            auth_provider,
            service,
            region,
        )

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

    def count_search_messages(self, message, headers):
        return len(self.search_messages(message, headers))

    def search_messages(self, message, headers):
        uri = '_msearch'
        body = """
               {"index" : "*", "search_type" : "dfs_query_then_fetch"}
               {"query" : {"match" : {"message":" """+message+""" "}}}
        """
        response, body = self.post(self._uri(uri), body, headers)
        self.expected_success(200, response.status)
        body = self.deserialize(body)
        return body['responses'][0].get('hits', {}).get('hits', [])

    def _uri(self, url):
        return '{}/{}'.format(self.uri_prefix, url)
