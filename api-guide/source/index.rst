..
      Copyright 2014-2017 Fujitsu LIMITED

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

===============
Monasca Log API
===============

The monasca-log-api project has a RESTful HTTP service called the
Monasca Log API. Through this API users are able to send logs from entire
cloud.

This guide covers the concepts in the Monasca Log API.
For a full reference listing, please see:
`Monasca Log API Reference <https://developer.openstack.org/api-ref/monitoring-log-api/>`__.

We welcome feedback, comments, and bug reports at
`storyboard/monasca <https://storyboard.openstack.org/#!/project_group/59>`__.

Intended audience
=================

This guide assists software developers who want to develop applications
using the Monasca Log API. To use this information, you should
have access to an account from an OpenStack Compute provider, or have
access to your own deployment, and you should also be familiar with the
following concepts:

*  Monasca services
*  RESTful HTTP services
*  HTTP/1.1
*  JSON data serialization formats

End User and Operator APIs
==========================

The Log API includes all end user and operator API calls.
The API works with keystone and, at the monent, uses custom RBAC to
enforce API security.

API Versions
============

Following the Newton release, every Nova deployment should have
the following endpoints:

* / - list of available versions
* /v2.0 - the first version, permitted only single log to be send per request
* /v3.0 - the next version, allows sending multiple logs at once

Contents
========

.. toctree::
    :maxdepth: 2

    general_info
    logs

