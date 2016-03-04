# Copyright 2015 kornicameister@gmail.com
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

import datetime
import re
import sys

from falcon import errors as falcon_errors
from monasca_common.rest import utils as rest_utils
from oslo_config import cfg
from oslo_log import log

from monasca_log_api.api import exceptions
from monasca_log_api.api import logs_api

LOG = log.getLogger(__name__)
CONF = cfg.CONF

_DEFAULT_MAX_LOG_SIZE = 1024 * 1024

service_opts = [
    cfg.StrOpt('region',
               default=None,
               help='Region'),
    cfg.IntOpt('max_log_size',
               default=_DEFAULT_MAX_LOG_SIZE,
               help=('Refers to payload/envelope size. If either is exceeded'
                     'API will throw an error'))
]
service_group = cfg.OptGroup(name='service', title='service')

CONF.register_group(service_group)
CONF.register_opts(service_opts, service_group)

APPLICATION_TYPE_CONSTRAINTS = {
    'MAX_LENGTH': 255,
    'PATTERN': re.compile('^[a-zA-Z0-9_\\.\\-]+$')
}
"""Application type constraint used in validation.

See :py:func:`Validations.validate_application_type`
"""
DIMENSION_NAME_CONSTRAINTS = {
    'MAX_LENGTH': 255,
    'PATTERN': re.compile('[^><={}(), \'";&]+$')
}
"""Constraint for name of single dimension.

See :py:func:`Validations.validate_dimensions`
"""
DIMENSION_VALUE_CONSTRAINTS = {
    'MAX_LENGTH': 255
}
"""Constraint for value of single dimension.

See :py:func:`Validations.validate_dimensions`
"""
EPOCH_START = datetime.datetime(1970, 1, 1)
SUPPORTED_CONTENT_TYPE = {'application/json', 'text/plain'}


class LogEnvelopeException(Exception):
    pass


class Validations(object):
    """Contains validation logic."""

    @staticmethod
    def validate_application_type(application_type=None):
        """Validates application type.

           Validation won't take place if application_type is None.
           For details see: :py:data:`APPLICATION_TYPE_CONSTRAINTS`
           """

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
        """Validates dimensions type.

           Empty dimensions are not being validated.
           For details see:

           * :py:data:`DIMENSION_NAME_CONSTRAINTS`
           * :py:data:`DIMENSION_VALUE_CONSTRAINTS`
           """

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

    @staticmethod
    def validate_content_type(req):
        """Validates content type.

        Method validates request against correct
        content type.

        If content-type cannot be established (i.e. header is missing),
        :py:class:`falcon.HTTPMissingHeader` is thrown.
        If content-type is not **application/json** or **text/plain**,
        :py:class:`falcon.HTTPUnsupportedMediaType` is thrown.


        :param :py:class:`falcon.Request` req: current request

        :exception: :py:class:`falcon.HTTPMissingHeader`
        :exception: :py:class:`falcon.HTTPUnsupportedMediaType`
        """
        content_type = req.content_type

        LOG.debug('Content-Type is %s', content_type)

        if content_type is None or len(content_type) == 0:
            raise falcon_errors.HTTPMissingHeader(u'Content-Type')

        if content_type not in SUPPORTED_CONTENT_TYPE:
            sup_types = ', '.join(SUPPORTED_CONTENT_TYPE)
            details = u'Only [%s] are accepted as logs representations' % str(
                sup_types)
            raise falcon_errors.HTTPUnsupportedMediaType(description=details)

    @staticmethod
    def validate_payload_size(req):
        """Validates payload size.

        Method validates sent payload size.
        It expects that http header **Content-Length** is present.
        If it does not, method raises :py:class:`falcon.HTTPLengthRequired`.
        Otherwise values is being compared with ::

            [service]
            max_log_size = 1048576

        **max_log_size** refers to the maximum allowed content length.
        If it is exceeded :py:class:`falcon.HTTPRequestEntityTooLarge` is
        thrown.

        :param :py:class:`falcon.Request` req: current request

        :exception: :py:class:`falcon.HTTPLengthRequired`
        :exception: :py:class:`falcon.HTTPRequestEntityTooLarge`

        """
        payload_size = req.content_length
        max_size = CONF.service.max_log_size

        LOG.debug('Payload (content-length) is %s', str(payload_size))

        if payload_size is None:
            raise falcon_errors.HTTPLengthRequired(
                title=u'Content length header is missing',
                description=u'Content length is required to estimate if '
                            u'payload can be processed'
            )

        if payload_size >= max_size:
            raise falcon_errors.HTTPRequestEntityTooLarge(
                title=u'Log payload size exceeded',
                description=u'Maximum allowed size is %d bytes' % max_size
            )

    @staticmethod
    def validate_envelope_size(envelope=None):
        """Validates envelope size before sending to kafka.

        Validates the case similar to what
        :py:meth:`.Validations.validate_payload_size`. Difference is
        that this method checks if log envelope (already serialized)
        can be safely sent to Kafka.

        For more information check kafka documentation regarding
        Message Size Too Large exception.

        :param str envelope: serialized envelope
        :exception: :py:class:`falcon.HTTPInternalServerError`
        """
        max_size = CONF.service.max_log_size
        envelope_size = sys.getsizeof(envelope) if envelope is not None else -1

        LOG.debug('Envelope size is %s', envelope_size)

        if envelope_size >= max_size:
            raise falcon_errors.HTTPInternalServerError(
                title=u'Envelope size exceeded',
                description=u'Maximum allowed size is %d bytes' % max_size
            )

    @staticmethod
    def validate_log_message(log_object):
        """Validates log property.

        Log property should have message property.

        Args:
            log_object (dict): log property
           """
        if 'message' not in log_object:
            raise exceptions.HTTPUnprocessableEntity(
                'Log property should have message'
            )


class LogCreator(object):
    """Transforms logs,

    Takes care of transforming information received via
    HTTP requests into log and log envelopes objects.

    For more details see following:

    * :py:func:`LogCreator.new_log`
    * :py:func:`LogCreator.new_log_envelope`

    """
    def __init__(self):
        self._log = log.getLogger('service.LogCreator')
        self._log.info('Initializing LogCreator')

    @staticmethod
    def _create_meta_info(tenant_id):
        """Creates meta block for log envelope.

        Additionally method accesses oslo configuration,
        looking for *service.region* configuration property.

        For more details see :py:data:`service_opts`

        :param tenant_id: ID of the tenant
        :type tenant_id: str
        :return: meta block
        :rtype: dict

        """
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
        """Creates new log object.

        :param str application_type: origin of the log
        :param dict dimensions: dictionary of dimensions (any data sent to api)
        :param stream payload: stream to read log entry from
        :param str content_type: actual content type used to send data to
                                 server
        :param bool validate: by default True, marks if log should be validated
        :return: log object
        :rtype: dict

        :keyword: log_object
        """

        payload = rest_utils.read_body(payload, content_type)
        if not payload:
            return None

        # normalize_yet_again
        application_type = parse_application_type(application_type)
        dimensions = parse_dimensions(dimensions)

        if validate:
            self._log.debug('Validation enabled, proceeding with validation')
            Validations.validate_application_type(application_type)
            Validations.validate_dimensions(dimensions)

        self._log.debug(
            'application_type=%s,dimensions=%s' % (
                application_type, dimensions)
        )

        log_object = {}
        if content_type == 'application/json':
            log_object.update(payload)
        else:
            log_object.update({'message': payload})

        Validations.validate_log_message(log_object)

        log_object.update({
            'application_type': application_type,
            'dimensions': dimensions
        })

        return log_object

    def new_log_envelope(self, log_object, tenant_id):
        """Creates new log envelope.

        Log envelope is combined ouf of following properties

        * log - dict
        * creation_time - timestamp
        * meta - meta block

        Example output json would like this:

        .. code-block:: json

            {
                "log": {
                  "message": "Some message",
                  "application_type": "monasca-log-api",
                  "dimension": {
                    "hostname": "devstack"
                  }
                },
                "creation_time": 1447834886,
                "meta": {
                  "tenantId": "e4bd29509eda473092d32aadfee3e7b1",
                  "region": "pl"
                }
            }

        :param dict log_object: log object created with
                                :py:meth:`LogCreator.new_log`
        :param str tenant_id: ID of the tenant
        :return: log envelope object
        :rtype: dict

        :keyword: log_envelope

        """

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
