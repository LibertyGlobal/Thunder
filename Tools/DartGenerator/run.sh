#!/bin/bash

# for i in json-defs/*; do 
#   python3 ParsePluginApi.py  $i xxx
# done 
# parallel --tag --keep-order --jobs 32 --no-notice  python3 ParsePluginApi.py  {} xxx ::: `find json-defs/ -type f`
# parallel --keep-order --jobs 32 --no-notice  python3 ParsePluginApi.py  {} xxx ::: `find json-defs/ -type f -name "*.json"`

mkdir out
for i in json-defs/*; do 
  echo $i
  python3 jsonrpc_to_dart.py -i $i -o out/`basename -s .json $i`.dart 
done  &>/dev/null
