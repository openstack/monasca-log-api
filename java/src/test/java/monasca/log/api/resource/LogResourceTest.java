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

import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.testng.Assert.assertEquals;

import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.core.MediaType;

import org.testng.annotations.Test;

import com.sun.jersey.api.client.ClientResponse;
import com.sun.jersey.api.client.WebResource;

import monasca.log.api.app.LogService;
import monasca.log.api.app.command.CreateLogCommand;
import monasca.log.api.model.Log;
import monasca.log.api.resource.exception.ErrorMessages;

@Test
public class LogResourceTest extends AbstractMonApiResourceTest {
  private String applicationType;
  private String dimensionsStr;
  private Map<String, String> dimensionsMap;
  private String jsonMessage;
  private String textMessage;
  private String tenantId;
  private String longString;
  private LogService service;

  @Override
  @SuppressWarnings("unchecked")
  protected void setupResources() throws Exception {
    super.setupResources();
    applicationType = "apache";
    dimensionsStr = "app_name:WebService01,environment:production";
    dimensionsMap = new HashMap<String, String>();
    dimensionsMap.put("app_name", "WebService01");
    dimensionsMap.put("environment", "production");
    jsonMessage = "{\n  \"message\":\"Hello, world!\",\n  \"from\":\"hoover\"\n}";
    textMessage = "Hello, world!";
    tenantId = "abc";
    longString =
        "12345678901234567890123456789012345678901234567890" + "12345678901234567890123456789012345678901234567890"
            + "12345678901234567890123456789012345678901234567890" + "12345678901234567890123456789012345678901234567890"
            + "12345678901234567890123456789012345678901234567890123456";

    service = mock(LogService.class);
    doNothing().when(service).create(any(Log.class), anyString());

    addResources(new LogResource(service));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessage() {
    ClientResponse response = createResponseForJson(null, null, jsonMessage);
    Log log = new Log(null, null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageByText() {
    ClientResponse response = createResponseForText(null, null, jsonMessage);
    Log log = new Log(null, null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessage() {
    ClientResponse response = createResponseForText(null, null, textMessage);
    Log log = new Log(null, null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageByJson() {
    ClientResponse response = createResponseForJson(null, null, textMessage);
    Log log = new Log(null, null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateEmptyMessageByJson() {
    ClientResponse response = createResponseForJson(null, null, "");
    Log log = new Log(null, null, "");

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateEmptyMessageByText() {
    ClientResponse response = createResponseForText(null, null, "");
    Log log = new Log(null, null, "");

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithType() {
    ClientResponse response = createResponseForJson(applicationType, null, jsonMessage);
    Log log = new Log(applicationType, null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithType() {
    ClientResponse response = createResponseForText(applicationType, null, textMessage);
    Log log = new Log(applicationType, null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithEmptyType() {
    ClientResponse response = createResponseForJson("", null, jsonMessage);
    Log log = new Log("", null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithEmptyType() {
    ClientResponse response = createResponseForText("", null, textMessage);
    Log log = new Log("", null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithNonNumericAZType() {
    ClientResponse response = createResponseForJson("azAZ19.-_", null, jsonMessage);
    Log log = new Log("azAZ19.-_", null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithNonNumericAZType() {
    ClientResponse response = createResponseForText("azAZ19.-_", null, textMessage);
    Log log = new Log("azAZ19.-_", null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithSpaceType() {
    ClientResponse response = createResponseForJson(" apache ", null, jsonMessage);
    Log log = new Log("apache", null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithSpaceType() {
    ClientResponse response = createResponseForText(" apache ", null, textMessage);
    Log log = new Log("apache", null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInType() {
    ClientResponse response = createResponseForJson("@apache", null, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Application type @apache may only contain: a-z A-Z 0-9 _ - .");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithIllegalCharsInType() {
    ClientResponse response = createResponseForText("@apache", null, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Application type @apache may only contain: a-z A-Z 0-9 _ - .");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongType() {
    String tooLongType = longString;
    ClientResponse response = createResponseForJson(tooLongType, null, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Application type %s must be %d characters or less", tooLongType, CreateLogCommand.MAX_NAME_LENGTH));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithTooLongType() {
    String tooLongType = longString;
    ClientResponse response = createResponseForText(tooLongType, null, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Application type %s must be %d characters or less", tooLongType, CreateLogCommand.MAX_NAME_LENGTH));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensions() {
    ClientResponse response = createResponseForJson(null, dimensionsStr, jsonMessage);
    Log log = new Log(null, dimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithDimensions() {
    ClientResponse response = createResponseForText(null, dimensionsStr, textMessage);
    Log log = new Log(null, dimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithEmptyDimensions() {
    ClientResponse response = createResponseForJson(null, "", jsonMessage);
    Log log = new Log(null, null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithEmptyDimensions() {
    ClientResponse response = createResponseForText(null, "", textMessage);
    Log log = new Log(null, null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithPartiallyEmptyDimensions() {
    String partiallyEmptyDimensions = ",environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, partiallyEmptyDimensions, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithPartiallyEmptyDimensions() {
    String partiallyEmptyDimensions = ",environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForText(null, partiallyEmptyDimensions, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithPartiallyEmptyDimensions_2() {
    String partiallyEmptyDimensions = "environment:production,";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, partiallyEmptyDimensions, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithPartiallyEmptyDimensions_2() {
    String partiallyEmptyDimensions = "environment:production,";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForText(null, partiallyEmptyDimensions, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithSpaceInKey() {
    String spaceInKeyDimensions = " app_name :WebService01, environment :production";

    ClientResponse response = createResponseForJson(null, spaceInKeyDimensions, jsonMessage);
    Log log = new Log(null, dimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithDimensionsWithSpaceInKey() {
    String spaceInKeyDimensions = " app_name :WebService01, environment :production";

    ClientResponse response = createResponseForText(null, spaceInKeyDimensions, textMessage);
    Log log = new Log(null, dimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithSpaceInValue() {
    String spaceInValueDimensions = "app_name: WebService01 ,environment: production ";

    ClientResponse response = createResponseForJson(null, spaceInValueDimensions, jsonMessage);
    Log log = new Log(null, dimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithDimensionsWithSpaceInValue() {
    String spaceInValueDimensions = "app_name: WebService01 ,environment: production ";

    ClientResponse response = createResponseForText(null, spaceInValueDimensions, textMessage);
    Log log = new Log(null, dimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithEmptyKeyDimensions() {
    String emptyKeyDimensionsStr = ":WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension name cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithEmptyKeyDimensions() {
    String emptyKeyDimensionsStr = ":WebService01,environment:production";
    ClientResponse response = createResponseForText(null, emptyKeyDimensionsStr, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension name cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithEmptyValueDimensions() {
    String emptyKeyDimensionsStr = "app_name:,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension app_name cannot have an empty value");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithEmptyValueDimensions() {
    String emptyKeyDimensionsStr = "app_name:,environment:production";
    ClientResponse response = createResponseForText(null, emptyKeyDimensionsStr, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension app_name cannot have an empty value");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithDimensionsWithoutColon() {
    String emptyKeyDimensionsStr = "app_name,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "app_name is not a valid dimension");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithDimensionsWithoutColon() {
    String emptyKeyDimensionsStr = "app_name,environment:production";
    ClientResponse response = createResponseForText(null, emptyKeyDimensionsStr, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "app_name is not a valid dimension");
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithMultipleColonDimensions() {
    String multipleColonDimensionsStr = "app_name:WebService01:abc,environment:production";
    Map<String, String> multipleColonDimensionsMap = new HashMap<String, String>();
    multipleColonDimensionsMap.put("app_name", "WebService01:abc");
    multipleColonDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, multipleColonDimensionsStr, jsonMessage);
    Log log = new Log(null, multipleColonDimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithMultipleColonDimensions() {
    String multipleColonDimensionsStr = "app_name:WebService01:abc,environment:production";
    Map<String, String> multipleColonDimensionsMap = new HashMap<String, String>();
    multipleColonDimensionsMap.put("app_name", "WebService01:abc");
    multipleColonDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForText(null, multipleColonDimensionsStr, textMessage);
    Log log = new Log(null, multipleColonDimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithoutIllgalCharsInKey() {
    String legalCharsInKeyDimensionsStr = "azAZ19.-_:WebService01,environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("azAZ19.-_", "WebService01");
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, legalCharsInKeyDimensionsStr, jsonMessage);
    Log log = new Log(null, expectedDimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithDimensionsWithoutIllegalCharsInKey() {
    String legalCharsInKeyDimensionsStr = "azAZ19.-_:WebService01,environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("azAZ19.-_", "WebService01");
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForText(null, legalCharsInKeyDimensionsStr, textMessage);
    Log log = new Log(null, expectedDimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInKey() {
    String illegalCharsInKeyDimensionsStr = "{app_name:WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, illegalCharsInKeyDimensionsStr, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name {app_name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithIllegalCharsInKey() {
    String illegalCharsInKeyDimensionsStr = "{app_name:WebService01,environment:production";
    ClientResponse response = createResponseForText(null, illegalCharsInKeyDimensionsStr, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name {app_name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInKey_2() {
    String illegalCharsInKeyDimensionsStr = "app=name:WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, illegalCharsInKeyDimensionsStr, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name app=name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithIllegalCharsInKey_2() {
    String illegalCharsInKeyDimensionsStr = "app=name:WebService01,environment:production";
    ClientResponse response = createResponseForText(null, illegalCharsInKeyDimensionsStr, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name app=name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithLegalCharsInValue() {
    String legalCharsInValueDimensionsStr = "app_name:@WebService01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "@WebService01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, legalCharsInValueDimensionsStr, jsonMessage);
    Log log = new Log(null, legalCharsInValueDimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithLegalCharsInValue() {
    String legalCharsInValueDimensionsStr = "app_name:@WebService01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "@WebService01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForText(null, legalCharsInValueDimensionsStr, textMessage);
    Log log = new Log(null, legalCharsInValueDimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithLegalCharsInValue_2() {
    String legalCharsInValueDimensionsStr = "app_name:Web Service01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "Web Service01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, legalCharsInValueDimensionsStr, jsonMessage);
    Log log = new Log(null, legalCharsInValueDimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithLegalCharsInValue_2() {
    String legalCharsInValueDimensionsStr = "app_name:Web Service01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "Web Service01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForText(null, legalCharsInValueDimensionsStr, textMessage);
    Log log = new Log(null, legalCharsInValueDimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongKey() {
    String tooLongKey = longString;
    ClientResponse response = createResponseForJson(null, tooLongKey + ":abc", jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension name %s must be 255 characters or less", tooLongKey));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithTooLongKey() {
    String tooLongKey = longString;
    ClientResponse response = createResponseForText(null, tooLongKey + ":abc", textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension name %s must be 255 characters or less", tooLongKey));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongValue() {
    String tooLongValue = longString;
    ClientResponse response = createResponseForJson(null, "abc:" + tooLongValue, jsonMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension value %s must be 255 characters or less", tooLongValue));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTextMessageWithTooLongValue() {
    String tooLongValue = longString;
    ClientResponse response = createResponseForText(null, "abc:" + tooLongValue, textMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension value %s must be 255 characters or less", tooLongValue));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithTypeAndDimensions() {
    ClientResponse response = createResponseForJson(applicationType, dimensionsStr, jsonMessage);
    Log log = new Log(applicationType, dimensionsMap, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateTextMessageWithTypeAndDimensions() {
    ClientResponse response = createResponseForText(applicationType, dimensionsStr, textMessage);
    Log log = new Log(applicationType, dimensionsMap, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTooLongJsonMessage() {
    String tmpString = longString + longString + longString + longString;
    StringBuffer buf = new StringBuffer(1024 * 1024 + 1);
    buf.append("{\"a\":\"");
    for (int i = 0; i < 1024; i++) {
      buf.append(tmpString);
    }
    buf.append("\"}");
    String tooLongMessage = buf.toString();
    ClientResponse response = createResponseForJson(null, null, tooLongMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Log must be 1048576 characters or less");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTooLongTextMessage() {
    String tmpString = longString + longString + longString + longString;
    StringBuffer buf = new StringBuffer(1024 * 1024 + 1);
    for (int i = 0; i < 1024; i++) {
      buf.append(tmpString);
    }
    buf.append('0');
    String tooLongMessage = buf.toString();
    ClientResponse response = createResponseForText(null, null, tooLongMessage);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Log must be 1048576 characters or less");
  }

  public void shouldErrorOnCreateJsonMessageWithCrossTenant() {
    ClientResponse response = createResponseForJsonWithCrossTenant(null, null, jsonMessage, "illegal-role", "def");

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("forbidden", 403, "Project abc cannot POST cross tenant");
  }

  public void shouldErrorOnCreateTextMessageWithCrossTenant() {
    ClientResponse response = createResponseForTextWithCrossTenant(null, null, textMessage, "illegal-role", "def");

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("forbidden", 403, "Project abc cannot POST cross tenant");
  }

  public void shouldCreateJsonMessageWithCrossTenant() {
    ClientResponse response = createResponseForJsonWithCrossTenant(null, null, jsonMessage, "monitoring-delegate", "def");
    Log log = new Log(null, null, jsonMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq("def"));
  }

  public void shouldCreateTextMessageWithCrossTenant() {
    ClientResponse response = createResponseForTextWithCrossTenant(null, null, textMessage, "monitoring-delegate", "def");
    Log log = new Log(null, null, textMessage);

    assertEquals(response.getStatus(), 204);
    verify(service).create(eq(log), eq("def"));
  }

  private ClientResponse createResponseForJson(String applicationType, String dimensions, String message) {
    WebResource.Builder builder =
        client().resource("/v2.0/log/single").header("X-Tenant-Id", tenantId).header("Content-Type", MediaType.APPLICATION_JSON);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }

  private ClientResponse createResponseForText(String applicationType, String dimensions, String message) {
    WebResource.Builder builder = client().resource("/v2.0/log/single").header("X-Tenant-Id", tenantId).header("Content-Type", MediaType.TEXT_PLAIN);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }

  private ClientResponse createResponseForJsonWithCrossTenant(String applicationType, String dimensions, String message, String roles,
      String crossTenantId) {
    WebResource.Builder builder =
        client().resource("/v2.0/log/single?tenant_id=" + crossTenantId).header("X-Tenant-Id", tenantId).header("X-Roles", roles)
            .header("Content-Type", MediaType.APPLICATION_JSON);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }

  private ClientResponse createResponseForTextWithCrossTenant(String applicationType, String dimensions, String message, String roles,
      String crossTenantId) {
    WebResource.Builder builder =
        client().resource("/v2.0/log/single?tenant_id=" + crossTenantId).header("X-Tenant-Id", tenantId).header("X-Roles", roles)
            .header("Content-Type", MediaType.TEXT_PLAIN);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }
}
