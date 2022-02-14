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
  var inputStatusChanged = ds_api.createStreamController<ConnectedVideoDisplaysUpdatedEvent>();
  inputStatusChanged.stream.listen((event) {print ('event: ${event.runtimeType}');});
}

