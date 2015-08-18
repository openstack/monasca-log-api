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
package monasca.log.api.app.command;

import static org.testng.AssertJUnit.assertEquals;
import static org.testng.AssertJUnit.assertFalse;
import static org.testng.AssertJUnit.assertTrue;

import java.util.HashMap;
import java.util.Map;

import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import monasca.log.api.app.command.CreateLogCommand;
import monasca.log.api.model.Log;

@Test
public class CreateLogCommandTest {
  private final String APPLICATION_TYPE = "Application/Json";
  private final Map<String, String> dimensions = new HashMap<String, String>();
  private final String MESSAGE = "message";
  CreateLogCommand createLogCommand;

  @BeforeMethod
  protected void beforeMethod() {
    dimensions.clear();
    dimensions.put("a", "b");
    createLogCommand = new CreateLogCommand(APPLICATION_TYPE, dimensions, MESSAGE);
  }

  public void testHashEquals() {
    CreateLogCommand createLogCommandTmp1 = new CreateLogCommand(APPLICATION_TYPE, dimensions, MESSAGE);
    CreateLogCommand createLogCommandTmp2 = new CreateLogCommand(APPLICATION_TYPE, dimensions, "");
    CreateLogCommand createLogCommandTmp3 = new CreateLogCommand(APPLICATION_TYPE, dimensions, null);
    CreateLogCommand createLogCommandTmp4 = new CreateLogCommand(APPLICATION_TYPE, null, MESSAGE);
    dimensions.clear();
    dimensions.put("1", "2");
    CreateLogCommand createLogCommandTmp5 = new CreateLogCommand(APPLICATION_TYPE, dimensions, MESSAGE);
    CreateLogCommand createLogCommandTmp6 = new CreateLogCommand(null, dimensions, MESSAGE);
    CreateLogCommand createLogCommandTmp7 = new CreateLogCommand("", dimensions, MESSAGE);

    assertFalse(createLogCommand.equals(new String()));
    assertFalse(createLogCommand.equals(null));
    assertTrue(createLogCommand.equals(createLogCommand));
    assertTrue(createLogCommand.equals(createLogCommandTmp1));
    assertFalse(createLogCommand.equals(createLogCommandTmp2));
    assertFalse(createLogCommand.equals(createLogCommandTmp3));
    assertFalse(createLogCommand.equals(createLogCommandTmp4));
    assertFalse(createLogCommand.equals(createLogCommandTmp5));
    assertFalse(createLogCommand.equals(createLogCommandTmp6));
    assertFalse(createLogCommand.equals(createLogCommandTmp7));

    assertEquals(createLogCommand.hashCode(), -446078499);

    createLogCommand = new CreateLogCommand();
    createLogCommand.message = "a";
    assertFalse(createLogCommand.equals(new CreateLogCommand(APPLICATION_TYPE, null, "a")));
    assertFalse(createLogCommand.equals(new CreateLogCommand(null, dimensions, "a")));
    assertTrue(createLogCommand.equals(new CreateLogCommand(null, null, "a")));
    assertEquals(createLogCommand.hashCode(), 2889727);
    assertFalse(new CreateLogCommand(APPLICATION_TYPE, dimensions, "a").equals(new CreateLogCommand("", dimensions, "a")));


  }

  public void testSetDimensions() {
    Map<String, String> validatedDimensions = new HashMap<String, String>();
    validatedDimensions.put("1", "2");
    dimensions.clear();
    dimensions.put(" 1", "2 ");
    createLogCommand.setDimensions(dimensions);
    assertEquals(createLogCommand.dimensions, validatedDimensions);
  }

  public void testSetApplicationType() {
    createLogCommand.setApplicationType(" aa ");
    assertEquals(createLogCommand.applicationType, "aa");
  }

  public void testToLog() {
    Log log = new Log(APPLICATION_TYPE, dimensions, MESSAGE);
    assertEquals(createLogCommand.toLog(), log);
  }

  @Test(expectedExceptions = Exception.class)
  public void testValidate() {
    createLogCommand.validate();
  }
}
