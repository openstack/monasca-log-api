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
package monasca.log.api.app.command;

import java.util.Map;

import javax.annotation.Nullable;
import javax.validation.constraints.Size;

import org.hibernate.validator.constraints.NotEmpty;

import monasca.log.api.app.validation.DimensionValidation;
import monasca.log.api.app.validation.LogApplicationTypeValidator;
import monasca.log.api.model.Log;
import monasca.log.api.resource.exception.Exceptions;

public class CreateLogCommand {
  public static final int MAX_NAME_LENGTH = 255;
  public static final int MAX_LOG_LENGTH = 1024 * 1024;

  @NotEmpty
  @Size(min = 1, max = MAX_NAME_LENGTH)
  public String applicationType;
  public Map<String, String> dimensions;
  public String message;

  public CreateLogCommand() {}

  public CreateLogCommand(@Nullable String applicationType, @Nullable Map<String, String> dimensions, String message) {
    setApplicationType(applicationType);
    setDimensions(dimensions);
    this.message = message;
  }

  public void setDimensions(Map<String, String> dimensions) {
    // White spaces have been already trimmed, but normalize just in case.
    this.dimensions = DimensionValidation.normalize(dimensions);
  }

  public void setApplicationType(String applicationType) {
    this.applicationType = LogApplicationTypeValidator.normalize(applicationType);
  }

  public Log toLog() {
    return new Log(applicationType, dimensions, message);
  }

  public void validate() {
    // Validate applicationType
    if (applicationType != null && !applicationType.isEmpty()) {
      LogApplicationTypeValidator.validate(applicationType);
    }

    // Validate dimensions
    if (dimensions != null) {
      DimensionValidation.validate(dimensions, null);
    }

    // Validate log message
    if (message.length() > MAX_LOG_LENGTH)
      throw Exceptions.unprocessableEntity("Log must be %d characters or less", MAX_LOG_LENGTH);
  }

  @Override
  public boolean equals(Object obj) {
    if (this == obj)
      return true;
    if (obj == null)
      return false;
    if (getClass() != obj.getClass())
      return false;
    CreateLogCommand other = (CreateLogCommand) obj;
    if (dimensions == null) {
      if (other.dimensions != null)
        return false;
    } else if (!dimensions.equals(other.dimensions))
      return false;
    if (applicationType == null) {
      if (other.applicationType != null)
        return false;
    } else if (!applicationType.equals(other.applicationType))
      return false;
    if (!message.equals(other.message))
      return false;
    return true;
  }

  @Override
  public int hashCode() {
    final int prime = 31;
    int result = 1;
    result = prime * result + ((dimensions == null) ? 0 : dimensions.hashCode());
    result = prime * result + ((applicationType == null) ? 0 : applicationType.hashCode());
    result = prime * result * message.hashCode();
    return result;
  }

}
