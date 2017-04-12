# Monasca Log API

Date: May 27, 2016

Document Version: v2.2.2

# Logs
The logs resource allows logs to be created and queried.

## Create Logs
Create logs.

### POST /v3.0/logs

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Content-Type (string, required) - application/json

#### Path Parameters
None.

#### Query Parameters
* tenant_id (string, optional, restricted) - Tenant ID (project ID) to create
  log on behalf of. Usage of this query parameter requires the role specified
  in the configuration option `delegate_roles` .

#### Request Body
JSON object which can have a maximum size of 5 MB. It consists of global
dimensions (optional) and array of logs. Each single log message with 
resulting envelope can have a maximum size of 1 MB.
Dimensions is a dictionary of key-value pairs and should be consistent with
metric dimensions.

Logs is an array of JSON objects describing the log entries. Every log object
can have individual set of dimensions which has higher precedence than global
ones. It should be noted that dimensions presented in each log record are also
optional.

    If both global (at the root level) and local (at log entry level)
    dimensions would be present, they will be merged into one dictionary.
    Please note that local dimensions are logically considered as more
    specific thus in case of conflict (i.e. having two entries with the same
    key in both global and local dimensions) local dimensions take
    precedence over global dimensions.

#### Request Examples

POST logs

```
POST /v3.0/logs HTTP/1.1
Host: 192.168.10.4:5607
Content-Type: application/json
X-Auth-Token: 27feed73a0ce4138934e30d619b415b0
Cache-Control: no-cache

{
    "dimensions":{
        "hostname":"mini-mon",
        "service":"monitoring"
    },
    "logs":[
        {
            "message":"msg1",
            "dimensions":{
                "component":"mysql",
                "path":"/var/log/mysql.log"
            }
        },
        {
            "message":"msg2",
            "dimensions":{
                "component":"monasca-api",
                "path":"/var/log/monasca/monasca-api.log"
            }
        }
    ]
}
```

### Response
#### Status Code
* 204 - No content

#### Response Body
This request does not return a response body.

## List logs
Get precise log listing filtered by dimensions.

    Note that this API is in development, and is not currently implemented.

This interface can used to obtain log entries for a time range, based on
matching a set of exact dimension values. By default, entries will be returned
in descending timestamp order (newest first). The log entries returned by this
API will not necessarily be identical to those POST-ed to the service, as the
data returned will have been subjected to deployment-specific transformation
stages (i.e. the "monasca-log-transform" service).

### GET /v3.0/logs

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Accept (string) - application/json

#### Path Parameters
None.

#### Query Parameters
* tenant_id (string, optional, restricted) - Tenant ID from which to get logs
from. This parameter can be used to get logs from a tenant other than the tenant
the request auth token is scoped to. Usage of this query parameter is restricted
to users with the monasca admin role, as defined in the monasca-log-api
configuration file, which defaults to `monasca-admin`.
* dimensions (string, optional) - A dictionary to filter logs by specified as a
comma separated array of (key, value) pairs as `key1:value1,key2:value2, ...`,
multiple values for a key may be specified as
`key1:value1|value2|...,key2:value4,...`. If the value is omitted in the form
`key1,key2, ...`, then entries are returned where the dimension exists with
any value.
* start_time (string, optional) - The start time in ISO 8601 combined date and
time format in UTC.
* end_time (string, optional) - The end time in ISO 8601 combined date and time
format in UTC.
* offset (integer, optional) - Number of log entries to skip (Default: 0).
* limit (integer, optional) - Limit number of logs returned (Default: 10).
* sort_by (string, optional) - Comma separated list of fields or dimensions to
sort by. Fields may be followed by 'asc' or 'desc' to set the direction, e.g.
'timestamp asc'. Allowed fields for sort_by are currently: 'timestamp'.
(Default: no sorting)

#### Request Body
None.

#### Request Examples
```
GET /v3.0/logs?dimensions=hostname:devstack&start_time=2015-03-00T00:00:01Z HTTP/1.1
Host: 192.168.10.4:5607
Content-Type: application/json
X-Auth-Token: 2b8882ba2ec44295bf300aecb2caa4f7
Cache-Control: no-cache
```

### Response
#### Status Code
* 200 - OK

#### Response Body
Returns a JSON object with a 'links' array of links and an 'elements' array of
log entry objects with the following fields:

* timestamp (timestamp) - The originating time in ISO 8601 combined date and
time format in UTC, with millisecond resolution if available.
* message (string) - The contents of the log message.
* dimensions ({string(255): string(255)}) - Dimensions of the log, either
supplied with the log or added by transformation.

#### Response Examples
```
{
    "links": [
        {
            "rel": "prev",
            "href": "http://192.168.10.4:5607/v3.0/logs?start_time=2015-03-00T00%3A00%3A00Z&dimensions=hostname%3Adevstack"
        },
        {
            "rel": "self",
            "href": "http://192.168.10.4:5607/v3.0/logs?offset=10&start_time=2015-03-00T00%3A00%3A00Z&dimensions=hostname%3Adevstack"
        },
        {
            "rel": "next",
            "href": "http://192.168.10.4:5607/v3.0/logs?offset=20&start_time=2015-03-00T00%3A00%3A00Z&dimensions=hostname%3Adevstack"
        }
    ],
    "elements": [
        {
            "timestamp":"2015-03-03T05:24:55.202Z",
            "message":"msg1",
            "dimensions":{
                "hostname":"devstack",
                "component":"mysql",
                "path":"/var/log/mysql.log"
            }
        },
        {
            "timestamp":"2015-03-01T02:22:09.112Z",
            "message":"msg2",
            "dimensions":{
                "hostname":"devstack",
                "component":"monasca-api",
                "path":"/var/log/monasca/monasca-api.log"
            }
        }
    ]
}
```


# Healthcheck

    Note that following part is updated for Python implementation.

The *Monasca Log API* comes with a built-in health check mechanism.
It is available in two flavors, both accessible under ```/healthcheck```
endpoint.

## Complex check
The complex check not only returns a response with success code if *Monasca Log API*
is up and running but it also verifies if peripheral components, such as **Kafka**,
are healthy too.

*Monasca Log API* will respond with following codes:

* 200 - both API and external components are healthy.
* 503 - API is running but problems with peripheral components have been spotted.

Example:
```curl -XGET 192.168.10.4:5607/healthcheck```

### Peripheral checks

* **Kafka** is considered healthy if connection to broker can be established
and configured topics can be found.

## Simple check
The simple check only returns response only if *Monasca Log API* is up and running.
It does not return any data because it is accessible only for ```HEAD``` requests.
If the *Monasca Log API* is running the following response code: ```204``` is expected.

Example:
```curl -XHEAD 192.168.10.4:5607/healthcheck```


=======
### POST /v2.0/log/single (deprecated)

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Content-Type (string, required) - application/json; text/plain
* X-Application-Type (string(255), optional) - Type of application
* X-Dimensions ({string(255):string(255)}, required) - A dictionary consisting of (key, value) pairs used to structure logs.

#### Path Parameters
None.

#### Request Body
Consists of a single plain text message or a JSON object which can have a maximum length of 1048576 characters.

#### Request Examples

##### Plain text log - single line
POST a single line of plain text log.

```
POST /v2.0/log/single HTTP/1.1
Host: 192.168.10.4:5607
Content-Type: text/plain
X-Auth-Token: 27feed73a0ce4138934e30d619b415b0
X-Application-Type: apache
X-Dimensions: applicationname:WebServer01,environment:production
Cache-Control: no-cache

Hello World
```

##### Plain text log - multi lines
POST a multiple lines of plain text log.

```
POST /v2.0/log/single HTTP/1.1
Host: 192.168.10.4:5607
Content-Type: text/plain
X-Auth-Token: 27feed73a0ce4138934e30d619b415b0
X-Application-Type: apache
X-Dimensions: applicationname:WebServer01,environment:production
Cache-Control: no-cache

Hello\nWorld
```

##### JSON log
POST a JSON log

```
POST /v2.0/log/single HTTP/1.1
Host: 192.168.10.4:5607
Content-Type: application/json
X-Auth-Token: 27feed73a0ce4138934e30d619b415b0
X-Application-Type: apache
X-Dimensions: applicationname:WebServer01,environment:production
Cache-Control: no-cache

{
  "message":"Hello World!",
  "from":"hoover"
}

```

### Response
#### Status Code
* 204 - No content

#### Response Body
This request does not return a response body.

    # Copyright 2016-2017 FUJITSU LIMITED
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
