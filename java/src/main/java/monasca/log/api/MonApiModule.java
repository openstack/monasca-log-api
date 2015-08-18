/*
 * Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
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
package monasca.log.api;

import java.util.Properties;

import javax.inject.Singleton;

import kafka.javaapi.producer.Producer;
import kafka.producer.ProducerConfig;

import com.google.common.base.Joiner;
import com.google.inject.AbstractModule;
import com.google.inject.Provides;

import monasca.log.api.app.ApplicationModule;

/**
 * Monitoring API server bindings.
 */
public class MonApiModule extends AbstractModule {
  private final ApiConfig config;

  public MonApiModule(ApiConfig config) {
    this.config = config;
  }

  @Override
  protected void configure() {
    bind(ApiConfig.class).toInstance(config);
    install(new ApplicationModule());
  }

  @Provides
  @Singleton
  public Producer<String, String> getProducer() {
    Properties props = new Properties();
    props.put("metadata.broker.list", Joiner.on(',').join(config.kafka.brokerUris));
    props.put("serializer.class", "kafka.serializer.StringEncoder");
    props.put("request.required.acks", "1");
    ProducerConfig config = new ProducerConfig(props);
    return new Producer<String, String>(config);
  }
}
