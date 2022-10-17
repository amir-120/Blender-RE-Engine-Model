import struct
from typing import Literal


def ReadInt(array: list[int], pos: int = 0, size: int = 4, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    buffer: list[int] = []
    for i in range(size):
        buffer.append(array[pos + i])
    return int.from_bytes(buffer, endianness, signed=signed)


def ReadByte(array: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    buffer = [array[pos]]
    return int.from_bytes(buffer, endianness, signed=signed)


def ReadInt16(array: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    buffer = [array[pos], array[pos + 1]]
    return int.from_bytes(buffer, endianness, signed=signed)


def ReadInt32(array: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    buffer = [array[pos], array[pos + 1], array[pos + 2], array[pos + 3]]
    return int.from_bytes(buffer, endianness, signed=signed)


def ReadInt64(array: list[int], pos: int = 0, signed: bool = False, endianness: Literal["little", "big"] = "little") -> int:
    buffer = [array[pos], array[pos + 1], array[pos + 2], array[pos + 3], array[pos + 4], array[pos + 5], array[pos + 6],
             array[pos + 7]]
    return int.from_bytes(buffer, endianness, signed=signed)


def ReadHalfFloat(array: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    buffer = [array[pos], array[pos + 1]]
    byteFormat = 'e'
    if endianness == 'little':
        byteFormat = '<e'
    elif endianness == "big":
        byteFormat = '>e'
    return struct.unpack(byteFormat, bytes(buffer))[0]


def ReadFloat(array: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    buffer = [array[pos], array[pos + 1], array[pos + 2], array[pos + 3]]
    byteFormat = 'f'
    if endianness == 'little':
        byteFormat = '<f'
    elif endianness == "big":
        byteFormat = '>f'
    return struct.unpack(byteFormat, bytes(buffer))[0]


def ReadHalfDoubleFloat(array: list[int], pos: int = 0, endianness: Literal["little", "big"] = "little") -> float:
    buffer = [array[pos], array[pos + 1], array[pos + 2], array[pos + 3],
              array[pos + 4], array[pos + 5], array[pos + 6], array[pos + 7]]
    byteFormat = 'd'
    if endianness == 'little':
        byteFormat = '<d'
    elif endianness == "big":
        byteFormat = '>d'
    return struct.unpack(byteFormat, bytes(buffer))[0]


def ReadUTF8String(array: list[int], pos: int = 0, size: int = 0) -> str:
    buffer: list[int] = []
    index = 0
    while not array[pos + index] == 0:
        buffer.append(array[pos + index])
        index += 1
        if size != 0 and index == size:
            break
    return bytes(buffer).decode("utf-8")


def ReadUTF16String(array: list[int], pos: int = 0, size: int = 0) -> str:
    buffer: list[int] = []
    index = 0
    while not (array[pos + index] == 0 and array[pos + index + 1] == 0):
        buffer.append(array[pos + index])
        buffer.append(array[pos + index + 1])
        index += 2
        if size != 0 and index == size * 2:
            break
    return bytes(buffer).decode("utf-16")


ReadString = ReadUTF8String
ReadWString = ReadUTF16String
