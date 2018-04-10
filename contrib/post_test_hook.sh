#
# (C) Copyright 2015 Hewlett Packard Enterprise Development Company LP
# (C) Copyright 2016-2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Sleep some time until all services are starting
sleep 6

function load_devstack_utilities {
    source $BASE/new/devstack/stackrc
    source $BASE/new/devstack/functions
    source $BASE/new/devstack/openrc admin admin

    # print OS_ variables
    env | grep OS_
}

function setup_monasca_log {
    local constraints="-c $REQUIREMENTS_DIR/upper-constraints.txt"

    pushd $TEMPEST_DIR
    sudo -EH pip install $constraints -r requirements.txt -r test-requirements.txt
    popd;

    pushd $MONASCA_LOG_API_DIR
    sudo -EH pip install $constraints -r requirements.txt -r test-requirements.txt
    sudo -EH python setup.py install
    popd;
}

function set_tempest_conf {

    local conf_file=$TEMPEST_DIR/etc/tempest.conf
    pushd $TEMPEST_DIR
    oslo-config-generator \
        --config-file tempest/cmd/config-generator.tempest.conf \
        --output-file $conf_file
    popd

    cp -f $DEST/tempest/etc/logging.conf.sample $DEST/tempest/etc/logging.conf

    # set identity section
    iniset $conf_file identity admin_domain_scope True

    iniset $conf_file identity user_unique_last_password_count 2
    iniset $conf_file identity user_locakout_duration 5
    iniset $conf_file identity user_lockout_failure_attempts 2

    iniset $conf_file identity uri $OS_AUTH_URL/v2.0
    iniset $conf_file identity uri_v3 $OS_AUTH_URL/v3
    iniset $conf_file identity auth_version v$OS_IDENTITY_API_VERSION
    iniset $conf_file identity region $OS_REGION_NAME

    # NOTE(trebskit) we're processing a lot here, increase http timeout
    iniset $conf_file identity-feature-enabled http_timeout 120

    # set auth section
    iniset $conf_file auth use_dynamic_credentials True
    iniset $conf_file auth admin_username $OS_USERNAME
    iniset $conf_file auth admin_password $OS_PASSWORD
    iniset $conf_file auth admin_domain_name $OS_PROJECT_DOMAIN_ID
    iniset $conf_file auth admin_project_name $OS_PROJECT_NAME
    iniset $conf_file auth tempest_roles monasca-user

    # set monitoring section
    iniset $conf_file monitoring kibana_version 4.6.3
}

function function_exists {
    declare -f -F $1 > /dev/null
}

if ! function_exists echo_summary; then
    function echo_summary {
        echo $@
    }
fi

echo_summary "monasca-log's post_test_hook.sh was called..."
(set -o posix; set)

# save ref to monasca-api dir
export MONASCA_LOG_API_DIR="$BASE/new/monasca-log-api"
export TEMPEST_DIR="$BASE/new/tempest"

sudo chown -R "${USER}":stack $MONASCA_LOG_API_DIR
sudo chown -R "${USER}":stack $TEMPEST_DIR

load_devstack_utilities
setup_monasca_log
set_tempest_conf
