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

import java.util.Map;

import com.google.common.base.Preconditions;

/**
 * A log envelope.
 */
public class LogEnvelope {
  public Log log;
  public Map<String, Object> meta;
  public long creationTime;

  protected LogEnvelope() {
  }

  public LogEnvelope(Log log) {
    Preconditions.checkNotNull(log, "log");
    this.log = log;
    this.creationTime = System.currentTimeMillis() / 1000;
  }

  public LogEnvelope(Log log, Map<String, Object> meta) {
    this(log);
    Preconditions.checkNotNull(meta, "meta");
    this.meta = meta;
  }
}
