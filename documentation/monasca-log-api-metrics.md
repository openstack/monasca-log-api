# Monitoring for monasca-log-api

**monasca-log-api** can be monitored by examining following metrics

| Name                                      | Meaning | Dimensions  |
|-------------------------------------------|-------------------------|---------------|
| monasca.log.in_logs                       | Amount of received logs | version |
| monasca.log.in_logs_rejected              | Amount of rejected logs (see below for details) | version |
| monasca.log.in_bulks_rejected             | Amount of rejected bulks (see below for details) | version |
| monasca.log.in_logs_bytes                 | Size received logs (a.k.a. *Content-Length)* in bytes | version |
| monasca.log.out_logs                      | Amount of logs published to kafka | |
| monasca.log.out_logs_lost                 | Amount of logs lost during publish phase | |
| monasca.log.out_logs_truncated_bytes      | Amount of truncated bytes, removed from message | |
| monasca.log.publish_time_ms               | Time Log-Api needed to publish all logs to kafka | |
| monasca.log.processing_time_ms            | Time Log-Api needed to process received logs. | version |

Additionally each metric contains following dimensions:
- **component** - monasca-log-api
- **service** - monitoring

## Metrics explained

### monasca.log.in_logs

Metric sent with amount of logs that were received by **Log-API**
and successfully passed initial validation. For **v2.0** this
metric will be always send with value one, for **v3.0** this metric's values
are equivalent to amount of element in bulk request.

### monasca.log.in_logs_rejected <a name="monasca_log_logs_rejected">

Logs can be rejected because of:

* checking content-type
* checking content-length
* reading payload
* retrieving logs from payload
* validating global dimensions (if set)(only valid for v3.0)

### monasca.log.in_bulks_rejected (only v3.0)

In **v2.0** bulk request is equivalent to single request (i.e. single-element bulk).
However in **v3.0** rejecting logs is done in two phases.

*Phase 1* is when there is no way to determine actual amount of logs
that were sent by client (see [monasca.log.in_logs_rejected](#monasca_log_logs_rejected))
If any of these steps was impossible to be executed entire bulk is
considered lost and thus all logs within.

If *Phase 1* passes, *Phase 2* is executed. At this point every
piece of data is available, however still some logs can be rejected,
because of:

* lack of certain fields (i.e. message)
* invalid local dimensions (if set)

In *Phase 2* metric [monasca.log.in_logs_rejected](#monasca_log_logs_rejected)
is produced.

### monasca.log.in_logs_bytes

Metric allows to track to size of requests API receives.
In **v3.0** To simplify implementation it is equivalent to **Content-Length** value.
However amount of global dimensions and other metadata when compared
to size of logs is negligible.

### monasca.log.out_logs

Amount of logs successfully published to kafka queue.

### monasca.log.out_logs_lost

Amount of logs that were not sent to kafka and **Log-API** was unable
to recover from error situation

### monasca.log.out_logs_truncated_bytes

Metric is sent with the amount of bytes that log's message is shorten
by if necessary. To read more about truncation see [here](/documentation/monasca-log-api-kafka.md).
If truncation did not happen, which should be normal situation for most
of the time, metric is updated with value **0**.

### monasca.log.publish_time_ms

Time that was needed to send all the logs into all the topics.
*monasca.log.processing_time_ms* includes value of that metric
within. It exists to see how much does publishing take in entire
processing.

### monasca.log.processing_time_ms

Total amount of time logs spent inside **Log-API**. Metric does not
include time needed to communicate with Keystone to authenticate request.
As far as possible it is meant to track **Log-API** itself

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
