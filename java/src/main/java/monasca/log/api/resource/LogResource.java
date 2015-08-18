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
package monasca.log.api.resource;

import java.util.Map;

import javax.inject.Inject;
import javax.ws.rs.Consumes;
import javax.ws.rs.HeaderParam;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.UriInfo;

import com.codahale.metrics.annotation.Timed;
import com.google.common.base.Splitter;
import com.google.common.base.Strings;

import monasca.log.api.app.LogService;
import monasca.log.api.app.command.CreateLogCommand;
import monasca.log.api.app.validation.Validation;
import monasca.log.api.resource.exception.Exceptions;

/**
 * Log resource implementation.
 */
@Path("/v2.0/log")
public class LogResource {
  private static final String MONITORING_DELEGATE_ROLE = "monitoring-delegate";
  private static final Splitter COMMA_SPLITTER = Splitter.on(',').omitEmptyStrings().trimResults();

  private final LogService service;

  @Inject
  public LogResource(LogService service) {
    this.service = service;
  }

  @POST
  @Timed
  @Consumes({MediaType.APPLICATION_JSON, MediaType.TEXT_PLAIN})
  @Path("/single")
  public void single(@Context UriInfo uriInfo,
      @HeaderParam("X-Tenant-Id") String tenantId,
      @HeaderParam("X-Roles") String roles,
      @HeaderParam("X-Application-Type") String applicationType,
      @HeaderParam("X-Dimensions") String dimensionsStr,
      @QueryParam("tenant_id") String crossTenantId, String message) {

    boolean isDelegate = !Strings.isNullOrEmpty(roles) && COMMA_SPLITTER.splitToList(roles).contains(MONITORING_DELEGATE_ROLE);

    Map<String, String> dimensions = Strings.isNullOrEmpty(dimensionsStr) ? null : Validation.parseLogDimensions(dimensionsStr);

    CreateLogCommand command = new CreateLogCommand(applicationType, dimensions, message);

    if (!isDelegate) {
      if (!Strings.isNullOrEmpty(crossTenantId)) {
        throw Exceptions.forbidden("Project %s cannot POST cross tenant metrics", tenantId);
      }
    }

    command.validate();

    service.create(command.toLog(), Strings.isNullOrEmpty(crossTenantId) ? tenantId : crossTenantId);
  }
}
