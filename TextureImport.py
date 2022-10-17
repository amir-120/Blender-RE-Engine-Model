from ctypes import *
from typing import Literal
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
LoadDDS.argtypes = [c_char_p]
LoadDDS.restype = RawImage2D

LoadTEX = utils.LoadTEX
LoadTEX.argtypes = [c_char_p]
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
    def __init__(self, path: str):
        raw: RawImage2D = LoadTEX(path.encode("utf-8"))

        if raw.hresult < 0:
            raise RuntimeError("Failed to load the TEX file!")

        self.isLinear = raw.isLinear
        self.w = raw.width
        self.h = raw.height
        self.pixelStride = raw.pixelStride
        self.num_pixels = raw.width * raw.height
        self.size_in_bytes = self.num_pixels * raw.pixelStride
        self.data = bytearray(self.size_in_bytes)

        for i in range(self.size_in_bytes):
            self.data[i] = raw.pBuffer[i]

        if Free(addressof(raw.pBuffer.contents)) < 0:
            raise RuntimeError("Failed to free temporary image data buffer!")

        raw.pBuffer = None

    def GetPixelByIndex(self, index: int) -> tuple[int, int, int, int]:
        if index > self.num_pixels or index < 0:
            return -1, -1, -1, -1

        offset = index * self.pixelStride
        return (self.data[offset + 0],
                self.data[offset + 1],
                self.data[offset + 2],
                self.data[offset + 3])

    def GetPixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        index = y * self.w + x
        return self.GetPixelByIndex(index)

    def RegeneratePixels(self, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', vFlip: bool = False,
                         hFlip: bool = False):
        for y in range(self.h):
            for x in range(self.w):
                pixel = self.GetPixel(self.w - 1 - x if hFlip else x, self.h - 1 - y if vFlip else y)
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
                alpha = pixel[3]

                if mode == 'RGBA':
                    yield from (red, green, blue, alpha)
                elif mode == 'RGB':
                    yield from (red, green, blue)
                elif mode == 'R':
                    yield red
                elif mode == 'G':
                    yield green
                elif mode == 'B':
                    yield blue
                elif mode == 'A':
                    yield alpha

    def RegeneratePixelsF(self, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', vFlip: bool = False,
                          hFlip: bool = False):
        for y in range(self.h):
            for x in range(self.w):
                pixel = self.GetPixel(self.w - 1 - x if hFlip else x, self.h - 1 - y if vFlip else y)
                red = pixel[0] / 255.0
                green = pixel[1] / 255.0
                blue = pixel[2] / 255.0
                alpha = pixel[3] / 255.0

                if mode == 'RGBA':
                    yield from (red, green, blue, alpha)
                elif mode == 'RGB':
                    yield from (red, green, blue)
                elif mode == 'R':
                    yield red
                elif mode == 'G':
                    yield green
                elif mode == 'B':
                    yield blue
                elif mode == 'A':
                    yield alpha


class DDS:
    def __init__(self, path: str):
        raw: RawImage2D = LoadDDS(path.encode("utf-8"))

        if raw.hresult < 0:
            raise RuntimeError("Failed to load the DDS file!")

        self.isLinear = raw.isLinear
        self.w = raw.width
        self.h = raw.height
        self.pixelStride = raw.pixelStride
        self.num_pixels = raw.width * raw.height
        self.size_in_bytes = self.num_pixels * raw.pixelStride
        self.data = bytearray(self.size_in_bytes)

        for i in range(self.size_in_bytes):
            self.data[i] = raw.pBuffer[i]

        if Free(addressof(raw.pBuffer.contents)) < 0:
            raise RuntimeError("Failed to free temporary image data buffer!")

        raw.pBuffer = None

    def GetPixelByIndex(self, index: int) -> tuple[int, int, int, int]:
        if index > self.num_pixels or index < 0:
            return -1, -1, -1, -1

        offset = index * self.pixelStride
        return (self.data[offset + 0],
                self.data[offset + 1],
                self.data[offset + 2],
                self.data[offset + 3])

    def GetPixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        index = y * self.w + x
        return self.GetPixelByIndex(index)

    def RegeneratePixels(self, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', vFlip: bool = False,
                         hFlip: bool = False):
        for y in range(self.h):
            for x in range(self.w):
                pixel = self.GetPixel(self.w - 1 - x if hFlip else x, self.h - 1 - y if vFlip else y)
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
                alpha = pixel[3]

                if mode == 'RGBA':
                    yield from (red, green, blue, alpha)
                elif mode == 'RGB':
                    yield from (red, green, blue)
                elif mode == 'R':
                    yield red
                elif mode == 'G':
                    yield green
                elif mode == 'B':
                    yield blue
                elif mode == 'A':
                    yield alpha

    def RegeneratePixelsF(self, mode: Literal['RGBA', 'RGB', 'R', 'G', 'B', 'A'] = 'RGBA', vFlip: bool = False,
                          hFlip: bool = False):
        for y in range(self.h):
            for x in range(self.w):
                pixel = self.GetPixel(self.w - 1 - x if hFlip else x, self.h - 1 - y if vFlip else y)
                red = pixel[0] / 255.0
                green = pixel[1] / 255.0
                blue = pixel[2] / 255.0
                alpha = pixel[3] / 255.0

                if mode == 'RGBA':
                    yield from (red, green, blue, alpha)
                elif mode == 'RGB':
                    yield from (red, green, blue)
                elif mode == 'R':
                    yield red
                elif mode == 'G':
                    yield green
                elif mode == 'B':
                    yield blue
                elif mode == 'A':
                    yield alpha
