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

import com.fasterxml.jackson.core.JsonProcessingException;
import monasca.common.util.Exceptions;

/**
 * Utilities for working with LogEnvelopes.
 */
public final class LogEnvelopes {
  private LogEnvelopes() {
  }

  /**
   * Returns the LogEnvelope for the {@code logJson}.
   *
   * @throws RuntimeException if an error occurs while parsing {@code logJson}
   */
  public static LogEnvelope fromJson(byte[] logJson) {
    try {
      String jsonStr = new String(logJson, "UTF-8");
      return Logs.OBJECT_MAPPER.readValue(jsonStr, LogEnvelope.class);
    } catch (Exception e) {
      throw Exceptions.uncheck(e, "Failed to parse log json: %s", new String(logJson));
    }
  }

  /**
   * Returns the JSON representation of the {@code envelope} else null if it could not be converted
   * to JSON.
   */
  public static String toJson(LogEnvelope envelope) {
    try {
      return Logs.OBJECT_MAPPER.writeValueAsString(envelope);
    } catch (JsonProcessingException e) {
      return null;
    }
  }
}
