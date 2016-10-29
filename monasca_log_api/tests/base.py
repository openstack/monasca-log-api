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
import falcon
from oslo_config import fixture as oo_cfg
from oslo_context import fixture as oo_ctx

from monasca_log_api.api.core import request


def mock_config(test):
    return test.useFixture(oo_cfg.Config())


def mock_context(test):
    return test.useFixture(oo_ctx.ClearRequestContext())


class MockedAPI(falcon.API):
    """MockedAPI

    Subclasses :py:class:`falcon.API` in order to overwrite
    request_type property with custom :py:class:`request.Request`

    """

    def __init__(self):
        super(MockedAPI, self).__init__(
            media_type=falcon.DEFAULT_MEDIA_TYPE,
            request_type=request.Request,
            response_type=falcon.Response,
            middleware=None,
            router=None
        )
