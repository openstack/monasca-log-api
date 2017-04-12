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

import random
import string

from oslo_config import cfg
from tempest.common import credentials_factory as cred_factory
from tempest import test
from tempest import exceptions

from monasca_log_api_tempest import clients

CONF = cfg.CONF
_ONE_MB = 1024 * 1024  # MB


def _get_message_size(size_base):
    """Returns message size in number of characters.

    Method relies on UTF-8 where 1 character = 1 byte.

    """
    return int(round(size_base * _ONE_MB, 1))


_SMALL_MESSAGE_SIZE = _get_message_size(0.001)
_MEDIUM_MESSAGE_SIZE = _get_message_size(0.01)
_LARGE_MESSAGE_SIZE = _get_message_size(0.1)
_REJECTABLE_MESSAGE_SIZE = _get_message_size(1.1)


def generate_unique_message(message=None, size=50):
    letters = string.ascii_lowercase

    def rand(amount, space=True):
        space = ' ' if space else ''
        return ''.join((random.choice(letters + space) for _ in range(amount)))

    sid = rand(10, space=False)

    if not message:
        message = rand(size)
    return sid, sid + ' ' + message


def generate_small_message(message=None):
    return generate_unique_message(message, _SMALL_MESSAGE_SIZE)


def generate_medium_message(message=None):
    return generate_unique_message(message, _MEDIUM_MESSAGE_SIZE)


def generate_large_message(message=None):
    return generate_unique_message(message, _LARGE_MESSAGE_SIZE)


def generate_rejectable_message(message=None):
    return generate_unique_message(message, _REJECTABLE_MESSAGE_SIZE)


def _get_headers(headers=None, content_type="application/json"):
    if not headers:
        headers = {}
    headers.update({
        'Content-Type': content_type,
        'kbn-version': CONF.monitoring.kibana_version
    })
    return headers


def _get_data(message, content_type="application/json", version="v3"):
    if version == "v3":
        data = {
            'logs': [{
                'message': message
            }]
        }
    elif 'application/json' == content_type:
        data = {
            'message': message
        }
    return data


class BaseLogsTestCase(test.BaseTestCase):
    """Base test case class for all Monitoring API tests."""

    @classmethod
    def skip_checks(cls):
        super(BaseLogsTestCase, cls).skip_checks()

    @classmethod
    def resource_setup(cls):
        super(BaseLogsTestCase, cls).resource_setup()
        auth_version = CONF.identity.auth_version
        cred_provider = cred_factory.get_credentials_provider(
            cls.__name__,
            identity_version=auth_version)
        credentials = cred_provider.get_creds_by_roles(
            ['monasca-user', 'admin']).credentials
        cls.os = clients.Manager(credentials=credentials)

        cls.logs_clients = cls.os.log_api_clients
        cls.logs_search_client = cls.os.log_search_client

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except exceptions.EndpointNotFound:
                pass
