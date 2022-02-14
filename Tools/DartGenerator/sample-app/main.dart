// If not stated otherwise in this file or this component's LICENSE file the
// following copyright and licenses apply:
//
// Copyright 2022 Liberty Global Service B.V.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:onemw_api/onemw_api.dart';

int f(var x) {
  // String x = "123";
  return x is int ? x :  int.parse(x);

}

void main() async {
  var ds_api = DisplaySettings();
  var di_api = DisplayInfo();
  print("di out hdcpprotectionPr: ${await di_api.hdcpprotectionProperty()}");
  print("di out hdrsettingProper: ${await di_api.hdrsettingProperty()}");
  print("di out heightProperty(): ${await di_api.heightProperty()}");
  print("di out widthProperty()}: ${await di_api.widthProperty()}");
  print("di out connectedPropert: ${await di_api.connectedProperty()}");
  print("di out isaudiopassthrou: ${await di_api.isaudiopassthroughProperty()}");
  print("di out freegpuramProper: ${await di_api.freegpuramProperty()}");
  print("di out totalgpuramPrope: ${await di_api.totalgpuramProperty()}");



  print("ds out: ${await ds_api.getConnectedAudioPorts()}");
  print("ds out: ${await ds_api.getConnectedAudioPorts()}");
  print("ds out: ${await ds_api.getVolumeLevel("HDMI0")}");
  print("ds out: ${await ds_api.getTvHDRSupport()}.standards");
  print("ds out: ${await ds_api.getTvHDRSupport()}.supportsHDR");
  print("ds out: ${await ds_api.getDefaultResolution()}");

  ds_api.stream.listen((event) {print ('event: ${event.runtimeType} ${event}');});
}

