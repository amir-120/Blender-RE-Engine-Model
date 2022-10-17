from .BinaryFunctions import *
from enum import Enum

class Header:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.magic = ReadInt32(buffer, pos + 0)
        if self.magic != 0x4853454D:  # MESH
            raise RuntimeError("Wrong magic, file format not supported!")
        self.version = ReadInt32(buffer, pos + 4)
        self.fileSize = ReadInt32(buffer, pos + 8)
        self.lodGroupHash = ReadInt32(buffer, pos + 12)
        self.flag = ReadByte(buffer, pos + 16)
        self.solvedOffset = ReadByte(buffer, pos + 17)
        self.nameTableNodeCount = ReadInt16(buffer, pos + 18)
        self.padding1 = ReadInt32(buffer, pos + 20)
        self.lodDescriptionsOffset = ReadInt64(buffer, pos + 24)
        self.shadowLODDescriptionsOffset = ReadInt64(buffer, pos + 32)
        self.occluderMeshOffset = ReadInt64(buffer, pos + 40)
        self.armatureHeaderOffset = ReadInt64(buffer, pos + 48)
        self.topologoyOffset = ReadInt64(buffer, pos + 56)
        self.bsHeader = ReadInt64(buffer, pos + 64)
        self.boundingBoxHeaderOffset = ReadInt64(buffer, pos + 72)
        self.vertexBufferHeaderOffset = ReadInt64(buffer, pos + 80)
        self.padding2 = ReadInt64(buffer, pos + 88)
        self.materialNameIndexBufferOffset = ReadInt64(buffer, pos + 96)
        self.boneNameIndexBufferOffset = ReadInt64(buffer, pos + 104)
        self.bsIndexBufferOffset = ReadInt64(buffer, pos + 112)
        self.nameTableOffset = ReadInt64(buffer, pos + 120)

    size = 128

class VertexPosition:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.x = ReadFloat(buffer, pos + 0)
        self.y = ReadFloat(buffer, pos + 4)
        self.z = ReadFloat(buffer, pos + 8)

    size = 12


class Face:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.indices: list[int] = []
        self.indices.append(ReadInt16(buffer, pos + 0))
        self.indices.append(ReadInt16(buffer, pos + 2))
        self.indices.append(ReadInt16(buffer, pos + 4))

    size = 6


class NormalAndTangent:
    def __init__(self, buffer: list[int], pos: int = 0):

        self.normalX = self.__NormalizeByte(ReadByte(buffer, pos + 0, signed=True))
        self.normalY = self.__NormalizeByte(ReadByte(buffer, pos + 1, signed=True))
        self.normalZ = self.__NormalizeByte(ReadByte(buffer, pos + 2, signed=True))
        self.normalW = self.__NormalizeByte(ReadByte(buffer, pos + 3, signed=True))
        self.tangentX = self.__NormalizeByte(ReadByte(buffer, pos + 4, signed=True))
        self.tangentY = self.__NormalizeByte(ReadByte(buffer, pos + 5, signed=True))
        self.tangentZ = self.__NormalizeByte(ReadByte(buffer, pos + 6, signed=True))
        self.tangentW = self.__NormalizeByte(ReadByte(buffer, pos + 7, signed=True))

    @staticmethod
    def __NormalizeByte(byte: int) -> float:
        return byte / (128.0 if byte & 0b10000000 else 127.0)

    size = 8


class UV:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.u = 1.0 - ReadHalfFloat(buffer, pos + 0)
        self.v = 1.0 - ReadHalfFloat(buffer, pos + 2)

    size = 4


class SkinWeights:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.indices: list[int] = []
        self.indices.append(ReadByte(buffer, pos + 0))
        self.indices.append(ReadByte(buffer, pos + 1))
        self.indices.append(ReadByte(buffer, pos + 2))
        self.indices.append(ReadByte(buffer, pos + 3))
        self.indices.append(ReadByte(buffer, pos + 4))
        self.indices.append(ReadByte(buffer, pos + 5))
        self.indices.append(ReadByte(buffer, pos + 6))
        self.indices.append(ReadByte(buffer, pos + 7))

        self.weights: list[float] = []
        self.weights.append(ReadByte(buffer, pos + 8) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 9) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 10) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 11) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 12) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 13) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 14) / 255.0)
        self.weights.append(ReadByte(buffer, pos + 15) / 255.0)

    size = 16

class BoneTransform:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.transformMatrix: list[list[float]] = [[ReadFloat(buffer, pos + 0), ReadFloat(buffer, pos + 4), ReadFloat(buffer, pos + 8), ReadFloat(buffer, pos + 12)],
                                                   [ReadFloat(buffer, pos + 16), ReadFloat(buffer, pos + 20), ReadFloat(buffer, pos + 24), ReadFloat(buffer, pos + 28)],
                                                   [ReadFloat(buffer, pos + 32), ReadFloat(buffer, pos + 36), ReadFloat(buffer, pos + 40), ReadFloat(buffer, pos + 48)],
                                                   [ReadFloat(buffer, pos + 48), ReadFloat(buffer, pos + 52), ReadFloat(buffer, pos + 56), ReadFloat(buffer, pos + 60)]]

    size = 64

class BoneHierarchy:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.index = ReadInt16(buffer, pos + 0, signed=True)
        self.parent = ReadInt16(buffer, pos + 2, signed=True)
        self.nextSibling = ReadInt16(buffer, pos + 4, signed=True)
        self.nextChild = ReadInt16(buffer, pos + 6, signed=True)
        self.cousin = ReadInt16(buffer, pos + 8, signed=True)
        self.ukn1 = ReadInt16(buffer, pos + 10, signed=True)
        self.ukn2 = ReadInt16(buffer, pos + 12, signed=True)
        self.ukn3 = ReadInt16(buffer, pos + 14, signed=True)

    size = 16


class ArmatureHeader:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.boneCount = ReadInt32(buffer, pos + 0)
        self.skinMapSize = ReadInt32(buffer, pos + 4)
        self.ukn1 = ReadInt64(buffer, pos + 8)
        self.boneHierarchyTableOffset = ReadInt32(buffer, pos + 16)
        self.localBoneTransformsTableOffset = ReadInt32(buffer, pos + 24)
        self.globalBoneTransformsTableOffset = ReadInt32(buffer, pos + 32)
        self.inverseGlobalBoneTransformsTableOffset = ReadInt32(buffer, pos + 40)

        # Calculated data
        self.skinBoneMap: list[int] = [] # Index of the bone index in the BoneMapIndices
        self.boneHierArchy: list[BoneHierarchy] = []
        self.localBoneTransforms: list[BoneTransform] = []
        self.globalBoneTransforms: list[BoneTransform] = []
        self.inverseGlobalTransfroms: list[BoneTransform] = []

        for i in range(self.skinMapSize):
            self.skinBoneMap.append(ReadInt16(buffer, pos + self.size + i * 2))

        for i in range(self.boneCount):
            self.boneHierArchy.append(BoneHierarchy(buffer, self.boneHierarchyTableOffset + i * BoneHierarchy.size))
            self.localBoneTransforms.append(BoneTransform(buffer, self.localBoneTransformsTableOffset + i * BoneTransform.size))
            self.globalBoneTransforms.append(BoneTransform(buffer, self.globalBoneTransformsTableOffset + i * BoneTransform.size))
            self.inverseGlobalTransfroms.append(BoneTransform(buffer, self.inverseGlobalBoneTransformsTableOffset + i * BoneTransform.size))

    size = 48


class VertexElementHeader:
    class ElementType(Enum):
        VertexPosition = 0
        NormalsTangents = 1
        UV0 = 2
        UV1 = 3
        BoneInfo = 4

    def __init__(self, buffer: list[int], pos: int = 0):
        self.elementType = self.ElementType(ReadInt16(buffer, pos + 0))
        self.bytesPerVertex = ReadInt16(buffer, pos + 2)
        self.offsetInVertexBuffer = ReadInt32(buffer, pos + 4)

    size = 8


class GeometryBuffersHeader:
    def __init__(self, buffer: list[int], pos: int = 0, fileBuffer: list[int] = -1):
        self.vertexElementHeadersOffset = ReadInt64(buffer, pos + 0)
        self.vertexBufferOffset = ReadInt64(buffer, pos + 8)
        self.faceIndexBufferOffset = ReadInt64(buffer, pos + 16)
        self.vertexBufferSize = ReadInt32(buffer, pos + 24)
        self.faceIndexBufferSize = ReadInt32(buffer, pos + 28)
        self.vertexElementCount = [ReadInt16(buffer, pos + 32), ReadInt16(buffer, pos + 34)]
        self.ukn = ReadInt64(buffer, pos + 36)
        self.blendShapesOffset = ReadInt32(buffer, pos + 44, signed=True)

        # Calculated data
        self.fileBuffer = fileBuffer
        self.vertexElementHeaders: list[VertexElementHeader] = []
        for i in range(self.vertexElementCount[1]):
            self.vertexElementHeaders.append(VertexElementHeader(buffer, self.vertexElementHeadersOffset + i * VertexElementHeader.size))

    size = 48


class SubMesh:
    def __init__(self, buffer: list[int], pos: int = 0, vertexBufferHeader: GeometryBuffersHeader = -1, vertexCount: int = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False, preview: bool = False):
        self.materialID = ReadInt32(buffer, pos + 0)
        self.faceIndexCount = ReadInt32(buffer, pos + 4)
        self.faceIndicesBefore = ReadInt32(buffer, pos + 8)
        self.verticesBefore = ReadInt32(buffer, pos + 12)

        # Calculated data
        self.vertexCount = vertexCount

        if preview:
            return

        if vertexBufferHeader == -1 or vertexBufferHeader.fileBuffer == -1:
            return

        self.faces: list[Face] = []
        self.vertexBuffer: list[VertexPosition] = []
        self.normalsTangents: list[NormalAndTangent] = []
        self.uv0s: list[UV] = []
        self.uv1s: list[UV] = []
        self.boneInfo: list[SkinWeights] = []

        self.faceIndexBufferRange: tuple[int, int]
        self.faceIndexBufferRange = (faceBufferOffset + vertexBufferHeader.faceIndexBufferOffset + self.faceIndicesBefore * 2, faceBufferOffset + vertexBufferHeader.faceIndexBufferOffset + self.faceIndicesBefore * 2 + self.faceIndexCount * 2)

        for i in range(self.faceIndexCount // 3):
            self.faces.append(Face(vertexBufferHeader.fileBuffer, self.faceIndexBufferRange[0] + i * Face.size))

        self.elemIdxRange: tuple[int, int]
        if isShadowGeo:
            self.elemIdxRange = (vertexBufferHeader.vertexElementCount[0] - 1, vertexBufferHeader.vertexElementCount[1])
        else:
            self.elemIdxRange = (0, vertexBufferHeader.vertexElementCount[0])

        self.elementOffsets: list[int] = []
        for i in range(self.elemIdxRange[0], self.elemIdxRange[1]):
            elementInfo = vertexBufferHeader.vertexElementHeaders[i]
            self.elementOffsets.append(vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer)
            match elementInfo.elementType:
                case elementInfo.ElementType.VertexPosition:
                    for j in range(self.vertexCount):
                        self.vertexBuffer.append(VertexPosition(vertexBufferHeader.fileBuffer, vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer + self.verticesBefore * elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex))

                case elementInfo.ElementType.NormalsTangents:
                    for j in range(self.vertexCount):
                        self.normalsTangents.append(NormalAndTangent(vertexBufferHeader.fileBuffer, vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer + self.verticesBefore * elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex))

                case elementInfo.ElementType.UV0:
                    for j in range(self.vertexCount):
                        self.uv0s.append(UV(vertexBufferHeader.fileBuffer, vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer + self.verticesBefore * elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex))

                case elementInfo.ElementType.UV1:
                    for j in range(self.vertexCount):
                        self.uv1s.append(UV(vertexBufferHeader.fileBuffer, vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer + self.verticesBefore * elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex))

                case elementInfo.ElementType.BoneInfo:
                    for j in range(self.vertexCount):
                        self.boneInfo.append(SkinWeights(vertexBufferHeader.fileBuffer, vertexBufferHeader.vertexBufferOffset + elementInfo.offsetInVertexBuffer + self.verticesBefore * elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex))

    size = 16

    def GetVertexBuffer(self) -> list[tuple[float, float, float]]:
        retVertexBuffer: list[tuple[float, float, float]] = []

        for i in range(self.vertexCount):
            retVertexBuffer.append((self.vertexBuffer[i].x, self.vertexBuffer[i].y, self.vertexBuffer[i].z))
        return retVertexBuffer

    def GetFaceIndexBuffer(self) -> list[tuple[int, int, int]]:
        retFaceIndexBuffer: list[tuple[int, int, int]] = []

        for i in range(self.faceIndexCount // 3):
            retFaceIndexBuffer.append((self.faces[i].indices[0], self.faces[i].indices[1], self.faces[i].indices[2]))
        return retFaceIndexBuffer



class Mainmesh:
    def __init__(self, buffer: list[int], pos: int = 0, vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.groupID = ReadByte(buffer, pos + 0)
        self.submeshCount = ReadByte(buffer, pos + 1)
        self.ukn1: list[int] = [ReadByte(buffer, pos + 2), ReadByte(buffer, pos + 3)]
        self.ukn2 = ReadInt32(buffer, pos + 4)
        self.mainmeshVertexCount = ReadInt32(buffer, pos + 8)
        self.mainmeshFaceIndexCount = ReadInt32(buffer, pos + 12)

        # Calculated data
        Mainmesh.verticesRead += self.mainmeshVertexCount
        self.submeshes: list[SubMesh] = []
        for i in range(self.submeshCount):
            self.submeshes.append(SubMesh(buffer, pos + Mainmesh.size + i * SubMesh.size, vertexBufferHeader, faceBufferOffset=faceBufferOffset, isShadowGeo=isShadowGeo, preview=True))

        for i in range(1, self.submeshCount):
            self.submeshes[i - 1].vertexCount = self.submeshes[i].verticesBefore - self.submeshes[i - 1].verticesBefore
        self.submeshes[-1].vertexCount = self.verticesRead - self.submeshes[-1].verticesBefore

        for i in range(self.submeshCount):
            submeshVertexCount = self.submeshes[i].vertexCount
            self.submeshes[i] = SubMesh(buffer, pos + Mainmesh.size + i * SubMesh.size, vertexBufferHeader, submeshVertexCount, faceBufferOffset, isShadowGeo)

    @staticmethod
    def Reset():
        Mainmesh.verticesRead = 0

    verticesRead = 0

    size = 16


class LODGroup:
    def __init__(self, buffer: list[int], pos: int = 0, vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.mainmeshCount = ReadByte(buffer, pos + 0)
        self.ukn1 = [ReadByte(buffer, pos + 1), ReadByte(buffer, pos + 2), ReadByte(buffer, pos + 3)]
        self.ukn2 = ReadFloat(buffer, pos + 4)
        self.mainmeshHeaderOffsetsOffset = ReadInt64(buffer, pos + 8)

        # Calculated info
        self.faceBufferTotalSize: int = 0
        self.mainmeshOffsets: list[int] = []
        self.mainmeshes: list[Mainmesh] = []
        for i in range(self.mainmeshCount):
            self.mainmeshOffsets.append(ReadInt64(buffer, self.mainmeshHeaderOffsetsOffset + i * 8))
            self.mainmeshes.append(Mainmesh(buffer, self.mainmeshOffsets[-1], vertexBufferHeader, faceBufferOffset, isShadowGeo))
            self.faceBufferTotalSize += self.mainmeshes[-1].mainmeshFaceIndexCount * 2  # Size of each index value in bytes (unsigned short)

    size = 16


class BoundingBox:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.min: tuple[float, float, float, float] = (ReadFloat(buffer, pos + 32), ReadFloat(buffer, pos + 36), ReadFloat(buffer, pos + 40), ReadFloat(buffer, pos + 44)) # Bottom back left
        self.max: tuple[float, float, float, float] = (ReadFloat(buffer, pos + 48), ReadFloat(buffer, pos + 52), ReadFloat(buffer, pos + 56), ReadFloat(buffer, pos + 60)) # Top right front

        # Calculated data
        self.botLeftBack = self.min
        self.botRightBack = (self.max[0], self.min[1], self.min[2], self.min[3])
        self.topRightBack = (self.max[0], self.min[1], self.max[2], self.max[3])
        self.botLeftBack  = (self.min[0], self.min[1], self.max[2], self.max[3])

        self.botLeftFront  = (self.min[0], self.max[1], self.min[2], self.min[3])
        self.botRightFront = (self.max[0], self.min[1], self.min[2], self.min[3])
        self.topRightFront = self.max
        self.topLeftFront  = (self.min[0], self.max[1], self.max[2], self.max[3])

    size = 32

class ModelInfo:
    def __init__(self, buffer: list[int], pos: int = 0, vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.lodGroupCount = ReadByte(buffer, pos + 0)
        self.materialCount = ReadByte(buffer, pos + 1)
        self.uvLayerCount = ReadByte(buffer, pos + 2)
        self.ukn1 = ReadByte(buffer, pos + 3)
        self.totalMeshCount = ReadInt32(buffer, pos + 4)
        self.ukn2 = ReadInt64(buffer, pos + 8)
        self.ukn3 = [ReadFloat(buffer, pos + 16), ReadFloat(buffer, pos + 20), ReadFloat(buffer, pos + 24), ReadFloat(buffer, pos + 28)]
        self.boundingBox = BoundingBox(buffer, pos + 32)
        self.ukn4 = ReadInt64(buffer, pos + 64)

        # Calculated info
        self.faceBufferTotalSize: int = 0
        self.uniqueLodCount = 0
        self.lodGroupOffsets: list[int] = []
        for i in range(self.lodGroupCount):
            self.lodGroupOffsets.append(ReadInt64(buffer, pos + 72 + i * 8))
        self.uniqueLODGroupOffsets = list(dict.fromkeys(self.lodGroupOffsets))
        self.uniqueLodCount = self.uniqueLODGroupOffsets.__len__()

        self.lodGroups: list[LODGroup] = []
        Mainmesh.Reset()
        for i in range(self.uniqueLodCount):
            self.lodGroups.append(LODGroup(buffer, self.uniqueLODGroupOffsets[i], vertexBufferHeader, faceBufferOffset, isShadowGeo))
            self.faceBufferTotalSize += self.lodGroups[-1].faceBufferTotalSize

    size = 72


class NameTable:
    def __init__(self, buffer: list[int], pos: int = 0, nodeCount: int = 0):
        self.nameOffsets: list[int] = []
        self.nameList: list[str] = []

        for i in range(nodeCount):
            stringOffset = ReadInt64(buffer, pos + i * 8)
            self.nameOffsets.append(stringOffset)
            self.nameList.append(ReadString(buffer, stringOffset))


class BoundingBoxHeader:
    def __init__(self, buffer: list[int], pos: int = 0):
        self.boundingBoxCount = ReadInt64(buffer, pos + 0)
        self.boundingBoxBufferOffset = ReadInt64(buffer, pos + 8)


class REEMesh:
    def __init__(self, fileBuffer: list[int]):
        # Taking the file buffer in
        self.fileBuffer = fileBuffer

        # Read the main file header
        self.header = Header(self.fileBuffer, 0)

        # Read vertex buffer header
        self.vertexBufferHeader = GeometryBuffersHeader(self.fileBuffer, self.header.vertexBufferHeaderOffset, self.fileBuffer)

        # Read vertex element headers
        self.vertexElementHeaders: list[VertexElementHeader] = []
        for i in range(self.vertexBufferHeader.vertexElementCount[1]):
            self.vertexElementHeaders.append(VertexElementHeader(self.fileBuffer, self.vertexBufferHeader.vertexElementHeadersOffset + i * VertexElementHeader.size))

        # Read LOD groups descriptions
        self.mainModel = ModelInfo(self.fileBuffer, self.header.lodDescriptionsOffset, self.vertexBufferHeader)

        # Read shadow LOD groups descriptions if exists
        self.hasShadowGeo: bool = False
        if self.header.shadowLODDescriptionsOffset:
            self.hasShadowGeo = True
            self.shadowModel = ModelInfo(self.fileBuffer, self.header.shadowLODDescriptionsOffset, self.vertexBufferHeader, self.mainModel.faceBufferTotalSize, True)

        # Read armature info
        self.armature = ArmatureHeader(self.fileBuffer, self.header.armatureHeaderOffset)

        # Name table
        self.nameTable = NameTable(self.fileBuffer, self.header.nameTableOffset, self.header.nameTableNodeCount)

        # Material name index buffer
        self.materialNameIndexBuffer: list[int] = []
        for i in range(max([self.mainModel.materialCount, self.shadowModel.materialCount]) if self.hasShadowGeo else self.mainModel.materialCount):
            self.materialNameIndexBuffer.append(ReadInt16(self.fileBuffer, self.header.materialNameIndexBufferOffset + i * 2))

        # Bone name index buffer
        self.boneNameIndexBuffer: list[int] = []
        for i in range(self.armature.boneCount):
            self.boneNameIndexBuffer.append(ReadInt16(self.fileBuffer, self.header.boneNameIndexBufferOffset + i * 2))

        # Skin map bounding boxes
        self.boundingBoxHeader = BoundingBoxHeader(self.fileBuffer, self.header.boundingBoxHeaderOffset)

        self.boundingBoxes: list[BoundingBox] = []
        for i in range(self.boundingBoxHeader.boundingBoxCount):
            self.boundingBoxes.append(BoundingBox(self.fileBuffer, self.boundingBoxHeader.boundingBoxBufferOffset + i * BoundingBox.size))
