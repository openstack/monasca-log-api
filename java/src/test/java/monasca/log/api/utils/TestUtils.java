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
 */

package monasca.log.api.utils;


import java.nio.charset.Charset;

public class TestUtils {

  public static String generateRandomStr(final int length) {
    final StringBuilder builder = new StringBuilder();
    for (int i = 0; i < length; i++) {
      builder.append(i);
    }
    return builder.toString();
  }

  public static String generateByteLengthString(final double length) {
    int currentLength = 0;
    int size;

    String currentString;

    do {
      currentString = generateRandomStr(currentLength++);
      size = currentString.getBytes(Charset.forName("UTF-8")).length;
      if (size == length) {
        break;
      }
    } while (currentLength < length);

    return currentString;
  }

}
