#
# Copyright 2016 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function
from keystoneclient.v2_0 import client
import sys


def get_token(url, cacert, username, password, tenant_name):
    if not username or not password:
        print('If token is not given, keystone_admin and keystone_admin_password must be given', file=sys.stderr)
        return False

    if not tenant_name:
        print('If token is not given, keystone_admin_project must be given', file=sys.stderr)
        return False

    kwargs = {
        'username': username,
        'password': password,
        'tenant_name': tenant_name,
        'auth_url': url,
        'cacert': cacert
    }

    key = client.Client(**kwargs)
    token = key.auth_token
    return token



def add_service_endpoint(key, name, description, type, url, region):
    """Add the Monasca service to the catalog with the specified endpoint, if it doesn't yet exist."""
    service_names = {service.name: service.id for service in key.services.list()}
    if name in service_names.keys():
        service_id = service_names[name]
    else:
        service = key.services.create(name=name, service_type=type, description=description)
        print("Created service '{}' of type '{}'".format(name, type))
        service_id = service.id

    for endpoint in key.endpoints.list():
        if endpoint.service_id == service_id:
            if endpoint.publicurl == url and endpoint.adminurl == url and endpoint.internalurl == url:
                return True
            else:
                key.endpoints.delete(endpoint.id)

    key.endpoints.create(region=region, service_id=service_id, publicurl=url, adminurl=url, internalurl=url)
    print("Added service endpoint '{}' at '{}'".format(name, url))
    return True


def add_monasca_service():
    return True


def main(argv):
    """ Get token if needed and then call methods to add tenants, users and roles """
    service_host = argv[0]
    url = 'http://' + service_host + ':35357/v2.0'

    token = None

    cacert = None

    if not token:
        username = argv[1]
        password = argv[2]
        tenant_name = argv[3]
        token = get_token(url, cacert, username, password, tenant_name)

    key = client.Client(token=token, endpoint=url, cacert=cacert)

    monasca_log_url = 'http://' + service_host + ':5607/v2.0'

    if not add_service_endpoint(key, 'logs', 'Monasca log service', 'logs', monasca_log_url, 'RegionOne'):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
