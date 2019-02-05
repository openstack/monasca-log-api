#!/bin/sh

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

# Starting script.
# All checks and configuration templating you need to do before service
# could be safely started should be added in this file.

set -eo pipefail  # Exit the script if any statement returns error.

# Test services we need before starting our service.
echo "Start script: waiting for needed services"
python3 /kafka_wait_for_topics.py

# Template all config files before start, it will use env variables.
# Read usage examples: https://pypi.org/project/Templer/
echo "Start script: creating config files from templates"
templer -v -f /etc/monasca/monasca-log-api.conf.j2  /etc/monasca/monasca-log-api.conf
templer -v -f /etc/monasca/log-api-gunicorn.conf.j2 /etc/monasca/log-api-gunicorn.conf
templer -v -f /etc/monasca/log-api-logging.conf.j2  /etc/monasca/log-api-logging.conf
templer -v -f /etc/monasca/log-api-paste.ini.j2     /etc/monasca/log-api-paste.ini

# Start our service.
# gunicorn --args
echo "Start script: starting container"
gunicorn \
    --config /etc/monasca/log-api-gunicorn.conf \
    --paste /etc/monasca/log-api-paste.ini

# Allow server to stay alive in case of failure for 2 hours for debugging.
RESULT=$?
if [ $RESULT != 0 ] && [ "$STAY_ALIVE_ON_FAILURE" = "true" ]; then
  echo "Service died, waiting 120 min before exiting"
  sleep 7200
fi
exit $RESULT
