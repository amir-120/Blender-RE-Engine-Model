import struct
import numpy as np
from typing import Literal


def ReadInt(buffer: bytes, pos: int = 0, size: int = 4, signed: bool = False,
            endianness: Literal['little', 'big'] = "little") -> int:
    return int.from_bytes(buffer[pos:pos + size], endianness, signed=signed)


def ReadByte(buffer: bytes, pos: int = 0, count: int = 0, signed: bool = False,
             endianness: Literal['little', 'big'] = "little") -> int or np.ndarray:
    if count > 0:
        npType = np.byte if signed else np.ubyte
        dt = np.dtype(npType).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        return int.from_bytes(buffer[pos:pos+1], endianness, signed=signed)


def ReadInt16(buffer: bytes, pos: int = 0, count: int = 0, signed: bool = False,
              endianness: Literal['little', 'big'] = "little") -> int or np.ndarray:
    if count > 0:
        npType = np.short if signed else np.ushort
        dt = np.dtype(npType).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        return int.from_bytes(buffer[pos:pos+2], endianness, signed=signed)


def ReadInt32(buffer: bytes, pos: int = 0, count: int = 0, signed: bool = False,
              endianness: Literal['little', 'big'] = "little") -> int or np.ndarray:
    if count > 0:
        npType = np.intc if signed else np.uintc
        dt = np.dtype(npType).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        return int.from_bytes(buffer[pos:pos+4], endianness, signed=signed)


def ReadInt64(buffer: bytes, pos: int = 0, count: int = 0, signed: bool = False,
              endianness: Literal['little', 'big'] = "little") -> int or np.ndarray:
    if count > 0:
        npType = np.longlong if signed else np.ulonglong
        dt = np.dtype(npType).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        return int.from_bytes(buffer[pos:pos+8], endianness, signed=signed)


def ReadHalfFloat(buffer: bytes, pos: int = 0, count: int = 0,
                  endianness: Literal['little', 'big'] = "little") -> float or np.ndarray:
    if count > 0:
        dt = np.dtype(np.half).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        byteFormat = 'e'
        if endianness == 'little':
            byteFormat = '<e'
        elif endianness == "big":
            byteFormat = '>e'
        return struct.unpack(byteFormat, bytes(buffer[pos:pos+2]))[0]


def ReadFloat(buffer: bytes, pos: int = 0, count: int = 0,
              endianness: Literal['little', 'big'] = "little") -> float or np.ndarray:
    if count > 0:
        dt = np.dtype(np.single).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        byteFormat = 'f'
        if endianness == 'little':
            byteFormat = '<f'
        elif endianness == "big":
            byteFormat = '>f'
        return struct.unpack(byteFormat, bytes(buffer[pos:pos+4]))[0]


def ReadDouble(buffer: bytes, pos: int = 0, count: int = 0,
               endianness: Literal['little', 'big'] = "little") -> float or np.ndarray:
    if count > 0:
        dt = np.dtype(np.double).newbyteorder('>' if endianness == 'big' else '<')
        return np.frombuffer(buffer, dt, count, pos)
    else:
        byteFormat = 'd'
        if endianness == 'little':
            byteFormat = '<d'
        elif endianness == "big":
            byteFormat = '>d'
        return struct.unpack(byteFormat, bytes(buffer[pos:pos+8]))[0]


def ReadUTF8String(buffer: bytes, pos: int = 0, size: int = 0) -> str:
    strLen = 0
    while not buffer[int(pos+strLen)] == 0:
        strLen += 1
        if size != 0 and strLen == size:
            break
    return bytes(np.frombuffer(buffer, np.byte, strLen, pos)).decode('utf-8')
    #return bytes(buffer[pos:pos+len]).decode("utf-8")


def ReadUTF16String(buffer: bytes, pos: int = 0, size: int = 0) -> str:
    strLen = 0
    while not (buffer[pos+strLen] == 0 and buffer[pos+strLen+1] == 0):
        strLen += 2
        if size != 0 and strLen == size:
            break
    return bytes(np.frombuffer(buffer, np.byte, strLen, pos)).decode('utf-16')
    #return bytes(buffer[pos:pos+len]).decode("utf-16")


ReadString = ReadUTF8String
ReadWString = ReadUTF16String
