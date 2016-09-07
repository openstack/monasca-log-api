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
from oslo_log import log

from monasca_log_api.api import exceptions
from monasca_log_api.api import headers
from monasca_log_api.api import logs_api
from monasca_log_api.monitoring import metrics
from monasca_log_api.reference.common import validation
from monasca_log_api.reference.v3.common import bulk_processor
from monasca_log_api.reference.v3.common import helpers

LOG = log.getLogger(__name__)


class Logs(logs_api.LogsApi):

    VERSION = 'v3.0'
    SUPPORTED_CONTENT_TYPES = {'application/json'}

    def __init__(self):
        super(Logs, self).__init__()

        self._processor = bulk_processor.BulkProcessor(
            logs_in_counter=self._logs_in_counter,
            logs_rejected_counter=self._logs_rejected_counter
        )
        self._bulks_rejected_counter = self._statsd.get_counter(
            name=metrics.LOGS_BULKS_REJECTED_METRIC,
            dimensions=self._metrics_dimensions
        )

    def on_post(self, req, res):
        with self._logs_processing_time.time(name=None):
            try:
                validation.validate_payload_size(req)
                validation.validate_content_type(req,
                                                 Logs.SUPPORTED_CONTENT_TYPES)

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

            except Exception as ex:
                LOG.error('Entire bulk package has been rejected')
                LOG.exception(ex)

                self._bulks_rejected_counter.increment(value=1)

                raise ex

            self._bulks_rejected_counter.increment(value=0)
            self._logs_size_gauge.send(name=None,
                                       value=int(req.content_length))

            try:
                self._processor.send_message(
                    logs=log_list,
                    global_dimensions=global_dimensions,
                    log_tenant_id=tenant_id if tenant_id else cross_tenant_id
                )
            except Exception as ex:
                res.status = getattr(ex, 'status', falcon.HTTP_500)
                return

            res.status = falcon.HTTP_204

    @staticmethod
    def _get_global_dimensions(request_body):
        """Get the top level dimensions in the HTTP request body."""
        global_dims = request_body.get('dimensions', {})
        validation.validate_dimensions(global_dims)
        return global_dims

    @staticmethod
    def _get_logs(request_body):
        """Get the logs in the HTTP request body."""
        if 'logs' not in request_body:
            raise exceptions.HTTPUnprocessableEntity(
                'Unprocessable Entity Logs not found')
        return request_body['logs']
