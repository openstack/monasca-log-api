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
package monasca.log.api.app.validation;

import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.WebApplicationException;

import com.google.common.base.Splitter;
import com.google.common.base.Strings;

import monasca.log.api.resource.exception.Exceptions;

/**
 * Validation related utilities.
 */
public final class Validation {

  private static final Splitter COMMA_SPLITTER_FOR_LOG = Splitter.on(',').trimResults();

  private Validation() {}

  /**
   * @throws WebApplicationException if the {@code value} is null or empty.
   */
  public static Map<String, String> parseLogDimensions(String dimensionsStr) {
    Validation.validateNotNullOrEmpty(dimensionsStr, "dimensions");

    Map<String, String> dimensions = new HashMap<String, String>();
    for (String dimensionStr : COMMA_SPLITTER_FOR_LOG.split(dimensionsStr)) {
      if (dimensionStr.isEmpty())
        throw Exceptions.unprocessableEntity("Dimension cannot be empty");

      int index = dimensionStr.indexOf(':');
      if (index == -1)
        throw Exceptions.unprocessableEntity("%s is not a valid dimension", dimensionStr);
      String dimensionKey = dimensionStr.substring(0, index);
      String dimensionValue = dimensionStr.substring(index + 1);

      dimensions.put(dimensionKey, dimensionValue);
    }

    return dimensions;
  }

  /**
   * @throws WebApplicationException if the {@code value} is null or empty.
   */
  public static void validateNotNullOrEmpty(String value, String parameterName) {
    if (Strings.isNullOrEmpty(value))
      throw Exceptions.unprocessableEntity("%s is required", parameterName);
  }
}
