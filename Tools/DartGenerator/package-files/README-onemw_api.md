## onemw-api
This package provides bindings for JSONRPC thunder/rdkservices API. The classes within the package are automatically generated
from the API definition files.

## Main classes
Following API classes are the entry points for using the OneMW API:
- [DisplaySettings]
- [HdmiCec]
- [HdcpProfile]
- [XCast]

## Eventing
Each API class provides a `stream` which allows to listen for API specific events.
```
  var api = DisplaySettings();
  ds_api.stream.listen((event) {print ('event: ${event}');});
```

The list of events emitted by each API class is provided in the documentation of the class.

Each API class defines its own base event, the API specific events inherit from this class. Events are classes generated
by [freezed](https://pub.dev/packages/freezed) module, meaning they have all freeze-generated convenience methods (e.g. `map`, `when`, `maybeMap`, `maybeWhen`).


## Debugging
There is a verbose flag to enable debug info from API class. Error reports shall include verbose logs.
```
  var api = DisplaySettings();
  api.verbose = True;
```

## Environment
The library respects the `CPE_HOST` environment variable, which may contain the IP address of CPE device. This allows to
use the library on the PC host and connect to the remote CPE device.


## Using API
```dart
import 'package:onemw_api/onemw_api.dart';

void main() async {
  var ds_api = DisplaySettings();
  var di_api = DisplayInfo();

  di_api.verbose = true;
  print("di out hdcpprotectionProperty: ${await di_api.hdcpprotectionProperty()}");

  print("ds out: ${await ds_api.getConnectedAudioPorts()}");
  print("ds out: ${(await ds_api.getTvHDRSupport()).standards}");
  print("ds out: ${(await ds_api.getTvHDRSupport()).supportsHDR}");
  print("ds out: ${await ds_api.getDefaultResolution()}");
  print("ds out: ${await ds_api.getVolumeLevel(audioPort:"HDMI0")}");
  print("ds out: ${ds_api.setPreferredOutputColorSpace(["BT2020_NCL"], videoDisplay:"HDMI0")}");

  ds_api.stream.listen((event) {print ('event: ${event}');});
}
```

## Definition of the API
The best effort was made to document the dart classes. The original API definition in json files is provided here for reference:
 * [DisplaySettings.json](https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20220329/LgiDisplaySettings/LgiDisplaySettings.json)
 * [LgiHdmiCec.json](https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20220329/LgiHdmiCec/LgiHdmiCec.json)
 * [LgiHdcpProfile.json](https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20220329/LgiHdcpProfile/LgiHdcpProfile.json)
 * [XCast.json](https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20220329/XCast/XCast.json)

## Tests
There are 2 types of tests: mocks and CPE based.
The mocks are using real jsons from communication with CPE.
Jsons can be grabbed using command:
CPE_HOST=[Your CPE IP] dart test --chain-stack-traces ./test/tool/*
To run the tests please execute:
dart test --chain-stack-traces ./test/*_test.dart
To run the tests on CPE please execute:
CPE_HOST=[Your CPE IP] dart test --chain-stack-traces ./test/cpe/*
