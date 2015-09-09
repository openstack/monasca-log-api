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
package monasca.log.api.app.validation;

import java.util.regex.Pattern;

import javax.ws.rs.WebApplicationException;

import com.google.common.base.CharMatcher;

import monasca.log.api.common.LogApiConstants;
import monasca.log.api.resource.exception.Exceptions;

/**
 * Utilities for validating log application types.
 */
public class LogApplicationTypeValidator {
  private static final Pattern VALID_APPLICATION_TYPE = Pattern.compile("^[a-zA-Z0-9_\\.\\-]+$");

  private LogApplicationTypeValidator() {}

  /**
   * Normalizes the {@code applicationType} by removing whitespace.
   */
  public static String normalize(String applicationType) {
    return applicationType == null ? null : CharMatcher.WHITESPACE.trimFrom(applicationType);
  }

  /**
   * Validates the {@code applicationType} for the character constraints.
   *
   * @throws WebApplicationException if validation fails
   */
  public static void validate(String applicationType) {
    if (applicationType.length() > LogApiConstants.MAX_NAME_LENGTH)
      throw Exceptions.unprocessableEntity("Application type %s must be %d characters or less",
          applicationType,
          LogApiConstants.MAX_NAME_LENGTH);

    if (!VALID_APPLICATION_TYPE.matcher(applicationType).matches())
      throw Exceptions.unprocessableEntity("Application type %s may only contain: a-z A-Z 0-9 _ - .",
          applicationType);
  }
}
