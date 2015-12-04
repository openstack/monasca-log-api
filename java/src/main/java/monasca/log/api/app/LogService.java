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
package monasca.log.api.app;

import static monasca.log.api.common.LogApiConstants.LOG_MARKER;
import static monasca.log.api.common.LogApiConstants.LOG_MARKER_KAFKA;
import static monasca.log.api.common.LogApiConstants.LOG_MARKER_WARN;

import java.nio.charset.Charset;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import javax.inject.Inject;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import monasca.log.api.ApiConfig;
import monasca.log.api.app.unload.JsonPayloadTransformer;
import monasca.log.api.app.validation.DimensionValidation;
import monasca.log.api.app.validation.LogApplicationTypeValidator;
import monasca.log.api.common.LogRequestBean;
import monasca.log.api.common.PayloadTransformer;
import monasca.log.api.model.Log;
import monasca.log.api.model.LogEnvelope;
import monasca.log.api.resource.exception.Exceptions;

/**
 * Log service implementation.
 */
public class LogService {
  private static final Logger LOGGER = LoggerFactory.getLogger(LogService.class);
  private static final Comparator<Map.Entry<String, String>> DIMENSIONS_COMPARATOR;

  static {
    DIMENSIONS_COMPARATOR = new Comparator<Map.Entry<String, String>>() {
      @Override
      public int compare(Entry<String, String> o1, Entry<String, String> o2) {
        int nameCmp = o1.getKey().compareTo(o2.getKey());
        return (nameCmp != 0 ? nameCmp : o1.getValue().compareTo(o2.getValue()));
      }
    };
  }

  protected ApiConfig config;
  protected Producer<String, String> producer;
  protected LogSerializer serializer;
  protected Map<MediaType, PayloadTransformer> payloadTransformers;

  @Inject
  public LogService(final ApiConfig config,
                    final Producer<String, String> producer,
                    final LogSerializer logSerializer) {
    this.config = config;
    this.producer = producer;
    this.serializer = logSerializer;
    this.payloadTransformers = Maps.newHashMapWithExpectedSize(2);
  }

  protected LogService() {
    this(null, null, null);
  }

  @Inject
  public void setJsonPayloadTransformer(final JsonPayloadTransformer jsonPayloadTransformer) {
    this.payloadTransformers.put(MediaType.APPLICATION_JSON_TYPE, jsonPayloadTransformer);
  }

  public Log newLog(final LogRequestBean logRequestBean) {
    LOGGER.debug(LOG_MARKER, "Creating new log from bean = {}", logRequestBean);
    return this.newLog(logRequestBean, true);
  }

  public Log newLog(final LogRequestBean logRequestBean, final boolean validate) {
    LOGGER.debug(LOG_MARKER, "Creating new log from bean = {}, validation is {}",
        logRequestBean, validate ? "enabled" : "disabled");

    Preconditions.checkNotNull(logRequestBean, "LogBean must not be null");
    Preconditions.checkNotNull(logRequestBean.getPayload(), "Payload should not be null");

    final String payload = logRequestBean.getPayload();
    final Log log;

    try {
      log = this.payloadTransformers.get(logRequestBean.getContentType()).transform(payload);
    } catch (Exception exp) {
      LOGGER.warn(LOG_MARKER_WARN, "Failed to unpack payload \n\"{}\"", payload);
      throw Exceptions.unprocessableEntity("{} couldn't be processed", payload);
    }

    log.setApplicationType(LogApplicationTypeValidator
        .normalize(logRequestBean.getApplicationType()));
    log.setDimensions(DimensionValidation
        .normalize(logRequestBean.getDimensions()));

    if (validate) {
      this.validate(log);
    }

    return log;
  }

  public void validate(final Log log) {

    LOGGER.trace(LOG_MARKER, "Validating log {}", log);

    try {
      if (log.getApplicationType() != null && !log.getApplicationType().isEmpty()) {
        LogApplicationTypeValidator.validate(log.getApplicationType());
      }
      if (log.getDimensions() != null) {
        DimensionValidation.validate(log.getDimensions(), null);
      }
    } catch (Exception exp) {
      LOGGER.warn(LOG_MARKER_WARN, "Log {} not valid, error is {}", log, exp);
      throw exp;
    }

    LOGGER.debug(LOG_MARKER, "Log {} considered valid", log);

  }

  public void sendToKafka(Log log, String tenantId) {
    final String envelope = this.serializer
        .logEnvelopeToJson(this.newLogEnvelope(log, tenantId));

    this.validateEnvelopeSize(envelope);

    final KeyedMessage<String, String> keyedMessage = new KeyedMessage<>(
        this.config.logTopic,
        this.buildKey(tenantId, log),
        envelope
    );

    LOGGER.debug(LOG_MARKER_KAFKA, "Shipping kafka message {}", keyedMessage);

    this.producer.send(keyedMessage);
  }

  public void validateContentLength(final Integer contentLength) {

    LOGGER.debug("validateContentLength(length=%d)", contentLength);

    if (contentLength == null) {
      throw Exceptions.lengthRequired(
          "Content length header is missing",
          "Content length is required to estimate if payload can be processed"
      );
    }

    if (contentLength >= this.config.logSize) {
      throw Exceptions.payloadTooLarge(
          "Log payload size exceeded",
          String.format("Maximum allowed size is %d bytes", this.config.logSize)
      );
    }

  }

  public void validateContentType(final MediaType contentType) {
    if(contentType == null){
      throw Exceptions.headerMissing(HttpHeaders.CONTENT_TYPE);
    }
  }

  public void validateEnvelopeSize(final String envelope) {
    if (!StringUtils.isEmpty(envelope)) {
      // that must be length in bytes in common encoding

      final int size = envelope.getBytes(Charset.forName("UTF-8")).length;
      if (size >= this.config.logSize) {
        throw Exceptions.internalServerError(
            "Envelope size exceeded",
            String.format("Maximum allowed size is %d bytes", this.config.logSize),
            null
        );
      }
    }
  }

  protected LogEnvelope newLogEnvelope(final Log log, final String tenantId) {
    return new LogEnvelope(
        log,
        new ImmutableMap
            .Builder<String, Object>()
            .put("tenantId", tenantId)
            .put("region", this.config.region)
            .build()
    );
  }

  private String buildKey(String tenantId, Log log) {
    final StringBuilder key = new StringBuilder();

    key.append(tenantId);

    if (StringUtils.isNotEmpty(log.getApplicationType())) {
      key.append(log.getApplicationType());
    }

    if (MapUtils.isNotEmpty(log.getDimensions())) {
      for (final Map.Entry<String, String> dim : this.buildSortedDimSet(log.getDimensions())) {
        key.append(dim.getKey());
        key.append(dim.getValue());
      }
    }

    return key.toString();
  }

  /**
   * Key must be the same for the same log so sort the dimensions so they will
   * be in known order
   *
   * @param dimMap unsorted dimensions
   *
   * @return sorted dimensions
   */
  private List<Map.Entry<String, String>> buildSortedDimSet(final Map<String, String> dimMap) {
    final List<Map.Entry<String, String>> dims = Lists.newArrayList(dimMap.entrySet());
    Collections.sort(dims, DIMENSIONS_COMPARATOR);
    return dims;
  }

}
