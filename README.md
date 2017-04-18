Team and repository tags
========================

[![Team and repository tags](https://governance.openstack.org/badges/monasca-log-api.svg)](https://governance.openstack.org/reference/tags/index.html)

<!-- Change things from this point on -->

# Overview

`monasca-log-api` is a RESTful API server that is designed with a layered architecture [layered architecture](http://en.wikipedia.org/wiki/Multilayered_architecture).

The full API Specification can be found in [documentation/monasca-log-api-spec.md](documentation/monasca-log-api-spec.md)

## Monasca-log-api Python

### Installation

To install the python api implementation, git clone the source and run the
following command:
```sh
    sudo python setup.py install
```

### Configuration

If it installs successfully, you will need to make changes to the following
two files to reflect your system settings, especially where kafka server is
located::

```sh
    /etc/monasca/log-api-config.conf
    /etc/monasca/log-api-config.ini
    /etc/monasca/log-api-logging.conf
```

Once the configurations are modified to match your environment, you can start
up the server using either Gunicorn or Apache.

### Start the Server -- for Gunicorn

The server can be run in the foreground, or as daemons:

Running the server in foreground mode with Gunicorn:

```sh
    gunicorn -k eventlet --worker-connections=2000 --backlog=1000
             --paste /etc/monasca/log-api-config.ini
```

Running the server as daemons with Gunicorn:

```sh
    gunicorn -k eventlet --worker-connections=2000 --backlog=1000
             --paste /etc/monasca/log-api-config.ini -D
```

### Start the Server -- for Apache

To start the server using Apache: create a modwsgi file,
create a modwsgi config file, and enable the wsgi module
in Apache.

The modwsgi conf file may look something like this, and the site will need to be enabled:

```sh
    Listen myhost:8082
    Listen 127.0.0.1:8082

    <VirtualHost *:8082>
        WSGIDaemonProcess log-api processes=4 threads=4 socket-timeout=120 user=log group=log python-path=/usr/local/lib/python2.7/site-packages
        WSGIProcessGroup log-api
        WSGIApplicationGroup log-api
        WSGIScriptAlias / /var/www/log/log-api.wsgi

        ErrorLog /var/log/log-api/wsgi.log
        LogLevel info
        CustomLog /var/log/log-api/wsgi-access.log combined

        <Directory /usr/local/lib/python2.7/site-packages/monasca_log_api>
          Options Indexes FollowSymLinks MultiViews
          Require all granted
          AllowOverride None
          Order allow,deny
          allow from all
          LimitRequestBody 102400
        </Directory>

        SetEnv no-gzip 1

    </VirtualHost>

```

The wsgi file may look something like this:

```sh
    from monasca_log_api.server import get_wsgi_app

    application = get_wsgi_app(config_base_path='/etc/monasca')
```

## Testing

### Commandline run
To check the server from the commandline:

```sh
    python server.py
```

### PEP8 guidelines
To check if the code follows python coding style, run the following command
from the root directory of this project:

```sh
    tox -e pep8
```

### Unit Tests
To run all the unit test cases, run the following command from the root
directory of this project:

```sh
    tox -e py27
    tox -e py35
```

### Coverage
To generate coverage results, run the following command from the root
directory of this project:

```sh
    tox -e cover
```

### Building

To build an installable package, run the following command from the root
directory of this project:

```sh
  python setup.py sdist
```

### Documentation

To generate documentation, run the following command from the root
directory of this project:

```sh
    tox -e docs
```

That will create documentation under build folder relative to root of the
project.

## Architectural layers

Requests flow through the following architectural layers from top to bottom:

* Resource
  * Serves as the entrypoint into the service.
  * Responsible for handling web service requests, and performing structural request validation.
* Application
  * Responsible for providing application level implementations for specific use cases.
* Domain
  * Contains the technology agnostic core domain model and domain service definitions.
  * Responsible for upholding invariants and defining state transitions.
* Infrastructure
  * Contains technology specific implementations of domain services.

## Documentation

* API Specification: [/documentation/monasca-log-api-spec.md](/documentation/monasca-log-api-spec.md).
* Kafka communication: [/documentation/monasca-log-api-kafka.md](/documentation/monasca-log-api-kafka.md).
* API Monitoring: [/documentation/monasca-log-api-metrics.md](/documentation/monasca-log-api-metrics.md).

# License

    # Copyright 2015 kornicameister@gmail.com
    # Copyright 2015-2017 FUJITSU LIMITED
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
