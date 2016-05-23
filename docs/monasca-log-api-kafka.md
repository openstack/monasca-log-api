# Monasca Log API - Kafka

Date: April 18, 2016

Document Version: v0.2

## Introduction

**monasca-log-api** uses kafka transport to ship received logs down to the
processing pipeline.

For more information about Kafka, please see [official documentation]
(http://kafka.apache.org/documentation.html).

## Output message format
Messages sent to kafka should have following format
(top level object is called **envelope**) and is combined out of three
elements:
* log
* creation_time
* meta


    "log": <object>,
    "creation_time": <number, timestamp>,
    "meta": <object>

Log property should have at least following form:

    "message": <string>,
    "dimensions": <object>

Meta property should have following form:

    "tenantId": <string>,
    "region": <string>

Full example as json:
```json
  {
    "log": {
      "message": "2015-11-13 12:44:42.411 27297 DEBUG kafka [-] Read 31/31 bytes from Kafka _read_bytes /opt/monasca/monasca-log-api/lib/python2.7/site-packages/kafka/conn.py:103",
      "dimensions": {
        "hostname": "devstack"
      }
    },
    "creation_time": 1447834886,
    "meta": {
      "tenantId": "e4bd29509eda473092d32aadfee3e7b1",
      "region": "pl"
    }
  }
```

### Fields explanation

* log - contains log specific information collected from the system. In the
most lean case that would be: **message**, **dimensions**
 * message - normally that represent a single line from a log file
 * dimensions - informations such as hostname where application is running
* creation_time - UNIX timestamp representing moment when log message was created
by monasca-log-api
* meta - contains tenantId and its region

**log** entry may of course contain many more fields that are considered valid
in given case. However two mentioned in this documentation are required.

All fields, apart from **creation_time** and **log**, are created from HTTP headers.
Description is available [here](/docs/monasca-log-api-spec.md).

## Truncating too large message

    Following section mostly applies to monasca-log-api v3.0

Each *envelope* sent to Kafka is serialized into JSON string. This string must
comply to Kafka limitation about [maximum message size](https://kafka.apache.org/08/configuration.html).
If JSON message is too big following actions are taken
1) difference between maximum allowed size and JSON message size (both in bytes).
   ```diff = (size(json_envelope) + size(envelope_key) + KAFKA_METADATA_SIZE) - maximum_allowed_size + TRUNCATION_SAFE_OFFSET```.
   **KAFKA_METADATA_SIZE** is amount of bytes Kafka adds during transformation
   of each message prior to sending it
2) log is enriched with property **truncated** set to **true** (```log['truncated'] = True```)
3) log's message is truncated by ```diff + TRUNCATED_PROPERTY_SIZE```.
  **TRUNCATED_PROPERTY_SIZE** is the size of newly added property.

Variables explanation:

* **envelope_key** is the key used when routing logs into specific kafka partitions.
Its byte size is always fixed (determined from the byte size of timestamp represented as string).
```len(bytearray(str(int(time.time() * 1000)).encode('utf-8')))```
* **KAFKA_METADATA_SIZE** equals to 200 bytes.
* **TRUNCATION_SAFE_OFFSET** is equal to 1 ensuring that diff size will be always positive number
* **TRUNCATED_PROPERTY_SIZE** is calculated as byte size of expression ```log['truncated'] = True```
for each run of log-api.

## Configuration

### Java

Configuration for kafka should be placed in *.yml file and look similar to:
```yml
logTopic: logs
kafka:
  brokerUris:
    - localhost:8900
  zookeeperUris:
    - localhost:2181
  healthCheckTopic: healthcheck
```

It is composed out of two relevant pieces
* logTopic - topic where data should be sent
* kafka - section containing information required to communicate in kafka.
For more details see [here](https://github.com/openstack/monasca-common/blob/master/java/monasca-common-kafka/src/main/java/monasca/common/messaging/kafka/KafkaConfiguration.java)

### Python

Configuration for kafka should be placed in *.conf file and look similar to:

```conf
[log_publisher]
topics = 'logs'
kafka_url = 'localhost:8900'
```

There are only two relevant options:
* topics - comma delimited list of topics where data should be sent
* kafka_url - adress where kafka server is running

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
