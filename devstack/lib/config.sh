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

# Non configurable settings or settings derived from another settings

_XTRACE_LOG_API_CONFIG=$(set +o | grep xtrace)
set +o xtrace

if [[ ${USE_VENV} = True ]]; then
    PROJECT_VENV["monasca-log-api"]=${MONASCA_LOG_API_DIR}.venv
    MONASCA_LOG_API_BIN_DIR=${PROJECT_VENV["monasca-log-api"]}/bin
else
    MONASCA_LOG_API_BIN_DIR=$(get_python_exec_prefix)
fi

MONASCA_LOG_API_WSGI=$MONASCA_LOG_API_BIN_DIR/monasca-log-api-wsgi
MONASCA_LOG_API_DEPLOY=`determine_log_api_deploy_mode`
if is_service_enabled tls-proxy; then
    MONASCA_LOG_API_SERVICE_PROTOCOL="https"
fi
if [ "$MONASCA_LOG_API_USE_MOD_WSGI" == "True" ]; then
    MONASCA_LOG_API_BASE_URI=${MONASCA_LOG_API_SERVICE_PROTOCOL}://${MONASCA_LOG_API_SERVICE_HOST}/logs
else
    MONASCA_LOG_API_BASE_URI=${MONASCA_LOG_API_SERVICE_PROTOCOL}://${MONASCA_LOG_API_SERVICE_HOST}:${MONASCA_LOG_API_SERVICE_PORT}
fi
MONASCA_LOG_API_URI_V2=${MONASCA_LOG_API_BASE_URI}/v2.0
MONASCA_LOG_API_URI_V3=${MONASCA_LOG_API_BASE_URI}/v3.0

MONASCA_LOG_API_CONF_DIR=${MONASCA_LOG_API_CONF_DIR:-/etc/monasca}
MONASCA_LOG_API_LOG_DIR=${MONASCA_LOG_API_LOG_DIR:-/var/log/monasca}
MONASCA_LOG_API_CACHE_DIR=${MONASCA_LOG_API_CACHE_DIR:-/var/cache/monasca-log-api}
MONASCA_LOG_API_WSGI_DIR=${MONASCA_LOG_API_WSGI_DIR:-/var/www/monasca-log-api}

MONASCA_LOG_API_CONF=${MONASCA_LOG_API_CONF:-$MONASCA_LOG_API_CONF_DIR/log-api.conf}
MONASCA_LOG_API_PASTE=${MONASCA_LOG_API_PASTE:-$MONASCA_LOG_API_CONF_DIR/log-api-paste.ini}
MONASCA_LOG_API_LOGGING_CONF=${MONASCA_LOG_API_LOGGING_CONF:-$MONASCA_LOG_API_CONF_DIR/log-api-logging.conf}
MONASCA_LOG_API_UWSGI_CONF=${MONASCA_LOG_API_UWSGI_CONF:-$MONASCA_LOG_API_CONF_DIR/log-api-uwsgi.ini}

MONASCA_LOG_API_USE_MOD_WSGI=${MONASCA_LOG_API_USE_MOD_WSGI:-$ENABLE_HTTPD_MOD_WSGI_SERVICES}

# configuration bits of various services
LOG_PERSISTER_DIR=$DEST/monasca-log-persister
LOG_TRANSFORMER_DIR=$DEST/monasca-log-transformer
LOG_METRICS_DIR=$DEST/monasca-log-metrics
LOG_AGENT_DIR=$DEST/monasca-log-agent

ELASTICSEARCH_DIR=$DEST/elasticsearch
ELASTICSEARCH_CFG_DIR=$ELASTICSEARCH_DIR/config
ELASTICSEARCH_LOG_DIR=$LOGDIR/elasticsearch
ELASTICSEARCH_DATA_DIR=$DATA_DIR/elasticsearch

KIBANA_DIR=$DEST/kibana
KIBANA_CFG_DIR=$KIBANA_DIR/config

LOGSTASH_DIR=$DEST/logstash

PLUGIN_FILES=$MONASCA_LOG_API_DIR/devstack/files
# configuration bits of various services

# Files inside this directory will be visible in gates log
GATE_CONFIGURATION_DIR=/etc/monasca-log-api

# clone monasca-{common,statsd} directly from repo
GITREPO["monasca-common"]=${MONASCA_COMMON_REPO}
GITBRANCH["monasca-common"]=${MONASCA_COMMON_BRANCH}
GITDIR["monasca-common"]=${MONASCA_COMMON_DIR}

GITREPO["monasca-statsd"]=${MONASCA_STATSD_REPO}
GITBRANCH["monasca-statsd"]=${MONASCA_STATSD_BRANCH}
GITDIR["monasca-statsd"]=${MONASCA_STATSD_DIR}

LIBS_FROM_GIT="${LIBS_FROM_GIT:-""},monasca-common,monasca-statsd"
# clone monasca-{common,statsd} directly from repo

# public facing bits
MONASCA_LOG_API_SERVICE_HOST=${MONASCA_LOG_API_SERVICE_HOST:-${SERVICE_HOST}}
MONASCA_LOG_API_SERVICE_PORT=${MONASCA_LOG_API_SERVICE_PORT:-5607}
MONASCA_LOG_API_SERVICE_PORT_INT=${MONASCA_LOG_API_SERVICE_PORT:-15607}
MONASCA_LOG_API_SERVICE_PROTOCOL=${MONASCA_LOG_API_SERVICE_PROTOCOL:-${SERVICE_PROTOCOL}}

ES_SERVICE_BIND_HOST=${ES_SERVICE_BIND_HOST:-${SERVICE_HOST}}
ES_SERVICE_BIND_PORT=${ES_SERVICE_BIND_PORT:-9200}
ES_SERVICE_PUBLISH_HOST=${ES_SERVICE_PUBLISH_HOST:-${SERVICE_HOST}}
ES_SERVICE_PUBLISH_PORT=${ES_SERVICE_PUBLISH_PORT:-9300}

KIBANA_SERVICE_HOST=${KIBANA_SERVICE_HOST:-${SERVICE_HOST}}
KIBANA_SERVICE_PORT=${KIBANA_SERVICE_PORT:-5601}
KIBANA_SERVER_BASE_PATH=${KIBANA_SERVER_BASE_PATH:-"/dashboard/monitoring/logs_proxy"}

KAFKA_SERVICE_HOST=${KAFKA_SERVICE_HOST:-${SERVICE_HOST}}
KAFKA_SERVICE_PORT=${KAFKA_SERVICE_PORT:-9092}
# public facing bits

${_XTRACE_LOG_API_CONFIG}
