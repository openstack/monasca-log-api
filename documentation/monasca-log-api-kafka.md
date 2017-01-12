# Monasca Log API - Kafka

Date: November 18, 2015

Document Version: v0.1

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
    "application_type": <string>,
    "dimensions": <object>

Meta property should have following form:

    "tenantId": <string>,
    "region": <string>

Full example as json:
```json
  {
    "log": {
      "message": "2015-11-13 12:44:42.411 27297 DEBUG kafka [-] Read 31/31 bytes from Kafka _read_bytes /opt/monasca/monasca-log-api/lib/python2.7/site-packages/kafka/conn.py:103",
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
```

### Fields explanation

* log - contains log specific information collected from the system. In the
most lean case that would be: **message**, **application_type**, **dimensions**
 * message - normally that represent a single line from a log file
 * application_type - represent the application that log was collected
 * dimensions - informations such as hostname where application is running
* creation_time - UNIX timestamp representing moment when log message was created
by monasca-log-api
* meta - contains tenantId and its region

**log** entry main of course contain many more fields that are considered valid
in given case. However three mentioned in this documentation are required.

All fields, apart from **creation_time** and **log**, are created from HTTP headers.
Description is available [here](/docs/monasca-log-api-spec.md).

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
