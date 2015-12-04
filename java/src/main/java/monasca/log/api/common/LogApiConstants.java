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

import org.slf4j.Marker;
import org.slf4j.MarkerFactory;

public final class LogApiConstants {

  public static final Marker LOG_MARKER = MarkerFactory.getMarker("log-api");
  public static final Marker LOG_MARKER_WARN = MarkerFactory.getMarker("log-api-warn");
  public static final Marker LOG_MARKER_KAFKA = MarkerFactory.getMarker("log-api-kafka");

  public static final int MAX_NAME_LENGTH = 255;
  public static final int MAX_LOG_LENGTH = 1024 * 1024;

  private LogApiConstants() {
  }
}
