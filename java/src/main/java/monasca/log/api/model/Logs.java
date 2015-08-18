/*
 * Copyright 2015 FUJITSU LIMITED
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
 *
 */
package monasca.log.api.model;

import java.io.IOException;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.module.SimpleModule;
import monasca.common.util.Exceptions;
import org.apache.commons.lang3.StringEscapeUtils;

/**
 * Utilities for working with Logs.
 */
public final class Logs {
  static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  static {
    OBJECT_MAPPER.setPropertyNamingStrategy(PropertyNamingStrategy.CAMEL_CASE_TO_LOWER_CASE_WITH_UNDERSCORES);
    SimpleModule module = new SimpleModule();
    module.addSerializer(new LogSerializer());
    OBJECT_MAPPER.registerModule(module);
  }

  private Logs() {
  }

  /**
   * Returns the Log for the {@code logJson}.
   *
   * @throws RuntimeException if an error occurs while parsing {@code logJson}
   */
  public static Log fromJson(byte[] logJson) {
    try {
      String jsonStr = StringEscapeUtils.unescapeJava(new String(logJson, "UTF-8"));
      return OBJECT_MAPPER.readValue(jsonStr, Log.class);
    } catch (Exception e) {
      throw Exceptions.uncheck(e, "Failed to parse log json: %s", new String(logJson));
    }
  }

  /**
   * Returns the JSON representation of the {@code log} else null if it could not be converted to
   * JSON.
   */
  public static String toJson(Log log) {
    try {
      return OBJECT_MAPPER.writeValueAsString(log);
    } catch (JsonProcessingException e) {
      return null;
    }
  }

  /** Log serializer */
  private static class LogSerializer
      extends JsonSerializer<Log> {
    @Override
    public Class<Log> handledType() {
      return Log.class;
    }

    public void serialize(Log log, JsonGenerator jgen, SerializerProvider provider)
        throws IOException, JsonProcessingException {
      jgen.writeStartObject();

      if (log.applicationType != null && !log.applicationType.isEmpty()) {
        jgen.writeStringField("application_type", log.applicationType);
      }
      if (log.dimensions != null && !log.dimensions.isEmpty()) {
        jgen.writeObjectField("dimensions", log.dimensions);
      }
      jgen.writeStringField("message", log.message);

      jgen.writeEndObject();
    }
  }
}
