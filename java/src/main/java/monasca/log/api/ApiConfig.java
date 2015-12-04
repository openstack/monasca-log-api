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
package monasca.log.api;

import io.dropwizard.Configuration;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;

import org.hibernate.validator.constraints.NotEmpty;

import monasca.common.messaging.kafka.KafkaConfiguration;
import monasca.log.api.common.LogApiConstants;
import monasca.log.api.infrastructure.middleware.MiddlewareConfiguration;

public class ApiConfig extends Configuration {

  /**
   * Refers to payload/envelope size.
   * If either is exceeded API will throw an error.
   */
  private static final Integer DEFAULT_LOG_SIZE = LogApiConstants.MAX_LOG_LENGTH;

  @NotEmpty
  public String region;
  @NotEmpty
  public String logTopic = "log";
  @Valid
  public Integer logSize = DEFAULT_LOG_SIZE;
  @Valid
  @NotNull
  public KafkaConfiguration kafka;
  @Valid
  @NotNull
  public MiddlewareConfiguration middleware;
}
