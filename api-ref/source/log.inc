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
Log
====

Accepts just a single log entry sent from log-agent of another client.
Can work with logs specified as json (application/json) and text (text/plain)

Send logs
=========

.. rest_method:: POST /v2.0/log/single

Accepts single log entry.

.. rest_status_code:: success http_codes.yaml

   - 204

.. rest_status_code:: error http_codes.yaml

   - 422: no_dims
   - 422: app_type_too_long
   - 422: dim_name_too_long
   - 422: dim_name_underscore
   - 422: dim_name_forbidden_chars
   - 422: dim_name_empty
   - 422: dim_value_too_long
   - 422: dim_value_empty
   - 422: log_no_msg
   - 422: bad_envelope
   - 503

Request
-------

 .. rest_parameters:: parameters.yaml

    - log_json: log_json
    - log_text: log_text
    - X_Dimensions: X_Dimensions
    - X_Application_Type: X_Application_Type

**Example 1: Simple request with single log (json)**

.. literalinclude:: ../../doc/api_samples/v2/req_json.json
   :language: javascript

**Example 2: Simple request with single log (text)**

.. literalinclude:: ../../doc/api_samples/v2/req_text.txt
   :language: text


Response
--------

No body content is returned on a successful POST
