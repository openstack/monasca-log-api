.. _configuration-files:

-------------------
Configuration files
-------------------

Overview of monasca-log-api's configuration files.

log-api.conf
------------

This is the main configuration file of monasca-log-api.
It can be located in several places. During startup,
monasca-log-api searches for it in the following directories:

* ``~/.monasca``
* ``~/``
* ``/etc/monasca``
* ``/etc``

Alternatively, you can roll with a multi-file-based configuration model.
In this case, monasca-log-api searches the configuration files
in the following directories:

* ``~/.monasca/monasca.conf.d/``
* ``~/.monasca/log-api.conf.d/``
* ``~/monasca.conf.d/``
* ``~/log-api.conf.d/``
* ``/etc/monasca/monasca.conf.d/``
* ``/etc/monasca/log-api.conf.d/``
* ``/etc/monasca.conf.d/``
* ``/etc/log-api.conf.d/``

Regardless of the location, the name of the main configuration file
should always be ``log-api.conf``. For files located
in ``.conf.d`` directories, the name is irrelevant, but it should
indicate the file content.

For example, when guring keystone communication. The
`keystonemiddleware <https://docs.openstack.org/keystonemiddleware/latest/>`_
configuration would be, therefore, located in, for example,
``/etc/log-api.conf.d/keystonemiddleware.conf``

A sample of this configuration file is also available
:ref:`here <sample-configuration-api>`

log-api-logging.conf
--------------------

This file contains the logging setup for monasca-log-api. It should be
referenced from ``log-api.conf`` using, for example,
the following code snippet::

    [DEFAULT]
    log_config_append = /etc/monasca/log-api-logging.conf

A sample of this configuration file is also available
:ref:`here <sample-configuration-logging>`

log-api-paste.ini
-----------------

This file contains the `PasteDeploy <http://pastedeploy.readthedocs.io/en/latest/>`_
configuration. It describes all pipelines that are running within a single
instance of monasca-log-api.

There is nothing you should try and modify in this file,
apart from enabling/disabling ``oslo_middleware.debug:Debug``.

To enable ``oslo_middleware.debug:Debug`` for ``Log v3`` pipeline,
``log-api-paste.ini`` should contain code similar to this one::

  [composite:main]
  use = egg:Paste#urlmap
  /v3.0: la_api_v3

  [pipeline:la_api_v3]
  pipeline = debug {{ other pipeline members }}

  [filter:debug]
  paste.filter_factory = oslo_middleware.debug:Debug.factory

This particular filter might be useful for examining the
WSGI environment during troubleshooting or local development.

