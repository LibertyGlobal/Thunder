#!/bin/bash -eu

# If not stated otherwise in this file or this component's LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2022 Liberty Global Service B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

function CamelCase_to_snake_case() {
  #copied from: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
  python3 -c 'import re,sys; print(re.sub(r"(?<!^)(?=[A-Z])", "_", sys.argv[1]).lower())' $1
}

outdir=./onemw-rdkservices-api/
lib_main_file=$outdir/lib/onemw_api.dart

mkdir -p $outdir/lib/src

cp ./package-files/pubspec-onemw_api.yaml $outdir/pubspec.yaml 
cp ./package-files/README-onemw_api.md    $outdir/README.md 
cp ./package-files/cpe_client_factory.dart  $outdir/lib/src/

RDKSERVICES_ROOT=../../../rdkservices

API_FILES="\
$RDKSERVICES_ROOT/LgiDisplaySettings/LgiDisplaySettings.json \
$RDKSERVICES_ROOT/LgiHdmiCec/LgiHdmiCec.json \
$RDKSERVICES_ROOT/DisplayInfo/DisplayInfo.json \
$RDKSERVICES_ROOT/ActivityMonitor/ActivityMonitor.json \
$RDKSERVICES_ROOT/PlayerInfo/PlayerInfo.json \
$RDKSERVICES_ROOT/SecurityAgent/SecurityAgent.json \
$RDKSERVICES_ROOT/XCast/XCast.json \
"

for i in $API_FILES; do 
  echo $i
  corefilename=`basename -s .json $i`.dart
  dartfilename=`CamelCase_to_snake_case $corefilename`
  dartfilepath=$outdir/lib/src/${dartfilename}
  python3 jsonrpc_to_dart.py -i $i -o  ${dartfilepath}
  dart format -l 120 ${dartfilepath}
done 

rm -rf $lib_main_file
for f in `find $outdir/lib/src -name "*.dart" | grep -v "freeze" | grep -v "\.g\." | grep -v "cpe_client_factory.dart"`; do
  echo "export 'src/`basename $f`';" >> $outdir/lib/onemw_api.dart
  dart format $outdir/lib/onemw_api.dart
done

pushd $outdir
echo ">>>>> dart pub get"
dart pub get

echo ">>>>> dart build_runner"
dart run build_runner build

echo ">>>>> dart analyze"
dart analyze

echo ">>>>> dart doc"
if [ -x $HOME/.pub-cache/bin/dartdoc ]; then
  $HOME/.pub-cache/bin/dartdoc
fi
popd

echo ">>>>> running sample app"
pushd sample-app/
dart pub get
dart main.dart
popd

