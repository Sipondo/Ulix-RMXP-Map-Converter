DEFAULT_ENCODING = "utf8"

import io
import re

from rubymarshal.classes import (
    Extended,
    Module,
    RubyObject,
    RubyString,
    Symbol,
    UserDef,
    UsrMarshal,
)
from rubymarshal.classes import registry as global_registry
from rubymarshal.constants import (
    TYPE_ARRAY,
    TYPE_BIGNUM,
    TYPE_CLASS,
    TYPE_DATA,
    TYPE_EXTENDED,
    TYPE_FALSE,
    TYPE_FIXNUM,
    TYPE_FLOAT,
    TYPE_HASH,
    TYPE_IVAR,
    TYPE_LINK,
    TYPE_MODULE,
    TYPE_NIL,
    TYPE_OBJECT,
    TYPE_REGEXP,
    TYPE_STRING,
    TYPE_STRUCT,
    TYPE_SYMBOL,
    TYPE_SYMLINK,
    TYPE_TRUE,
    TYPE_USERDEF,
    TYPE_USRMARSHAL,
)
from rubymarshal.utils import read_sbyte, read_ubyte, read_ushort

__author__ = "Matthieu Gallet"


# class RubyObject:
#     """Simple container class."""

#     __slots__ = ["typename", "values", "ivars"]

#     def __init__(self, typename, values, ivars=None):
#         self.typename = typename
#         self.values = {k.lstrip("@"): v for k, v in values.items()}

#     def __getattr__(self, x):
#         try:
#             return self.values[x]
#         except KeyError:
#             raise AttributeError(x) from None

#     def __setattr__(self, x, y):
#         try:
#             object.__setattr__(self, x, y)
#         except AttributeError:
#             if x in self.values:
#                 self.values[x] = y
#             else:
#                 raise AttributeError(x) from None

#     def __dir__(self):
#         return list(self.values.keys())

#     def __repr__(self):
#         return "#<%s:0x%08x>" % (self.typename, id(self))


class DecodeError(RuntimeError):
    pass


class ArrayDecodeError(DecodeError):
    pass


class SymbolDecodeError(DecodeError):
    pass


class SymlinkDecodeError(DecodeError):
    pass


class ObjlinkDecodeError(DecodeError):
    pass


true = True
false = False
nil = None


# class RubyString:
#     def __init__(self, s):
#         self.s = s
#         self.encoding = DEFAULT_ENCODING

#     def __str__(self):
#         return self.s.decode(self.encoding)

#     def __repr__(self):
#         return "RubyString(" + repr(self.s.decode(self.encoding)) + ")"


class Symbol:
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return ":" + self.s


class Reader:
    @staticmethod
    def register_load(name):
        def wrapper(f):
            nonlocal name
            Reader.REGISTERED[name] = f
            return f

        return wrapper

    REGISTERED = {}

    def __init__(self, fd, registry=None):
        self.symbols = []
        self.objects = []
        # print(fd)
        self.stream = fd
        self.fd = fd
        self.version = self.read_version()
        self.registry = registry or global_registry

    def read(self):
        MAP = {
            b"i": self.read_fixnum,
            b":": self.read_symbol,
            b";": self.read_symlink,
            b"@": self.read_objlink,
            b"[": self.read_array,
            b"T": self.read_true,
            b"F": self.read_false,
            b"0": self.read_null,
            b"o": self.read_object,
            b'"': self.read_bytes,
            b"I": self.read_ivard_object,
            b"u": self.read_userobject,
            b"{": self.read_hash,
            b"}": self.read_empty_hash,
            b"f": self.read_float,
            b"d": self.read_dataobject,
            b"/": self.read_regexp,
            b"S": self.read_struct,
            b"C": self.read_userclass,
            b"U": self.read_usermarshal,
            b"e": self.read_extended,
            b"L": self.read_bignum,
            b"c": self.read_class,
            b"m": self.read_module,
            b"M": self.read_classmodule,
        }

        i = self.stream.read(1)
        if i in MAP:
            # print(MAP[i].__name__)
            return MAP[i]()
        else:
            try:
                raise DecodeError(
                    self.stream.tell(), "Unknown ID %s" % (i.decode("ascii"))
                )
            except UnicodeDecodeError:
                raise DecodeError(self.stream.tell(), "Unknown ID \\x%02x" % (i[0]))

    def read_class(self):
        raise NotImplementedError("Type ID 'c' not implemented.")

    def read_module(self):
        raise NotImplementedError("Type ID 'm' not implemented.")

    def read_classmodule(self):
        raise NotImplementedError("Type ID 'M' not implemented.")

    def read_bignum(self):
        raise NotImplementedError("Type ID 'I' not implemented yet, TODO!")

    def read_extended(self):
        raise NotImplementedError("Type ID 'e' not implemented yet, TODO!")

    def read_usermarshal(self):
        raise NotImplementedError("Type ID 'U' not implemented yet, TODO!")

    def read_struct(self):
        raise NotImplementedError("Type ID 'S' not implemented yet, TODO!")

    def read_userclass(self):
        raise NotImplementedError("Type ID 'C' not implemented yet, TODO!")

    def read_dataobject(self):
        raise NotImplementedError("Type ID 'd' not implemented yet, TODO!")

    def read_regexp(self):
        raise NotImplementedError("Type ID '/' not implemented yet, TODO!")

    def read_float(self):
        self.objects.append(float(self.stream.read(self.read_fixnum())))
        return self.objects[-1]

    def read_object(self):
        self.objects.append(None)
        oid = len(self.objects) - 1

        typename = self.read().s
        n_of_vars = self.read_fixnum()
        vars = {}
        for _ in range(n_of_vars):
            name = self.read().s
            value = self.read()
            vars[name] = value
        obj = RubyObject(typename, vars)

        self.objects[oid] = obj
        return obj

    def read_bytes(self):
        self.objects.append(None)
        oid = len(self.objects) - 1

        obj = RubyString(self.stream.read(self.read_fixnum()))

        self.objects[oid] = obj
        return obj

    def read_ivard_object(self):
        obj = self.read()
        n_ivars = self.read_fixnum()
        ivars = {}
        for _ in range(n_ivars):
            name = self.read().s
            value = self.read()
            ivars[name] = value

        if isinstance(obj, RubyString):
            if "E" in ivars:
                if ivars["E"] is true:
                    obj.encoding = "utf8"
                else:
                    raise ValueError(
                        self.stream.tell(), "Unknown string :E encoding %s" % ivars["E"]
                    )

            elif "encoding" in ivars:
                # print(ivars["encoding"])
                obj.encoding = str(ivars["encoding"])

        else:
            obj.ivars = ivars

        return obj

    def read_true(self):
        return true

    def read_false(self):
        return false

    def read_null(self):
        return None

    def read_version(self):
        major = self.stream.read(1)[0]
        minor = self.stream.read(1)[0]
        return major, minor

    def read_array(self):
        length = self.read_fixnum()
        if length < 0:
            raise ArrayDecodeError(self.stream.tell(), "Array length is < 0")

        self.objects.append(None)
        oid = len(self.objects) - 1
        arr = [self.read() for _ in range(length)]
        self.objects[oid] = arr

        return arr

    def read_symlink(self):
        index = self.read_fixnum()
        if index < 0:
            raise SymlinkDecodeError(self.stream.tell(), "Symlink # is negative")
        return self.symbols[index]

    def read_objlink(self):
        index = self.read_fixnum()
        if index < 0:
            raise ObjlinkDecodeError(self.stream.tell(), "Objlink # is negative")
        try:
            return self.objects[index]
        except IndexError:
            raise ObjlinkDecodeError(
                self.stream.tell(), "Objlink %d out of range" % (index)
            ) from None

    def read_symbol(self):
        length = self.read_fixnum()
        if length < 0:
            raise SymbolDecodeError(self.stream.tell(), "Symbol length is negative")

        sym = Symbol(self.stream.read(length).decode("utf8"))
        self.symbols.append(sym)
        return sym

    def read_fixnum(self):
        stream = self.stream

        id_byte = stream.read(1)[0]
        if id_byte == 0x00:
            return 0

        elif id_byte == 0x01:
            X = stream.read(1)[0]
            return X

        elif id_byte == 0xFF:
            X = stream.read(1)[0]
            return -X - 1

        elif id_byte == 0xFF:
            X = stream.read(1)[0]
            return -X - 1

        elif id_byte == 0x02:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            return (Y << 8) + X

        elif id_byte == 0xFE:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            if X == 0 and Y == 0:
                return -65536
            return -((~((Y << 8) + X) + 1) & 65535)

        elif id_byte == 0x03:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            Z = stream.read(1)[0]
            return (Z << 16) + (Y << 8) + X

        elif id_byte == 0xFD:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            Z = stream.read(1)[0]
            if X == 0 and Y == 0 and Z == 0:
                return -16777215
            return -((~((Z << 16) + (Y << 8) + X) + 1) & 16777215)

        elif id_byte == 0x04:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            Z = stream.read(1)[0]
            W = stream.read(1)[0]
            return (W << 24) + (Z << 16) + (Y << 8) + X

        elif id_byte == 0xFC:
            X = stream.read(1)[0]
            Y = stream.read(1)[0]
            Z = stream.read(1)[0]
            W = stream.read(1)[0]
            if X == 0 and Y == 0 and Z == 0:
                return -4294967295
            return -((~((W << 24) + (Z << 16) + (Y << 8) + X) + 1) & 4294967295)

        if id_byte >= 0b10000000:
            id_byte = -(((~id_byte) + 1) & 255)

        if id_byte > 0:
            return id_byte - 5
        return id_byte + 5

    def read_empty_hash(self):
        self.objects.append({})
        return self.objects[-1]

    def read_hash(self):
        self.objects.append(None)
        oid = len(self.objects) - 1
        n_keyvalues = self.read_fixnum()
        obj = {}
        for _ in range(n_keyvalues):
            k = self.read()
            v = self.read()
            obj[k] = v
        self.objects[oid] = obj
        return obj

    def read_userobject(self):
        self.objects.append(None)
        oid = len(self.objects) - 1

        name = self.read().s
        dlen = self.read_fixnum()
        if name not in Reader.REGISTERED:
            raise DecodeError("Don't know how to decode class %s" % name)
        obj = Reader.REGISTERED[name](self.stream.read(dlen))

        obj.dlen = dlen
        self.objects[oid] = obj
        return obj


def load(fd, registry=None):
    assert fd.read(1) == b"\x04"
    assert fd.read(1) == b"\x08"

    loader = Reader(fd, registry=registry)
    return loader.read()


def loads(byte_text, registry=None):
    return load(io.BytesIO(byte_text), registry=registry)
