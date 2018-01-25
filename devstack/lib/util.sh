#!/bin/bash

# Copyright 2017 FUJITSU LIMITED
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

# Set of utility-like methods that are not bound to any particular
# service

_XTRACE_LOG_API_UTILS=$(set +o | grep xtrace)
set +o xtrace

run_process_sleep() {
    local name=$1
    local cmd=$2
    local sleepTime=${3:-1}
    run_process "$name" "$cmd"
    sleep ${sleepTime}
}

is_logstash_required() {
    is_service_enabled monasca-log-persister \
        || is_service_enabled monasca-log-transformer \
        || is_service_enabled monasca-log-metrics \
        || is_service_enabled monasca-log-agent \
        && return 0
}

# MONASCA_LOG_API_DEPLOY defines how monasca-log-api is deployed, allowed values:
# - mod_wsgi : Run monasca-log-api under Apache HTTPd mod_wsgi
# - uwsgi : Run monasca-log-api under uwsgi
# - gunicorn: Run monasca-log-api under gunicorn
determine_log_api_deploy_mode() {
    MONASCA_LOG_API_USE_MOD_WSGI=$(trueorfalse False MONASCA_LOG_API_USE_MOD_WSGI)
    if [ "$MONASCA_LOG_API_USE_MOD_WSGI" == "True" ]; then
        if [[ "$WSGI_MODE" == "uwsgi" ]]; then
            echo "uwsgi"
        else
            echo "mod_wsgi"
        fi
    else
        echo "gunicorn"
    fi
}

${_XTRACE_LOG_API_UTILS}
