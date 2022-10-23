from .BinaryFunctions import *
from enum import Enum

class Header:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
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

class NormalAndTangent:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        readBuff = ReadByte(buffer, pos + 0, 8, signed=True)
        self.normalX = self.__NormalizeByte(readBuff[0])
        self.normalY = self.__NormalizeByte(readBuff[1])
        self.normalZ = self.__NormalizeByte(readBuff[2])
        self.normalW = self.__NormalizeByte(readBuff[3])
        self.tangentX = self.__NormalizeByte(readBuff[4])
        self.tangentY = self.__NormalizeByte(readBuff[5])
        self.tangentZ = self.__NormalizeByte(readBuff[6])
        self.tangentW = self.__NormalizeByte(readBuff[7])

    @staticmethod
    def __NormalizeByte(byte: int) -> float:
        return byte / (128.0 if byte & 0b10000000 else 127.0)

    size = 8

class SkinWeights:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        self.indices: np.ndarray[int] = ReadByte(buffer, pos, 8)
        self.weights: np.ndarray[float] = np.array([w / 255.0 for w in ReadByte(buffer, pos + 8, 8)])

    size = 16

class BoneTransform:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        self.transformMatrix: np.ndarray[tuple[float, float, float, float]] = ReadFloat(buffer,
                                                                                        pos + 0, 16).reshape((-1, 4))

    size = 64

class BoneHierarchy:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        readBuffer = ReadInt16(buffer, pos, 8, signed=True)
        self.index = readBuffer[0]
        self.parent = readBuffer[1]
        self.nextSibling = readBuffer[2]
        self.nextChild = readBuffer[3]
        self.cousin = readBuffer[4]
        self.ukn1 = readBuffer[5]
        self.ukn2 = readBuffer[6]
        self.ukn3 = readBuffer[7]

    size = 16


class ArmatureHeader:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        self.boneCount = ReadInt32(buffer, pos + 0)
        self.skinMapSize = ReadInt32(buffer, pos + 4)
        self.ukn1 = ReadInt64(buffer, pos + 8)
        self.boneHierarchyTableOffset = ReadInt32(buffer, pos + 16)
        self.localBoneTransformsTableOffset = ReadInt32(buffer, pos + 24)
        self.globalBoneTransformsTableOffset = ReadInt32(buffer, pos + 32)
        self.inverseGlobalBoneTransformsTableOffset = ReadInt32(buffer, pos + 40)

        # Calculated data
        # Index of the bone index in the BoneMapIndices
        self.skinBoneMap: np.ndarray[int] = ReadInt16(buffer, pos + self.size, self.skinMapSize)
        self.boneHierarchy: list[BoneHierarchy] = [None] * self.boneCount
        self.localBoneTransforms: list[BoneTransform] = [None] * self.boneCount
        self.globalBoneTransforms: list[BoneTransform] = [None] * self.boneCount
        self.inverseGlobalTransfroms: list[BoneTransform] = [None] * self.boneCount

        for i in range(self.boneCount):
            self.boneHierarchy[i] = BoneHierarchy(buffer, self.boneHierarchyTableOffset + i * BoneHierarchy.size)
            self.localBoneTransforms[i] = BoneTransform(buffer,
                                                          self.localBoneTransformsTableOffset + i * BoneTransform.size)
            self.globalBoneTransforms[i] = BoneTransform(buffer, self.globalBoneTransformsTableOffset +
                                                           i * BoneTransform.size)
            self.inverseGlobalTransfroms[i] = BoneTransform(buffer, self.inverseGlobalBoneTransformsTableOffset +
                                                              i * BoneTransform.size)

    size = 48


class VertexElementHeader:
    class ElementType(Enum):
        VertexPosition = 0
        NormalsTangents = 1
        UV0 = 2
        UV1 = 3
        BoneInfo = 4

    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        self.elementType = self.ElementType(ReadInt16(buffer, pos + 0))
        self.bytesPerVertex = ReadInt16(buffer, pos + 2)
        self.offsetInVertexBuffer = ReadInt32(buffer, pos + 4)

    size = 8


class GeometryBuffersHeader:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0, fileBuffer: list[int] = -1):
        self.vertexElementHeadersOffset = ReadInt64(buffer, pos + 0)
        self.vertexBufferOffset = ReadInt64(buffer, pos + 8)
        self.faceIndexBufferOffset = ReadInt64(buffer, pos + 16)
        self.vertexBufferSize = ReadInt32(buffer, pos + 24)
        self.faceIndexBufferSize = ReadInt32(buffer, pos + 28)
        self.vertexElementCount = ReadInt16(buffer, pos + 32, 2)
        self.ukn = ReadInt64(buffer, pos + 36)
        self.blendShapesOffset = ReadInt32(buffer, pos + 44, signed=True)

        # Calculated data
        self.fileBuffer = fileBuffer
        self.vertexElementHeaders: list[VertexElementHeader] = [None] * self.vertexElementCount[1]

        for i in range(self.vertexElementCount[1]):
            self.vertexElementHeaders[i] = VertexElementHeader(buffer, self.vertexElementHeadersOffset +
                                                                 i * VertexElementHeader.size)

    size = 48


class SubMesh:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0, vertexBufferHeader: GeometryBuffersHeader = -1,
                 vertexCount: int = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False, preview: bool = False):
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

        self.faceIndexBufferPos = faceBufferOffset + vertexBufferHeader.faceIndexBufferOffset +\
                                                        self.faceIndicesBefore * 2

        self.faces: np.ndarray[tuple[int, int, int]] = ReadInt16(buffer, self.faceIndexBufferPos,
                                                           self.faceIndexCount).reshape((-1, 3))
        self.vertexBuffer: np.ndarray[tuple[float, float, float]] #[None] * self.vertexCount
        self.normalsTangents: list[NormalAndTangent] = [None] * self.vertexCount
        self.uv0s: np.ndarray[tuple[float, float]] = np.array([]) #[None] * self.vertexCount
        self.uv1s: np.ndarray[tuple[float, float]] = np.array([])#[None] * self.vertexCount
        self.boneInfo: list[SkinWeights] = [None] * self.vertexCount

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
                    self.vertexBuffer = ReadFloat(buffer, vertexBufferHeader.vertexBufferOffset +
                                                  elementInfo.offsetInVertexBuffer + self.verticesBefore *
                                                  elementInfo.bytesPerVertex, 3 * self.vertexCount).reshape((-1, 3))

                case elementInfo.ElementType.NormalsTangents:
                    for j in range(self.vertexCount):
                        self.normalsTangents[j] = NormalAndTangent(vertexBufferHeader.fileBuffer,
                                                                   vertexBufferHeader.vertexBufferOffset +
                                                                   elementInfo.offsetInVertexBuffer +
                                                                   self.verticesBefore * elementInfo.bytesPerVertex +
                                                                   j * elementInfo.bytesPerVertex)

                case elementInfo.ElementType.UV0:
                    self.uv0s = ReadHalfFloat(buffer, vertexBufferHeader.vertexBufferOffset +
                                              elementInfo.offsetInVertexBuffer + self.verticesBefore *
                                              elementInfo.bytesPerVertex, 2 * self.vertexCount).reshape((-1, 2))
#
                case elementInfo.ElementType.UV1:
                    self.uv1s = ReadHalfFloat(buffer, vertexBufferHeader.vertexBufferOffset +
                                              elementInfo.offsetInVertexBuffer + self.verticesBefore *
                                              elementInfo.bytesPerVertex, 2 * self.vertexCount).reshape((-1, 2))

                case elementInfo.ElementType.BoneInfo:
                    for j in range(self.vertexCount):
                        self.boneInfo[j] = SkinWeights(vertexBufferHeader.fileBuffer,
                                                         vertexBufferHeader.vertexBufferOffset +
                                                         elementInfo.offsetInVertexBuffer + self.verticesBefore *
                                                         elementInfo.bytesPerVertex + j * elementInfo.bytesPerVertex)

    size = 16

class Mainmesh:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0,
                 vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.groupID = ReadByte(buffer, pos + 0)
        self.submeshCount = ReadByte(buffer, pos + 1)
        self.ukn1: np.ndarray[int] = ReadByte(buffer, pos + 2, 2)
        self.ukn2 = ReadInt32(buffer, pos + 4)
        self.mainmeshVertexCount = ReadInt32(buffer, pos + 8)
        self.mainmeshFaceIndexCount = ReadInt32(buffer, pos + 12)

        # Calculated data
        Mainmesh.verticesRead += self.mainmeshVertexCount
        self.submeshes: list[SubMesh]  = [None] * self.submeshCount
        for i in range(self.submeshCount):
            self.submeshes[i] = SubMesh(buffer, pos + Mainmesh.size + i * SubMesh.size, vertexBufferHeader,
                                          faceBufferOffset=faceBufferOffset, isShadowGeo=isShadowGeo, preview=True)

        for i in range(1, self.submeshCount):
            self.submeshes[i - 1].vertexCount = self.submeshes[i].verticesBefore - self.submeshes[i - 1].verticesBefore
        self.submeshes[-1].vertexCount = self.verticesRead - self.submeshes[-1].verticesBefore

        for i in range(self.submeshCount):
            submeshVertexCount = self.submeshes[i].vertexCount
            self.submeshes[i] = SubMesh(buffer, pos + Mainmesh.size + i * SubMesh.size, vertexBufferHeader,
                                        submeshVertexCount, faceBufferOffset, isShadowGeo)

    @staticmethod
    def Reset():
        Mainmesh.verticesRead = 0

    verticesRead = 0

    size = 16


class LODGroup:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0,
                 vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.mainmeshCount = ReadByte(buffer, pos + 0)
        self.ukn1 = ReadByte(buffer, pos + 1, 3)
        self.ukn2 = ReadFloat(buffer, pos + 4)
        self.mainmeshHeaderOffsetsOffset = ReadInt64(buffer, pos + 8)

        # Calculated info
        self.faceBufferTotalSize: int = 0
        self.mainmeshOffsets: list[int] = [None] * self.mainmeshCount
        self.mainmeshes: list[Mainmesh] = [None] * self.mainmeshCount
        for i in range(self.mainmeshCount):
            self.mainmeshOffsets[i] = ReadInt64(buffer, self.mainmeshHeaderOffsetsOffset + i * 8)
            self.mainmeshes[i] = Mainmesh(buffer, self.mainmeshOffsets[i], vertexBufferHeader, faceBufferOffset,
                                            isShadowGeo)
            # Size of each index value in bytes (unsigned short)
            self.faceBufferTotalSize += self.mainmeshes[i].mainmeshFaceIndexCount * 2
    size = 16


class BoundingBox:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        # Bottom back left
        self.min: tuple[float, float, float, float] = tuple(ReadFloat(buffer, pos + 32, 4))
        # Top right front
        self.max: tuple[float, float, float, float] = tuple(ReadFloat(buffer, pos + 48, 4))

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
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0,
                 vertexBufferHeader: GeometryBuffersHeader = -1, faceBufferOffset: int = 0, isShadowGeo: bool = False):
        self.lodGroupCount = ReadByte(buffer, pos + 0)
        self.materialCount = ReadByte(buffer, pos + 1)
        self.uvLayerCount = ReadByte(buffer, pos + 2)
        self.ukn1 = ReadByte(buffer, pos + 3)
        self.totalMeshCount = ReadInt32(buffer, pos + 4)
        self.ukn2 = ReadInt64(buffer, pos + 8)
        self.ukn3 = ReadFloat(buffer, pos + 16, 4)
        self.boundingBox = BoundingBox(buffer, pos + 32)
        self.ukn4 = ReadInt64(buffer, pos + 64)

        # Calculated info
        self.faceBufferTotalSize: int = 0
        self.uniqueLodCount = 0
        self.lodGroupOffsets: list[int] = [None] * self.lodGroupCount
        for i in range(self.lodGroupCount):
            self.lodGroupOffsets[i] = ReadInt64(buffer, pos + 72 + i * 8)
        self.uniqueLODGroupOffsets = list(dict.fromkeys(self.lodGroupOffsets))
        self.uniqueLodCount = self.uniqueLODGroupOffsets.__len__()

        self.lodGroups = [None] * self.uniqueLodCount
        Mainmesh.Reset()
        for i in range(self.uniqueLodCount):
            self.lodGroups[i] = LODGroup(buffer, self.uniqueLODGroupOffsets[i], vertexBufferHeader, faceBufferOffset,
                                           isShadowGeo)
            self.faceBufferTotalSize += self.lodGroups[i].faceBufferTotalSize

    size = 72


class NameTable:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0, nodeCount: int = 0):
        self.nameOffsets: list[int] = [int] * nodeCount
        self.nameList: list[str] = [str] * nodeCount

        stringOffsets = ReadInt64(buffer, pos, nodeCount)
        for i in range(nodeCount):
            self.nameOffsets[i] = stringOffsets[i]
            self.nameList[i] = ReadString(buffer, stringOffsets[i])


class BoundingBoxHeader:
    def __init__(self, buffer: bytes or bytearray or list[int], pos: int = 0):
        self.boundingBoxCount = ReadInt64(buffer, pos + 0)
        self.boundingBoxBufferOffset = ReadInt64(buffer, pos + 8)


class REEMesh:
    def __init__(self, fileBuffer: bytes or bytearray or list[int]):
        # Taking the file buffer in
        self.fileBuffer = fileBuffer

        # Read the main file header
        self.header = Header(self.fileBuffer, 0)

        # Read vertex buffer header
        self.vertexBufferHeader = GeometryBuffersHeader(self.fileBuffer, self.header.vertexBufferHeaderOffset,
                                                        self.fileBuffer)

        # Read vertex element headers
        self.vertexElementHeaders: list[VertexElementHeader] =\
            [VertexElementHeader] * self.vertexBufferHeader.vertexElementCount[1]
        for i in range(self.vertexBufferHeader.vertexElementCount[1]):
            self.vertexElementHeaders[i] = VertexElementHeader(self.fileBuffer,
                                                                 self.vertexBufferHeader.vertexElementHeadersOffset +
                                                                 i * VertexElementHeader.size)

        # Read LOD groups descriptions
        self.mainModel = ModelInfo(self.fileBuffer, self.header.lodDescriptionsOffset, self.vertexBufferHeader)

        # Read shadow LOD groups descriptions if exists
        self.hasShadowGeo: bool = False
        if self.header.shadowLODDescriptionsOffset:
            self.hasShadowGeo = True
            self.shadowModel = ModelInfo(self.fileBuffer, self.header.shadowLODDescriptionsOffset,
                                         self.vertexBufferHeader, self.mainModel.faceBufferTotalSize, True)

        # Read armature info
        self.armature = ArmatureHeader(self.fileBuffer, self.header.armatureHeaderOffset)

        # Name table
        self.nameTable = NameTable(self.fileBuffer, self.header.nameTableOffset, self.header.nameTableNodeCount)

        # Material name index buffer
        matNIdxBuffLen = max([self.mainModel.materialCount, self.shadowModel.materialCount])\
            if self.hasShadowGeo else self.mainModel.materialCount
        self.materialNameIndexBuffer: np.ndarray[int] = ReadInt16(self.fileBuffer, self.header.materialNameIndexBufferOffset,
                                                            matNIdxBuffLen)

        # Bone name index buffer
        self.boneNameIndexBuffer: np.ndarray[int] = ReadInt16(self.fileBuffer, self.header.boneNameIndexBufferOffset,
                                                        self.armature.boneCount)

        # Skin map bounding boxes
        self.boundingBoxHeader = BoundingBoxHeader(self.fileBuffer, self.header.boundingBoxHeaderOffset)

        self.boundingBoxes: list[BoundingBox] = [BoundingBox] * self.boundingBoxHeader.boundingBoxCount
        for i in range(self.boundingBoxHeader.boundingBoxCount):
            self.boundingBoxes[i] = BoundingBox(self.fileBuffer, self.boundingBoxHeader.boundingBoxBufferOffset + i *
                                                  BoundingBox.size)
