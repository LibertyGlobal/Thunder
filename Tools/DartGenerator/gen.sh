#!/bin/bash -eu

outdir=./onemw_api
lib_main_file=$outdir/lib/onemw_api.dart

mkdir -p $outdir/lib/src

cp pubspec-onemw_api.yaml $outdir/pubspec.yaml 
cp README-onemw_api.md $outdir/README.md 

API_FILES="\
json-defs/LgiDisplaySettings.json \
json-defs/LgiHdmiCec.json \
json-defs/DisplayInfo.json \
json-defs/ActivityMonitor.json \
json-defs/PlayerInfo.json \
json-defs/SecurityAgent.json \
"
# API_FILES="\
# json-defs/LgiDisplaySettings.json \
# json-defs/LgiHdmiCec.json \
# "
# API_FILE=`find ./json-defs/ -name "*.json"`

for i in $API_FILES; do 
  echo $i
  python3 jsonrpc_to_dart.py -i $i -o $outdir/lib/src/`basename -s .json $i`.dart 
done 

rm -rf $lib_main_file
for f in `find $outdir/lib/src -name "*.dart" | grep -v "freeze" | grep -v "\.g\." `; do
  echo "export 'src/`basename $f`';" >> $outdir/lib/onemw_api.dart
done


pushd $outdir
echo ">>>>> dart pub get"
dart pub get

echo ">>>>> dart build_runner"
dart pub run build_runner build
popd

echo ">>>>> running sample app"
pushd sample-app/
dart pub get
dart main.dart
popd


# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/LgiDisplaySettings/LgiDisplaySettings.json
# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/LgiHdmiCec/LgiHdmiCec.json
# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/DisplayInfo/DisplayInfo.json
# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/ActivityMonitor/ActivityMonitor.json
# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/PlayerInfo/PlayerInfo.json
# https://github.com/LibertyGlobal/rdkservices/blob/lgi-main-20210920/SecurityAgent/SecurityAgent.json

