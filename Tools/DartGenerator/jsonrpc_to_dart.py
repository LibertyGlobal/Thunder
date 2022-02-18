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


#todo:
# - subscribe + stream management ( T should be BaseEvent )
# - debugs from dart functions (printing json api.verbose = true)
# - change: json_serializable -> freeze

# - disposal!
# - generate usage of each function
# - context in parser (file/method)
# - verbose debugs (parser)
# - verbose comments (in dart code) (parser)


import sys
import json
import argparse
from jsonrpc_ast import APIClass, Method, MethodResult, StructType, SimpleType, ArrayType, StructProperty, MethodArgument, Event, Property

program_options = None

################################################################################

g_json_filename = ""
g_method_name = ""
g_ws_api = None

def handleVoid(name, properties, defined_type=False):
    # print(f"void")
    return VoidType()

def handleSimpleType(name, type_description, defined_type=False):
    # print(f"{type_description['type']} {name}")
    return SimpleType(type_description['type'])

def handleArray(name, array_description, defined_type=False):
    # print(f"---> array: {array_description['type']} {name} {array_description}")

    item_type = None
    if 'type' in array_description['items']:
        it = array_description['items']['type']
        item_type = typehandlers[ it ](f"{name}_array", array_description['items'])
    elif '$ref' in array_description['items']:
        item_type,xxx = handleRefDefinition(f"{name}_unused_array", array_description['items'])

    # print(f"array: {type}[]")
    return ArrayType(item_type)

def handleObject(name, object_description, defined_type=False):
    struct_doc  = object_description['summary'] if 'summary' in object_description else None
    struct_type = StructType(f"{name}_struct", struct_doc, defined_type)

    # print(f"handleObject: {object_description} {name}")
    # print(f"xxstruct {name}" + "{")
    object_properties = object_description['properties']
    for property in object_properties:
        property_description = object_properties[property]
        if 'type' in property_description:
            # print(f"---> xxx {sys.argv[1]} {g_method_name} {property} : {property_description['type']}")
            property_doc  = property_description['summary'] if 'summary' in property_description else None
            property_type = typehandlers[ property_description['type'] ](property, property_description)
            struct_type.addProperty(StructProperty(property, property_type, property_doc))
        elif '$ref' in property_description:
            property_type, property_doc = handleRefDefinition(property, property_description)
            struct_type.addProperty(StructProperty(property, property_type, property_doc))
    # print("}")
    if 'required' in object_description:
        struct_type.setRequiredProperties(object_description['required'])

    return struct_type


typehandlers = {
'array':   handleArray,
'boolean': handleSimpleType,
'integer': handleSimpleType,
'number':  handleSimpleType,
'object':  handleObject,
'string':  handleSimpleType,
'null':    handleVoid,
}

def handleRefDefinition(name, params):
    path = params["$ref"].split('/')
    def_name = path[-1].replace('\"','')
    # print(f"ref: {g_ws_api['definitions'][def_name]}")

    def_root = g_ws_api
    for path_item in path:
        if path_item == "#":
            continue

        def_root = def_root[path_item]

    # print(f"ref: {g_method_name} {name} {params} {def_name} {path} {def_root}")
    def_properties = def_root

    assert 'type' in def_properties
    name = path[-1]
    doc = def_properties['summary'] if 'summary' in def_properties else ""
    return typehandlers[ def_properties['type'] ](name, def_properties, True), doc

def handleArgumentBundleObject(name, object_description):
    arguments = []

    # print(f"---> object: {g_method_name}:bundle {object_description}")
    object_properties = object_description['properties']
    for property in object_properties:
        if 'type' in object_properties[property]:
            # print(f"---> xxx {sys.argv[1]} {g_method_name} {property} : {object_properties[property]}")
            property_type = typehandlers[ object_properties[property]['type'] ](property, object_properties[property])
            property_doc = object_properties[property]['summary'] if 'summary' in object_properties[property] else ""
            arguments.append(MethodArgument(property, property_type, property_doc))
        elif '$ref' in object_properties[property]:
            # print(f"---> xxx/ref {sys.argv[1]} {g_method_name} {property} : {object_properties[property]}")
            property_type,property_doc = handleRefDefinition(property, object_properties[property])
            arguments.append(MethodArgument(property, property_type, property_doc))

    return arguments

def handleMethodParams(method_name, params_description):
    global g_method_name
    g_method_name = method_name
    arguments = []
    if 'type' in params_description:
        param_type = params_description['type'] 
        if param_type != "object":
            # print(f"non-object param: ---> {sys.argv[1]} {method_name} {params_description}")
            assert param_type in typehandlers.keys()
            name=f"{method_name}_unnamed_parameter"
            t = typehandlers[ param_type ](name, params_description)
            doc = params_description['summary'] if 'summary' in params_description else ""
            arguments.append(MethodArgument(name, t, doc))
        else:
            arguments = handleArgumentBundleObject("", params_description)
    elif '$ref' in params_description:
        name=f"{method_name}_unnamed_parameter_ref"
        t, doc = handleRefDefinition(name, params_description)
        arguments.append(MethodArgument(name, t, doc))
    else:
        print(f"---> {sys.argv[1]} {method_name}")
        print(f"error: no type: {params_description}")

    return arguments

def handlePropertyParams(property_name, params_description):
    global g_method_name
    g_method_name = property_name
    argument = None
    # print(f"handlePropertyParams param: ---> {property_name} {params_description}")
    if 'type' in params_description:
        param_type = params_description['type'] 
        # print(f"non-object param: ---> {property_name} {params_description}")
        assert param_type in typehandlers.keys()
        name=f"{property_name}Property"
        t = typehandlers[ param_type ](name, params_description)
        doc = params_description['summary'] if 'summary' in params_description else ""
        argument = MethodArgument(name, t, doc)
    elif '$ref' in params_description:
        name=f"{property_name}_unnamed_parameter_ref"
        t, doc = handleRefDefinition(name, params_description)
        argument = MethodArgument(name, t, doc)
    else:
        print(f"---> {sys.argv[1]} {property_name} / property")
        print(f"error: no type: {params_description}")

    return argument


def handleEventParams(event_name, params_description):
    global g_method_name
    g_method_name = event_name
    arguments = []
    if 'type' in params_description:
        param_type = params_description['type'] 
        # print(f"non-object param: ---> {event_name} {params_description}")
        assert param_type in typehandlers.keys()
        name=f"{event_name}Event"
        t = typehandlers[ param_type ](name, params_description)
        doc = params_description['summary'] if 'summary' in params_description else ""
        arguments.append(MethodArgument(name, t, doc))
    elif '$ref' in params_description:
        name=f"{event_name}_unnamed_parameter_ref"
        t, doc = handleRefDefinition(name, params_description)
        arguments.append(MethodArgument(name, t, doc))
    else:
        print(f"---> {sys.argv[1]} {event_name} / event")
        print(f"error: no type: {params_description}")

    return arguments


def handleResultBundleObject(name, result_description):
    # print(f"object: {g_method_name}:bundle {params}")
    method_result = StructType(name, None)

    object_properties = result_description['properties']
    for property in object_properties:
        if 'type' in object_properties[property]:
            # print(f"---> xxx {sys.argv[1]} {g_method_name} {property} : {object_properties[property]['type']}")
            property_type = typehandlers[ object_properties[property]['type'] ](property, object_properties[property])
            property_doc = object_properties[property]['summary'] if 'summary' in object_properties[property] else ""
            method_result.addProperty(StructProperty(property, property_type, property_doc))

        elif '$ref' in object_properties[property]:
            property_type, property_doc = handleRefDefinition(property, object_properties[property])
            method_result.addProperty(StructProperty(property, property_type, property_doc))

    if 'required' in result_description:
        method_result.setRequiredProperties(result_description['required'])

    return method_result

def handleMethodResult(method_name, result_description):
    global g_method_name
    g_method_name = method_name
    method_result = None
    if 'type' in result_description:
        if result_description['type'] != "object":
            method_result_doc = result_description['summary'] if 'summary' in result_description else None;
            method_result_type = typehandlers[ result_description['type'] ]("@result", result_description)
            method_result = MethodResult(method_result_type, method_result_doc)
            # print(f"---> {sys.argv[1]} {method_name}")
            # print(f"non-object result_description: {result_description}")
            # print("xxx-result: single-type")
        else:
            # print(f"xxx-result: {method_name} object {len(result_description['properties'])} {result_description}")
            method_result_doc = result_description['summary'] if 'summary' in result_description else None;
            method_result = MethodResult(handleResultBundleObject(f"{method_name}_result", result_description), method_result_doc)
    elif '$ref' in result_description:
        # print("xxx-result: ref")
        method_result_type, method_result_doc = handleRefDefinition(f"{method_name}_result", result_description)
        method_result = MethodResult(method_result_type, method_result_doc)
    else:
        print(f"---> {g_json_filename} {g_method_name}")
        print(f"error: result no type: {result_description}")

    return method_result

def buildMethods(apiclass, wsapi, json_filename, filename):
    if "methods" in wsapi:
        for method_name, method_def in wsapi['methods'].items():

            if apiclass.name+".1." in method_name:
                callsign = method_name
            else:
                callsign = apiclass.name+".1."+method_name

            # print(f"//---------------------------------------------------------- {sys.argv[1]}::{g_method_name}")
            method_doc = method_def['summary'] if 'summary' in method_def else ""
            method = Method(method_name, callsign, method_doc)
            if 'result' in method_def:
                result_description = method_def['result']
                if result_description:
                    method_result = handleMethodResult(method_name, result_description)
                    method.addResult(method_result)
                else:
                    assert False

            if 'params' in method_def:
                params_description = method_def['params']
                if params_description:
                    method_arguments = handleMethodParams(method_name, params_description)
                    for a in method_arguments:
                        method.addArgument(a)

            apiclass.addMethod(method)

def buildEvents(apiclass, wsapi, json_filename, filename):
    if 'events' in wsapi:
        for event_name, event_def in wsapi['events'].items():
            event_doc = event_def['summary'] if 'summary' in event_def else ""
            event = Event(event_name, event_doc)
            if 'params' in event_def:
                event_params_description = event_def['params']
                if event_params_description:
                    event_arguments = handleEventParams(event_name, event_params_description)
                    assert len(event_arguments) == 1
                    event.addEventArgument(event_arguments[0])
            else:
                #add empty type for event
                empty_event_type = StructType(f"{event_name}Event", None, False)
                event.addEventArgument(MethodArgument(f"{event_name}Event", empty_event_type, None))

            apiclass.addEvent(event)

def buildProperties(apiclass, wsapi, json_filename, filename):
    if 'properties' in wsapi:
        for property_name, property_def in wsapi['properties'].items():
            property_doc = property_def['summary'] if 'summary' in property_def else ""
            if 'params' in property_def:
                property_params_description = property_def['params']
                if property_params_description:
                    property_argument = handlePropertyParams(property_name, property_params_description)
                    callsign = apiclass.name+".1."+property_name
                    # print(f"---> {g_json_filename} {property_name} {property_argument.type}")
                    property = Property(property_name, property_argument.type, callsign, property_doc)
                    apiclass.addProperty(property)
            else:
                print(f"---> {g_json_filename} {property_name}")
                print(f"error: property no params: {property_def}")

def buildAST(wsapi, json_filename, filename):
    # print(f"//---------------------------------------------------------- {program_options.in_file}")
    classname = "XXXXX"
    if 'class' in wsapi['info']:
        classname = wsapi['info']['class']
    elif 'callsign' in wsapi['info']:
        classname = wsapi['info']['callsign']

    class_description = None
    if 'description' in wsapi['info']:
        class_description = wsapi['info']['description']

    apiclass = APIClass(classname, class_description, filename)

    global g_json_filename
    g_json_filename = json_filename
    global g_ws_api
    g_ws_api = wsapi

    buildMethods(apiclass, wsapi, json_filename, filename)
    buildEvents(apiclass, wsapi, json_filename, filename)
    buildProperties(apiclass, wsapi, json_filename, filename)

    return apiclass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='rdkservices dart API generator')
    arg_parser.add_argument('-i','--in', help="file to read json from", action="store", dest='in_file',  default='json-defs/DisplayInfo.json', type=str)
    arg_parser.add_argument('-o','--out', help="file to write generated dart code to", action="store", dest='out_file',  default=None, type=str)
    arg_parser.add_argument('-x', help="do not generate code", action="store_true", dest='skip_generation',  default=False)
    arg_parser.add_argument('-v', help="show ast items", action="store_true", dest='show_ast',  default=False)
    program_options = arg_parser.parse_args()

    wsapi = None
    with open(program_options.in_file) as f:
        wsapi = json.loads( f.read() )

    filename = "empty_filename"
    if program_options.out_file:
        outfile = open(program_options.out_file,"w+") 
        filename = program_options.out_file.split('/')[-1].split('.')[0]
    else:
        outfile = sys.stdout

    apiclass = buildAST(wsapi, program_options.in_file, filename)
    if not program_options.skip_generation:
        apiclass.generateCode(filename, outfile, program_options.show_ast)

    if program_options.out_file:
        f.close()
