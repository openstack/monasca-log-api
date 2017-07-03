.. -*- rst -*-
..
      Copyright 2017 Fujitsu LIMITED

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

====
Logs
====

Accepts logs send from log-agents. Logs are basically raw lines,
as collected from physical resources, enriched with dimensions.

Send logs
=========

.. rest_method:: POST /v3.0/logs

Accepts multiple logs (i.e. bulk mode). Each log can be enriched with set
of dimensions. If necessary some of the dimensions can be specified as global
dimensions (that is particularly useful, to make request smaller,
if there is a lot of duplicates among each log entry dimensions)

.. rest_status_code:: success http_codes.yaml

   - 204

.. rest_status_code:: error http_codes.yaml

   - 400
   - 401
   - 403
   - 411
   - 413
   - 422: log_no_msg
   - 422: bad_envelope
   - 503

Request
-------

 .. rest_parameters:: parameters.yaml

    - dimensions: dimensions
    - logs: logs

**Example 1: Simple request with single log**

.. literalinclude:: ../../doc/api_samples/v3/req_single_log.json
   :language: javascript

**Example 2: Send multiple logs at once**

.. literalinclude:: ../../doc/api_samples/v3/req_multiple_logs.json
   :language: javascript

**Example 3: Specify global dimensions for each log entry**

.. literalinclude:: ../../doc/api_samples/v3/req_global_dims.json
   :language: javascript

Response
--------

No body content is returned on a successful POST
