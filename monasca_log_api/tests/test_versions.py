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

import falcon

from monasca_log_api.app.controller import versions
from monasca_log_api.tests import base


def _get_versioned_url(version_id):
    return '/version/%s' % version_id


class TestApiVersions(base.BaseApiTestCase):

    def setUp(self):
        super(TestApiVersions, self).setUp()
        self.versions = versions.Versions()
        self.app.add_route("/", self.versions)
        self.app.add_route("/version/", self.versions)
        self.app.add_route("/version/{version_id}", self.versions)

    def test_should_fail_for_unsupported_version(self):
        unsupported_version = 'v5.0'
        uri = _get_versioned_url(unsupported_version)

        res = self.simulate_request(
            path=uri,
            method='GET',
            headers={
                'Content-Type': 'application/json'
            }
        )

        self.assertEqual(falcon.HTTP_400, res.status)

    def test_should_return_all_supported_versions(self):

        def _check_elements():
            self.assertIn('elements', response)
            elements = response.get('elements')
            self.assertIsInstance(elements, list)

            for el in elements:
                # do checkup by expected keys
                self.assertIn('id', el)
                self.assertItemsEqual([
                    u'id',
                    u'links',
                    u'status',
                    u'updated'
                ], el.keys())

                ver = el.get('id')
                self.assertIn(ver, expected_versions)

        def _check_global_links():
            self.assertIn('links', response)
            links = response.get('links')
            self.assertIsInstance(links, list)

            for link in links:
                self.assertIn('rel', link)
                key = link.get('rel')
                self.assertIn(key, expected_links_keys)
                href = link.get('href')
                self.assertTrue(href.startswith(expected_url))

        expected_versions = 'v2.0', 'v3.0'
        expected_links_keys = 'self', 'version', 'healthcheck'
        expected_protocol = 'http'
        expected_host = 'fakehost.com'
        expected_url = '{}://{}'.format(expected_protocol, expected_host)

        for expected_path in ['/', '/version']:
            res = self.simulate_request(
                path=expected_path,
                protocol=expected_protocol,
                host=expected_host,
                method='GET',
                headers={
                    'Content-Type': 'application/json'
                }
            )
            self.assertEqual(falcon.HTTP_200, res.status)

            response = res.json

            _check_elements()
            _check_global_links()

    def test_should_return_expected_version_id(self):
        expected_versions = 'v2.0', 'v3.0'
        for expected_version in expected_versions:
            uri = _get_versioned_url(expected_version)
            res = self.simulate_request(
                path=uri,
                method='GET',
                headers={
                    'Content-Type': 'application/json'
                },
            )
            self.assertEqual(falcon.HTTP_200, res.status)

            response = res.json
            self.assertIn('elements', response)
            self.assertIn('links', response)

            elements = response.get('elements')
            self.assertIsInstance(elements, list)
            self.assertEqual(1, len(elements))

            el = elements[0]
            ver = el.get('id')
            self.assertEqual(expected_version, ver)
