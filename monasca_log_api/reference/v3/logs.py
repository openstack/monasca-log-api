# Copyright 2016 Hewlett Packard Enterprise Development Company, L.P.
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
from oslo_config import cfg
from oslo_log import log

from monasca_log_api.api import exceptions
from monasca_log_api.api import headers
from monasca_log_api.api import logs_api
from monasca_log_api.reference.common import log_publisher
from monasca_log_api.reference.common import model
from monasca_log_api.reference.common import validation
from monasca_log_api.reference.v3.common import helpers

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class Logs(logs_api.LogsApi):

    VERSION = 'v3.0'
    SUPPORTED_CONTENT_TYPES = {'application/json'}

    def __init__(self):
        super(Logs, self).__init__()
        self._log_publisher = log_publisher.LogPublisher()

    def on_post(self, req, res):
        validation.validate_payload_size(req)
        validation.validate_content_type(req, Logs.SUPPORTED_CONTENT_TYPES)

        cross_tenant_id = req.get_param('tenant_id')
        tenant_id = req.get_header(*headers.X_TENANT_ID)
        validation.validate_cross_tenant(
            tenant_id=tenant_id,
            cross_tenant_id=cross_tenant_id,
            roles=req.get_header(*headers.X_ROLES)
        )

        request_body = helpers.read_json_msg_body(req)
        log_list = self._get_logs(request_body)
        global_dimensions = self._get_global_dimensions(request_body)

        envelopes = []
        for log_element in log_list:
            try:
                LOG.trace('Processing log %s', log_element)

                validation.validate_log_message(log_element)

                dimensions = self._get_dimensions(log_element,
                                                  global_dimensions)
                envelope = self._create_log_envelope(tenant_id,
                                                     cross_tenant_id,
                                                     dimensions,
                                                     log_element)
                envelopes.append(envelope)

                LOG.trace('Log %s processed into envelope %s',
                          log_element,
                          envelope)
            except Exception as ex:
                LOG.error('Failed to process log %s', log_element)
                LOG.exception(ex)
                res.status = getattr(ex, 'status', falcon.HTTP_500)
                return

        self._send_logs(envelopes)
        res.status = falcon.HTTP_204

    def _get_dimensions(self, log_element, global_dims):
        """Get the dimensions in the log element."""
        local_dims = log_element.get('dimensions', {})
        if local_dims:
            validation.validate_dimensions(local_dims)
            if global_dims:
                dimensions = global_dims.copy()
                dimensions.update(local_dims)
            else:
                dimensions = local_dims
        else:
            dimensions = global_dims

        return dimensions

    def _get_global_dimensions(self, request_body):
        """Get the top level dimensions in the HTTP request body."""
        global_dims = request_body.get('dimensions', {})
        validation.validate_dimensions(global_dims)
        return global_dims

    def _get_logs(self, request_body):
        """Get the logs in the HTTP request body."""
        if 'logs' not in request_body:
            raise exceptions.HTTPUnprocessableEntity(
                'Unprocessable Entity Logs not found')
        return request_body['logs']

    def _create_log_envelope(self,
                             tenant_id,
                             cross_tenant_id,
                             dimensions=None,
                             log_element=None):
        """Create a log envelope and return it as a json string."""

        envelope = model.Envelope.new_envelope(
            log=log_element,
            tenant_id=tenant_id if tenant_id else cross_tenant_id,
            region=CONF.service.region,
            dimensions=dimensions
        )

        return envelope

    def _send_logs(self, logs):
        """Send the logs to Kafka."""
        try:
            self._log_publisher.send_message(logs)
        except Exception as ex:
            LOG.exception(ex)
            raise ex
