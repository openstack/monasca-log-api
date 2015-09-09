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

import os
from wsgiref import simple_server

import falcon
from oslo_config import cfg
from oslo_log import log
import paste.deploy
import simport

LOG = log.getLogger(__name__)
CONF = cfg.CONF

dispatcher_opts = [
    cfg.StrOpt('versions',
               default=None,
               help='Versions'),
    cfg.StrOpt('logs',
               default=None,
               help='Logs')
]
dispatcher_group = cfg.OptGroup(name='dispatcher', title='dispatcher')
CONF.register_group(dispatcher_group)
CONF.register_opts(dispatcher_opts, dispatcher_group)


def launch(conf, config_file='/etc/monasca/log-api-config.conf'):
    if conf and 'config_file' in conf:
        config_file = conf.get('config_file')

    log.register_options(CONF)
    log.set_defaults()
    CONF(args=[],
         project='monasca_log_api',
         default_config_files=[config_file])
    log.setup(CONF, 'monasca_log_api')

    app = falcon.API()

    load_versions_resource(app)
    load_logs_resource(app)

    LOG.debug('Dispatcher drivers have been added to the routes!')

    return app


def load_logs_resource(app):
    logs = simport.load(CONF.dispatcher.logs)()
    app.add_route('/v1.0/logs/single', logs)


def load_versions_resource(app):
    versions = simport.load(CONF.dispatcher.versions)()
    app.add_route("/", versions)
    app.add_route("/{version_id}", versions)


if __name__ == '__main__':

    base_path = '%s/..' % os.getcwd()
    global_conf = {'config_file': (
        '%s/%s' % (base_path, '/etc/monasca/log-api-config.conf'))}

    wsgi_app = (
        paste.deploy.loadapp(
            'config:etc/monasca/log-api-config.ini',
            relative_to=base_path,
            global_conf=global_conf
        )
    )

    httpd = simple_server.make_server('127.0.0.1', 8080, wsgi_app)
    httpd.serve_forever()
