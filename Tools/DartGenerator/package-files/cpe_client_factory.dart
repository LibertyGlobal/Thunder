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

import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:json_rpc_2/json_rpc_2.dart';
import 'dart:io' show Platform;

enum CpeRpcService { thunder, rmfstreamer, lgias }

//copied from: horizon_shared/lib/src/hgo_platform/cpe_platform.dart
abstract class CpePlatform {
  static const String _localHost = 'localhost';
  static const String _cpeHostKey = 'CPE_HOST';

  static String get host {
    final envHost = Platform.environment[_cpeHostKey];
    if (envHost == null) {
      return _localHost;
    } else if (envHost.contains(':')) {
      //quick check for IPV6
      return '[$envHost]'; //IPV6 needs to be enclosed in []
    } else {
      return envHost;
    }
  }
}

class CpeRpcClient {
  late WebSocketChannel _socket;
  late Peer _client;
  static final Map<CpeRpcService, CpeRpcClient> _cache = <CpeRpcService, CpeRpcClient>{};

  static final Map<CpeRpcService, String> _rpcServiceUrl = <CpeRpcService, String>{
    CpeRpcService.thunder:      'ws://${CpePlatform.host}:9998/jsonrpc',
    CpeRpcService.rmfstreamer:  'ws://${CpePlatform.host}:9998/jsonrpc',
    CpeRpcService.lgias:        'ws://${CpePlatform.host}:10015'
  };

  CpeRpcClient._create(String url) {
    _socket = WebSocketChannel.connect( Uri.parse(url));
    _client = Peer( _socket.cast<String>() );
    _client.listen();
  }

  factory CpeRpcClient(CpeRpcService service) {
    if (_cache.containsKey(service)) {
      return _cache[service]!;
    } else {
      final url = _rpcServiceUrl[service]!;
      final cpeRpcClient = CpeRpcClient._create(url);
      _cache[service] = cpeRpcClient;
      return cpeRpcClient;
    }
  }

  Peer get client {
    return _client;
  }
}
