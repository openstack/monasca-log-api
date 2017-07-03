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

===========
Healthcheck
===========

The *Monasca Log API* comes with a built-in health check mechanism.
It is available in two flavors (simple and complex).

Simple check
============

The simple check only returns response only if API is up
and running. It does not return any data because it is accessible only
for ```HEAD``` requests.

.. rest_method:: HEAD /healthcheck

.. rest_status_code:: success http_codes.yaml

   - 204: la_up

Complex check
=============

# TODO(trebskit) add note to api-guide about peripheral checks

The complex check not only returns a response with success code if API
is up and running but it also verifies if peripheral components are
in expected condition.

.. rest_method:: GET /healthcheck

.. rest_status_code:: success http_codes.yaml

   - 200: la_up

.. rest_status_code:: error http_codes.yaml

   - 503: no_health
