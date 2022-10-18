import struct
from typing import Literal


def ReadInt(array: list[int], pos: int = 0, size: int = 4, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    return int.from_bytes(array[pos:pos+size], endianness, signed=signed)


def ReadByte(buffer: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    return int.from_bytes(buffer[pos:pos+1], endianness, signed=signed)


def ReadInt16(buffer: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    return int.from_bytes(buffer[pos:pos+2], endianness, signed=signed)


def ReadInt32(buffer: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    return int.from_bytes(buffer[pos:pos+4], endianness, signed=signed)


def ReadInt64(buffer: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    return int.from_bytes(buffer[pos:pos+8], endianness, signed=signed)


def ReadHalfFloat(buffer: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    byteFormat = 'e'
    if endianness == 'little':
        byteFormat = '<e'
    elif endianness == "big":
        byteFormat = '>e'
    return struct.unpack(byteFormat, bytes(buffer[pos:pos+2]))[0]


def ReadFloat(buffer: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    byteFormat = 'f'
    if endianness == 'little':
        byteFormat = '<f'
    elif endianness == "big":
        byteFormat = '>f'
    return struct.unpack(byteFormat, bytes(buffer[pos:pos+4]))[0]


def ReadDouble(buffer: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    byteFormat = 'd'
    if endianness == 'little':
        byteFormat = '<d'
    elif endianness == "big":
        byteFormat = '>d'
    return struct.unpack(byteFormat, bytes(buffer[pos:pos+8]))[0]


def ReadUTF8String(buffer: list[int], pos: int = 0, size: int = 0) -> str:
    len = 0
    while not buffer[pos+len] == 0:
        len += 1
        if size != 0 and len == size:
            break
    return bytes(buffer[pos:pos+len]).decode("utf-8")


def ReadUTF16String(buffer: list[int], pos: int = 0, size: int = 0) -> str:
    len = 0
    while not (buffer[pos+len] == 0 and buffer[pos+len+1] == 0):
        len += 2
        if size != 0 and len == size:
            break
    return bytes(buffer[pos:pos+len]).decode("utf-16")


ReadString = ReadUTF8String
ReadWString = ReadUTF16String
