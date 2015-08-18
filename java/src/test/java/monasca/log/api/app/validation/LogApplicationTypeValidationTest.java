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
package monasca.log.api.app.validation;

import static org.testng.AssertJUnit.assertEquals;
import static org.testng.AssertJUnit.assertNull;
import static org.testng.AssertJUnit.assertTrue;

import java.io.IOException;

import javax.ws.rs.WebApplicationException;

import org.testng.annotations.Test;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;

import monasca.log.api.app.validation.LogApplicationTypeValidator;

@Test
public class LogApplicationTypeValidationTest {

  private final String toNormalize = " Json Application ";
  private final String normalized = "Json Application";

  public void testNormalize() {

    String result = LogApplicationTypeValidator.normalize(toNormalize);
    assertEquals(normalized, result);
    result = LogApplicationTypeValidator.normalize(null);
    assertNull(result);
  }

  public void testValidateWrongFormat() throws JsonParseException, IOException {
    int exceptionCount = 0;
    try {
      LogApplicationTypeValidator.validate(normalized);
    } catch (WebApplicationException e) {
      exceptionCount++;
      String msg = getMessage((String) e.getResponse().getEntity());
      assertEquals(msg, "Application type Json Application may only contain: a-z A-Z 0-9 _ - .");
    }

    assertEquals("Method throws Exception with correct message", 1, exceptionCount);
  }

  public void testValidateWrongLength() throws JsonParseException, IOException {
    StringBuilder message = new StringBuilder();
    int exceptionCount = 0;
    for (int i = 0; i < 256; i++) {
      message.append('a');
    }
    try {
      LogApplicationTypeValidator.validate(message.toString());
    } catch (WebApplicationException e) {
      exceptionCount++;
      String msg = getMessage((String) e.getResponse().getEntity());
      assertTrue(msg.contains("must be 255 characters or less"));
    }
    assertEquals("Method throws Exception with correct message", 1, exceptionCount);
  }

  private String getMessage(String json) throws JsonParseException, IOException {
    JsonFactory factory = new JsonFactory();
    JsonParser jp = factory.createParser(json);
    jp.nextToken();
    while (jp.nextToken() != JsonToken.END_OBJECT) {
      String fieldname = jp.getCurrentName();
      jp.nextToken();
      if ("message".equals(fieldname)) {

        return jp.getText();
      }
    }
    jp.close();
    return null;
  }
}
