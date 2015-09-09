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

package monasca.log.api.common;

import java.util.Map;

import javax.ws.rs.core.MediaType;

public class LogRequestBean {
  protected String applicationType;
  protected Map<String, String> dimensions;
  protected String payload;
  protected MediaType contentType;

  public LogRequestBean setApplicationType(final String applicationType) {
    this.applicationType = applicationType;
    return this;
  }

  public LogRequestBean setDimensions(final Map<String, String> dimensions) {
    this.dimensions = dimensions;
    return this;
  }

  public LogRequestBean setPayload(final String message) {
    this.payload = message;
    return this;
  }

  public LogRequestBean setContentType(final MediaType contentType) {
    this.contentType = contentType;
    return this;
  }

  public String getApplicationType() {
    return this.applicationType;
  }

  public Map<String, String> getDimensions() {
    return this.dimensions;
  }

  public String getPayload() {
    return this.payload;
  }

  public MediaType getContentType() {
    return this.contentType;
  }
}
