================================
Docker image for Monasca Log API
================================
The Monasca log API image is based on the monasca-base image.


Building monasca-base image
===========================
See https://github.com/openstack/monasca-common/tree/master/docker/README.rst


Building Monasca log API image
==============================

Example:
  $ ./build_image.sh <repository_version> <upper_constains_branch> <common_version>


Requirements from monasca-base image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
health_check.py
  This file will be used for checking the status of the Monasca Log API
  application.


Scripts
~~~~~~~
start.sh
  In this starting script provide all steps that lead to the proper service
  start. Including usage of wait scripts and templating of configuration
  files. You also could provide the ability to allow running container after
  service died for easier debugging.

build_image.sh
  Please read detailed build description inside the script.


Environment variables
~~~~~~~~~~~~~~~~~~~~~
============================== ======================================================================= ==========================================
Variable                       Default                                                                 Description
============================== ======================================================================= ==========================================
KAFKA_URI                      kafka:9092                                                              URI to Apache Kafka (distributed streaming platform)
KAFKA_WAIT_FOR_TOPICS          log                                                                     The topic where log-api streams the log messages
KAFKA_WAIT_RETRIES             24                                                                      Number of kafka connect attempts
KAFKA_WAIT_DELAY               5                                                                       Seconds to wait between attempts
MONASCA_CONTAINER_LOG_API_PORT 5607                                                                    The port from the log pipeline endpoint
MEMCACHED_URI                  memcached:11211                                                         URI to Keystone authentication cache
AUTHORIZED_ROLES               admin,domainuser,domainadmin,monasca-user                               Roles for Monasca users (full API access)
AGENT_AUTHORIZED_ROLES         monasca-agent                                                           Roles for Monasca agents (sending data only)
KEYSTONE_IDENTITY_URI          http://keystone:35357                                                   URI to Keystone admin endpoint
KEYSTONE_AUTH_URI              http://keystone:5000                                                    URI to Keystone public endpoint
KEYSTONE_ADMIN_USER            admin                                                                   OpenStack administrator user name
KEYSTONE_ADMIN_PASSWORD        secretadmin                                                             OpenStack administrator user password
KEYSTONE_ADMIN_TENANT          admin                                                                   OpenStack administrator tenant name
KEYSTONE_ADMIN_DOMAIN          default                                                                 OpenStack administrator domain
GUNICORN_WORKERS               9                                                                       Number of gunicorn (WSGI-HTTP server) workers
GUNICORN_WORKER_CLASS          gevent                                                                  Used gunicorn worker class
GUNICORN_WORKER_CONNECTIONS    2000                                                                    Number of gunicorn worker connections
GUNICORN_BACKLOG               1000                                                                    Number of gunicorn backlogs
GUNICORN_TIMEOUT               10                                                                      Gunicorn connection timeout
PYTHONIOENCODING               utf-8                                                                   Python encoding
ADD_ACCESS_LOG                 false                                                                   Enable gunicorn request/access logging
ACCESS_LOG_FORMAT              "%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s" Define the logging format
ACCESS_LOG_FIELDS              '%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'       Define the fields to be logged
LOG_LEVEL_ROOT                 WARN                                                                    Log level for root logging
LOG_LEVEL_CONSOLE              INFO                                                                    Log level for console logging
LOG_LEVEL_ACCESS               INFO                                                                    Log level for access logging
STAY_ALIVE_ON_FAILURE          false                                                                   If true, container runs 2 hours after tests fail
============================== ======================================================================= ==========================================


Provide configuration templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* monasca-log-api.conf.j2
* log-api-gunicorn.conf.j2
* log-api-logging.conf.j2
* log-api.paste.ini.j2


Links
~~~~~
https://docs.openstack.org/monasca-log-api/latest/configuration/

https://github.com/openstack/monasca-log-api/blob/master/README.rst
