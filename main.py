import dataclasses
import google.protobuf.message

class FooProto(google.protobuf.message.Message):
    x: str

@dataclasses.dataclass
class Foo:
    x: str = ""

google.protobuf.message.non_existent()

proto_to_dataclass: Foo = FooProto()
dataclass_to_proto: FooProto = Foo()
