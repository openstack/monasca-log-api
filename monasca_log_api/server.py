# Copyright 2015 kornicameister@gmail.com
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

import os
from wsgiref import simple_server

import falcon
from monasca_common.simport import simport
from oslo_config import cfg
from oslo_log import log
import paste.deploy

from monasca_log_api import uri_map

LOG = log.getLogger(__name__)
CONF = cfg.CONF

dispatcher_opts = [
    cfg.StrOpt('versions',
               default=None,
               required=True,
               help='Versions endpoint'),
    cfg.StrOpt('logs',
               default=None,
               required=True,
               help='Logs endpoint'),
    cfg.StrOpt('healthchecks',
               default=None,
               required=True,
               help='Healthchecks endpoint'),
    cfg.StrOpt('logs_v3',
               default=None,
               help='Logs')
]
dispatcher_group = cfg.OptGroup(name='dispatcher', title='dispatcher')
CONF.register_group(dispatcher_group)
CONF.register_opts(dispatcher_opts, dispatcher_group)
log.register_options(CONF)


def launch(conf, config_file='/etc/monasca/log-api-config.conf'):
    if conf and 'config_file' in conf:
        config_file = conf.get('config_file')

    log.set_defaults()
    CONF(args=[],
         project='monasca_log_api',
         default_config_files=[config_file])
    log.setup(CONF, 'monasca_log_api')

    app = falcon.API()

    load_versions_resource(app)
    load_logs_resource(app)
    load_healthcheck_resource(app)

    LOG.debug('Dispatcher drivers have been added to the routes!')

    return app


def load_healthcheck_resource(app):
    healthchecks = simport.load(CONF.dispatcher.healthchecks)()
    app.add_route(uri_map.HEALTHCHECK_URI, healthchecks)


def load_logs_resource(app):
    logs = simport.load(CONF.dispatcher.logs)()
    app.add_route(uri_map.V2_LOGS_URI, logs)

    logs_v3 = simport.load(CONF.dispatcher.logs_v3)()
    app.add_route(uri_map.V3_LOGS_URI, logs_v3)


def load_versions_resource(app):
    versions = simport.load(CONF.dispatcher.versions)()
    app.add_route("/version", versions)
    app.add_route("/version/{version_id}", versions)


def get_wsgi_app(config_base_path=None):
    if config_base_path is None:
        config_base_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), '../etc/monasca')
    global_conf = {'config_file': (
        os.path.join(config_base_path, 'log-api-config.conf'))}

    wsgi_app = (
        paste.deploy.loadapp(
            'config:log-api-config.ini',
            relative_to=config_base_path,
            global_conf=global_conf
        )
    )
    return wsgi_app

if __name__ == '__main__':
    wsgi_app = get_wsgi_app()
    httpd = simple_server.make_server('127.0.0.1', 5607, wsgi_app)
    httpd.serve_forever()
