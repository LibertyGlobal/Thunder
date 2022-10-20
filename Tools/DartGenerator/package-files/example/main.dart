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

import 'package:onemw_rdkservices_api/onemw_rdkservices_api.dart';

void main() async {
  var ds_api = DisplaySettings();
  var cc_api = HdmiCec();
  var hdcp_api = HdcpProfile();
  cc_api.verbose = true;
  ds_api.verbose = true;

  ds_api.stream.listen((event) {print ('event: ${event.runtimeType} ${event}');});
  cc_api.stream.listen((event) {print ('event: ${event.runtimeType} ${event}');});
  hdcp_api.stream.listen((event) {print ('event: ${event.runtimeType} ${event}');});

  print("ds out: ${await ds_api.getConnectedAudioPorts()}");
  print("ds out: ${ds_api.setPreferredOutputColorSpace(colorSpaces:["BT2020_NCL"], videoDisplay:"HDMI0"  )}");

  print("cc out: ${await cc_api.getCECAddresses()}");
  print("cc out: ${await cc_api.getEnabled()}");
  print("cc out: ${await cc_api.getConnectedDevices()}");
  print("cc out: ${cc_api.setOneTouchViewPolicy(turnOffAllDevices:true)}");

  // var timer = Timer(Duration(milliseconds: 100), () => exit(0));
}

