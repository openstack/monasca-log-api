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

package monasca.log.api.model;

import java.beans.Transient;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;

/**
 * Represents a log.
 *
 * It allows any set of fields to be placed as log entity.
 * That is particularly useful for JSON based messages where
 * known fields can not be clearly determined and only requirement
 * is to append:
 *
 * <ol>
 * <li>{@code application_type}</li>
 * <li>{@code dimensions}</li>
 * </ol>
 */
@SuppressWarnings("unchecked")
public class Log
    extends HashMap<String, Object> {
  private static final long serialVersionUID = 685205295808136758L;
  private static final String KEY_DIMENSIONS = "dimensions";
  private static final String KEY_APPLICATION_TYPE = "application_type";
  private static final String KEY_MESSAGE = "message";

  public Log() {
    super(3);  // 3 fields at least
  }

  public Log(final String applicationType,
             final Map<String, String> dimensions,
             final String message) {
    this();
    if (StringUtils.isNotEmpty(applicationType)) {
      this.setApplicationType(applicationType);
    }
    if (dimensions != null) {
      this.setDimensions(dimensions);
    }
    if (message != null) {
      this.setMessage(message);
    }
  }

  public Log setDimensions(final Map<String, String> dimensions) {
    if (dimensions != null) {
      this.put(KEY_DIMENSIONS, dimensions);
    }
    return this;
  }

  @Transient
  public Map<String, String> getDimensions() {
    return (Map<String, String>) this.get(KEY_DIMENSIONS);
  }

  public Log setApplicationType(final String applicationType) {
    if (StringUtils.isNotEmpty(applicationType)) {
      this.put(KEY_APPLICATION_TYPE, applicationType);
    }
    return this;
  }

  @Transient
  public String getApplicationType() {
    final String val = (String) this.get(KEY_APPLICATION_TYPE);
    return val != null ? val : StringUtils.EMPTY;
  }

  public Log setMessage(final String message) {
    this.put(KEY_MESSAGE, message);
    return this;
  }

  @Transient
  public String getMessage() {
    final String val = (String) this.get(KEY_MESSAGE);
    return val != null ? val : StringUtils.EMPTY;
  }

  public Log append(final String key, final String val) {
    this.put(key, val);
    return this;
  }

}
