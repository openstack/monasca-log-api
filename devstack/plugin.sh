#!/bin/bash

#
# Copyright 2016-2017 FUJITSU LIMITED
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

# source lib/*
source ${MONASCA_LOG_API_DIR}/devstack/lib/util.sh
source ${MONASCA_LOG_API_DIR}/devstack/lib/config.sh
# source lib/*

# TOP_LEVEL functions called from devstack coordinator
###############################################################################
function pre_install {
    install_elk
    install_node_nvm
    install_gate_config_holder
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

function install_gate_config_holder {
    sudo install -d -o $STACK_USER $GATE_CONFIGURATION_DIR
}

function install_monasca_common {
    if use_library_from_git "monasca-common"; then
        git_clone_by_name "monasca-common"
        setup_dev_lib "monasca-common"
    fi
}

function install_monasca_statsd {
    if use_library_from_git "monasca-statsd"; then
        git_clone_by_name "monasca-statsd"
        setup_dev_lib "monasca-statsd"
    fi
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
    stop_monasca_log_api
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
    clean_gate_config_holder
}
###############################################################################

function install_monasca-log-api {
    echo_summary "Installing monasca-log-api"

    git_clone $MONASCA_LOG_API_REPO $MONASCA_LOG_API_DIR $MONASCA_LOG_API_BRANCH
    setup_develop $MONASCA_LOG_API_DIR

    install_keystonemiddleware
    install_monasca_common
    install_monasca_statsd

    if [ "$MONASCA_LOG_API_DEPLOY" == "mod_wsgi" ]; then
        install_apache_wsgi
    elif [ "$MONASCA_LOG_API_DEPLOY" == "uwsgi" ]; then
        pip_install uwsgi
    else
        pip_install gunicorn
    fi

    if [ "$MONASCA_LOG_API_DEPLOY" != "gunicorn" ]; then
        if is_ssl_enabled_service "monasca-log-api"; then
            enable_mod_ssl
        fi
    fi
}

function configure_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Configuring monasca-log-api"

        configure_monasca_log_api_core
        if [ "$MONASCA_LOG_API_DEPLOY" == "mod_wsgi" ]; then
            configure_monasca_log_api_mod_wsgi
        elif [ "$MONASCA_LOG_API_DEPLOY" == "uwsgi" ]; then
            configure_monasca_log_api_uwsgi
        fi

        # link configuration for the gate
        ln -sf $MONASCA_LOG_API_CONF $GATE_CONFIGURATION_DIR
        ln -sf $MONASCA_LOG_API_PASTE $GATE_CONFIGURATION_DIR
        ln -sf $MONASCA_LOG_API_LOGGING_CONF $GATE_CONFIGURATION_DIR

    fi
}

function configure_monasca_log_api_core {
    # Put config files in ``$MONASCA_LOG_API_CONF_DIR`` for everyone to find
    sudo install -d -o $STACK_USER $MONASCA_LOG_API_CONF_DIR
    sudo install -m 700 -d -o $STACK_USER $MONASCA_LOG_API_CACHE_DIR
    sudo install -d -o $STACK_USER $MONASCA_LOG_API_LOG_DIR

    # ensure fresh installation of configuration files
    rm -rf $MONASCA_LOG_API_CONF $MONASCA_LOG_API_PASTE $MONASCA_LOG_API_LOGGING_CONF

    $MONASCA_LOG_API_BIN_DIR/oslo-config-generator \
        --config-file $MONASCA_LOG_API_DIR/config-generator/monasca-log-api.conf \
        --output-file /tmp/log-api.conf

    install -m 600 /tmp/log-api.conf $MONASCA_LOG_API_CONF && rm -rf /tmp/log-api.conf
    install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-paste.ini $MONASCA_LOG_API_PASTE
    install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-logging.conf $MONASCA_LOG_API_LOGGING_CONF

    # configure log-api.conf
    iniset "$MONASCA_LOG_API_CONF" DEFAULT log_config_append $MONASCA_LOG_API_LOGGING_CONF
    iniset "$MONASCA_LOG_API_CONF" service region $REGION_NAME

    iniset "$MONASCA_LOG_API_CONF" log_publisher kafka_url $KAFKA_SERVICE_HOST:$KAFKA_SERVICE_PORT
    iniset "$MONASCA_LOG_API_CONF" log_publisher topics log

    iniset "$MONASCA_LOG_API_CONF" kafka_healthcheck kafka_url $KAFKA_SERVICE_HOST:$KAFKA_SERVICE_PORT
    iniset "$MONASCA_LOG_API_CONF" kafka_healthcheck kafka_topics log

    iniset "$MONASCA_LOG_API_CONF" roles_middleware path "/v2.0/log,/v3.0/logs"
    iniset "$MONASCA_LOG_API_CONF" roles_middleware default_roles monasca-user
    iniset "$MONASCA_LOG_API_CONF" roles_middleware agent_roles monasca-agent
    iniset "$MONASCA_LOG_API_CONF" roles_middleware delegate_roles admin

    # configure keystone middleware
    configure_auth_token_middleware "$MONASCA_LOG_API_CONF" "admin" $MONASCA_LOG_API_CACHE_DIR
    iniset "$MONASCA_LOG_API_CONF" keystone_authtoken region_name $REGION_NAME
    iniset "$MONASCA_LOG_API_CONF" keystone_authtoken project_name "admin"
    iniset "$MONASCA_LOG_API_CONF" keystone_authtoken password $ADMIN_PASSWORD

    # insecure
    if is_service_enabled tls-proxy; then
        iniset "$MONASCA_LOG_API_CONF" keystone_authtoken insecure False
    fi

    # configure log-api-paste.ini
    iniset "$MONASCA_LOG_API_PASTE" server:main bind $MONASCA_LOG_API_SERVICE_HOST:$MONASCA_LOG_API_SERVICE_PORT
    iniset "$MONASCA_LOG_API_PASTE" server:main chdir $MONASCA_LOG_API_DIR
    iniset "$MONASCA_LOG_API_PASTE" server:main workers $API_WORKERS
}

function configure_monasca_log_api_uwsgi {
    rm -rf $MONASCA_LOG_API_UWSGI_CONF
    install -m 600 $MONASCA_LOG_API_DIR/etc/monasca/log-api-uwsgi.ini $MONASCA_LOG_API_UWSGI_CONF

    write_uwsgi_config "$MONASCA_LOG_API_UWSGI_CONF" "$MONASCA_LOG_API_WSGI" "/logs"
}

function configure_monasca_log_api_mod_wsgi {
    sudo install -d $MONASCA_LOG_API_WSGI_DIR

    local monasca_log_api_apache_conf
    monasca_log_api_apache_conf=$(apache_site_config_for monasca-log-api)

    local monasca_log_api_ssl=""
    local monasca_log_api_certfile=""
    local monasca_log_api_keyfile=""
    local monasca_log_api_api_port=$MONASCA_LOG_API_SERVICE_PORT
    local venv_path=""

    if is_ssl_enabled_service monasca_log_api; then
        monasca_log_api_ssl="SSLEngine On"
        monasca_log_api_certfile="SSLCertificateFile $MONASCA_LOG_API_SSL_CERT"
        monasca_log_api_keyfile="SSLCertificateKeyFile $MONASCA_LOG_API_SSL_KEY"
    fi
    if is_service_enabled tls-proxy; then
        monasca_log_api_api_port=$MONASCA_LOG_API_SERVICE_PORT_INT
    fi
    if [[ ${USE_VENV} = True ]]; then
        venv_path="python-path=${PROJECT_VENV["monasca_log_api"]}/lib/$(python_version)/site-packages"
    fi

    # copy proxy vhost and wsgi helper files
    sudo cp $PLUGIN_FILES/apache-log-api.template $monasca_log_api_apache_conf
    sudo sed -e "
        s|%PUBLICPORT%|$monasca_log_api_api_port|g;
        s|%APACHE_NAME%|$APACHE_NAME|g;
        s|%PUBLICWSGI%|$MONASCA_LOG_API_BIN_DIR/monasca-log-api-wsgi|g;
        s|%SSLENGINE%|$monasca_log_api_ssl|g;
        s|%SSLCERTFILE%|$monasca_log_api_certfile|g;
        s|%SSLKEYFILE%|$monasca_log_api_keyfile|g;
        s|%USER%|$STACK_USER|g;
        s|%VIRTUALENV%|$venv_path|g
        s|%APIWORKERS%|$API_WORKERS|g
    " -i $monasca_log_api_apache_conf
}

function create_log_api_cache_dir {
    sudo install -m 700 -d -o $STACK_USER $MONASCA_LOG_API_CACHE_DIR
}

function clean_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Cleaning monasca-log-api"

        sudo rm -f $MONASCA_LOG_API_CONF || true
        sudo rm -f $MONASCA_LOG_API_PASTE  || true
        sudo rm -f $MONASCA_LOG_API_LOGGING_CONF || true
        sudo rm -rf $MONASCA_LOG_API_CACHE_DIR || true
        sudo rm -rf $MONASCA_LOG_API_CONF_DIR || true

        sudo rm -rf $MONASCA_LOG_API_DIR || true

        if [ "$MONASCA_LOG_API_USE_MOD_WSGI" == "True" ]; then
            clean_monasca_log_api_wsgi
        fi
    fi
}

function clean_monasca_log_api_wsgi {
    sudo rm -f $MONASCA_LOG_API_WSGI_DIR/*
    sudo rm -f $(apache_site_config_for monasca-log-api)
}

function start_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        echo_summary "Starting monasca-log-api"

        local service_port=$MONASCA_LOG_API_SERVICE_PORT
        local service_protocol=$MONASCA_LOG_API_SERVICE_PROTOCOL
        if is_service_enabled tls-proxy; then
            service_port=$MONASCA_LOG_API_SERVICE_PORT_INT
            service_protocol="http"
        fi
        local service_uri

        if [ "$MONASCA_LOG_API_DEPLOY" == "mod_wsgi" ]; then
            local enabled_site_file
            enabled_site_file=$(apache_site_config_for monasca-log-api)
            service_uri=$service_protocol://$MONASCA_LOG_API_SERVICE_HOST/logs/v3.0
            if [ -f ${enabled_site_file} ]; then
                enable_apache_site monasca-log-api
                restart_apache_server
                tail_log monasca-log-api /var/log/$APACHE_NAME/monasca-log-api.log
            fi
        elif [ "$MONASCA_LOG_API_DEPLOY" == "uwsgi" ]; then
            service_uri=$service_protocol://$MONASCA_LOG_API_SERVICE_HOST/logs/v3.0
            run_process "monasca-log-api" "$MONASCA_LOG_API_BIN_DIR/uwsgi --ini $MONASCA_LOG_API_UWSGI_CONF" ""
        else
            service_uri=$service_protocol://$MONASCA_LOG_API_SERVICE_HOST:$service_port
            run_process "monasca-log-api" "$MONASCA_LOG_API_BIN_DIR/gunicorn --paste $MONASCA_LOG_API_PASTE" ""
        fi

        echo "Waiting for monasca-log-api to start..."
        if ! wait_for_service $SERVICE_TIMEOUT $service_uri; then
            die $LINENO "monasca-log-api did not start"
        fi

        if is_service_enabled tls-proxy; then
            start_tls_proxy monasca-log-api '*' $MONASCA_LOG_API_SERVICE_PORT $MONASCA_LOG_API_SERVICE_HOST $MONASCA_LOG_API_SERVICE_PORT_INT
        fi

        restart_service memcached
    fi
}

function stop_monasca_log_api {
    if is_service_enabled monasca-log-api; then
        if [ "$MONASCA_LOG_API_DEPLOY" == "mod_wsgi" ]; then
            disable_apache_site monasca-log-api
            restart_apache_server
        else
            stop_process "monasca-log-api"
            if [ "$MONASCA_LOG_API_DEPLOY" == "uwsgi" ]; then
                remove_uwsgi_config  "$MONASCA_LOG_API_UWSGI_CONF" "$MONASCA_LOG_API_WSGI"
            fi
        fi
    fi
}

function install_logstash {
    if is_logstash_required; then
        echo_summary "Installing Logstash ${LOGSTASH_VERSION}"

        local logstash_tarball=logstash-${LOGSTASH_VERSION}.tar.gz
        local logstash_url=http://download.elastic.co/logstash/logstash/${logstash_tarball}

        local logstash_dest
        logstash_dest=`get_extra_file ${logstash_url}`

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

        local es_dest
        es_dest=`get_extra_file ${es_url}`

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

        ln -sf $ELASTICSEARCH_CFG_DIR/elasticsearch.yml $GATE_CONFIGURATION_DIR/elasticsearch.yml
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
        run_process_sleep "elasticsearch" "$ELASTICSEARCH_DIR/bin/elasticsearch" $esSleepTime
    fi
}

function install_kibana {
    if is_service_enabled kibana; then
        echo_summary "Installing Kibana ${KIBANA_VERSION}"

        local kibana_tarball=kibana-${KIBANA_VERSION}.tar.gz
        local kibana_tarball_url=http://download.elastic.co/kibana/kibana/${kibana_tarball}

        local kibana_tarball_dest
        kibana_tarball_dest=`get_extra_file ${kibana_tarball_url}`

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
            s|%KEYSTONE_AUTH_URI%|$KEYSTONE_AUTH_URI|g;
        " -i $KIBANA_CFG_DIR/kibana.yml

        ln -sf $KIBANA_CFG_DIR/kibana.yml $GATE_CONFIGURATION_DIR/kibana.yml
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
        sudo rm -rf $KIBANA_CFG_DIR || true
    fi
}

function start_kibana {
    if is_service_enabled kibana; then
        echo_summary "Starting Kibana ${KIBANA_VERSION}"
        local kibanaSleepTime=${KIBANA_SLEEP_TIME:-90}     # kibana takes some time to load up
        local kibanaCFG="$KIBANA_CFG_DIR/kibana.yml"
        run_process_sleep "kibana" "$KIBANA_DIR/bin/kibana --config $kibanaCFG" $kibanaSleepTime
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

        ln -sf $LOG_PERSISTER_DIR/persister.conf $GATE_CONFIGURATION_DIR/log-persister.conf
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

        ln -sf $LOG_TRANSFORMER_DIR/transformer.conf $GATE_CONFIGURATION_DIR/log-transformer.conf
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

        ln -sf $LOG_METRICS_DIR/log-metrics.conf $GATE_CONFIGURATION_DIR/log-metrics.conf
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

        ln -sf $LOG_AGENT_DIR/agent.conf $GATE_CONFIGURATION_DIR/log-agent.conf

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
        run_process "monasca-log-agent" "$logstash -f $LOG_AGENT_DIR/agent.conf" "root" "root"
    fi
}

function install_node_nvm {
    set -i
    if [[ ! -f "${HOME}/.nvm/nvm.sh" ]] && is_service_enabled kibana; then
        # note(trebskit) we need node to build kibana plugin
        # so if kibana is enabled in this environment, let's install node
        echo_summary "Install Node ${NODE_JS_VERSION} with NVM ${NVM_VERSION}"
        local nvmUrl=https://raw.githubusercontent.com/creationix/nvm/v${NVM_VERSION}/install.sh

        local nvmDest
        nvmDest=`get_extra_file ${nvmUrl}`

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

function clean_gate_config_holder {
    sudo rm -rf $GATE_CONFIGURATION_DIR || true
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
    echo_summary "Configuring Kafka topics"
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 \
        --replication-factor 1 --partitions 4 --topic log
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 \
        --replication-factor 1 --partitions 4 --topic transformed-log
}

function delete_kafka_topics {
    echo_summary "Deleting Kafka topics"
        /opt/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 \
                --topic log || true
        /opt/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 \
                --topic transformed-log || true
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
        delete_kafka_topics
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
