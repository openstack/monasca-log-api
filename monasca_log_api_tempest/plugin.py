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

import os

from tempest import config
from tempest.test_discover import plugins

from monasca_log_api_tempest import config as config_log_api

_ROOT_PCKG_NAME = "monasca_log_api_tempest"


class MonascaLogApiTempestPlugin(plugins.TempestPlugin):
    def load_tests(self):
        base_path = os.path.split(os.path.dirname(
            os.path.abspath(__file__)))[0]
        test_dir = "%s/tests" % _ROOT_PCKG_NAME
        full_test_dir = os.path.join(base_path, test_dir)
        return full_test_dir, base_path

    def register_opts(self, conf):
        config.register_opt_group(
            conf,
            config_log_api.service_available_group,
            config_log_api.ServiceAvailableGroup
        )
        config.register_opt_group(conf,
                                  config_log_api.monitoring_group,
                                  config_log_api.MonitoringGroup)

    def get_opt_lists(self):
        return [(config_log_api.monitoring_group.name,
                 config_log_api.MonitoringGroup)]
