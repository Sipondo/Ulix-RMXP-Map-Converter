import rubymarshal as rb
import os


def readruby(fname):
    with open(fname, "rb") as f:
        reader = rb.reader.Reader(f)
        return reader.read()


def writeruby(rubyobj, fname):
    with open("temp", "wb") as f:
        writer = rb.writer.Writer(f)
        writer.write(rubyobj)

    with open("temp", "rb") as i:
        rest = i.readlines()

    os.remove("temp")

    with open(fname, "wb") as o:
        first = (
            b"\x04\x08o:\rRPG::Map\x10:\t@bgmo:\x13RPG::AudioFile\x08:\x0c@volumeii:\n"
        )
        writer = o.writelines([first] + rest[1:])
