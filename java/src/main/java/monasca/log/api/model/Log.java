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

import java.io.Serializable;
import java.util.Map;

import javax.annotation.Nullable;

/**
 * Represents a log.
 */
public class Log
    implements Serializable {

  private static final long serialVersionUID = 685205295808136758L;

  public String applicationType;
  public Map<String, String> dimensions;
  public String message;

  public Log() {
  }

  public Log(@Nullable String applicationType, @Nullable Map<String, String> dimensions,
             String message) {
    this.applicationType = applicationType;
    this.dimensions = dimensions;
    this.message = message;
  }

  @Override
  public String toString() {
    return "Log{" + "applicationType='" + applicationType + '\'' + ", dimensions=" + dimensions
        + ", message=" + message + '}';
  }

  @Override
  public boolean equals(Object obj) {
    if (this == obj)
      return true;
    if (obj == null)
      return false;
    if (!(obj instanceof Log))
      return false;
    Log other = (Log) obj;
    if (dimensions == null) {
      if (other.dimensions != null)
        return false;
    } else if (!dimensions.equals(other.dimensions))
      return false;
    // internally handles null and empty strings as same for applicationType
    if (applicationType == null) {
      if (other.applicationType != null && !other.applicationType.isEmpty())
        return false;
    } else if (applicationType.isEmpty()) {
      if (other.applicationType != null && !other.applicationType.isEmpty())
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
    result = prime * result + message.hashCode();
    return result;
  }

  public String getApplicationType() {
    return applicationType;
  }

  public void setApplicationType(String applicationType) {
    this.applicationType = applicationType;
  }

  public Map<String, String> getDimensions() {
    return dimensions;
  }

  public void setDimensions(Map<String, String> dimensions) {
    this.dimensions = dimensions;
  }

  public String getMessage() {
    return message;
  }

  public void setMessage(String message) {
    this.message = message;
  }
}
