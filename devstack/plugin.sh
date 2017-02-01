#
# Copyright 2016 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Save trace setting
_XTRACE_LOG_API=$(set +o | grep xtrace)
set -o xtrace

_ERREXIT_LOG_API=$(set +o | grep errexit)
set -o errexit

# monasca-log-api settings
if [[ ${USE_VENV} = True ]]; then
    PROJECT_VENV["monasca-log-api"]=${MONASCA_LOG_API_DIR}.venv
    MONASCA_LOG_API_BIN_DIR=${PROJECT_VENV["monasca-log-api"]}/bin
else
    MONASCA_LOG_API_BIN_DIR=$(get_python_exec_prefix)
fi

MONASCA_LOG_API_BASE_URI=${MONASCA_LOG_API_SERVICE_PROTOCOL}://${MONASCA_LOG_API_SERVICE_HOST}:${MONASCA_LOG_API_SERVICE_PORT}
MONASCA_LOG_API_URI_V2=${MONASCA_LOG_API_BASE_URI}/v2.0
MONASCA_LOG_API_URI_V3=${MONASCA_LOG_API_BASE_URI}/v3.0

# configuration bits
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

# TOP_LEVEL functions called from devstack coordinator
###############################################################################
function pre_install {
    install_elk
    install_node_nvm
}

function install_monasca_log {
    build_kibana_plugin
    if is_service_enabled monasca-log-api; then
        # install_monasca-log-api is not called directly
        # stack_install_service calls it
        stack_install_service monasca-log-api
    fi
    install_log_agent
}

function install_elk {
    install_logstash
    install_elasticsearch
    install_kibana
}

function configure_monasca_log {
    configure_kafka
    configure_elasticsearch
    configure_kibana
    install_kibana_plugin

    configure_monasca_log_api
    configure_monasca_log_transformer
    configure_monasca_log_metrics
    configure_monasca_log_persister
    configure_monasca_log_agent
}

function init_monasca_log {
    enable_log_management
    create_log_management_accounts
}

function stop_monasca_log {
    stop_process "monasca-log-agent" || true
    stop_process "monasca-log-api" || true
    stop_process "monasca-log-metrics" || true
    stop_process "monasca-log-persister" || true
    stop_process "monasca-log-transformer" || true
    stop_process "kibana" || true
    stop_process "elasticsearch" || true
}

function start_monasca_log {
    start_elasticsearch
    start_kibana
    start_monasca_log_transformer
    start_monasca_log_metrics
    start_monasca_log_persister
    start_monasca_log_api
    start_monasca_log_agent
}

function clean_monasca_log {
    clean_monasca_log_agent
    clean_monasca_log_api
    clean_monasca_log_persister
    clean_monasca_log_transformer
    clean_kibana
    clean_elasticsearch
    clean_logstash
    clean_node_nvm
}
###############################################################################

function install_monasca-log-api {
    echo_summary "Installing monasca-log-api"

    git_clone $MONASCA_LOG_API_REPO $MONASCA_LOG_API_DIR $MONASCA_LOG_API_BRANCH
    setup_develop $MONASCA_LOG_API_DIR

    pip_install gunicorn
    pip_install_gr python-memcached

    if use_library_from_git "monasca-common"; then
        git_clone_by_name "monasca-common"
        setup_dev_lib "monasca-common"
    fi
    if use_library_from_git "monasca-statsd"; then
        git_clone_by_name "monasca-statsd"
        setup_dev_lib "monasca-statsd"
    fi
}

function configure_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Configuring monasca-log-api"

        # Put config files in ``$MONASCA_LOG_API_CONF_DIR`` for everyone to find
        sudo install -d -o $STACK_USER $MONASCA_LOG_API_CONF_DIR
        create_log_api_cache_dir

        if [[ "$MONASCA_LOG_API_CONF_DIR" != "$MONASCA_LOG_API_DIR/etc/monasca" ]]; then
            install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-config.conf $MONASCA_LOG_API_CONF
            install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-config.ini $MONASCA_LOG_API_PASTE_INI
            install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-logging.conf $MONASCA_LOG_API_LOGGING_CONF
        fi

        # configure log-api-config.conf
        iniset "$MONASCA_LOG_API_CONF" DEFAULT log_config_append $MONASCA_LOG_API_LOGGING_CONF
        iniset "$MONASCA_LOG_API_CONF" service region $REGION_NAME
        iniset "$MONASCA_LOG_API_CONF" log_publisher kafka_url $KAFKA_SERVICE_HOST:$KAFKA_SERVICE_PORT
        iniset "$MONASCA_LOG_API_CONF" kafka_healthcheck kafka_url $KAFKA_SERVICE_HOST:$KAFKA_SERVICE_PORT

        # configure keystone middleware
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken auth_url $KEYSTONE_AUTH_URI
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken auth_uri $KEYSTONE_AUTH_URI
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken identity_uri $KEYSTONE_SERVICE_URI
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken admin_user "admin"
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken admin_password $ADMIN_PASSWORD
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken admin_tenant_name "admin"

        # certs
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken cafile $SSL_BUNDLE_FILE
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken signing_dir $MONASCA_LOG_API_CACHE_DIR

        # memcached
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken memcached_servers $SERVICE_HOST:11211

        # insecure
        if is_service_enabled tls-proxy; then
            iniset "$MONASCA_LOG_API_CONF" keystone_authtoken insecure False
        fi

        # configure log-api-config.ini
        iniset "$MONASCA_LOG_API_PASTE_INI" server:main host $MONASCA_LOG_API_SERVICE_HOST
        iniset "$MONASCA_LOG_API_PASTE_INI" server:main port $MONASCA_LOG_API_SERVICE_PORT
        iniset "$MONASCA_LOG_API_PASTE_INI" server:main chdir $MONASCA_LOG_API_DIR
    fi
}

function create_log_api_cache_dir {
    sudo install -m 700 -d -o $STACK_USER $MONASCA_LOG_API_CACHE_DIR
}

function clean_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Cleaning monasca-log-api"

        sudo rm -f $MONASCA_LOG_API_CONF || true
        sudo rm -f $MONASCA_LOG_API_PASTE_INI  || true
        sudo rm -f $MONASCA_LOG_API_LOGGING_CONF || true
        sudo rm -rf $MONASCA_LOG_API_CACHE_DIR || true
        sudo rm -rf $MONASCA_LOG_API_CONF_DIR || true

        sudo rm -rf $MONASCA_LOG_API_DIR || true
    fi
}

function start_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Starting monasca-log-api"
        local gunicorn="$MONASCA_LOG_API_BIN_DIR/gunicorn"
        restart_service memcached
        run_process "monasca-log-api" "$gunicorn -n monasca-log-api -k eventlet --paste $MONASCA_LOG_API_PASTE_INI"
    fi
}

function install_logstash {
    if is_logstash_required; then
        echo_summary "Installing Logstash ${LOGSTASH_VERSION}"

        local logstash_tarball=logstash-${LOGSTASH_VERSION}.tar.gz
        local logstash_url=http://download.elastic.co/logstash/logstash/${logstash_tarball}
        local logstash_dest=${FILES}/${logstash_tarball}

        download_file ${logstash_url} ${logstash_dest}
        tar xzf ${logstash_dest} -C $DEST

        sudo chown -R $STACK_USER $DEST/logstash-${LOGSTASH_VERSION}
        ln -sf $DEST/logstash-${LOGSTASH_VERSION} $LOGSTASH_DIR
    fi
}

function clean_logstash {
    if is_logstash_required; then
        echo_summary "Cleaning Logstash ${LOGSTASH_VERSION}"

        sudo rm -rf $LOGSTASH_DIR || true
        sudo rm -rf $FILES/logstash-${LOGSTASH_VERSION}.tar.gz ||  true
        sudo rm -rf $DEST/logstash-${LOGSTASH_VERSION} || true
    fi
}

function install_elasticsearch {
    if is_service_enabled elasticsearch; then
        echo_summary "Installing ElasticSearch ${ELASTICSEARCH_VERSION}"

        local es_tarball=elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz
        local es_url=http://download.elasticsearch.org/elasticsearch/elasticsearch/${es_tarball}
        local es_dest=${FILES}/${es_tarball}

        download_file ${es_url} ${es_dest}
        tar xzf ${es_dest} -C $DEST

        sudo chown -R $STACK_USER $DEST/elasticsearch-${ELASTICSEARCH_VERSION}
        ln -sf $DEST/elasticsearch-${ELASTICSEARCH_VERSION} $ELASTICSEARCH_DIR
    fi
}

function configure_elasticsearch {
    if is_service_enabled elasticsearch; then
        echo_summary "Configuring ElasticSearch ${ELASTICSEARCH_VERSION}"

        local templateDir=$ELASTICSEARCH_CFG_DIR/templates

        for dir in $ELASTICSEARCH_LOG_DIR $templateDir $ELASTICSEARCH_DATA_DIR; do
            sudo install -m 755 -d -o $STACK_USER $dir
        done

        sudo cp -f "${PLUGIN_FILES}"/elasticsearch/elasticsearch.yml $ELASTICSEARCH_CFG_DIR/elasticsearch.yml
        sudo chown -R $STACK_USER $ELASTICSEARCH_CFG_DIR/elasticsearch.yml
        sudo chmod 0644 $ELASTICSEARCH_CFG_DIR/elasticsearch.yml

        sudo sed -e "
            s|%ES_SERVICE_BIND_HOST%|$ES_SERVICE_BIND_HOST|g;
            s|%ES_SERVICE_BIND_PORT%|$ES_SERVICE_BIND_PORT|g;
            s|%ES_SERVICE_PUBLISH_HOST%|$ES_SERVICE_PUBLISH_HOST|g;
            s|%ES_SERVICE_PUBLISH_PORT%|$ES_SERVICE_PUBLISH_PORT|g;
            s|%ES_DATA_DIR%|$ELASTICSEARCH_DATA_DIR|g;
            s|%ES_LOG_DIR%|$ELASTICSEARCH_LOG_DIR|g;
        " -i $ELASTICSEARCH_CFG_DIR/elasticsearch.yml
    fi
}

function clean_elasticsearch {
    if is_service_enabled elasticsearch; then
        echo_summary "Cleaning Elasticsearch ${ELASTICSEARCH_VERSION}"

        sudo rm -rf ELASTICSEARCH_DIR || true
        sudo rm -rf ELASTICSEARCH_CFG_DIR || true
        sudo rm -rf ELASTICSEARCH_LOG_DIR || true
        sudo rm -rf ELASTICSEARCH_DATA_DIR || true
        sudo rm -rf $FILES/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz || true
        sudo rm -rf $DEST/elasticsearch-${ELASTICSEARCH_VERSION} || true
    fi
}

function start_elasticsearch {
    if is_service_enabled elasticsearch; then
        echo_summary "Starting ElasticSearch ${ELASTICSEARCH_VERSION}"
        # 5 extra seconds to ensure that ES started properly
        local esSleepTime=${ELASTICSEARCH_SLEEP_TIME:-5}
        _run_process_sleep "elasticsearch" "$ELASTICSEARCH_DIR/bin/elasticsearch" $esSleepTime
    fi
}

function install_kibana {
    if is_service_enabled kibana; then
        echo_summary "Installing Kibana ${KIBANA_VERSION}"

        local kibana_tarball=kibana-${KIBANA_VERSION}.tar.gz
        local kibana_tarball_url=http://download.elastic.co/kibana/kibana/${kibana_tarball}
        local kibana_tarball_dest=${FILES}/${kibana_tarball}

        download_file ${kibana_tarball_url} ${kibana_tarball_dest}
        tar xzf ${kibana_tarball_dest} -C $DEST

        sudo chown -R $STACK_USER $DEST/kibana-${KIBANA_VERSION}
        ln -sf $DEST/kibana-${KIBANA_VERSION} $KIBANA_DIR
    fi
}

function configure_kibana {
    if is_service_enabled kibana; then
        echo_summary "Configuring Kibana ${KIBANA_VERSION}"

        sudo install -m 755 -d -o $STACK_USER $KIBANA_CFG_DIR

        sudo cp -f "${PLUGIN_FILES}"/kibana/kibana.yml $KIBANA_CFG_DIR/kibana.yml
        sudo chown -R $STACK_USER $KIBANA_CFG_DIR/kibana.yml
        sudo chmod 0644 $KIBANA_CFG_DIR/kibana.yml

        sudo sed -e "
            s|%KIBANA_SERVICE_HOST%|$KIBANA_SERVICE_HOST|g;
            s|%KIBANA_SERVICE_PORT%|$KIBANA_SERVICE_PORT|g;
            s|%KIBANA_SERVER_BASE_PATH%|$KIBANA_SERVER_BASE_PATH|g;
            s|%ES_SERVICE_BIND_HOST%|$ES_SERVICE_BIND_HOST|g;
            s|%ES_SERVICE_BIND_PORT%|$ES_SERVICE_BIND_PORT|g;
            s|%KIBANA_LOG_DIR%|$KIBANA_LOG_DIR|g;
            s|%KEYSTONE_AUTH_PORT%|$KEYSTONE_AUTH_PORT|g;
            s|%KEYSTONE_AUTH_HOST%|$KEYSTONE_AUTH_HOST|g;
            s|%KEYSTONE_AUTH_PROTOCOL%|$KEYSTONE_AUTH_PROTOCOL|g;
        " -i $KIBANA_CFG_DIR/kibana.yml
    fi
}

function install_kibana_plugin {
    if is_service_enabled kibana; then
        echo_summary "Install Kibana plugin"

        # note(trebskit) that needs to happen after kibana received
        # its configuration otherwise the plugin fails to be installed

        local pkg=file://$DEST/monasca-kibana-plugin.tar.gz

        $KIBANA_DIR/bin/kibana plugin -r monasca-kibana-plugin
        $KIBANA_DIR/bin/kibana plugin -i monasca-kibana-plugin -u $pkg
    fi
}

function clean_kibana {
    if is_service_enabled kibana; then
        echo_summary "Cleaning Kibana ${KIBANA_VERSION}"

        sudo rm -rf $KIBANA_DIR || true
        sudo rm -rf $FILES/kibana-${KIBANA_VERSION}.tar.gz || true
        sudo rm -rf $KIBANA_LOG_DIR || true
        sudo rm -rf $KIBANA_CFG_DIR || true
    fi
}

function start_kibana {
    if is_service_enabled kibana; then
        echo_summary "Starting Kibana ${KIBANA_VERSION}"
        local kibanaSleepTime=${KIBANA_SLEEP_TIME:-90}     # kibana takes some time to load up
        local kibanaCFG="$KIBANA_CFG_DIR/kibana.yml"
        _run_process_sleep "kibana" "$KIBANA_DIR/bin/kibana --config $kibanaCFG" $kibanaSleepTime
    fi
}

function configure_monasca_log_persister {
    if is_service_enabled monasca-log-persister; then
        echo_summary "Configuring monasca-log-persister"

        sudo install -m 755 -d -o $STACK_USER $LOG_PERSISTER_DIR

        sudo cp -f "${PLUGIN_FILES}"/monasca-log-persister/persister.conf $LOG_PERSISTER_DIR/persister.conf
        sudo chown $STACK_USER $LOG_PERSISTER_DIR/persister.conf
        sudo chmod 0640 $LOG_PERSISTER_DIR/persister.conf

        sudo sed -e "
            s|%ES_SERVICE_BIND_HOST%|$ES_SERVICE_BIND_HOST|g;
        " -i $LOG_PERSISTER_DIR/persister.conf
    fi
}

function clean_monasca_log_persister {
    if is_service_enabled monasca-log-persister; then
        echo_summary "Cleaning monasca-log-persister"
        sudo rm -rf $LOG_PERSISTER_DIR || true
    fi
}

function start_monasca_log_persister {
    if is_service_enabled monasca-log-persister; then
        echo_summary "Starting monasca-log-persister"
        local logstash="$LOGSTASH_DIR/bin/logstash"
        run_process "monasca-log-persister" "$logstash -f $LOG_PERSISTER_DIR/persister.conf"
    fi
}

function configure_monasca_log_transformer {
    if is_service_enabled monasca-log-transformer; then
        echo_summary "Configuring monasca-log-transformer"

        sudo install -m 755 -d -o $STACK_USER $LOG_TRANSFORMER_DIR

        sudo cp -f "${PLUGIN_FILES}"/monasca-log-transformer/transformer.conf $LOG_TRANSFORMER_DIR/transformer.conf
        sudo chown $STACK_USER $LOG_TRANSFORMER_DIR/transformer.conf
        sudo chmod 0640 $LOG_TRANSFORMER_DIR/transformer.conf

        sudo sed -e "
            s|%KAFKA_SERVICE_HOST%|$KAFKA_SERVICE_HOST|g;
            s|%KAFKA_SERVICE_PORT%|$KAFKA_SERVICE_PORT|g;
        " -i $LOG_TRANSFORMER_DIR/transformer.conf
    fi
}

function clean_monasca_log_transformer {
    if is_service_enabled monasca-log-transformer; then
        echo_summary "Cleaning monasca-log-transformer"
        sudo rm -rf $LOG_TRANSFORMER_DIR || true
    fi
}

function start_monasca_log_transformer {
    if is_service_enabled monasca-log-transformer; then
        echo_summary "Starting monasca-log-transformer"
        local logstash="$LOGSTASH_DIR/bin/logstash"
        run_process "monasca-log-transformer" "$logstash -f $LOG_TRANSFORMER_DIR/transformer.conf"
    fi
}

function configure_monasca_log_metrics {
    if is_service_enabled monasca-log-metrics; then
        echo_summary "Configuring monasca-log-metrics"

        sudo install -m 755 -d -o $STACK_USER $LOG_METRICS_DIR

        sudo cp -f "${PLUGIN_FILES}"/monasca-log-metrics/log-metrics.conf $LOG_METRICS_DIR/log-metrics.conf
        sudo chown $STACK_USER $LOG_METRICS_DIR/log-metrics.conf
        sudo chmod 0640 $LOG_METRICS_DIR/log-metrics.conf

        sudo sed -e "
            s|%KAFKA_SERVICE_HOST%|$KAFKA_SERVICE_HOST|g;
            s|%KAFKA_SERVICE_PORT%|$KAFKA_SERVICE_PORT|g;
        " -i $LOG_METRICS_DIR/log-metrics.conf
    fi
}

function clean_monasca_log_metrics {
    if is_service_enabled monasca-log-metrics; then
        echo_summary "Cleaning monasca-log-metrics"
        sudo rm -rf $LOG_METRICS_DIR || true
    fi
}

function start_monasca_log_metrics {
    if is_service_enabled monasca-log-metrics; then
        echo_summary "Starting monasca-log-metrics"
        local logstash="$LOGSTASH_DIR/bin/logstash"
        run_process "monasca-log-metrics" "$logstash -f $LOG_METRICS_DIR/log-metrics.conf"
    fi
}

function install_log_agent {
    if is_service_enabled monasca-log-agent; then
        echo_summary "Installing monasca-log-agent [monasca-output-plugin]"

        local monasca_log_agent_version=0.5.2
        local ls_plugin_filename=logstash-output-monasca_log_api-${monasca_log_agent_version}.gem

        $LOGSTASH_DIR/bin/plugin install "${PLUGIN_FILES}"/monasca-log-agent/${ls_plugin_filename}
    fi
}

function configure_monasca_log_agent {
    if is_service_enabled monasca-log-agent; then
        echo_summary "Configuring monasca-log-agent"

        sudo install -m 755 -d -o $STACK_USER $LOG_AGENT_DIR

        sudo cp -f "${PLUGIN_FILES}"/monasca-log-agent/agent.conf $LOG_AGENT_DIR/agent.conf
        sudo chown $STACK_USER $LOG_AGENT_DIR/agent.conf
        sudo chmod 0640 $LOG_AGENT_DIR/agent.conf

        sudo sed -e "
            s|%MONASCA_LOG_API_URI_V3%|$MONASCA_LOG_API_URI_V3|g;
            s|%KEYSTONE_AUTH_URI_V3%|$KEYSTONE_AUTH_URI_V3|g;
        " -i $LOG_AGENT_DIR/agent.conf

    fi
}

function clean_monasca_log_agent {
    if is_service_enabled monasca-log-agent; then
        echo_summary "Cleaning monasca-log-agent"
        sudo rm -rf $LOG_AGENT_DIR || true
    fi
}

function start_monasca_log_agent {
    if is_service_enabled monasca-log-agent; then
        echo_summary "Starting monasca-log-agent"
        local logstash="$LOGSTASH_DIR/bin/logstash"
        run_process "monasca-log-agent" "sudo $logstash -f $LOG_AGENT_DIR/agent.conf"
    fi
}

function install_node_nvm {
    set -i
    if [[ ! -f "${HOME}/.nvm/nvm.sh" ]] && is_service_enabled kibana; then
        # note(trebskit) we need node to build kibana plugin
        # so if kibana is enabled in this environment, let's install node
        echo_summary "Install Node ${NODE_JS_VERSION} with NVM ${NVM_VERSION}"
        local nvmUrl=https://raw.githubusercontent.com/creationix/nvm/v${NVM_VERSION}/install.sh
        local nvmDest=${FILES}/nvm_install.sh
        download_file ${nvmUrl} ${nvmDest}
        bash ${nvmDest}
    fi
    if is_service_enabled kibana; then
        # refresh installation
        (
            source "${HOME}"/.nvm/nvm.sh >> /dev/null; \
            nvm install ${NODE_JS_VERSION}; \
            nvm use ${NODE_JS_VERSION}; \
            npm config set registry "http://registry.npmjs.org/"; \
            npm config set proxy "${HTTP_PROXY}"; \
            npm set strict-ssl false;
        )
    fi
    set +i
}

function clean_node_nvm {
    if [[ -f "${HOME}/.nvm/nvm.sh" ]] && is_service_enabled kibana; then
        echo_summary "Cleaning Node ${NODE_JS_VERSION} with NVM ${NVM_VERSION}"
        sudo rm ${FILES}/nvm_install.sh
        sudo rm -rf "${HOME}/.nvm/nvm.sh"
    fi
}

function build_kibana_plugin {
    if is_service_enabled kibana; then
        echo "Building Kibana plugin"

        git_clone $MONASCA_KIBANA_PLUGIN_REPO $MONASCA_KIBANA_PLUGIN_DIR \
            $MONASCA_KIBANA_PLUGIN_BRANCH

        pushd $MONASCA_KIBANA_PLUGIN_DIR

        local monasca_kibana_plugin_version
        monasca_kibana_plugin_version="$(python -c 'import json; \
            obj = json.load(open("package.json")); print obj["version"]')"

        set -i
        (source "${HOME}"/.nvm/nvm.sh >> /dev/null; nvm use ${NODE_JS_VERSION}; npm install)
        (source "${HOME}"/.nvm/nvm.sh >> /dev/null; nvm use ${NODE_JS_VERSION}; npm run package)
        set +i

        local pkg=$MONASCA_KIBANA_PLUGIN_DIR/target/monasca-kibana-plugin-${monasca_kibana_plugin_version}.tar.gz
        local easyPkg=$DEST/monasca-kibana-plugin.tar.gz

        ln -sf $pkg $easyPkg

        popd
    fi
}

function configure_kafka {
    echo_summary "Configuring kafka topics"
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 4 --topic log
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 4 --topic transformed-log
}

function create_log_management_accounts {
    if is_service_enabled monasca-log-api; then
        echo_summary "Enable Log Management in Keystone"

        # note(trebskit) following points to Kibana which is bad,
        # but we do not have search-api in monasca-log-api now
        # this code will be removed in future
        local log_search_url="http://$KIBANA_SERVICE_HOST:$KIBANA_SERVICE_PORT/"

        get_or_create_service "logs" "logs" "Monasca Log service"
        get_or_create_endpoint \
            "logs" \
            "$REGION_NAME" \
            "$MONASCA_LOG_API_URI_V3" \
            "$MONASCA_LOG_API_URI_V3" \
            "$MONASCA_LOG_API_URI_V3"

        get_or_create_service "logs_v2" "logs_v2" "Monasca Log V2.0 service"
        get_or_create_endpoint \
            "logs_v2" \
            "$REGION_NAME" \
            "$MONASCA_LOG_API_URI_V2" \
            "$MONASCA_LOG_API_URI_V2" \
            "$MONASCA_LOG_API_URI_V2"

        get_or_create_service "logs-search" "logs-search" "Monasca Log search service"
        get_or_create_endpoint \
            "logs-search" \
            "$REGION_NAME" \
            "$log_search_url" \
            "$log_search_url" \
            "$log_search_url"

    fi
}

function enable_log_management {
    if is_service_enabled horizon && is_service_enabled kibana; then
        echo_summary "Configure Horizon with Kibana access"

        local localSettings=${DEST}/horizon/monitoring/config/local_settings.py

        sudo sed -e "
            s|ENABLE_KIBANA_BUTTON = getattr(settings, 'ENABLE_KIBANA_BUTTON', False)|ENABLE_KIBANA_BUTTON = getattr(settings, 'ENABLE_KIBANA_BUTTON', True)|g;
            s|KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http://192.168.10.4:5601/')|KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http://${KIBANA_SERVICE_HOST}:${KIBANA_SERVICE_PORT}/')|g;
        " -i ${localSettings}

        restart_apache_server
    fi
}

function _run_process_sleep {
    local name=$1
    local cmd=$2
    local sleepTime=${3:-1}
    run_process "$name" "$cmd"
    sleep ${sleepTime}
}

# download_file
#  $1 - url to download
#  $2 - location where to save url to
#
#  File won't be downloaded if it already exists.
#
#  Uses global variables:
#  - OFFLINE
#  - DOWNLOAD_FILE_TIMEOUT
# note(trebskit) maybe this function will enter upstream devstack in case it does
#                we should remove it from here
function download_file {
    local url=$1
    local file=$2

    # if file is not there and it is OFFLINE mode
    # that is bad...terminate everything
    if [[ ${OFFLINE} == "True" ]] && [[ ! -f ${file} ]]; then
        die $LINENO    "You are running in OFFLINE mode but
                        the target file \"$file\" was not found"
    fi

    local curl_z_flag=""
    if [[ -f ${file} ]]; then
        # If the file exists tell cURL to download only if newer version
        # is available
        curl_z_flag="-z $file"
    fi

    local timeout=0
    if [[ -n "${DOWNLOAD_FILE_TIMEOUT}" ]]; then
        timeout=${DOWNLOAD_FILE_TIMEOUT}
    fi

    # yeah...downloading...devstack...hungry..om, om, om
    time_start "download_file"
    _safe_permission_operation ${CURL_GET} -L $url --connect-timeout $timeout --retry 3 --retry-delay 5 -o $file $curl_z_flag
    time_stop "download_file"

}

function is_logstash_required {
    is_service_enabled monasca-log-persister \
        || is_service_enabled monasca-log-transformer \
        || is_service_enabled monasca-log-metrics \
        || is_service_enabled monasca-log-agent \
        && return 0
}

# check for service enabled
if is_service_enabled monasca-log; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring Monasca Log Management system services"
        pre_install

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Monasca Log Management"
        install_monasca_log

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Monasca Log Management"
        configure_monasca_log

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the Monasca service
        echo_summary "Initializing Monasca Log Management"
        init_monasca_log
        start_monasca_log
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down Monasca services
        echo_summary "Unstacking Monasca Log Management"
        stop_monasca_log
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        echo_summary "Cleaning Monasca Log Management"
        clean_monasca_log
    fi
fi

#Restore errexit
$_ERREXIT_LOG_API

# Restore xtrace
$_XTRACE_LOG_API
