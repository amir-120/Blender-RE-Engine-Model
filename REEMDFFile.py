from .BinaryFunctions import *
from enum import IntEnum

class ShaderType(IntEnum):
    Standard = 0x0,
    Decal = 0x1,
    DecalWithMetallic = 0x2,
    DecalNRMR = 0x3,
    Transparent = 0x4,
    Distortion = 0x5,
    PrimitiveMesh = 0x6,
    PrimitiveSolidMesh = 0x7,
    Water = 0x8,
    SpeedTree = 0x9,
    GUI = 0xA,
    GUIMesh = 0xB,
    GUIMeshTransparent = 0xC,
    ExpensiveTransparent = 0xD,
    Forward = 0xE,
    RenderTarget = 0xF,
    PostProcess = 0x10,
    PrimitiveMaterial = 0x11,
    PrimitiveSolidMaterial = 0x12,
    SpineMaterial = 0x13,
    Max = 0x14


class MaterialFlags(IntEnum):
    BaseTwoSideEnable = 0x01 << 0
    BaseAlphaTestEnable = 0x01 << 1
    ShadowCastDisable = 0x01 << 2
    VertexShaderUsed = 0x01 << 3
    EmissiveUsed = 0x01 << 4
    TessellationEnable = 0x01 << 5
    EnableIgnoreDepth = 0x01 << 6
    AlphaMaskUsed = 0x01 << 7
    ForcedTwoSideEnable = 0x01 << 8
    TwoSideEnable = 0x01 << 9
    TessFactor = 0x01 << 10
    PhongFactor = 0x01 << 16
    RoughTransparentEnable = 0x01 << 24
    ForcedAlphaTestEnable = 0x01 << 25
    AlphaTestEnable = 0x01 << 26
    SSSProfileUsed = 0x01 << 27
    EnableStencilPriority = 0x01 << 28
    RequireDualQuaternion = 0x01 << 29
    PixelDepthOffsetUsed = 0x01 << 30
    NoRayTracing = 0x01 << 31


class PropertyInfo:
    def __init__(self, buffer: list[int], pos: int = 0, propertyBufferOffset: int = 0):
        self.nameOffset = ReadInt64(buffer, pos + 0)
        self.utf16NameMurmur3 = ReadInt32(buffer, pos + 8)
        self.ut8NameMurmur3 = ReadInt32(buffer, pos + 12)
        self.parameterCount = ReadInt32(buffer, pos + 16)
        self.propertyOffsetInBuffer = ReadInt32(buffer, pos + 20)

        # Calculated data
        self.name = ReadWString(buffer, self.nameOffset)

        self.parameters: list[float] = ReadFloat(buffer, propertyBufferOffset + self.propertyOffsetInBuffer,
                                                 self.parameterCount)

    size = 24


class TextureInfo:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.typeOffset = ReadInt64(buffer, pos + 0)
        self.utf16TypeMurmur3 = ReadInt32(buffer, pos + 8)
        self.utf8TypeMurmur3 = ReadInt32(buffer, pos + 12)
        self.filePathOffset = ReadInt64(buffer, pos + 16)

        # Calculated data
        self.type = ReadWString(buffer, self.typeOffset)
        self.filePath = ReadWString(buffer, self.filePathOffset)

    size = 24


class Material:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.nameOffset = ReadInt64(buffer, pos + 0)
        self.nameHash = ReadInt32(buffer, pos + 8)
        self.propertyBufferSize = ReadInt32(buffer, pos + 12)
        self.propertyCount = ReadInt32(buffer, pos + 16)
        self.textureCount = ReadInt32(buffer, pos + 20)
        self.shaderType = ReadInt32(buffer, pos + 24)
        self.flags = ReadInt32(buffer, pos + 28)
        self.propertyInfoOffset = ReadInt64(buffer, pos + 32)
        self.textureInfoOffset = ReadInt64(buffer, pos + 40)
        self.propertyBufferOffset = ReadInt64(buffer, pos + 48)
        self.masterMaterialFilePathOffset = ReadInt64(buffer, pos + 56)

        # Calculated data
        self.name = ReadWString(buffer, self.nameOffset)
        self.masterMaterialFilePath = ReadWString(buffer, self.masterMaterialFilePathOffset)

        self.textureInfo: list[TextureInfo] = [None] * self.textureCount
        for i in range(self.textureCount):
            self.textureInfo[i] = TextureInfo(buffer, self.textureInfoOffset + i * TextureInfo.size)

        self.properties: list[PropertyInfo] = [None] * self.propertyCount
        for i in range(self.propertyCount):
            self.properties[i] = PropertyInfo(buffer, self.propertyInfoOffset + i * PropertyInfo.size,
                                                self.propertyBufferOffset)

    size = 64


class Header:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.magic = ReadInt32(buffer, pos + 0)
        if self.magic != 0x0046444D:  # MDF
            raise RuntimeError("Wrong magic, file format not supported!")
        self.version = ReadInt16(buffer, pos + 4)
        self.materialCount = ReadInt16(buffer, pos + 6)
        self.reserved = ReadInt64(buffer, pos + 8)

    size = 16


class MDF:
    def __init__(self, fileBuffer: bytes or bytearray or list[int]):
        # Taking the file buffer in
        self.fileBuffer = fileBuffer

        # Read the main file header
        self.header = Header(self.fileBuffer, 0)

        # Read materials info
        self.materials: list[Material] = [None] * self.header.materialCount
        for i in range(self.header.materialCount):
            self.materials[i] = Material(fileBuffer, 16 + i * Material.size)

        self.__nameIdxMap: dict[str:int] = {}
        for idx in range(self.header.materialCount):
            self.__nameIdxMap.update({self.materials[idx].name : self.materials[idx]})

    def __getitem__(self, key) -> Material or None:
        if type(key) == int:
            if key < self.header.materialCount:
                return self.materials[key]
            else:
                return None
        elif type(key) == str:
            if key in self.__nameIdxMap.keys():
                return self.__nameIdxMap[key]
            else:
                return None
