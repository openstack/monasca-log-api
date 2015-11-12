# Copyright 2015 kornicameister@gmail.com
# Copyright 2015 FUJITSU LIMITED
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

import datetime
import re

from oslo_config import cfg
from oslo_log import log

from monasca_log_api.api import exceptions
from monasca_log_api.api import logs_api
from monasca_log_api.api import rest_utils

LOG = log.getLogger(__name__)
CONF = cfg.CONF

service_opts = [
    cfg.StrOpt('region',
               default=None,
               help='Region')
]
service_group = cfg.OptGroup(name='service', title='service')

CONF.register_group(service_group)
CONF.register_opts(service_opts, service_group)

APPLICATION_TYPE_CONSTRAINTS = {
    'MAX_LENGTH': 255,
    'PATTERN': re.compile('^[a-zA-Z0-9_\\.\\-]+$')
}
DIMENSION_NAME_CONSTRAINTS = {
    'MAX_LENGTH': 255,
    'PATTERN': re.compile('[^><={}(), \'";&]+$')
}
DIMENSION_VALUE_CONSTRAINTS = {
    'MAX_LENGTH': 255
}
EPOCH_START = datetime.datetime(1970, 1, 1)


class LogEnvelopeException(Exception):
    pass


class Validations(object):

    @staticmethod
    def validate_application_type(application_type=None):

        def validate_length():
            if (len(application_type) >
                    APPLICATION_TYPE_CONSTRAINTS['MAX_LENGTH']):
                msg = ('Application type {type} must be '
                       '{length} characters or less')
                raise exceptions.HTTPUnprocessableEntity(
                    msg.format(
                        type=application_type,
                        length=APPLICATION_TYPE_CONSTRAINTS[
                            'MAX_LENGTH']
                    )
                )

        def validate_match():
            if (not APPLICATION_TYPE_CONSTRAINTS['PATTERN']
                    .match(application_type)):
                raise exceptions.HTTPUnprocessableEntity(
                    'Application type %s may only contain: "a-z A-Z 0-9 _ - ."'
                    % application_type
                )

        if application_type:
            validate_length()
            validate_match()

    @staticmethod
    def validate_dimensions(dimensions):

        def validate_name(name):
            if not name:
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension name cannot be empty'
                )
            if len(name) > DIMENSION_NAME_CONSTRAINTS['MAX_LENGTH']:
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension name %s must be 255 characters or less' %
                    name
                )
            if name[0] == '_':
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension name %s cannot start with underscore (_)' %
                    name
                )
            if not DIMENSION_NAME_CONSTRAINTS['PATTERN'].match(name):
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension name %s may not contain: %s' %
                    (name, '> < = { } ( ) \' " , ; &')
                )

        def validate_value(value):
            if not value:
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension value cannot be empty'
                )
            if len(value) > DIMENSION_VALUE_CONSTRAINTS['MAX_LENGTH']:
                raise exceptions.HTTPUnprocessableEntity(
                    'Dimension value %s must be 255 characters or less' %
                    value
                )

        if (isinstance(dimensions, dict) and not
                isinstance(dimensions, basestring)):

            for dim_name in dimensions:
                validate_name(dim_name)
                validate_value(dimensions[dim_name])

        else:
            raise exceptions.HTTPUnprocessableEntity(
                'Dimensions %s must be a dictionary (map)' % dimensions)


class LogCreator(object):
    def __init__(self):
        self._log = log.getLogger('service.LogCreator')
        self._log.info('Initializing LogCreator')

    @staticmethod
    def _create_meta_info(tenant_id):
        return {
            'tenantId': tenant_id,
            'region': cfg.CONF.service.region
        }

    def new_log(self,
                application_type,
                dimensions,
                payload,
                content_type='application/json',
                validate=True):

        payload = rest_utils.read_body(payload, content_type)
        if not payload:
            return None

        # normalize_yet_again
        application_type = parse_application_type(application_type)
        dimensions = parse_dimensions(dimensions)

        self._log.debug(
            'application_type=%s,dimensions=%s' % (
                application_type, dimensions)
        )

        if validate:
            self._log.debug('Validation enabled, proceeding with validation')
            Validations.validate_application_type(application_type)
            Validations.validate_dimensions(dimensions)

        log_object = {}
        if content_type == 'application/json':
            log_object.update(payload)
        else:
            log_object.update({'message': payload})

        log_object.update({
            'application_type': application_type,
            'dimensions': dimensions
        })

        return log_object

    def new_log_envelope(self, log_object, tenant_id):
        if not log_object:
            raise LogEnvelopeException('Envelope cannot be '
                                       'created without log')
        if not tenant_id:
            raise LogEnvelopeException('Envelope cannot be '
                                       'created without tenant')

        timestamp = (datetime.datetime.utcnow() - EPOCH_START).total_seconds()

        return {
            'log': log_object,
            'creation_time': timestamp,
            'meta': self._create_meta_info(tenant_id)
        }


def is_delegate(roles):
    if roles:
        roles = roles.split(',')
        return logs_api.MONITORING_DELEGATE_ROLE in roles
    return False


def parse_application_type(app_type):
    if app_type:
        app_type = app_type.strip()
    return app_type if app_type else None


def parse_dimensions(dimensions):
    if not dimensions:
        raise exceptions.HTTPUnprocessableEntity('Dimension are required')

    new_dimensions = {}
    dimensions = map(str.strip, dimensions.split(','))

    for dim in dimensions:
        if not dim:
            raise exceptions.HTTPUnprocessableEntity(
                'Dimension cannot be empty')
        elif ':' not in dim:
            raise exceptions.HTTPUnprocessableEntity(
                '%s is not a valid dimension' % dim)

        dim = dim.split(':')
        name = str(dim[0].strip()) if dim[0] else None
        value = str(dim[1].strip()) if dim[1] else None
        if name and value:
            new_dimensions.update({name: value})

    return new_dimensions
