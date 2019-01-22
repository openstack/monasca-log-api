ARG DOCKER_IMAGE=monasca/log-api
ARG APP_REPO=https://git.openstack.org/openstack/monasca-log-api

# Branch, tag or git hash to build from.
ARG REPO_VERSION=master
ARG CONSTRAINTS_BRANCH=master

# Extra Python3 dependencies.
ARG EXTRA_DEPS="gunicorn python-memcached gevent"

# Always start from `monasca-base` image and use specific tag of it.
ARG BASE_TAG=master
FROM monasca/base:$BASE_TAG

# Environment variables used for our service or wait scripts.
ENV \
    KAFKA_URI=kafka:9092 \
    KAFKA_WAIT_FOR_TOPICS=log \
    MONASCA_CONTAINER_LOG_API_PORT=5607 \
    MEMCACHED_URI=memcached:11211 \
    AUTHORIZED_ROLES=admin,domainuser,domainadmin,monasca-user \
    AGENT_AUTHORIZED_ROLES=monasca-agent \
    KEYSTONE_IDENTITY_URI=http://keystone:35357 \
    KEYSTONE_AUTH_URI=http://keystone:5000 \
    KEYSTONE_ADMIN_USER=admin \
    KEYSTONE_ADMIN_PASSWORD=secretadmin \
    KEYSTONE_ADMIN_TENANT=admin \
    KEYSTONE_ADMIN_DOMAIN=default \
    GUNICORN_WORKERS=9 \
    GUNICORN_WORKER_CLASS=gevent \
    GUNICORN_WORKER_CONNECTIONS=2000 \
    GUNICORN_BACKLOG=1000 \
    GUNICORN_TIMEOUT=10 \
    PYTHONIOENCODING=utf-8 \
    ADD_ACCESS_LOG=false \
    ACCESS_LOG_FORMAT="%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s" \
    ACCESS_LOG_FIELDS='%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s' \
    LOG_LEVEL_ROOT=INFO \
    LOG_LEVEL_CONSOLE=INFO \
    LOG_LEVEL_ACCESS=INFO \
    STAY_ALIVE_ON_FAILURE="false"

# Copy all neccessary files to proper locations.
COPY log-api* monasca-log-api* /etc/monasca/

# Run here all additionals steps your service need post installation.
# Stay with only one `RUN` and use `&& \` for next steps to don't create
# unnecessary image layers. Clean at the end to conserve space.
#RUN \
#    echo "Some steps to do after main installation." && \
#    echo "Hello when building."

# Expose port for specific service.
EXPOSE ${MONASCA_CONTAINER_LOG_API_PORT}

# Implement start script in `start.sh` file.
CMD ["/start.sh"]
