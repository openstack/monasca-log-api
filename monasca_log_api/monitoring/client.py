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

import monascastatsd

from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)
CONF = cfg.CONF

_DEFAULT_HOST = '127.0.0.1'
_DEFAULT_PORT = 8125
_DEFAULT_BUFFER_SIZE = 50
_DEFAULT_DIMENSIONS = {
    'service': 'monitoring',
    'component': 'monasca-log-api'
}
_CLIENT_NAME = 'monasca'

monitoring_opts = [
    cfg.IPOpt('statsd_host',
              default=_DEFAULT_HOST,
              help=('IP address of statsd server, default to %s'
                    % _DEFAULT_HOST)),
    cfg.PortOpt('statsd_port',
                default=_DEFAULT_PORT,
                help='Port of statsd server, default to %d' % _DEFAULT_PORT),
    cfg.IntOpt('statsd_buffer',
               default=_DEFAULT_BUFFER_SIZE,
               required=True,
               help=('Maximum number of metric to buffer before sending, '
                     'default to %d' % _DEFAULT_BUFFER_SIZE)),
    cfg.DictOpt('dimensions')
]

monitoring_group = cfg.OptGroup(name='monitoring', title='monitoring')

cfg.CONF.register_group(monitoring_group)
cfg.CONF.register_opts(monitoring_opts, monitoring_group)


def get_client(dimensions=None):
    """Creates statsd client

    Creates monasca-statsd client using configuration from
    config file and supplied dimensions.

    Configuration is composed out of ::

        [monitoring]
        statsd_host = 192.168.10.4
        statsd_port = 8125
        statsd_buffer = 50

    Dimensions are appended to following dictionary ::

        {
            'service': 'monitoring',
            'component': 'monasca-log-api'
        }

    Note:
        Passed dimensions do not override those specified in
        dictionary above

    :param dict dimensions: Optional dimensions
    :return: statsd client
    :rtype: monascastatsd.Client
    """
    dims = _DEFAULT_DIMENSIONS.copy()
    if dimensions:
        for key, val in dimensions.items():
            if key not in _DEFAULT_DIMENSIONS:
                dims[key] = val
            else:
                LOG.warning('Cannot override fixed dimension %s=%s', key,
                            _DEFAULT_DIMENSIONS[key])

    connection = monascastatsd.Connection(
        host=CONF.monitoring.statsd_host,
        port=CONF.monitoring.statsd_port,
        max_buffer_size=CONF.monitoring.statsd_buffer
    )
    client = monascastatsd.Client(name=_CLIENT_NAME,
                                  connection=connection,
                                  dimensions=dims)

    LOG.debug('Created statsd client %s[%s] = %s:%d', _CLIENT_NAME, dims,
              CONF.monitoring.statsd_host, CONF.monitoring.statsd_port)

    return client
