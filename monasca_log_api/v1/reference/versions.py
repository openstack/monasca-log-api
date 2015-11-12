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

from monasca_log_api.api import rest_utils
from monasca_log_api.api import versions_api

LOG = log.getLogger(__name__)
VERSIONS = {
    'v1.0': {
        'id': 'v1.0',
        'links': [
            {
                'rel': 'self',
                'href': ''
            },
            {
                'rel': 'links',
                'href': '/logs'
            }
        ],
        'status': 'CURRENT',
        'updated': "2013-03-06T00:00:00Z"
    }
}


class Versions(versions_api.VersionsAPI):
    def __init__(self):
        super(Versions, self).__init__()

    @staticmethod
    def handle_none_version_id(req, res, result):
        for version in VERSIONS:
            VERSIONS[version]['links'][0]['href'] = (
                req.uri.decode('utf8') + version)
            result['elements'].append(VERSIONS[version])
        res.body = rest_utils.as_json(result)
        res.status = falcon.HTTP_200

    @staticmethod
    def handle_version_id(req, res, version_id):
        if version_id in VERSIONS:
            VERSIONS[version_id]['links'][0]['href'] = (
                req.uri.decode(rest_utils.ENCODING)
            )
            for version in VERSIONS:
                VERSIONS[version]['links'][0]['href'] = (
                    req.uri.decode('utf8')
                )
            VERSIONS[version_id]['links'][1]['href'] = (
                req.uri.decode('utf8') +
                VERSIONS[version_id]['links'][1]['href']
            )
            res.body = rest_utils.as_json(VERSIONS[version_id])
            res.status = falcon.HTTP_200
        else:
            res.body = 'Invalid Version ID'
            res.status = falcon.HTTP_400

    def on_get(self, req, res, version_id=None):
        result = {
            'links': [{
                'rel': 'self',
                'href': req.uri.decode(rest_utils.ENCODING)
            }],
            'elements': []
        }
        if version_id is None:
            self.handle_none_version_id(req, res, result)
        else:
            self.handle_version_id(req, res, version_id)
