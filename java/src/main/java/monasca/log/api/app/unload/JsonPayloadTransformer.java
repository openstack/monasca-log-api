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

package monasca.log.api.app.unload;

import javax.ws.rs.core.MediaType;

import com.google.inject.Inject;
import org.apache.commons.lang3.StringUtils;

import monasca.log.api.app.LogSerializer;
import monasca.log.api.common.PayloadTransformer;
import monasca.log.api.model.Log;


public class JsonPayloadTransformer
    extends PayloadTransformer {

  private final LogSerializer serializer;

  @Inject
  public JsonPayloadTransformer(final LogSerializer serializer) {
    this.serializer = serializer;
  }

  @Override
  public Log transform(final String from) {
    if (StringUtils.isEmpty(from)) {
      return new Log().setMessage("");
    }
    return this.serializer.logFromJson(from.getBytes());
  }

  @Override
  public MediaType supportsMediaType() {
    return MediaType.APPLICATION_JSON_TYPE;
  }
}
