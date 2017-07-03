..
    monasca-log-api documentation master file
    Copyright 2017 FUJITSU LIMITED

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.

.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`mandatory_tox_env`: https://github.com/openstack/monasca-log-api/blob/master/tox.ini#L2

===
Tox
===

**monasca-log-api** uses `tox`_ to wrap up all the activities around
testing and linting the codebase.

List of environments
====================

There is a rather large number of tox environments that **monasca-log-api**
is using. If necessary they can be enlisted with::

  tox -a -v

An output will be similar to this::

  default environments:
  py27          -> Runs unit test using Python2.7
  py35          -> Runs unit test using Python3.5
  pep8          -> Runs set of linters against codebase (flake8, bandit,
                   bashate, checkniceness)
  cover         -> Calculates code coverage

  additional environments:
  api-guide     -> Called from CI scripts to test and publish the API Guide
  api-ref       -> Called from CI scripts to test and publish the API Ref
  apidocs       -> Generates codebase documentation
  bandit        -> [no description]
  bashate       -> Validates (pep8-like) devstack plugins
  checkjson     -> Validates all json samples inside doc folder
  checkniceness -> Validates (pep-like) documenation
  debug         -> Allows to run unit-test with debug mode enabled
  docs          -> Builds api-ref, api-guide, releasenotes and doc
  flake8        -> [no description]
  releasenotes  -> Called from CI script to test and publish the Release Notes
  venv          -> [no description]


Running tox
===========

Running tox is as simple as::

  tox

That will run all **mandatory** (for details refer to `mandatory_tox_env`_)
environments. Having them passed is *a must have*.

Running specific environments
=============================

If you require to run specific environments, please use::

  tox -e api-ref,api-guide,releasenotes

Result of which will be having all documentations sub-components generated
and ready in local dev environment.
