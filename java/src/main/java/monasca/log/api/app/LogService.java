/*
 * Copyright 2015 Fujitsu Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 */
package monasca.log.api.app;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import javax.inject.Inject;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;

import monasca.log.api.ApiConfig;
import monasca.log.api.model.Log;
import monasca.log.api.model.LogEnvelope;
import monasca.log.api.model.LogEnvelopes;

/**
 * Log service implementation.
 */
public class LogService {
  private static final Comparator<Map.Entry<String, String>> comparator;
  private final ApiConfig config;
  private final Producer<String, String> producer;

  static {
    comparator = new Comparator<Map.Entry<String, String>>() {
      @Override
      public int compare(Entry<String, String> o1, Entry<String, String> o2) {
        int nameCmp = o1.getKey().compareTo(o2.getKey());
        return (nameCmp != 0 ? nameCmp : o1.getValue().compareTo(o2.getValue()));
      }
    };
  }

  @Inject
  public LogService(ApiConfig config, Producer<String, String> producer) {
    this.config = config;
    this.producer = producer;
  }

  public void create(Log log, String tenantId) {
    Builder<String, Object> metaBuilder = new ImmutableMap.Builder<String, Object>().put("tenantId", tenantId).put("region", this.config.region);
    ImmutableMap<String, Object> meta = metaBuilder.build();

    LogEnvelope envelope = new LogEnvelope(log, meta);
    String key = buildKey(tenantId, log);
    String json = LogEnvelopes.toJson(envelope);
    String topic = this.config.logTopic;
    this.producer.send(new KeyedMessage<>(topic, key, json));
  }

  private String buildKey(String tenantId, Log log) {
    final StringBuilder key = new StringBuilder();

    // appends tenantId
    key.append(tenantId);

    // appends applicationType
    if (log.applicationType != null && !log.applicationType.isEmpty()) {
      key.append(log.applicationType);
    }

    // appends dimensions
    if (log.dimensions != null && !log.dimensions.isEmpty()) {
      for (final Map.Entry<String, String> dim : buildSortedDimSet(log.dimensions)) {
        key.append(dim.getKey());
        key.append(dim.getValue());
      }
    }

    return key.toString();
  }

  // Key must be the same for the same log so sort the dimensions so they will
  // be
  // in a known order
  private List<Map.Entry<String, String>> buildSortedDimSet(final Map<String, String> dimMap) {
    final List<Map.Entry<String, String>> dims = new ArrayList<>(dimMap.entrySet());
    Collections.sort(dims, comparator);
    return dims;
  }

}
