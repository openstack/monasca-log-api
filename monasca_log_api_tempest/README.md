# Introduction

**Monasca-Log-Api** requires following components set up in the environment:

* monasca-log-transformer - component receiving data from monasca-log-api
* monasca-log-persister - component saves data to ElasticSearch
* ElasticSearch - database that stores logs

Those three components are all part of [monasca-elkstack](https://github.com/FujitsuEnablingSoftwareTechnologyGmbH/ansible-monasca-elkstack)
Ansible role.

**Monasca-Log-Api** can be installed with following [role](https://github.com/FujitsuEnablingSoftwareTechnologyGmbH/ansible-monasca-log-api).
In order to setup schema (kafka topics) please see [this](https://github.com/FujitsuEnablingSoftwareTechnologyGmbH/ansible-monasca-log-schema) role.

## Installation next to monasca-api

**Monasca-Api** and  **Monasca-Log-Api** can be installed next to each other.
Each one has been designed to work with different aspects of monitoring.
Therefore it is possible to proceed with installation as described
[here](https://github.com/openstack/monasca-vagrant).

# Configuration
1. Clone the OpenStack Tempest repo, and cd to it.

```
    git clone https://git.openstack.org/openstack/tempest.git
    cd tempest
```

2. Create a virtualenv for running the Tempest tests and activate it.
For example in the Tempest root dir

```
    virtualenv .venv
    source .venv/bin/activate
```

3. Install the Tempest requirements in the virtualenv.

```
    pip install -r requirements.txt -r test-requirements.txt
    pip install nose
```

4. Create ```etc/tempest.conf``` in the Tempest root dir by
running the following command:

 ```
 oslo-config-generator --config-file etc/config-generator.tempest.conf --output-file etc/tempest.conf
 ```

 Add the following sections to ```tempest.conf``` for testing
 using the monasca-vagrant environment.

 ```
 [identity]
 auth_version = v3
 admin_domain_name = Default
 admin_tenant_name = admin
 admin_password = admin
 admin_username = admin
 alt_tenant_name = demo
 alt_password = admin
 alt_username = alt_demo
 tenant_name = mini-mon
 password = password
 username = mini-mon
 uri_v3 = http://192.168.10.5:35357/v3/
 uri = http://192.168.10.5:35357/v2.0/
 force_tenant_isolation = False
 allow_tenant_isolation = False
 disable_ssl_certificate_validation = True
 kibana_version = 4.4.0

 [auth]
 allow_tenant_isolation = true
 ```

 Edit the the variable values in the identity section to match your particular
 monasca-vagrant environment.

5. Create ```etc/logging.conf``` in the Tempest root dir by making a copying
```logging.conf.sample```.

6. Clone the monasca-log-api repo in a directory somewhere outside of the
Tempest root dir.

7. Install the monasca-log-api in your venv, which will also register
   the Monasca Log Api Tempest Plugin as, monasca_log_api_tempest.

   cd into the monasa-log-api root directory. Making sure that the tempest
   virtual env is still active, run the following command.

 ```
 python setup.py install
 ```

See the [OpenStack Tempest Plugin
Interface](http://docs.openstack.org/developer/tempest/plugin.html), for more
details on Tempest Plugins and the plugin registration process.

# Running the Monasca Log Api Tempest
The Monasca Tempest Tests can be run using a variety of methods including:
1. [Testr](https://wiki.openstack.org/wiki/Testr)
2. [Os-testr](http://docs.openstack.org/developer/os-testr/)
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
[Os-testr](http://docs.openstack.org/developer/os-testr/) is a test wrapper
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
* [Tempest - The OpenStack Integration Test Suite](http://docs.openstack.org/developer/tempest/overview.html#quickstart)
* [Tempest Configuration Guide](https://github.com/openstack/tempest/blob/master/doc/source/configuration.rst#id1)
* [OpenStack Tempest Plugin Interface](http://docs.openstack.org/developer/tempest/plugin.html)

In addition to the above references, another source of information is the following OpenStack projects:
* [Manila Tempest Tests](https://github.com/openstack/manila/tree/master/manila_tempest_tests)
* [Congress Tempest Tests](https://github.com/openstack/congress/tree/master/congress_tempest_tests).
In particular, the Manila Tempest Tests were used as a reference implementation to develop the Monasca Tempest Tests.
There is also a wiki [HOWTO use tempest with manila](https://wiki.openstack.org/wiki/Manila/docs/HOWTO_use_tempest_with_manila) that might be useful for Monasca too.

# Issues
* Update documentation for testing using Devstack when available.
* Consider changing from monasca_tempest_tests to monasca_api_tempest_tests.
