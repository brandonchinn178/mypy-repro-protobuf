## Overview

In `main.py`, we have:

```py
class FooProto(google.protobuf.message.Message):
    x: str

@dataclasses.dataclass
class Foo:
    x: str = ""

google.protobuf.message.non_existent()

proto_to_dataclass: Foo = FooProto()
dataclass_to_proto: FooProto = Foo()
```

Expected behavior:
* `Module has no attribute "non_existent"`
* `Incompatible types in assignment` on `proto_to_dataclass`
* `Incompatible types in assignment` on `dataclass_to_proto`

Current behavior (mypy 1.18.1):
* If `types-protobuf` and `protobuf` are installed in the same venv as `mypy`: :white_check_mark:
* If `types-protobuf` and `protobuf` are installed in one venv separate from `mypy`: :white_check_mark:
* If `types-protobuf`, `protobuf`, and `mypy` are all installed in different venvs: :x:
    * `google` import is not found
    * `non_existent` does not error
    * `proto_to_dataclass` does not error

## Scenarios

### `venv-1`

Install everything in 1 venv.

Works as expected.

```console
$ ./run_repro.py venv-1
main.py:11: error: Module has no attribute "non_existent"  [attr-defined]
main.py:13: error: Incompatible types in assignment (expression has type "FooProto", variable has type "Foo")  [assignment]
main.py:14: error: Incompatible types in assignment (expression has type "Foo", variable has type "FooProto")  [assignment]
Found 3 errors in 1 file (checked 1 source file)
```

### `venv-2`

Install `mypy` in one venv and `protobuf`/`types-protobuf` in another.

Works as expected.

```console
$ ./run_repro.py venv-2
main.py:11: error: Module has no attribute "non_existent"  [attr-defined]
main.py:13: error: Incompatible types in assignment (expression has type "FooProto", variable has type "Foo")  [assignment]
main.py:14: error: Incompatible types in assignment (expression has type "Foo", variable has type "FooProto")  [assignment]
Found 3 errors in 1 file (checked 1 source file)
```

### `venv-3`

Install `mypy`, `protobuf`, and `types-protobuf` in separate venvs.

Does not work as expected.

```console
$ ./run_repro.py venv-3
main.py:2: error: Skipping analyzing "google": module is installed, but missing library stubs or py.typed marker  [import-untyped]
main.py:2: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
main.py:14: error: Incompatible types in assignment (expression has type "Foo", variable has type "FooProto")  [assignment]
Found 2 errors in 1 file (checked 1 source file)
```
