# Introduction

**Monasca-Log-Api** requires following components set up in the environment:

* monasca-log-transformer - component receiving data from monasca-log-api, [config](../devstack/files/transformer.conf)
* monasca-log-persister - component saves data to ElasticSearch, [config](../devstack/files/persister.conf)
* ElasticSearch - database that stores logs, [config](../devstack/files/elasticsearch.yml)

Those three components are all part of [devstack](https://github.com/openstack/monasca-api/tree/master/devstack).

* Logstash - it is a prerequisite for monasca-log-transformer and monasca-log-persister components

**Monasca-Log-Api** can be installed using following [Github repo](https://github.com/openstack/monasca-log-api/).
In order to setup schema (kafka topics) please see [this](https://github.com/openstack/monasca-log-api/blob/master/devstack/plugin.sh#L198).

## Installation next to monasca-api

**Monasca-Api** and  **Monasca-Log-Api** can be installed next to each other.
Each one has been designed to work with different aspects of monitoring.
Therefore it is possible to proceed with installation as described
[here](https://github.com/openstack/monasca-log-api/blob/master/devstack/).

# Configuration
1. Clone the OpenStack Tempest repo, and cd to it.

```bash
    git clone https://git.openstack.org/openstack/tempest.git
    cd tempest
```

2. Create a virtualenv for running the Tempest tests and activate it.
For example in the Tempest root dir

```bash
    virtualenv .venv
    source .venv/bin/activate
```

3. Install the Tempest requirements in the virtualenv.

```bash
    pip install \
        -c https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt \
        -r requirements.txt \
        -r test-requirements.txt
```

4. Create ```etc/tempest.conf``` in the Tempest root dir by
running the following command:

```bash
    oslo-config-generator --config-file tempest/cmd/config-generator.tempest.conf --output-file etc/tempest.conf
```

 Add the following sections to ```tempest.conf``` for testing
 using the monasca-vagrant environment.

```ini
    [identity]
    region = RegionOne
    auth_version = v3
    uri = http://10.36.99.238/identity_admin/v2.0
    uri_v3 = http://10.36.99.238/identity_admin/v3
    user_lockout_failure_attempts = 2
    user_locakout_duration = 5
    user_unique_last_password_count = 2
    admin_domain_scope = True

    [auth]
    tempest_roles = monasca-user
    admin_project_name = admin
    admin_domain_name = default
    admin_password = secretadmin
    admin_username = admin
    use_dynamic_credentials = True

    [monitoring]
    kibana_version = 4.6.3
    api_version = v2.0 # or v3.0
```

Edit the variable values in the identity section to match your particular
monasca-vagrant environment. Best way to do this might be

```bash
    source devstack/openrc {username} {password}
```

and collect all relevant values using

```bash
    env | grep OS_
```

An output will be similar to this one

```bash
    OS_PROJECT_DOMAIN_ID=default
    OS_REGION_NAME=RegionOne
    OS_USER_DOMAIN_ID=default
    OS_PROJECT_NAME=admin
    OS_IDENTITY_API_VERSION=3
    OS_PASSWORD=secretadmin
    OS_AUTH_TYPE=password
    OS_AUTH_URL=http://10.36.99.238/identity_admin
    OS_USERNAME=admin
    OS_TENANT_NAME=admin
    OS_VOLUME_API_VERSION=2
    OS_NO_CACHE=True
```

5. Create ```etc/logging.conf``` in the Tempest root dir by making a copying
```logging.conf.sample```.

6. Clone the monasca-log-api repo in a directory somewhere outside of the
Tempest root dir.

7. Install the monasca-log-api in your venv, which will also register
   the Monasca Log Api Tempest Plugin as, monasca_log_api_tempest.

   cd into the monasca-log-api root directory. Making sure that the tempest
   virtual env is still active, run the following command.

```
    pip install \
        -c https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt \
        -r requirements.txt \
        -r test-requirements.txt
    python setup.py install
```

See the [OpenStack Tempest Plugin
Interface](https://docs.openstack.org/tempest/latest/plugin.html), for more
details on Tempest Plugins and the plugin registration process.

# Running the Monasca Log Api Tempest
The Monasca Tempest Tests can be run using a variety of methods including:
1. [Testr](https://wiki.openstack.org/wiki/Testr)
2. [Os-testr](https://docs.openstack.org/os-testr/latest/)
3. [PyCharm](https://www.jetbrains.com/pycharm/)
4. Tempest Scripts in Devstack

## Run the tests from the CLI using testr

[Testr](https://wiki.openstack.org/wiki/Testr) is a test runner that can be used to run the Tempest tests.

1. In the Tempest root dir, create a list of the Monasca Tempest Tests in a file.

 ```sh
 testr list-tests monasca_log_api_tempest > monasca_log_api_tempest
 ```

2. Run the tests using testr

 ```sh
 testr run --load-list=monasca_log_api_tempest
 ```

You can also use testr to create a list of specific tests for your needs.

## Run the tests from the CLI using os-testr (no file necessary)
[Os-testr](https://docs.openstack.org/os-testr/latest/) is a test wrapper
that can be used to run the Monasca Tempest tests.

1. In the Tempest root dir:

 ```
 ostestr --serial --regex monasca_log_api_tempest
 ```

 ```--serial``` option is necessary here. Monasca Log Api tempest tests can't
 be run in parallel (default option in ostestr) because some tests depend on the
 same data and will randomly fail.

## Running/Debugging the Monasca Tempest Tests in PyCharm

Assuming that you have already created a PyCharm project for the
```monasca-log-api``` do the following:

1. In PyCharm, Edit Configurations and add a new Python tests configuration by selecting Python tests->Nosetests.
2. Name the test. For example TestSingleLog.
3. Set the path to the script with the tests to run. For example, ~/repos/monasca-log-api/monasca_log_api_tempest/tests/test_single.py
4. Set the name of the Class to test. For example TestVersions.
5. Set the working directory to your local root Tempest repo. For example, ~/repos/tempest.
6. Select the Python interpreter for your project to be the same as the one virtualenv created above. For example, ~/repos/tempest/.venv
7. Run the tests. You should also be able to debug them.
8. Step and repeat for other tests.

## Run the tests from the CLI using tempest scripts in devstack

1. In /opt/stack/tempest, run ```./run_tempest.sh monasca_log_api_tempest```
2. If asked to create a new virtual environment, select yes
3. Activate the virtual environment ```source .venv/bin/activate```
4. In your monasca-log-api directory, run ```python setup.py install```
5. In /opt/stack/tempest, run ```./run_tempest.sh monasca_log_api_tempest```

# References
This section provides a few additional references that might be useful:
* [Tempest - The OpenStack Integration Test Suite](https://docs.openstack.org/tempest/latest/overview.html#quickstart)
* [Tempest Configuration Guide](https://github.com/openstack/tempest/blob/master/doc/source/configuration.rst#id1)
* [OpenStack Tempest Plugin Interface](https://docs.openstack.org/tempest/latest/plugin.html)

In addition to the above references, another source of information is the following OpenStack projects:
* [Manila Tempest Tests](https://github.com/openstack/manila/tree/master/manila_tempest_tests)
* [Congress Tempest Tests](https://github.com/openstack/congress/tree/master/congress_tempest_tests).
In particular, the Manila Tempest Tests were used as a reference implementation to develop the Monasca Tempest Tests.
There is also a wiki [HOWTO use tempest with manila](https://wiki.openstack.org/wiki/Manila/docs/HOWTO_use_tempest_with_manila) that might be useful for Monasca too.

# Issues
* Update documentation for testing using Devstack when available.
* Consider changing from monasca_tempest_tests to monasca_api_tempest_tests.
