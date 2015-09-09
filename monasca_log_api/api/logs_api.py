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

import falcon
from oslo_log import log

LOG = log.getLogger(__name__)

MONITORING_DELEGATE_ROLE = 'monitoring-delegate'


class LogsApi(object):
    def __init__(self):
        super(LogsApi, self).__init__()
        LOG.info('Initializing LogsApi!')

    def on_post(self, req, res):
        res.status = falcon.HTTP_501
