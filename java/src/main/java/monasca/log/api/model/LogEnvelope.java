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

import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.base.Preconditions;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

/**
 * A log envelope.
 */
public class LogEnvelope {
  protected Log log;
  protected Map<String, Object> meta;
  @JsonProperty("creation_time")
  protected long creationTime;

  protected LogEnvelope() {
  }

  public LogEnvelope(Log log) {
    Preconditions.checkNotNull(log, "log");
    this.log = log;
    this.creationTime = DateTime.now(DateTimeZone.UTC).getMillis() / 1000;
  }

  public LogEnvelope(Log log, Map<String, Object> meta) {
    this(log);
    Preconditions.checkNotNull(meta, "meta");
    this.meta = meta;
  }

  public LogEnvelope setLog(final Log log) {
    this.log = log;
    return this;
  }

  public LogEnvelope setMeta(final Map<String, Object> meta) {
    this.meta = meta;
    return this;
  }

  public LogEnvelope setCreationTime(final long creationTime) {
    this.creationTime = creationTime;
    return this;
  }

  public Log getLog() {
    return this.log;
  }

  public Map<String, Object> getMeta() {
    return this.meta;
  }

  public long getCreationTime() {
    return this.creationTime;
  }
}
