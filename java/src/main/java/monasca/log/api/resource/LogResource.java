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
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Request;

import com.codahale.metrics.annotation.Timed;
import com.google.common.base.Splitter;
import com.google.common.base.Strings;
import com.sun.jersey.api.core.HttpRequestContext;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import monasca.log.api.app.LogService;
import monasca.log.api.app.validation.Validation;
import monasca.log.api.common.LogRequestBean;
import monasca.log.api.model.Log;
import monasca.log.api.resource.exception.Exceptions;

/**
 * Log resource implementation.
 */
@Path("/v2.0/log")
public class LogResource {
  private static final Logger LOGGER = LoggerFactory.getLogger(LogResource.class);
  private static final String MONITORING_DELEGATE_ROLE = "monitoring-delegate";
  private static final Splitter COMMA_SPLITTER = Splitter.on(',').omitEmptyStrings().trimResults();
  private static final boolean VALIDATE_LOG = true;

  private final LogService service;

  @Inject
  public LogResource(final LogService service) {
    this.service = service;
  }

  @POST
  @Timed
  @Consumes(MediaType.APPLICATION_JSON)
  @Path("/single")
  public void single(@Context Request request,
                     @HeaderParam("X-Tenant-Id") String tenantId,
                     @HeaderParam("X-Roles") String roles,
                     @HeaderParam("X-Application-Type") String applicationType,
                     @HeaderParam("X-Dimensions") String dimensionsStr,
                     @QueryParam("tenant_id") String crossTenantId,
                     String payload) {

    LOGGER.debug("/single/{}", tenantId);

    final MediaType contentType = this.getContentType(request);

    this.service.validateContentLength(this.getContentLength(request));
    this.service.validateContentType(contentType);

    if (!this.isDelegate(roles)) {
      LOGGER.trace(String.format("/single/%s is not delegated request, checking for crossTenantId",
          tenantId));
      if (!Strings.isNullOrEmpty(crossTenantId)) {
        throw Exceptions.forbidden("Project %s cannot POST cross tenant metrics", tenantId);
      }
    }

    final Log log = service.newLog(
        new LogRequestBean()
            .setApplicationType(applicationType)
            .setDimensions(this.getDimensions(dimensionsStr))
            .setContentType(contentType)
            .setPayload(payload),
        VALIDATE_LOG
    );
    tenantId = this.getTenantId(tenantId, crossTenantId);

    LOGGER.debug("Shipping log={},tenantId={} pair to kafka", log, tenantId);

    this.service.sendToKafka(log, tenantId);
  }

  private MediaType getContentType(final Request request) {
    return ((HttpRequestContext) request).getMediaType();
  }

  private Integer getContentLength(final Request request){
    final String value = ((HttpRequestContext) request).getHeaderValue(HttpHeaders.CONTENT_LENGTH);
    return StringUtils.isNotEmpty(value) ? Integer.valueOf(value) : null;
  }

  private String getTenantId(final String tenantId, final String crossTenantId) {
    return Strings.isNullOrEmpty(crossTenantId) ? tenantId : crossTenantId;
  }

  private Map<String, String> getDimensions(final String dimensionsStr) {
    return Strings.isNullOrEmpty(dimensionsStr) ? null : Validation.parseLogDimensions(dimensionsStr);
  }

  private boolean isDelegate(final String roles) {
    return !Strings.isNullOrEmpty(roles) && COMMA_SPLITTER
        .splitToList(roles)
        .contains(MONITORING_DELEGATE_ROLE);
  }

}
