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

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import javax.ws.rs.WebApplicationException;
import javax.ws.rs.core.MediaType;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.common.collect.ImmutableMap;
import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;
import org.mockito.Mockito;
import org.testng.Assert;
import org.testng.annotations.BeforeTest;
import org.testng.annotations.Test;

import monasca.log.api.ApiConfig;
import monasca.log.api.common.LogApiConstants;
import monasca.log.api.model.Log;
import monasca.log.api.model.LogEnvelope;
import monasca.log.api.utils.TestUtils;

@Test
public class LogServiceTest {
  private final String APPLICATION_TYPE = "Application/Json";
  private final Map<String, String> dimensions = new HashMap<String, String>();
  private final String MESSAGE = "message";
  private final String TENANT_ID = "Fujitsu";
  private final String TOPIC = "topic";
  private final String REGION = "region";

  private ApiConfig config;
  private Producer<String, String> producer;
  private LogService logService;
  private LogSerializer serializer;
  private ObjectMapper mapper;

  @BeforeTest
  @SuppressWarnings("unchecked")
  protected void beforeMethod() {
    dimensions.clear();
    dimensions.put("a", "b");

    config = new ApiConfig();
    config.region = REGION;
    config.logTopic = TOPIC;

    this.producer = Mockito.mock(Producer.class);
    this.mapper = new ApplicationModule().objectMapper();
    this.serializer = Mockito.spy(new LogSerializer(this.mapper));
    this.logService = Mockito.spy(new LogService(this.config, this.producer, this.serializer));
  }

  public void testValidate_shouldFail_ApplicationType_TooLarge() {
    final String str = TestUtils.generateRandomStr(LogApiConstants.MAX_NAME_LENGTH + new Random()
        .nextInt(10));
    try {
      final Log log = new Log(str, null, null);
      this.logService.validate(log);
    } catch (Exception exp) {
      Assert.assertTrue(WebApplicationException.class.isAssignableFrom(exp.getClass()));
      return;
    }
    Assert.fail("Should fail for invalid error message");
  }

  public void testCreate() throws JsonProcessingException {
    final String key = "FujitsuApplication/Jsonab";
    final Log log = new Log(APPLICATION_TYPE, dimensions, MESSAGE);
    final LogEnvelope envelope = new LogEnvelope(log, new ImmutableMap
        .Builder<String, Object>()
        .put("region", this.config.region)
        .put("tenantId", TENANT_ID)
        .build()
    );
    final String json = new ObjectMapper().configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true).writeValueAsString(envelope);
    final KeyedMessage<String, String> keyMessage = new KeyedMessage<>("topic", key, json);

    Mockito.stub(this.logService.newLogEnvelope(log, TENANT_ID)).toReturn(envelope);

    this.logService.sendToKafka(log, TENANT_ID);

    Mockito.verify(this.producer, Mockito.times(1)).send(keyMessage);
    Mockito.verify(this.serializer, Mockito.times(1)).logEnvelopeToJson(envelope);
    Mockito.verify(this.serializer, Mockito.times(1)).toJson(Mockito.anyObject());

    Mockito.verifyZeroInteractions(this.producer, this.serializer);
  }

  public void testValidateContentLength_OK() {
    final Integer contentLength = this.config.logSize / 2;
    this.logService.validateContentLength(contentLength);
  }

  public void testValidateContentLength_PayloadTooLarge() throws IOException {
    final Integer contentLength = this.config.logSize * 2;
    try {
      this.logService.validateContentLength(contentLength);
    } catch (WebApplicationException exp) {
      final Map map = this.mapper.readValue((String) exp.getResponse().getEntity(), Map.class);
      Assert.assertTrue(map.containsKey("payload_too_large"));
    }
  }

  public void testValidateContentLength_MissingHeader() throws IOException {
    final Integer contentLength = null;
    try {
      this.logService.validateContentLength(contentLength);
    } catch (WebApplicationException exp) {
      final Map map = this.mapper.readValue((String) exp.getResponse().getEntity(), Map.class);
      Assert.assertTrue(map.containsKey("length_required"));
    }
  }

  public void testValidateEnvelopeSize_OK() {
    this.config.logSize = 100;
    final int length = this.config.logSize / 2;

    final String msg = TestUtils.generateByteLengthString(length);
    this.logService.validateEnvelopeSize(msg);
  }

  public void testValidateEnvelopeSize_Exceeded() throws IOException {
    this.config.logSize = 100;
    final int length = this.config.logSize * 2;

    final String msg = TestUtils.generateByteLengthString(length);
    try {
      this.logService.validateEnvelopeSize(msg);
    } catch (WebApplicationException exp) {
      final Map map = this.mapper.readValue((String) exp.getResponse().getEntity(), Map.class);
      Assert.assertTrue(map.containsKey("server_error"));
      return;
    }

    Assert.assertFalse(true, "Should not happen");
  }

  public void testShouldThrowExceptionIfContentTypeNull() throws IOException {
    try {
      this.logService.validateContentType(null);
    } catch (WebApplicationException exp){
      final Map map = this.mapper.readValue((String) exp.getResponse().getEntity(), Map.class);
      Assert.assertTrue(map.containsKey("missing_header"));
      return;
    }

    Assert.assertFalse(true, "Should not happen");
  }


  public void testShouldNotThrowExceptionIfContentTypeSet() throws IOException {
    this.logService.validateContentType(MediaType.APPLICATION_ATOM_XML_TYPE);
    Assert.assertTrue(true);
  }

}
