# Monasca Log Management DevStack Plugin

The Monasca Log Management DevStack plugin currently only works on Ubuntu 14.04 (Trusty).
More Linux Distributions will be supported in the future.

Monasca Log Management Devstack plugin requires Monasca Devstack plugin.
Running the Monasca DevStack plugin and Monasca Log Management Devstack plugin requires a machine with 14GB of RAM.

Directions for installing and running Devstack can be found here:
```
http://docs.openstack.org/developer/devstack/
```

To run Monasca Log Management in DevStack, do the following three steps.

1. Clone the DevStack repo.

```
git clone https://git.openstack.org/openstack-dev/devstack
```

2. Add the following to the DevStack local.conf file in the root of the devstack directory. You may
   need to create the local.conf if it does not already exist.

```
[[local|localrc]]
MYSQL_PASSWORD=secretmysql
DATABASE_PASSWORD=secretdatabase
RABBIT_PASSWORD=secretrabbit
ADMIN_PASSWORD=secretadmin
SERVICE_PASSWORD=secretservice
SERVICE_TOKEN=111222333444

LOGFILE=$DEST/logs/stack.sh.log
LOGDIR=$DEST/logs
LOG_COLOR=False

# The following two variables allow switching between Java and Python for the implementations
# of the Monasca API and the Monasca Persister. If these variables are not set, then the
# default is to install the Python implementations of both the Monasca API and the Monasca Persister.

# Uncomment one of the following two lines to choose Java or Python for the Monasca API.
MONASCA_API_IMPLEMENTATION_LANG=${MONASCA_API_IMPLEMENTATION_LANG:-java}
# MONASCA_API_IMPLEMENTATION_LANG=${MONASCA_API_IMPLEMENTATION_LANG:-python}

# Uncomment of the following two lines to choose Java or Python for the Monasca Pesister.
MONASCA_PERSISTER_IMPLEMENTATION_LANG=${MONASCA_PERSISTER_IMPLEMENTATION_LANG:-java}
# MONASCA_PERSISTER_IMPLEMENTATION_LANG=${MONASCA_PERSISTER_IMPLEMENTATION_LANG:-python}

# Uncomment one of the following two lines to choose either InfluxDB or Vertica.
MONASCA_METRICS_DB=${MONASCA_METRICS_DB:-influxdb}
# MONASCA_METRICS_DB=${MONASCA_METRICS_DB:-vertica}

# This line will enable all of Monasca.
enable_plugin monasca-api git://git.openstack.org/openstack/monasca-api
enable_plugin monasca-log-api https://github.com/openstack/monasca-log-api.git
```

3.   Run './stack.sh' from the root of the devstack directory.


After finishing the installation, you can find the "Log Management" button on
"Overview" of "Monitoring" tab, if you log in OpenStack as admin.
At first time, you need to specify the index pattern and time-field name.

The index name is created as the following format.
  \[mini-mon tenant id\]-YYYY-MM-DD
For example:
  20c4fbd37a2345dd84266dfc92da7bd1-2016-04-07

Set the value as the above to index pattern.
Or you can use "\*" as a wild card, like below.
  20c4fbd37a2345dd84266dfc92da7bd1-\*

Select @timestamp as time-field name.

# Using Vagrant

Vagrant can be used to deploy a VM with Devstack and Monasca Logging
running in it using the Vagrantfile. After installing Vagrant,
just run the command `vagrant up` as usual in the `monasca-log-api/devstack`
directory.

```
# Copyright 2016 FUJITSU LIMITED
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
```
