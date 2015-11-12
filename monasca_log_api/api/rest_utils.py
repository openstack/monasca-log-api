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
import simplejson as json

ENCODING = 'utf8'


def read_body(payload, content_type='application/json'):
    try:
        content = payload.read()
        if not content:
            return False
    except Exception as ex:
        raise falcon.HTTPBadRequest(title='Failed to read body',
                                    description=ex.message)

    if content_type == 'application/json':
        try:
            content = from_json(content)
        except Exception as ex:
            raise falcon.HTTPBadRequest(title='Failed to read body as json',
                                        description=ex.message)

    return content


def as_json(data):
    return json.dumps(data,
                      encoding=ENCODING,
                      sort_keys=False,
                      ensure_ascii=False)


def from_json(data):
    return json.loads(data, encoding=ENCODING)
