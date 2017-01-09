# Copyright 2015-2016 FUJITSU LIMITED
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

from tempest import clients

from monasca_log_api_tempest.services import log_api_v2_client
from monasca_log_api_tempest.services import log_api_v3_client
from monasca_log_api_tempest.services import log_search_client


class Manager(clients.Manager):
    def __init__(self, credentials=None):
        super(Manager, self).__init__(credentials)

        self.log_api_clients = {
            "v2": log_api_v2_client.LogApiV2Client(
                self.auth_provider,
                'logs_v2',
                None
            ),
            "v3": log_api_v3_client.LogApiV3Client(
                self.auth_provider,
                'logs',
                None
            )
        }
        self.log_search_client = log_search_client.LogsSearchClient(
            self.auth_provider,
            'logs-search',
            None
        )
