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
 */

package monasca.log.api.app;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.inject.Inject;

import monasca.common.util.Exceptions;
import monasca.log.api.model.Log;
import monasca.log.api.model.LogEnvelope;

public class LogSerializer {

  private final ObjectMapper objectMapper;

  @Inject
  public LogSerializer(final ObjectMapper objectMapper) {
    this.objectMapper = objectMapper;
  }

  public Log logFromJson(final byte[] bytes) {
    return this.fromJson(bytes, Log.class);
  }

  public LogEnvelope logEnvelopeFromJson(final byte[] bytes) {
    return this.fromJson(bytes, LogEnvelope.class);
  }

  public String logToJson(final Log log) {
    return this.toJson(log);
  }

  public String logEnvelopeToJson(final LogEnvelope envelope) {
    return this.toJson(envelope);
  }

  /**
   * Returns the Log for the {@code logJson}.
   *
   * @throws RuntimeException if an error occurs while parsing {@code logJson}
   */
  protected <T> T fromJson(final byte[] logJson, final Class<T> target) {
    try {
      return this.objectMapper.readValue(new String(logJson, "UTF-8"), target);
    } catch (Exception e) {
      throw Exceptions.uncheck(e, "Failed to parse log json: %s", new String(logJson));
    }
  }

  /**
   * Returns the JSON representation of the {@code log} else null if it could not be converted to
   * JSON.
   */
  protected <T> String toJson(final T log) {
    try {
      return this.objectMapper.writeValueAsString(log);
    } catch (JsonProcessingException e) {
      throw Exceptions.uncheck(e, "Failed to create log json: %s", log);
    }
  }

}
