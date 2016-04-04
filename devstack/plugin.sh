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
XTRACE=$(set +o | grep xtrace)
set -o xtrace

ERREXIT=$(set +o | grep errexit)
set -o errexit

function pre_install_monasca_log {
:
}

function install_monasca_log {
    install_logstash
    configure_kafka
    install_monasca_elasticsearch
    configure_log_persister
    configure_log_transformer
    install_monasca_log_api
    install_kibana
}

function extra_monasca_log {
    enable_log_management
    add_log_api_service
    configure_log_agent
}

function install_monasca_log_api {
    echo_summary "install monasca log api"
    sudo mkdir -p /opt/monasca-log-api
    sudo chown $STACK_USER:monasca /opt/monasca-log-api
    (cd /opt/monasca-log-api; virtualenv .)

    PIP_VIRTUAL_ENV=/opt/monasca-log-api
    pip_install gunicorn
    pip_install python-memcached

    (cd "${MONASCA_BASE}"/monasca-log-api ; sudo python setup.py sdist)
    MONASCA_LOG_API_SRC_DIST=$(ls -td "${MONASCA_BASE}"/monasca-log-api/dist/monasca-log-api-*.tar.gz)
    pip_install ${MONASCA_LOG_API_SRC_DIST}

    unset PIP_VIRTUAL_ENV

    sudo useradd --system -g monasca mon-log-api || true

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-api/monasca-log-api.conf /etc/init/monasca-log-api.conf
    sudo chown root:root /etc/init/monasca-log-api.conf
    sudo chmod 0744 /etc/init/monasca-log-api.conf

    sudo mkdir -p /var/log/monasca/ || true
    sudo chown root:monasca /var/log/monasca
    sudo chmod 0755 /var/log/monasca

    sudo mkdir -p /var/log/monasca/log-api || true
    sudo chown mon-log-api:monasca /var/log/monasca/log-api
    sudo chmod 0755 /var/log/monasca/log-api

    sudo mkdir -p /etc/monasca || true
    sudo chown root:monasca /etc/monasca
    sudo chmod 0755 /etc/monasca

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-api/log-api-config.conf /etc/monasca/log-api-config.conf
    sudo chown mon-log-api:root /etc/monasca/log-api-config.conf
    sudo chmod 0660 /etc/monasca/log-api-config.conf

    if [[ ${SERVICE_HOST} ]]; then
        # set kafka ip address
        sudo sed -i "s/127\.0\.0\.1:9092/${SERVICE_HOST}:9092/g" /etc/monasca/log-api-config.conf
        # set keystone ip address
        sudo sed -i "s/identity_uri = http:\/\/127\.0\.0\.1:35357/identity_uri = http:\/\/${SERVICE_HOST}:35357/g" /etc/monasca/log-api-config.conf
        sudo sed -i "s/auth_uri = http:\/\/127\.0\.0\.1:5000/auth_uri = http:\/\/${SERVICE_HOST}:5000/g" /etc/monasca/log-api-config.conf
    fi
    sudo ln -sf /etc/monasca/log-api-config.conf /etc/log-api-config.conf

    sudo cp  -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-api/log-api-config.ini /etc/monasca/log-api-config.ini
    sudo chown mon-log-api:root /etc/monasca/log-api-config.ini
    sudo chmod 0660 /etc/monasca/log-api-config.ini

    if [[ ${SERVICE_HOST} ]]; then
        # set influxdb ip address
        sudo sed -i "s/host = 127\.0\.0\.1/host = ${SERVICE_HOST}/g" /etc/monasca/log-api-config.ini
    fi
    sudo ln -sf /etc/monasca/log-api-config.ini /etc/log-api-config.ini
    sudo start monasca-log-api || sudo restart monasca-log-api
}

function install_logstash {
    echo_summary "install logstash"

    sudo curl -L http://download.elastic.co/logstash/logstash/logstash-${LOGSTASH_VERSION}.tar.gz -o /opt/logstash-${LOGSTASH_VERSION}.tar.gz
    sudo tar xzf /opt/logstash-${LOGSTASH_VERSION}.tar.gz -C /opt
    sudo rm -f /opt/logstash-${LOGSTASH_VERSION}.tar.gz

    sudo ln -sf /opt/logstash-${LOGSTASH_VERSION} /opt/logstash

    install_logstash_monasca_output_plugin
}

function install_logstash_monasca_output_plugin {
    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-agent/logstash-output-monasca_log_api-0.3.3.gem /opt/logstash/logstash-output-monasca_log_api-0.3.3.gem
    sudo /opt/logstash/bin/plugin install /opt/logstash/logstash-output-monasca_log_api-0.3.3.gem
    sudo rm -f /opt/logstash/logstash-output-monasca_log_api-0.3.3.gem
}

function install_monasca_elasticsearch {
    echo_summary "install elastic search"

    sudo groupadd --system elastic || true
    sudo useradd --system -g elastic elastic || true

    sudo curl -L http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz -o /opt/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz
    sudo tar xzf /opt/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz -C /opt
    sudo rm -f /opt/elasticsearch-${ELASTICSEARCH_VERSION}.tar.gz

    sudo chown -R elastic:elastic /opt/elasticsearch-${ELASTICSEARCH_VERSION}

    sudo ln -sf /opt/elasticsearch-${ELASTICSEARCH_VERSION} /opt/elasticsearch

    sudo mkdir -p /var/log/elasticsearch || true
    sudo chown elastic:elastic /var/log/elasticsearch
    sudo chmod 750 /var/log/elasticsearch

    sudo mkdir -p /opt/elasticsearch/config/templates || true
    sudo chown elastic:elastic /opt/elasticsearch/config/templates
    sudo chmod 750 /opt/elasticsearch/config/templates

    sudo mkdir -p /var/data/elasticsearch || true
    sudo chown elastic:elastic /var/data/elasticsearch
    sudo chmod 750 /var/data/elasticsearch

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/elasticsearch/elasticsearch.yml /opt/elasticsearch/config/elasticsearch.yml
    sudo chown elastic:elastic /opt/elasticsearch/config/elasticsearch.yml
    sudo chmod 0640 /opt/elasticsearch/config/elasticsearch.yml

    if [[ ${SERVICE_HOST} ]]; then
        # set ip address
        sudo sed -i "s/network.publish_host: 127\.0\.0\.1/network.publish_host: ${SERVICE_HOST}/g" /opt/elasticsearch/config/elasticsearch.yml
    fi

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/elasticsearch/elasticsearch.conf /etc/init/elasticsearch.conf
    sudo chown elastic:elastic /etc/init/elasticsearch.conf
    sudo chmod 0640 /etc/init/elasticsearch.conf

    sudo start elasticsearch || sudo restart elasticsearch
}

function configure_kafka {
    echo_summary "configure_kafka"
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 4 --topic log
    /opt/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 4 --topic transformed-log
}

function add_log_api_service {
    echo_summary "configure_keystone"
    sudo apt-get -y install python-dev
    PIP_VIRTUAL_ENV=/opt/monasca-log-api

    pip_install python-keystoneclient

    unset PIP_VIRTUAL_ENV
    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/keystone/create_monasca_log_service.py /usr/local/bin/create_monasca_log_service.py
    sudo chmod 0700 /usr/local/bin/create_monasca_log_service.py

    if [[ ${SERVICE_HOST} ]]; then
        sudo /opt/monasca-log-api/bin/python /usr/local/bin/create_monasca_log_service.py ${SERVICE_HOST} ${OS_USERNAME} ${OS_PASSWORD} ${OS_PROJECT_NAME}
    else
        sudo /opt/monasca-log-api/bin/python /usr/local/bin/create_monasca_log_service.py "127.0.0.1" ${OS_USERNAME} ${OS_PASSWORD} ${OS_PROJECT_NAME}
    fi
}

function configure_log_persister {
    echo_summary "configure_log_persister"

    sudo useradd --system -g monasca mon-persister || true

    sudo mkdir -p /etc/monasca || true
    sudo chown root:monasca /etc/monasca
    sudo chmod 0755 /etc/monasca

    sudo mkdir -p /etc/monasca/log || true
    sudo chown root:monasca /etc/monasca/log
    sudo chmod 0755 /etc/monasca/log

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-persister/persister.conf /etc/monasca/log/persister.conf
    sudo chown mon-persister:monasca /etc/monasca/log/persister.conf
    sudo chmod 0640 /etc/monasca/log/persister.conf

    if [[ ${SERVICE_HOST} ]]; then
        # set zookeeper ip address
        sudo sed -i "s/zk_connect => \"127\.0\.0\.1:2181\"/zk_connect => \"${SERVICE_HOST}:2181\"/g" /etc/monasca/log/persister.conf
    fi

    sudo mkdir -p /var/log/monasca || true
    sudo chown root:monasca /var/log/monasca
    sudo chmod 0755 /var/log/monasca

    sudo mkdir -p /var/log/monasca/monasca-log-persister || true
    sudo chown mon-persister:monasca /var/log/monasca/monasca-log-persister
    sudo chmod 0750 /var/log/monasca/monasca-log-persister

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-persister/monasca-log-persister.conf /etc/init/monasca-log-persister.conf
    sudo chown mon-persister:monasca /etc/init/monasca-log-persister.conf
    sudo chmod 0640 /etc/init/monasca-log-persister.conf

    sudo start monasca-log-persister || sudo restart monasca-log-persister
}

function configure_log_transformer {
    echo_summary "configure_log_persister"

    sudo useradd --system -g monasca mon-transformer || true

    sudo mkdir -p /var/log/monasca/monasca-log-transformer || true
    sudo chown mon-transformer:monasca /var/log/monasca/monasca-log-transformer
    sudo chmod 0750 /var/log/monasca/monasca-log-transformer

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-transformer/transformer.conf /etc/monasca/log/transformer.conf
    sudo chown mon-transformer:monasca /etc/monasca/log/transformer.conf
    sudo chmod 0640 /etc/monasca/log/transformer.conf

    if [[ ${SERVICE_HOST} ]]; then
        # set zookeeper ip address
        sudo sed -i "s/zk_connect => \"127\.0\.0\.1:2181\"/zk_connect => \"${SERVICE_HOST}:2181\"/g" /etc/monasca/log/transformer.conf
        # set kafka ip address
        sudo sed -i "s/bootstrap_servers => \"127\.0\.0\.1:9092\"/bootstrap_servers => \"${SERVICE_HOST}:9092\"/g" /etc/monasca/log/transformer.conf
    fi

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-transformer/monasca-log-transformer.conf /etc/init/monasca-log-transformer.conf
    sudo chown mon-transformer:monasca /etc/init/monasca-log-transformer.conf
    sudo chmod 0640 /etc/init/monasca-log-transformer.conf

    sudo start monasca-log-transformer || sudo restart monasca-log-transformer
}

function install_kibana {
    echo_summary "install_kibana"

    sudo groupadd --system kibana || true
    sudo useradd --system -g kibana kibana || true

    sudo curl -L http://download.elastic.co/kibana/kibana/kibana-${KIBANA_VERSION}.tar.gz -o /opt/kibana-${KIBANA_VERSION}.tar.gz
    sudo tar xzf /opt/kibana-${KIBANA_VERSION}.tar.gz -C /opt
    sudo rm -f /opt/kibana-${KIBANA_VERSION}.tar.gz

    sudo chown -R kibana:kibana /opt/kibana-${KIBANA_VERSION}

    sudo ln -sf /opt/kibana-${KIBANA_VERSION} /opt/kibana

    sudo mkdir -p /opt/kibana/config || true
    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/kibana/kibana.yml /opt/kibana/config/kibana.yml

    if [[ ${SERVICE_HOST} ]]; then
        # set bind host ip address
        sudo sed -i "s/server.host: 127\.0\.0\.1/server.host: ${SERVICE_HOST}/g" /opt/kibana/config/kibana.yml
    fi

    sudo mkdir -p /var/log/kibana || true
    sudo chown kibana:kibana /var/log/kibana
    sudo chmod 0750 /var/log/kibana

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/kibana/kibana.conf /etc/init/kibana.conf
    sudo chown kibana:kibana /etc/init/kibana.conf
    sudo chmod 0640 /etc/init/kibana.conf

    sudo start kibana || sudo restart kibana
}

function enable_log_management {
    echo_summary "configure_horizon"
    sudo sed -i "s/ENABLE_KIBANA_BUTTON = getattr(settings, 'ENABLE_KIBANA_BUTTON', False)/ENABLE_KIBANA_BUTTON = getattr(settings, 'ENABLE_KIBANA_BUTTON', True)/g" /opt/stack/horizon/monitoring/config/local_settings.py
    if [[ ${SERVICE_HOST} ]]; then
        sudo sed -i "s/KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http:\/\/192\.168\.10\.4:5601\/')/KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http:\/\/${SERVICE_HOST}:5601\/')/g" /opt/stack/horizon/monitoring/config/local_settings.py
    else
        sudo sed -i "s/KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http:\/\/192\.168\.10\.4:5601\/')/KIBANA_HOST = getattr(settings, 'KIBANA_HOST', 'http:\/\/127\.0\.0\.1:5601\/')/g" /opt/stack/horizon/monitoring/config/local_settings.py
    fi

    sudo /etc/init.d/apache2 stop || true
    sudo /etc/init.d/apache2 start
}

function post_config_monasca_log {
:
}

function configure_log_agent {
    echo_summary "configure_log_agent"

    sudo useradd --system -g monasca mon-log-agent || true

    sudo mkdir -p /var/log/monasca/monasca-log-agent || true
    sudo chown mon-log-agent:monasca /var/log/monasca/monasca-log-agent
    sudo chmod 0750 /var/log/monasca/monasca-log-agent

    sudo mkdir -p /etc/monasca/monasca-log-agent || true
    sudo chown mon-log-agent:monasca /etc/monasca/monasca-log-agent
    sudo chmod 0750 /etc/monasca/monasca-log-agent

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-agent/agent.conf /etc/monasca/monasca-log-agent/agent.conf
    sudo chown mon-log-agent:monasca /etc/monasca/monasca-log-agent/agent.conf
    sudo chmod 0640 /etc/monasca/monasca-log-agent/agent.conf

    if [[ ${SERVICE_HOST} ]]; then
        # set log api ip address
        sudo sed -i "s/monasca_log_api => \"http:\/\/127\.0\.0\.1:5607\"/monasca_log_api => \"http:\/\/${SERVICE_HOST}:5607\"/g" /etc/monasca/monasca-log-agent/agent.conf
    fi

    sudo cp -f "${MONASCA_BASE}"/monasca-log-api/devstack/files/monasca-log-agent/monasca-log-agent.conf /etc/init/monasca-log-agent.conf
    sudo chown mon-log-agent:monasca /etc/init/monasca-log-agent.conf
    sudo chmod 0640 /etc/init/monasca-log-agent.conf

    sudo start monasca-log-agent || sudo restart monasca-log-agent
}

function unstack_monasca_log {
    sudo stop monasca-log-agent || true
    sudo stop monasca-log-api || true
    sudo stop monasca-log-transformer || true
    sudo stop monasca-log-persister || true
    sudo stop kibana || true
    sudo stop elasticsearch || true
}

function clean_monasca_log {
    unstack_monasca_log

    clean_monasca_log_agent
    clean_monasca_log_api
    clean_monasca_log_transformer
    clean_monasca_log_persister
    clean_kibana
    clean_elastic_search
    clean_logstash
}

function clean_monasca_log_agent {
    echo_summary "clean_log_agent"

    sudo rm -rf /var/log/monasca/monasca-log-agent
    sudo rm -rf /etc/monasca/monasca-log-agent
    sudo rm -f /etc/init/monasca-log-agent.conf

    sudo userdel mon-log-agent || true
}

function clean_monasca_log_api {
    echo_summary "clean log api"

    sudo rm -rf /var/log/monasca/log-api
    sudo rm -f /etc/log-api-config.ini
    sudo rm -f /etc/log-api-config.conf
    sudo rm -f /etc/init/monasca-log-api.conf
    sudo rm -f /etc/monasca/log-api-config.conf
    sudo rm -f /etc/monasca/log-api-config.ini

    sudo rm -rf /opt/monasca-log-api

    sudo userdel mon-log-api || true
}

function clean_monasca_log_transformer {
    echo_summary "clean log transformer"

    sudo rm -rf /var/log/monasca/monasca-log-transformer
    sudo rm -rf /etc/monasca/log
    sudo rm -f /etc/init/monasca-log-transformer.conf

    sudo userdel mon-transformer || true
}

function clean_monasca_log_persister {
    echo_summary "clean log persister"

    sudo rm -rf /var/log/monasca/monasca-log-persister
    sudo rm -rf /etc/monasca/log
    sudo rm -f /etc/init/monasca-log-persister.conf

    sudo userdel mon-persister || true
}

function clean_kibana {
    echo_summary "clean kibana"

    sudo rm -rf /opt/kibana
    sudo rm -rf /opt/kibana-${KIBANA_VERSION}
    sudo rm -rf /var/log/kibana
    sudo rm -f /etc/init/kibana.conf

    sudo userdel kibana || true
    sudo groupdel kibana || true
}

function clean_elastic_search {
    echo_summary "clean elasticsearch"

    sudo rm -rf /opt/elasticsearch
    sudo rm -rf /opt/elasticsearch-${ELASTICSEARCH_VERSION}
    sudo rm -rf /var/log/elasticsearch
    sudo rm -rf /opt/elasticsearch/config/templates
    sudo rm -rf /var/data/elasticsearch
    sudo rm -f /etc/init/elasticsearch.conf

    sudo userdel elastic || true
    sudo groupdel elastic || true
}

function clean_logstash {
    echo_summary "clean logstash"

    sudo rm -rf /opt/logstash
    sudo rm -rf /opt/logstash-${LOGSTASH_VERSION}
}



# check for service enabled
if is_service_enabled monasca_log; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        # Set up system services
        echo_summary "Configuring Monasca Log Management system services"
        pre_install_monasca_log

    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        # Perform installation of service source
        echo_summary "Installing Monasca Log Management"
        install_monasca_log

    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configuring Monasca Log Management"
        post_config_monasca_log

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize and start the Monasca service
        echo_summary "Initializing Monasca Log Management"
        extra_monasca_log
    fi

    if [[ "$1" == "unstack" ]]; then
        # Shut down Monasca services
        echo_summary "Unstacking Monasca Log Management"
        unstack_monasca_log
    fi

    if [[ "$1" == "clean" ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        echo_summary "Cleaning Monasca Log Management"
        clean_monasca_log
    fi
fi

#Restore errexit
$ERREXIT

# Restore xtrace
$XTRACE
