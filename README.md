# Forked from https://github.com/openstack/monasca-api
This repository is forked from [monasca-api](https://github.com/openstack/monasca-api).

# Overview

`monasca-log-api` is a RESTful API server that is designed with a layered architecture [layered architecture](http://en.wikipedia.org/wiki/Multilayered_architecture).

The full API Specification can be found in [docs/monasca-log-api-spec.md](docs/monasca-log-api-spec.md)

## Java Build

Requires monasca-common from https://github.com/openstack/monasca-common. Download and do mvn install. Then:

```
cd java
mvn clean package
```

# OpenStack Java Build

There is a pom.xml in the base directory that should only be used for the OpenStack build. The OpenStack build is a rather strange build because of the limitations of the current OpenStack java jobs and infrastructure. We have found that the API runs faster if built with maven 3 but the OpenStack nodes only have maven 2. This build checks the version of maven and if not maven 3, it downloads a version of maven 3 and uses it. This build depends on jars that are from monasca-common. That StrackForge build uploads the completed jars to http://tarballs.openstack.org/ci/monasca-common, but they are just regular jars, and not in a maven repository and sometimes zuul takes a long time to do the upload. Hence, the first thing the maven build from the base project does is invoke build_common.sh in the common directory. This script clones monasca-common and then invokes maven 3 to build monasca-common in the common directory and install the jars in the local maven repository.

Since this is all rather complex, that part of the build only works on OpenStack so follow the simple instruction above if you are building your own monasca-log-api.

Currently this build is executed on the bare-precise nodes in OpenStack and they only have maven 2. So, this build must be kept compatible with Maven 2. If another monasca-common jar is added as a dependency to java/pom.xml, it must also be added to download/download.sh.

## Usage

```
java -jar target/monasca-log-api.jar server config-file.yml
```

## Keystone Configuration

For secure operation of the Monasca API, the API must be configured to use Keystone in the configuration file under the middleware section. Monasca only works with a Keystone v3 server. The important parts of the configuration are explained below:

* serverVIP - This is the hostname or IP Address of the Keystone server
* serverPort - The port for the Keystone server
* useHttps - Whether to use https when making requests of the Keystone API
* truststore - If useHttps is true and the Keystone server is not using a certificate signed by a public CA recognized by Java, the CA certificate can be placed in a truststore so the Monasca API will trust it, otherwise it will reject the https connection. This must be a JKS truststore
* truststorePassword - The password for the above truststore
* connSSLClientAuth - If the Keystone server requires the SSL client used by the Monasca server to have a specific client certificate, this should be true, false otherwise
* keystore - The keystore holding the SSL Client certificate if connSSLClientAuth is true
* keystorePassword - The password for the keystore
* defaultAuthorizedRoles - An array of roles that authorize a user to access the complete Monasca API. User must have at least one of these roles. See below
* agentAuthorizedRoles - An array of roles that authorize only the posting of logs. See Keystone Roles below
* adminAuthMethod - "password" if the Monasca API should adminUser and adminPassword to login to the Keystone server to check the user's token, "token" if the Monasca API should use adminToken
* adminUser - Admin user name
* adminPassword - Admin user password
* adminProjectId - Specify the project ID the api should use to request an admin token. Defaults to the admin user's default project. The adminProjectId option takes precedence over adminProjectName.
* adminProjectName - Specify the project name the api should use to request an admin token. Defaults to the admin user's default project. The adminProjectId option takes precedence over adminProjectName.
* adminToken - A valid admin user token if adminAuthMethod is token
* timeToCacheToken - How long the Monasca API should cache the user's token before checking it again

### Keystone Roles

See [Monasca API documentation](https://github.com/openstack/monasca-api/blob/master/README.md#keystone-roles) for the levels of access description.

## Design Overview

### Architectural layers

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

* API Specification: [/docs/monasca-log-api-spec.md](/docs/monasca-log-api-spec.md).
* Kafka communication: [/docs/monasca-log-api-kafka.md](/docs/monasca-log-api-kafka.md).

## Python monasca-log-api implementation

See here [/monasca_log_api/README.md](/monasca_log_api/README.md).

# License

    # Copyright 2015 kornicameister@gmail.com
    # Copyright 2015 FUJITSU LIMITED
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
