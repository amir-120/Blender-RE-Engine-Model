from ctypes import *
from typing import Literal
import struct
import numpy
import os


class RawImage2D(Structure):
    _fields_ = [("hresult", c_int32),
                ("isLinear", c_bool),
                ("width", c_size_t),
                ("height", c_size_t),
                ("pixelStride", c_size_t),
                ("pBuffer", POINTER(c_ubyte))]


utils = cdll.LoadLibrary(os.path.dirname(__file__) + R"\Texture.dll")

LoadDDS = utils.LoadDDS
# RawImage2D LoadDDS(const char* filePath, uint8_t channels, bool floatMode, bool hFlip, bool vFlip)
LoadDDS.argtypes = [c_char_p, c_uint8, c_bool, c_bool, c_bool]
LoadDDS.restype = RawImage2D

LoadTEX = utils.LoadTEX
# RawImage2D LoadTEX(const char* filePath, uint8_t channels, bool floatMode, bool hFlip, bool vFlip)
LoadTEX.argtypes = [c_char_p, c_uint8, c_bool, c_bool, c_bool]
LoadTEX.restype = RawImage2D

Free = utils.Free
Free.argtypes = [c_void_p]
Free.restype = c_uint32


def IsNormalMap(reTexType: str) -> bool:
    if reTexType in IsNormalMap.nrmrList:
        return True

    return False
IsNormalMap.nrmrList = [
    'NormalRoughnessMap', 'AppearNormalRoughnessMap', 'NormalMap', 'FlowNormalRoughnessMap', 'BlendNormalMap',
    'TransNormalNoiseMap', 'ChestVortex_NormalNoiseMap', 'Statue_NormalRoughnessMap', 'Liquid_NormalRoughnessMap',
    'LocalNormalMap', 'TransNormalRoughnessMap', 'BlendNormalRoughnessMap', 'MatA_NormalRoughnessMap',
    'MatB_NormalRoughnessMap', 'CavityNormalAlphaMap', 'NormalRoughness', 'NormalRoughness_Gauge',
    'AshNormalRoughnessMap', 'MaterialNormalRoughnessMap', 'NormalRoughnessMapArray', 'NormalAlphaMap_Small',
    'NormalAlphaMap_Middle', 'NormalAlphaMap_Large', 'WaterNormalRoughnessMap', 'FlowMap_NormalRoughnessMap',
    'Ice_NormalRoughnessMap', 'LimLight_FakeNormalMap', 'WrinkleNormalMap1', 'WrinkleNormalMap2', 'WrinkleNormalMap3',
    'Rec_Injury_NormalMap', 'Distortion_NormalMap', 'Bike_NormalMap', 'Mark_NormalMap', 'Trans_NormalRoughnessMap',
    'Detail_NormalRoughnessMap', 'TransMaterial_NormalRoughnessMap', 'Blend_NormalRoughnessMap', 'NormalAlphaMap',
    'NormalDisplacementMap'
    ]


class TEX:
    def __init__(self, path: str, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', floatMode: bool = False,
                 hFlip: bool = False, vFlip: bool = False):
        modeVal: int = 0

        if mode == 'RGBA':
            modeVal = 0b1111
        elif mode == 'RGB':
            modeVal = 0b1110
        elif mode == 'R':
            modeVal = 0b1000
        elif mode == 'G':
            modeVal = 0b0100
        elif mode == 'B':
            modeVal = 0b0010
        elif mode == 'A':
            modeVal = 0b0001

        if modeVal == 0:
            raise RuntimeError("Mode not supported!")

        self.__raw: RawImage2D = LoadTEX(path.encode("utf-8"), modeVal, floatMode, hFlip, vFlip)

        if self.__raw.hresult < 0:
            raise RuntimeError(f"Failed to load the TEX file! HResult = {hex(self.__raw.hresult)}")

        self.__isLinear = self.__raw.isLinear
        self.__width = self.__raw.width
        self.__height = self.__raw.height
        self.__pixelStride = self.__raw.pixelStride
        self.__numPixels = self.__raw.width * self.__raw.height
        self.__sizeInBytes = self.__numPixels * self.__raw.pixelStride
        self.__buffer = []

        if floatMode:
            numFloats = self.__sizeInBytes // 4
            cBuffer = cast(self.__raw.pBuffer, POINTER(c_float * numFloats))[0]
            self.__buffer = numpy.frombuffer(cBuffer, numpy.float32)
        else:
            cBuffer = cast(self.__raw.pBuffer, POINTER(c_ubyte * self.__sizeInBytes))[0]
            self.__buffer = numpy.frombuffer(cBuffer, numpy.uint8)

    def __del__(self):
        if Free(addressof(self.__raw.pBuffer.contents)) < 0:
            raise RuntimeError("Failed to free temporary image data buffer!")

        self.__raw.pBuffer = None

    @property
    def isLinear(self):
        return self.__isLinear

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def pixelStride(self):
        return self.__pixelStride

    @property
    def numPixels(self):
        return self.__numPixels

    @property
    def sizeInBytes(self):
        return self.__sizeInBytes

    @property
    def buffer(self):
        return self.__buffer

class DDS:
    def __init__(self, path: str, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', floatMode: bool = False,
                 hFlip: bool = False, vFlip: bool = False):
        modeVal: int = 0

        if mode == 'RGBA':
            modeVal = 0b1111
        elif mode == 'RGB':
            modeVal = 0b1110
        elif mode == 'R':
            modeVal = 0b1000
        elif mode == 'G':
            modeVal = 0b0100
        elif mode == 'B':
            modeVal = 0b0010
        elif mode == 'A':
            modeVal = 0b0001

        if modeVal == 0:
            raise RuntimeError("Mode not supported!")

        self.__raw: RawImage2D = LoadDDS(path.encode("utf-8"), modeVal, floatMode, hFlip, vFlip)

        if self.__raw.hresult < 0:
            raise RuntimeError(f"Failed to load the DDS file! HResult = {hex(self.__raw.hresult)}")

        self.__isLinear = self.__raw.isLinear
        self.__width = self.__raw.width
        self.__height = self.__raw.height
        self.__pixelStride = self.__raw.pixelStride
        self.__numPixels = self.__raw.width * self.__raw.height
        self.__sizeInBytes = self.__numPixels * self.__raw.pixelStride
        self.__buffer = []

        if floatMode:
            numFloats = self.__sizeInBytes // 4
            cBuffer = cast(self.__raw.pBuffer, POINTER(c_float * numFloats))[0]
            self.__buffer = numpy.frombuffer(cBuffer, numpy.float32)
        else:
            cBuffer = cast(self.__raw.pBuffer, POINTER(c_ubyte * self.__sizeInBytes))[0]
            self.__buffer = numpy.frombuffer(cBuffer, numpy.uint8)

    def __del__(self):
        if Free(addressof(self.__raw.pBuffer.contents)) < 0:
            raise RuntimeError("Failed to free temporary image data buffer!")

        self.__raw.pBuffer = None

    @property
    def isLinear(self):
        return self.__isLinear

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def pixelStride(self):
        return self.__pixelStride

    @property
    def numPixels(self):
        return self.__numPixels

    @property
    def sizeInBytes(self):
        return self.__sizeInBytes

    @property
    def buffer(self):
        return self.__buffer
