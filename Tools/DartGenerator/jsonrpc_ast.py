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

from enum import Enum
from jinja2 import Environment, FileSystemLoader

class VoidType:
    def __init__(self):
        pass

    def __str__(self):
        return "void"

    def instanceResultCreationCode(self, result=None):
        return "/*void*/"

class SimpleType(object):
    def __init__(self, simple_type):
        self.simple_type = simple_type

    def __str__(self):
        dartmap = {
           "boolean":"bool",
           "integer":"int",
           "string":"String",
           "number":"double",
        }
        return f"{dartmap[self.simple_type]}"

    def instanceResultCreationCode(self, result=None):
        dartmap = {
           "boolean":f"{result} as bool",
           "integer":f"{result} is int ? {result} : int.parse({result})",
           "string":f"{result}",
           "number":f"double.parse({result})",
        }
        return dartmap[self.simple_type]

class ArrayType:
    def __init__(self, item_type):
        self.item_type = item_type
        pass

    def __str__(self):
        return f"List<{self.item_type}>"

    def remapDynamicListCode(self, dynamic_list):
        return f"({dynamic_list} as List).map( (item) => item as {self.item_type} ).toList()"

    def instanceResultCreationCode(self, result=None):
        return self.remapDynamicListCode(result)

class StructTypeUsage(Enum):
    REGULAR=1
    RESULT=2
    ARG=3
    EVENT=4

def reduceType(intype):
    if type(intype) is not StructType:
        return intype, None
    assert intype.usage == StructTypeUsage.RESULT

    exlcluded = ["success","error"]
    reduced_properties = [ p for p in intype.properties if p.name not in exlcluded ]

    if len(reduced_properties)==1:
        return reduced_properties[0].type, reduced_properties[0].name

    if len(reduced_properties)>1:
        reduced_type = StructType(intype.struct_name+"_reduced", intype.doc)
        reduced_type.usage = intype.usage
        reduced_type.required_properties = intype.required_properties
        for p in reduced_properties:
            reduced_type.addProperty(p)
        return reduced_type, None

    return VoidType(), None

class StructProperty:
    def __init__(self, name, ptype, doc):
        self.name = name.replace(" ","")
        self.type = ptype
        self.doc = doc

    # used in fromMap call during deserialization
    def castedArgForm(self, mapName):
        if type(self.type) is ArrayType:
            return self.type.remapDynamicListCode(f"{mapName}['{self.name}']")
        return f"{mapName}['{self.name}']"

class StructType:
    registered_struct_types = {}
    duplicated_struct_types = {}

    def __init__(self, struct_name, doc, defined_type = False):
        self.properties = []
        self.struct_name = struct_name
        self.usage = StructTypeUsage.REGULAR
        self.required_properties = None
        self.doc = doc

        self.reduced_type = None
        self.reduced_property_field_name = None
        self.json_serializable = False
        self.json_serializable_from_json = None

        if struct_name not in StructType.duplicated_struct_types:
            StructType.duplicated_struct_types[struct_name] = 0
        StructType.duplicated_struct_types[struct_name] += 1

        #todo duplication
        if not defined_type:
            if struct_name in StructType.registered_struct_types:
                print(f"fuckup: {struct_name} / cleanup needed")
                self.struct_name += str(StructType.duplicated_struct_types[struct_name] )

            # assert struct_name not in StructType.registered_struct_types
        StructType.registered_struct_types[self.struct_name] = self

    def setJsonSerializable(self, enable):
        self.json_serializable = enable
        self.json_serializable_from_json = f"{self.structConvertedName()}_fromJson"

    def makeResult(self):
        self.usage = StructTypeUsage.RESULT

        #do reduction here:
        self.reduced_type, self.reduced_property_field_name = reduceType(self)

    def makeArg(self):
        self.usage = StructTypeUsage.ARG

    def makeEventArg(self):
        self.usage = StructTypeUsage.EVENT

    @staticmethod
    def cleanStructs():
        StructType.registered_struct_types.clear()

    @staticmethod
    def dumpStructs(outfile):
        for s in StructType.registered_struct_types.values():
            if s.usage != StructTypeUsage.EVENT:
                s.dump(outfile)

    def addProperty(self, property):
        self.properties.append(property)

    def setRequiredProperties(self, required_properties):
        self.required_properties = required_properties


    def arrayTypeSimplifier(name):
        converted_name = name
        if converted_name.endswith('List') or converted_name.endswith('list'):
            converted_name = converted_name[:-4]

        arrayNamesMapping = { "paths":"path", "devices":"devices", "properties":"property", "containers":"container", "connecteddevices":"connectedDevice", "ranges":"range" }
        if converted_name.lower() in arrayNamesMapping:
            converted_name = arrayNamesMapping[converted_name.lower()]

        return converted_name

    def structConvertedName(self):
        # return self.struct_name
        is_result = False
        converted_name = self.struct_name
        if converted_name.endswith('_reduced'):
            converted_name = converted_name[:-8]

        if converted_name.endswith('_struct'):
            converted_name = converted_name[:-7]

        if converted_name.endswith('_result'):
            converted_name = converted_name[:-7]

        if self.usage == StructTypeUsage.ARG:
            converted_name += "Arg"

        if self.usage == StructTypeUsage.RESULT:
            if converted_name.startswith('get'):
                converted_name = converted_name[3:]

            converted_name += "Result"

        return converted_name[0].upper() + converted_name[1:]

    def __str__(self):
        if self.reduced_type:
            return str(self.reduced_type)
        return f"{self.structConvertedName()}"


    def instanceResultCreationCode(self, result=None):
        #return HdcpProfile.fromJson(result[{self.result.rtype.reduced_property_field_name}]);
        if self.reduced_property_field_name:
            assert self.reduced_type
            return self.reduced_type.instanceResultCreationCode(f"{result}['{self.reduced_property_field_name}']")
        elif self.reduced_type:
            return self.reduced_type.instanceResultCreationCode(result)
        else:
            # args = [f"result{rf}['{str(p.name)}']" for p in self.properties]
            # return f"{self}.fromMap({', '.join(args)})"
            return f"{self}.fromMap(result)"

    def getFreezeCtorArgs(self):
        assert self.usage == StructTypeUsage.EVENT
        ctor_args = []
        for p in self.properties:
            o = '' if self.required_properties and p.name in self.required_properties else '?'
            json_key = ''
            if type(p.type) is StructType and p.type.json_serializable:
                json_key = f"@JsonKey(fromJson: {p.type.json_serializable_from_json}, toJson: null)"
            ctor_args.append(f"{json_key}{str(p.type)+o} {str(p.name)}")

        return ", ".join(ctor_args)

class MethodArgument:
    def __init__(self, name, atype, doc):
        self.name = name.replace(" ","")
        self.type = atype
        self.doc = doc

class MethodResult:
    def __init__(self, rtype, doc):
        self.rtype = rtype
        self.doc = doc

# api property
class Property:
    def __init__(self, name, ptype, callsign, doc):
        self.name = name
        self.callsign = callsign
        self.type = ptype
        self.doc = doc.replace("\n","\n/// ")
        self.arguments = []

    def addEventArgument(self, argument):
        assert type(argument)is MethodArgument
        if type(argument.type) is StructType:
            argument.type.makeEventArg()
        self.arguments.append(argument)

class Event:
    def __init__(self, name, doc):
        self.name = name
        self.doc = doc.replace("\n","\n/// ")
        self.arguments = []

    def markJsonSerializableProperties(self):
        print(">>>>> markJsonSerializableProperties ", self.name);
        ctor_args = []
        assert len(self.arguments) == 1
        if type(self.arguments[0].type) is StructType:
            print(">>>>> markJsonSerializableProperties ", 1)
            for p in self.arguments[0].type.properties:
                if type(p.type) is StructType:
                    print(">>>>> markJsonSerializableProperties ", p.type);
                    p.type.setJsonSerializable(True)

    def addEventArgument(self, argument):
        assert type(argument)is MethodArgument
        if type(argument.type) is StructType:
            argument.type.makeEventArg()
        self.arguments.append(argument)

class Method:
    def __init__(self, name, callsign, doc):
        self.name = name
        self.callsign = callsign
        self.doc = doc.replace("\n","\n/// ")
        self.arguments = []
        self.result = None

    def addArgument(self, argument):
        assert type(argument)is MethodArgument
        add = True
        if type(argument.type) is StructType:
            argument.type.makeArg()
            #we don't need arguments which are object with 0 properties (todo how to remove this type from StructType.registered_struct_types ?)
            if len(argument.type.properties) == 0:
                add = False

        if add:
            self.arguments.append(argument)

    def addResult(self, result):
        assert type(result) is MethodResult
        self.result = result
        if type(self.result.rtype) is StructType:
            self.result.rtype.makeResult()

def method_args(args):
    return ", ".join([f"{str(a.type)} {str(a.name)}" for a in args])

def struct_ctor_args(args):
    return ", ".join([f"this.{str(p.name)}" for p in args])
            
def struct_ctor_args_from_map(args):
    return ", ".join([f"{p.castedArgForm('map')}" for p in args])

class APIClass:
    def __init__(self, name, doc, filename):
        self.name = name
        self.doc = doc
        self.methods = []
        self.events = []
        self.structs = []
        self.properties = []
        self.baseEventName = self.name.split('.')[-1] + 'BaseEvent'
        self.filename = filename
        self.classname = self.name.split('.')[-1]

    def addEvent(self, event):
        self.events.append(event)

    def addMethod(self, method):
        self.methods.append(method)

    def addProperty(self, property):
        self.properties.append(property)

    def generateCode(self, filename, outfile):
        for e in self.events:
            e.markJsonSerializableProperties()

        for s in StructType.registered_struct_types.values():
            if s.usage != StructTypeUsage.EVENT:
                if not s.reduced_type:
                    self.structs.append(s)

        file_loader = FileSystemLoader('templates')
        env = Environment(loader=file_loader)
        env.filters['any'] = any
        env.filters['method_args'] = method_args
        env.filters['struct_ctor_args'] = struct_ctor_args
        env.filters['struct_ctor_args_from_map'] = struct_ctor_args_from_map

        template = env.get_template('dartclass.jinja')
        output = template.render(api=self)

        print(output, file=outfile)

