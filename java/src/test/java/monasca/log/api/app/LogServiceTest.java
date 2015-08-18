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

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import kafka.javaapi.producer.Producer;
import kafka.producer.KeyedMessage;

import org.mockito.Mockito;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import monasca.log.api.ApiConfig;
import monasca.log.api.model.Log;

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
  LogService logService;

  @BeforeMethod
  protected void beforeMethod() {

    dimensions.clear();
    dimensions.put("a", "b");
    config = new ApiConfig();
    config.region = REGION;
    config.logTopic = TOPIC;
    producer = Mockito.mock(Producer.class);
  }

  public void testCreate() {
    String key = "FujitsuApplication/Jsonab";
    String date = Long.toString(new Date().getTime()).substring(0, 10);
    String json = "{\"log\":{\"application_type\":\"Application/Json\",\"dimensions\":{\"a\":\"b\"},\"message\":\"message\"},\"meta\":{\"tenantId\":\"Fujitsu\",\"region\":\"region\"},\"creation_time\":"+ date +"}";
    KeyedMessage<String, String> keyMessage = new KeyedMessage<>("topic", key, json);
    Log log = new Log(APPLICATION_TYPE, dimensions, MESSAGE);
    logService = new LogService(config, producer);
    logService.create(log, TENANT_ID);
    Mockito.verify(producer, Mockito.times(1)).send(keyMessage);
  }
}
