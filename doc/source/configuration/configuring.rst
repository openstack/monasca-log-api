.. _basic-configuration:

-----------
Configuring
-----------

monasca-log-api has several configuration options. Some of them
are inherited from oslo libraries, others can be found in the monasca-log-api
codebase.

The entire configuration of monasca-log-api is defined in
configuration files.

.. note:: This is intended behaviour. One of possible ways to deploy
    monasca-log-api is to use **gunicorn**. Unfortunately gunicorn's
    argument parsing clashes with oslo's argument parsing.
    This means that gunicorn reports the CLI options of
    oslo as unknown, and vice versa.

There are 3 configuration files. For more details on the configuration
options, see :ref:`here <configuration-files>`.

Configuring Keystone Authorization
----------------------------------

Keystone authorization (i.e. verification of the token associated
with a request) is a critical part of monasca-log-api.
It prevents from unauthorized access and provides the isolation
needed for multi-tenancy.

The configuration for ``keystonemiddleware`` should either be provided in
``log-api.conf`` or in a file in one of the configuration directories.
For more details about configuration options, check
`here <https://docs.openstack.org/keystonemiddleware/latest/middlewarearchitecture.html#configuration>`_.

Configuring Log Publishing
--------------------------

monasca-log-api sends all logs to the Kafka Message Queue.
Proper configuration should include:

* ``kafka_url`` - comma-delimited list of Kafka brokers
* ``topics`` - names of the topics to which the logs will be pushed to
* ``max_message_size`` - maximum message size that can be posted a topic

The configuration for ``log_publisher`` should either be provided in
``log-api.conf`` or in a file in one of the configuration directories.

Configuring Healthcheck
-----------------------

Healthcheck is an essential part of monasca-log-api.
It allows sending HTTP requests and getting knowledge about the
availability of the API. Configuration of healthcheck includes:

* ``kafka_url`` - comma-delimited list of Kafka brokers
* ``kafka_topics`` - list of topics that existence is verified by healthcheck

The configuration for ``kafka_healthcheck`` should either be provided in
``log-api.conf`` or in a file in one of the configuration directories.

Configuring Monitoring
----------------------

monasca-log-api is capable of self-monitoring. This is achieved
through `monasca-statsd <https://github.com/openstack/monasca-statsd>`_.
It assumes that there is monasca-agent available on the system node and
that statsd-server has been launched.

There are several options you may want to tweak if necessary:

* ``statsd_host``- the host statsd-server is bound to
* ``statsd_port``- the port statsd-server is bound to
* ``statsd_buffer`` - the amount of metrics to buffer in memory before sending
  any
* ``dimensions`` - additional dimensions to be sent with all
  metrics for this monasca-log-api instance

The configuration for ``monitoring`` should either be provided in
``log-api.conf`` or in a file in one of the configuration directories.

Configuring RBAC
----------------

At the moment monasca-log-api does not feature RBAC with ``oslo.policies``.
It provides a custom mechanism, however, that can be configured as follows:

* ``path`` - list of URIs that RBAC applies to
* ``default_roles`` - list of roles that are permitted to access the API
* ``agent_roles`` - list of roles, that if present, means that requests come
  from log-agent
* ``delegate_roles`` - list of roles required by log-agent for sending logs
  on behalf of another project (tenant)

The configuration for ``roles_middleware`` should either be provided in
``log-api.conf`` or in a file in one of the configuration directories.

Configuring Logging
-------------------

Logging in monasca-log-api is controlled from the single
``log-api-logging.conf`` configuration file.
Here is a short list of several modifications you may want to apply,
based on your deployment:

* to log INFO to console::

    [handler_console]
    level = INFO

* to log DEBUG to file::

    [handler_file]
    level = DEBUG

* to change the log file location::

    [handler_file]
    args = ('/var/log/log-api.log', 'a')

* if you have an external script for log rotation::

    [handler_file]
    handler = logging.handlers.WatchedFileHandler
    args = ('/var/log/log-api.log', 'a')

  That will store up to 5 rotations (each having maximum size
  of 100MBs)

  The configuration of ``logging`` should be presented inside
  ``log-api-logging.conf`` file and referenced from ``log-api.conf`` using
  ``log_config_append`` option.

  If you want to know more about possible ways to save monasca-log-api logs,
  feel free to visit:

  * `oslo.log <https://docs.openstack.org/oslo.log/latest/index.html>`_
  * `Python HowTo <https://docs.python.org/2/howto/logging.html>`_
  * `Logging handlers <https://docs.python.org/2/library/logging.handlers.html>`_
