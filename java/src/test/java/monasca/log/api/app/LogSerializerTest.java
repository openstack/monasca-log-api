/*
 * Copyright 2015 FUJITSU LIMITED
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
 *
 */
package monasca.log.api.app;

import static org.testng.Assert.assertEquals;

import java.io.UnsupportedEncodingException;
import java.util.SortedMap;
import java.util.TreeMap;

import org.json.JSONException;
import org.skyscreamer.jsonassert.JSONAssert;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import monasca.log.api.model.Log;

/*
*
* TESTS here are order aware
* */

@Test
public class LogSerializerTest {

  private LogSerializer serializer;

  @BeforeMethod
  public void setUp() throws Exception {
    this.serializer = new LogSerializer(new ApplicationModule().objectMapper());
  }

  public void shouldSerializeValue() throws JSONException {
    String applicationType = "apache";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    String message = "Hello, world!";

    final Log log = new Log(applicationType, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"application_type\":\"apache\",\"dimensions\":{\"app_name\":\"WebService01\",\"environment\":\"production\"}," +
        "\"message\":\"Hello, world!\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithNull() throws JSONException {
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    String message = "Hello, world!";

    final Log log = new Log(null, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"dimensions\":{\"app_name\":\"WebService01\",\"environment\":\"production\"}," +
        "\"message\":\"Hello, world!\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithNull_2() throws JSONException {
    String applicationType = "apache";
    String message = "Hello, world!";

    final Log log = new Log(applicationType, null, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"application_type\":\"apache\"," + "\"message\":\"Hello, world!\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithNull_3() throws JSONException {
    String message = "Hello, world!";

    final Log log = new Log(null, null, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"message\":\"Hello, world!\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithEmpty() throws JSONException {
    String applicationType = "";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    String message = "Hello, world!";

    final Log log = new Log(applicationType, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"dimensions\":{\"app_name\":\"WebService01\",\"environment\":\"production\"}," +
        "\"message\":\"Hello, world!\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithEmpty_2() throws JSONException {
    String applicationType = "apache";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    String message = "";

    final Log log = new Log(applicationType, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"application_type\":\"apache\",\"dimensions\":{\"app_name\":\"WebService01\",\"environment\":\"production\"}," +
        "\"message\":\"\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeValueWithEmpty_3() throws JSONException {
    String applicationType = "";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    String message = "";

    final Log log = new Log(applicationType, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"dimensions\":{\"app_name\":\"WebService01\",\"environment\":\"production\"}," +
        "\"message\":\"\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeAndDeserialize() {
    String applicationType = "apache";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "Hello, world!";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithNull() {
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "Hello, world!";
    Log expected = new Log(null, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithNull_2() {
    String applicationType = "apache";
    SortedMap<String, String> dimensions = null;
    String message = "Hello, world!";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithNull_3() {
    String message = "Hello, world!";
    Log expected = new Log(null, null, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithEmpty() {
    String applicationType = "";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "Hello, world!";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithEmpty_2() {
    String applicationType = "apache";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeWithEmpty_3() {
    String applicationType = "";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "WebService01");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes());
    assertEquals(log, expected);
  }

  public void shouldSerializeValueUTF() throws JSONException {
    String applicationType = "foôbár";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "foôbár");
    dimensions.put("instance_id", "123");
    String message = "boôbár";

    final Log log = new Log(applicationType, dimensions, message);
    final String json = this.serializer.toJson(log);
    final String expected = "{\"application_type\":\"foôbár\",\"dimensions\":{\"app_name\":\"foôbár\",\"instance_id\":\"123\"}," +
        "\"message\":\"boôbár\"}";

    JSONAssert.assertEquals(expected, json, true);
  }

  public void shouldSerializeAndDeserializeUTF8() throws UnsupportedEncodingException {
    String applicationType = "foôbár";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "foôbár");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "foôbár";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes("UTF-8"));
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeUTF8_2() throws UnsupportedEncodingException {
    String applicationType = "fo\u00f4b\u00e1r";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "fo\u00f4b\u00e1r");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    String message = "fo\u00f4b\u00e1r";
    Log expected = new Log(applicationType, dimensions, message);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected).getBytes("UTF-8"));
    assertEquals(log, expected);
  }

  public void shouldSerializeAndDeserializeUTF8_3() throws UnsupportedEncodingException {
    String applicationType = "fo\u00f4b\u00e1r";
    String applicationType2 = "foôbár";
    SortedMap<String, String> dimensions = new TreeMap<String, String>();
    dimensions.put("app_name", "fo\u00f4b\u00e1r");
    dimensions.put("environment", "production");
    dimensions.put("instance_id", "123");
    SortedMap<String, String> dimensions2 = new TreeMap<String, String>();
    dimensions2.put("app_name", "foôbár");
    dimensions2.put("environment", "production");
    dimensions2.put("instance_id", "123");
    String message = "fo\u00f4b\u00e1r";
    String message2 = "foôbár";
    Log expected_escaped = new Log(applicationType, dimensions, message);
    Log expected_nonescaped = new Log(applicationType2, dimensions2, message2);

    Log log = this.serializer.logFromJson(this.serializer.logToJson(expected_escaped).getBytes("UTF-8"));
    assertEquals(log, expected_nonescaped);
  }
}
