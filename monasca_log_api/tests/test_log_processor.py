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

from monasca_log_api.tests import base


class TestBulkProcessor(testing.TestBase):
    def setUp(self):
        self.conf = base.mock_config(self)
        return super(TestBulkProcessor, self).setUp()
