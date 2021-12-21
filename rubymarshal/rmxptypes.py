import struct
from .reader import Reader
import numpy as np

# from .writer import Writer


class RMXPDecodeError(RuntimeError):
    pass


class Tone:
    def __init__(self, r, g, b, gr):
        self.r = r
        self.g = g
        self.b = b
        self.gr = gr

    @Reader.register_load("Tone")
    def _load(data):
        return Tone(*struct.unpack("<dddd", data))


class Color:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @Reader.register_load("Color")
    def _load(data):
        return Color(*struct.unpack("<dddd", data))


class Table:

    __slots__ = ["dim", "data", "w", "h", "d", "size", "dlen"]

    def __init__(self, dim, w, h, d, size):
        self.data = [0 for _ in range(w * h * d)]
        self.dim = dim
        self.w = w
        self.h = h
        self.d = d
        self.size = size

    def __getitem__(self, xyz):
        x, y, z = xyz
        return self.data[z * self.w * self.h + y * self.w + x]

    def __setitem__(self, xyz, v):
        x, y, z = xyz
        self.data[z * self.w * self.h + y * self.w + x] = v

    def from_array(self, array):
        for a in range(len(array)):
            for b in range(len(array[a])):
                for c in range(len(array[a, b])):
                    self[c, b, a] = array[a, b, c]

    def to_array(self):
        return np.array(self.data).reshape((self.d, self.h, self.w))

    def tobytes(self):
        dim = self.dim
        w = self.w
        h = self.h
        d = self.d
        size = self.size
        data = self.data

        b = struct.pack("<IIIII", dim, w, h, d, size)
        b += struct.pack("<" + "H" * w * h * d, *data)
        return b

    @Reader.register_load("Table")
    def frombytes(b):
        dim, w, h, d, size = struct.unpack("<IIIII", b[:20])

        # print(dim, w, h, d, size)
        if w * h * d != size:
            raise RMXPDecodeError("Table size doesn't match w * h * d")
        obj = Table(dim, w, h, d, size)
        obj.data = list(struct.unpack("<" + "H" * w * h * d, b[20:]))
        # print(obj.data)
        return obj

    # @Writer.register_load("Table")
    # def frombytes(b):
    #     dim, w, h, d, size = struct.unpack("<IIIII", b[:20])
    #     if w * h * d != size:
    #         raise RMXPDecodeError("Table size doesn't match w * h * d")
    #     obj = Table(w, h, d)
    #     obj.data = struct.unpack("<" + "H" * w * h * d, b[20:])
    #     return obj
