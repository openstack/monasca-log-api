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
import static org.mockito.Matchers.anyBoolean;
import static org.mockito.Matchers.anyString;
import static org.mockito.Matchers.eq;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.verify;
import static org.testng.Assert.assertEquals;

import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;

import com.google.common.collect.Maps;
import com.sun.jersey.api.client.ClientResponse;
import com.sun.jersey.api.client.WebResource;
import org.mockito.Mockito;
import org.testng.annotations.Test;

import monasca.log.api.ApiConfig;
import monasca.log.api.app.ApplicationModule;
import monasca.log.api.app.LogSerializer;
import monasca.log.api.app.LogService;
import monasca.log.api.app.unload.JsonPayloadTransformer;
import monasca.log.api.common.LogApiConstants;
import monasca.log.api.common.LogRequestBean;
import monasca.log.api.model.Log;
import monasca.log.api.resource.exception.ErrorMessages;
import monasca.log.api.resource.exception.Exceptions;
import monasca.log.api.utils.TestUtils;

@Test
public class LogResourceTest
    extends AbstractMonApiResourceTest {
  private String applicationType;
  private String dimensionsStr;
  private Map<String, String> dimensionsMap;
  private String jsonPayload;
  private String tenantId;
  private String longString;
  private LogService service;
  private String jsonMessage;
  private ApiConfig config;

  @Override
  @SuppressWarnings("unchecked")
  protected void setupResources() throws Exception {
    super.setupResources();
    applicationType = "apache";
    dimensionsStr = "app_name:WebService01,environment:production";
    dimensionsMap = Maps.newHashMap();
    dimensionsMap.put("app_name", "WebService01");
    dimensionsMap.put("environment", "production");
    jsonPayload = "{\n  \"message\":\"Hello, world!\",\n  \"from\":\"hoover\"\n}";
    jsonMessage = "Hello, world!";
    tenantId = "abc";
    longString =
        "12345678901234567890123456789012345678901234567890" + "12345678901234567890123456789012345678901234567890"
            + "12345678901234567890123456789012345678901234567890" + "12345678901234567890123456789012345678901234567890"
            + "12345678901234567890123456789012345678901234567890123456";

    final LogSerializer serializer = new LogSerializer(new ApplicationModule().objectMapper());

    config = new ApiConfig();

    service = Mockito.spy(new LogService(config, null, serializer));
    service.setJsonPayloadTransformer(new JsonPayloadTransformer(serializer));

    doNothing().when(service).sendToKafka(any(Log.class), anyString());
    doCallRealMethod().when(this.service).newLog(any(LogRequestBean.class), anyBoolean());
    doCallRealMethod().when(this.service).validate(any(Log.class));

    addResources(new LogResource(service));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessage() {
    ClientResponse response = createResponseForJson(null, null, jsonPayload);
    Log log = new Log(null, null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateEmptyMessageByJson() {
    ClientResponse response = createResponseForJson(null, null, "");
    Log log = new Log(null, null, "");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithType() {
    ClientResponse response = createResponseForJson(applicationType, null, jsonPayload);
    Log log = new Log(applicationType, null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithEmptyType() {
    ClientResponse response = createResponseForJson("", null, jsonPayload);
    Log log = new Log("", null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithNonNumericAZType() {
    ClientResponse response = createResponseForJson("azAZ19.-_", null, jsonPayload);
    Log log = new Log("azAZ19.-_", null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithSpaceType() {
    ClientResponse response = createResponseForJson(" apache ", null, jsonPayload);
    Log log = new Log("apache", null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInType() {
    ClientResponse response = createResponseForJson("@apache", null, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Application type @apache may only contain: a-z A-Z 0-9 _ - .");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongType() {
    String tooLongType = longString;
    ClientResponse response = createResponseForJson(tooLongType, null, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Application type %s must be %d characters or less", tooLongType, LogApiConstants.MAX_NAME_LENGTH));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensions() {
    ClientResponse response = createResponseForJson(null, dimensionsStr, jsonPayload);
    Log log = new Log(null, dimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithEmptyDimensions() {
    ClientResponse response = createResponseForJson(null, "", jsonPayload);
    Log log = new Log(null, null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithPartiallyEmptyDimensions() {
    String partiallyEmptyDimensions = ",environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, partiallyEmptyDimensions, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithPartiallyEmptyDimensions_2() {
    String partiallyEmptyDimensions = "environment:production,";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, partiallyEmptyDimensions, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithSpaceInKey() {
    String spaceInKeyDimensions = " app_name :WebService01, environment :production";

    ClientResponse response = createResponseForJson(null, spaceInKeyDimensions, jsonPayload);
    Log log = new Log(null, dimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithSpaceInValue() {
    String spaceInValueDimensions = "app_name: WebService01 ,environment: production ";

    ClientResponse response = createResponseForJson(null, spaceInValueDimensions, jsonPayload);
    Log log = new Log(null, dimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithEmptyKeyDimensions() {
    String emptyKeyDimensionsStr = ":WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension name cannot be empty");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithEmptyValueDimensions() {
    String emptyKeyDimensionsStr = "app_name:,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "Dimension app_name cannot have an empty value");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithDimensionsWithoutColon() {
    String emptyKeyDimensionsStr = "app_name,environment:production";
    ClientResponse response = createResponseForJson(null, emptyKeyDimensionsStr, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422, "app_name is not a valid dimension");
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithMultipleColonDimensions() {
    String multipleColonDimensionsStr = "app_name:WebService01:abc,environment:production";
    Map<String, String> multipleColonDimensionsMap = new HashMap<String, String>();
    multipleColonDimensionsMap.put("app_name", "WebService01:abc");
    multipleColonDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, multipleColonDimensionsStr, jsonPayload);
    Log log = new Log(null, multipleColonDimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithDimensionsWithoutIllgalCharsInKey() {
    String legalCharsInKeyDimensionsStr = "azAZ19.-_:WebService01,environment:production";
    Map<String, String> expectedDimensionsMap = new HashMap<String, String>();
    expectedDimensionsMap.put("azAZ19.-_", "WebService01");
    expectedDimensionsMap.put("environment", "production");

    ClientResponse response = createResponseForJson(null, legalCharsInKeyDimensionsStr, jsonPayload);
    Log log = new Log(null, expectedDimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInKey() {
    String illegalCharsInKeyDimensionsStr = "{app_name:WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, illegalCharsInKeyDimensionsStr, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name {app_name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithIllegalCharsInKey_2() {
    String illegalCharsInKeyDimensionsStr = "app=name:WebService01,environment:production";
    ClientResponse response = createResponseForJson(null, illegalCharsInKeyDimensionsStr, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        "Dimension name app=name may not contain: > < = { } ( ) ' \" , ; &");
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithLegalCharsInValue() {
    String legalCharsInValueDimensionsStr = "app_name:@WebService01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "@WebService01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, legalCharsInValueDimensionsStr, jsonPayload);
    Log log = new Log(null, legalCharsInValueDimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithLegalCharsInValue_2() {
    String legalCharsInValueDimensionsStr = "app_name:Web Service01,environment:production";
    Map<String, String> legalCharsInValueDimensionsMap = new HashMap<String, String>();
    legalCharsInValueDimensionsMap.put("app_name", "Web Service01");
    legalCharsInValueDimensionsMap.put("environment", "production");
    ClientResponse response = createResponseForJson(null, legalCharsInValueDimensionsStr, jsonPayload);
    Log log = new Log(null, legalCharsInValueDimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongKey() {
    String tooLongKey = longString;
    ClientResponse response = createResponseForJson(null, tooLongKey + ":abc", jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension name %s must be 255 characters or less", tooLongKey));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateJsonMessageWithTooLongValue() {
    String tooLongValue = longString;
    ClientResponse response = createResponseForJson(null, "abc:" + tooLongValue, jsonPayload);

    ErrorMessages.assertThat(response.getEntity(String.class)).matches("unprocessable_entity", 422,
        String.format("Dimension value %s must be 255 characters or less", tooLongValue));
  }

  @SuppressWarnings("unchecked")
  public void shouldCreateJsonMessageWithTypeAndDimensions() {
    ClientResponse response = createResponseForJson(applicationType, dimensionsStr, jsonPayload);
    Log log = new Log(applicationType, dimensionsMap, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq(tenantId));
  }

  @SuppressWarnings("unchecked")
  public void shouldErrorOnCreateTooLongJsonMessage() {
    String tmpString = longString + longString + longString + longString;
    StringBuffer buf = new StringBuffer(1024 * 1024 + 1);
    buf.append("{\"message\":\"");
    for (int i = 0; i < 1025; i++) {
      buf.append(tmpString);
    }
    buf.append("\"}");
    String tooLongMessage = buf.toString();
    ClientResponse response = createResponseForJson(null, null, tooLongMessage);

    ErrorMessages
        .assertThat(response.getEntity(String.class))
        .matches(
            "payload_too_large",
            Exceptions.FaultType.PAYLOAD_TOO_LARGE.statusCode,
            "Log payload size exceeded"
        );
  }

  public void shouldErrorOnCreateJsonMessageWithCrossTenant() {
    ClientResponse response = createResponseForJsonWithCrossTenant(null, null, jsonPayload, "illegal-role", "def");

    ErrorMessages
        .assertThat(response.getEntity(String.class))
        .matches("forbidden", 403, "Project abc cannot POST cross tenant");
  }

  public void shouldCreateJsonMessageWithCrossTenant() {
    ClientResponse response = createResponseForJsonWithCrossTenant(null, null, jsonPayload, "monitoring-delegate", "def");
    Log log = new Log(null, null, jsonMessage).append("from", "hoover");

    assertEquals(response.getStatus(), 204);
    verify(service).sendToKafka(eq(log), eq("def"));
  }

  private ClientResponse createResponseForJson(String applicationType, String dimensions, String message) {
    WebResource.Builder builder =
        client()
            .resource("/v2.0/log/single")
            .header("X-Tenant-Id", tenantId)
            .header(HttpHeaders.CONTENT_LENGTH, message != null ? message.length() : null)
            .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }

  private ClientResponse createResponseForJsonWithCrossTenant(String applicationType, String dimensions, String message, String roles,
                                                              String crossTenantId) {
    WebResource.Builder builder = client()
        .resource("/v2.0/log/single?tenant_id=" + crossTenantId)
        .header("X-Tenant-Id", tenantId)
        .header("X-Roles", roles)
        .header(HttpHeaders.CONTENT_LENGTH, message != null ? message.length() : null)
        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON);
    if (applicationType != null)
      builder = builder.header("X-Application-Type", applicationType);
    if (dimensions != null)
      builder = builder.header("X-Dimensions", dimensions);
    return builder.post(ClientResponse.class, message);
  }
}
