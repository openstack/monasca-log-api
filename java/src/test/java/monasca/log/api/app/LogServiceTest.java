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

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import javax.ws.rs.WebApplicationException;

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

  @BeforeTest
  @SuppressWarnings("unchecked")
  protected void beforeMethod() {
    dimensions.clear();
    dimensions.put("a", "b");
    config = new ApiConfig();
    config.region = REGION;
    config.logTopic = TOPIC;

    this.producer = Mockito.mock(Producer.class);
    this.serializer = Mockito.spy(new LogSerializer(new ApplicationModule().objectMapper()));
    this.logService = Mockito.spy(new LogService(this.config, this.producer, this.serializer));
  }

  public void testValidate_shouldFail_ApplicationType_TooLarge() {
    final String str = this.generateRandomStr(LogApiConstants.MAX_NAME_LENGTH + new Random().nextInt(10));
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

  private String generateRandomStr(final int length) {
    final StringBuilder builder = new StringBuilder();
    for (int i = 0; i < length; i++) {
      builder.append(i);
    }
    return builder.toString();
  }
}
