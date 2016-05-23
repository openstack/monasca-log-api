# Monasca Log API

Date: May 27, 2016

Document Version: v2.2.2

# Logs
The logs resource allows logs to be created.

## Create Logs
Create logs.

### POST /v3.0/logs

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Content-Type (string, required) - application/json

#### Path Parameters
None.

#### Query Parameters
* tenant_id (string, optional, restricted) - Tenant ID to create log on behalf of. Usage of this query parameter requires the `monitoring-delegate` role.

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
```curl -XGET 192.168.10.4:8080/healthcheck```

### Peripheral checks

* **Kafka** is considered healthy if connection to broker can be established
and configured topics can be found.

## Simple check
The simple check only returns response only if *Monasca Log API* is up and running.
It does not return any data because it is accessible only for ```HEAD``` requests.
If the *Monasca Log API* is running the following response code: ```204``` is expected.

Example:
```curl -XHEAD 192.168.10.4:8080/healthcheck```


=======
### POST /v2.0/log/single (deprecated)

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Content-Type (string, required) - application/json; text/plain
* X-Application-Type (string(255), optional) - Type of application
* X-Dimensions ({string(255):string(255)}, required) - A dictionary consisting of (key, value) pairs used to structure logs.

#### Path Parameters
None.

#### Query Parameters
* tenant_id (string, optional, restricted) - Tenant ID to create log on behalf of. Usage of this query parameter requires the `monitoring-delegate` role.

#### Request Body
Consists of a single plain text message or a JSON object which can have a maximum length of 1048576 characters.

#### Request Examples

##### Plain text log - single line
POST a single line of plain text log.

```
POST /v2.0/log/single HTTP/1.1
Host: 192.168.10.4:8080
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
Host: 192.168.10.4:8080
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
Host: 192.168.10.4:8080
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
