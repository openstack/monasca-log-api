# Monasca Log API

Date: November 18, 2015

Document Version: v2.1

# Log
The log resource allows logs to be created.

## Create Log
Create log.

### POST /v2.0/log/single

#### Headers
* X-Auth-Token (string, required) - Keystone auth token
* Content-Type (string, required) - application/json; text/plain
* X-Application-Type (string(255), optional) - Type of application
* X-Dimensions ({string(255):string(255)}, optional) - A dictionary consisting of (key, value) pairs used to structure logs.

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
