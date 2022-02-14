# onemw-api
This package provides bindings for thunder/rdkservices API. The classes within the package are automatically generated
from the API definition files.

## Main classes
Following classes are the entry points for using the OneMW API:
- `LgiDisplaySettings`
- `LgiHdmiCec`
- `DisplayInfo`
- `ActivityMonitor`
- `OCIContainer`
- `Packager`
- `PlayerInfo`
- `SecurityAgent`



## Using API
```dart
import 'package:onemw_api/onemw_api.dart';

void main() async {
  var api = DisplaySettings();
  print("out: ${await api.getConnectedAudioPorts()}");
  print("out: ${await api.getVolumeLevel("HDMI0")}");
  print("out: ${await api.getTvHDRSupport()}.standards");
  print("out: ${await api.getTvHDRSupport()}.supportsHDR");
  print("out: ${await api.getDefaultResolution()}");
}
```



