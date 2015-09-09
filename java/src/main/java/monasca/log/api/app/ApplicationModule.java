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
package monasca.log.api.app;

import java.util.TimeZone;

import javax.inject.Singleton;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import com.google.inject.name.Named;

import monasca.log.api.app.unload.JsonPayloadTransformer;

/**
 * Application layer bindings.
 */
public class ApplicationModule
    extends AbstractModule {
  // object mapper configuration
  private static final boolean FAIL_ON_UNKNOWN_PROPERTIES = false;
  private static final boolean ACCEPT_SINGLE_VALUE_AS_ARRAY = true;
  private static final boolean ORDER_MAP_ENTRIES_BY_KEYS = true;
  private static final String TIME_ZONE_UTC = "UTC";
  // object mapper configuration

  @Override
  protected void configure() {
    this.bind(LogSerializer.class).in(Singleton.class);
    this.bind(LogService.class).in(Singleton.class);

    // bind payload transformers
    this.bind(JsonPayloadTransformer.class).in(Singleton.class);
  }

  @Named("objectMapper")
  @Provides
  public ObjectMapper objectMapper() {
    return new ObjectMapper()
        .setPropertyNamingStrategy(PropertyNamingStrategy.CAMEL_CASE_TO_LOWER_CASE_WITH_UNDERSCORES)
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, FAIL_ON_UNKNOWN_PROPERTIES)
        .configure(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY, ACCEPT_SINGLE_VALUE_AS_ARRAY)
        .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, ORDER_MAP_ENTRIES_BY_KEYS)
        .setTimeZone(TimeZone.getTimeZone(TIME_ZONE_UTC))
        .setSerializationInclusion(JsonInclude.Include.NON_NULL);
  }

}
