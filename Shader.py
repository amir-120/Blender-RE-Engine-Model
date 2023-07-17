from typing import Callable
from .TextureImport import *
from .REEMDFFile import *
from . import CustomNodes
import bpy

def GuessREShaderType(matName: str,
                      mdfNode: bpy.types.Node = None) -> CustomNodes.REShaderNodeTreeEnum or Literal['Skin & WM']:
    if mdfNode is not None:
        mdfOutputNames: list[str] = [socket.name for socket in mdfNode.outputs]

        if ("WrinkleDiffuseMap1" in mdfOutputNames and "WrinkleDiffuseMap2" in mdfOutputNames and
            "WrinkleDiffuseMap3" in mdfOutputNames and "WrinkleNormalMap1" in mdfOutputNames and
            "WrinkleNormalMap2" in mdfOutputNames and "WrinkleNormalMap3" in mdfOutputNames) or \
                ("SSS_Channel" in mdfOutputNames and "Weight1" in mdfOutputNames):
            return 'Skin WM'

        if "OccDark" in mdfOutputNames and "BaseShiftMap" in mdfOutputNames:
            return 'Hair Shader'

        if "BaseAlphaMap" in mdfOutputNames:
            return 'Alba Shader'

        if "ReflectImage_Intensity" in mdfOutputNames and "ReflectImage_Distortion" in mdfOutputNames or \
                "ReflectImage_UseFishEye" in mdfOutputNames:
            return 'EyeOuter Shader'

        if "UseAlphaMap" in mdfOutputNames:
            return 'Transparent Shader'

    if matName in GuessREShaderType.nameTypeMap.keys():
        return GuessREShaderType.nameTypeMap[matName]

    return 'Default Shader'
GuessREShaderType.nameTypeMap = {
    "m_eye"         : 'Eye Shader',
    "m_eyebrow"     : 'Transparent Shader',
    "m_eyelash"     : 'Transparent Shader',
    "m_eyelash2"    : 'Transparent Shader',
    "m_beard"       : 'Hair Shader',
    "m_hair"        : 'Hair Shader',
    "hair_mat"      : 'Hair Shader',
    "m_eyeduct"     : 'Alba Shader',
    "m_eyeshadow"   : 'Alba Shader',
    "m_eyeouter"    : 'EyeOuter Shader',
    "m_eyewet"      : 'EyeOuter Shader',
    #"m_head"        : 'Skin Shader',
    #"m_hand"        : 'Skin Shader',
}


def AddMDFNode(mat: bpy.types.Material, mdfMat: Material) -> bpy.types.Node:
    nodes = mat.node_tree.nodes
    group = nodes.new(type='ShaderNodeGroup')
    group.node_tree = bpy.data.node_groups.new(type='ShaderNodeTree', name=f"{mdfMat.name} - RE Material Properties")
    group.label = "Material Definitions"
    group.width = 280.0

    inputs = group.node_tree.nodes.new(type='NodeGroupInput')
    outputs = group.node_tree.nodes.new(type='NodeGroupOutput')
    links = group.node_tree.links

    for tex in mdfMat.textureInfo:
        colName = tex.type
        alpName = f"{tex.type} - Alpha"
        group.node_tree.inputs.new(type='NodeSocketColor', name=colName)
        group.node_tree.inputs.new(type='NodeSocketFloat', name=alpName)
        group.node_tree.outputs.new(type='NodeSocketColor', name=colName)
        group.node_tree.outputs.new(type='NodeSocketFloat', name=alpName)
        links.new(inputs.outputs[colName], outputs.inputs[colName])
        links.new(inputs.outputs[alpName], outputs.inputs[alpName])

        #if IsNormalMap(colName):
        #    nmNode = mat.node_tree.nodes.new('ShaderNodeNormalMap')
        #    nmNode.name = f"{colName} - NormalMap"
        #    nmNode.label = colName
        #    mat.node_tree.links.new(group.node_tree.outputs[colName], nmNode.inputs['Color'])

    for prop in mdfMat.properties:
        if (prop.parameterCount == 4) and ("color" in prop.name.lower()) and not ("rate" in prop.name.lower()) or \
                prop.utf16NameMurmur3 == 0x3A130D0A or prop.utf16NameMurmur3 == 0x2FD71A4B or \
                prop.utf16NameMurmur3 == 0x114B33F4 or prop.utf16NameMurmur3 == 0xF1BACDAF or \
                prop.utf16NameMurmur3 == 0x033CB166 or prop.utf16NameMurmur3 == 0x7D0FA086 or \
                prop.utf16NameMurmur3 == 0x83EBFAB5 or prop.utf16NameMurmur3 == 0x77181233:
            name = prop.name
            group.node_tree.inputs.new(type='NodeSocketColor', name=name)
            group.node_tree.outputs.new(type='NodeSocketColor', name=name)
            group.inputs[name].default_value = (prop.parameters[0], prop.parameters[1],
                                                prop.parameters[2], prop.parameters[3])
            links.new(inputs.outputs[name], outputs.inputs[name])

        else:
            for idx, param in enumerate(prop.parameters):
                name = f"{prop.name} - {idx}" if prop.parameterCount > 1 else prop.name
                group.node_tree.inputs.new(type='NodeSocketFloat', name=name)
                group.node_tree.outputs.new(type='NodeSocketFloat', name=name)
                group.inputs[name].default_value = param
                links.new(inputs.outputs[name], outputs.inputs[name])

    group.hide = True

    RearrangeNodesInEditorWindow(group.node_tree.nodes, wMult=0.7, hMult=0.7)

    return group


def CreateMaterial(name: str, replace: bool = True) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)

    if mat is None:
        mat = bpy.data.materials.new(name=name)
    elif(replace == False):
        return mat

    mat.use_nodes = True

    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat


def AddRETextureToMaterial(mat: bpy.types.Material, texPath: str) -> bpy.types.Node:
    imageName = os.path.splitext(os.path.basename(texPath))[0]
    blenderImage: bpy.types.Image

    if (img := bpy.data.images.get(imageName)) is not None:
        blenderImage = img
    else:
        rawImage = TEX(texPath, 'RGBA', floatMode=True, vFlip=True)

        blenderImage = bpy.data.images.new(imageName, rawImage.width, rawImage.height, alpha=True,
                                           is_data=rawImage.isLinear)
        blenderImage.alpha_mode = 'CHANNEL_PACKED'
        blenderImage.pixels = rawImage.buffer
        blenderImage.update()

        # Pack image in blend file
        blenderImage.pack()
        #blenderImage.filepath = ""
        #blenderImage.filepath_raw = ""
        blenderImage.file_format = 'TARGA'

    nodes = mat.node_tree.nodes
    texNode = nodes.new('ShaderNodeTexImage')
    texNode.image = blenderImage
    texNode.label = imageName
    texNode.name = blenderImage.name

    return texNode


def LerpFloat(a, b, t):
    return (1.0 - t) * a + t * b


def GetNodePriorityByType(node):
    if node.type == 'NEW_GEOMETRY' or node.type == 'TEX_COORD' or node.type == 'GROUP_INPUT':
        return -6
    if node.type == 'VALUE' or node.type == 'ATTRIBUTE':
        return -5
    if node.type == 'SEPXYZ':
        return -4
    if node.type == 'SEPHSV' or node.type == 'SEPRGB' or node.type == 'BLACKBODY':
        return -3
    if node.type == 'MATH' or node.type == 'VECT_MATH':
        return -2
    if node.type == 'COMBXYZ':
        return -1
    if node.type == 'COMBHSV' or node.type == 'COMBRGB':
        return 1
    if node.type == 'MIX_RGB' or node.type == 'HUE_SAT':
        return 2
    if node.type == 'TEX_IMAGE' or node.type == 'TEX_MUSGRAVE' or node.type == 'TEX_BRICK' or \
            node.type == 'TEX_NOISE' or node.type == 'TEX_VORONOI':
        return 3
    if node.type == 'BSDF_DIFFUSE' or node.type == 'BSDF_PRINCIPLED' or node.type == 'EMISSION':
        return 4
    if node.type == 'HOLDOUT' or node.type == 'VOLUME_SCATTER' or node.type == 'VOLUME_ABSORPTION':
        return 5
    if node.type == 'MIX_SHADER':
        return 6
    if node.type == 'OUTPUT_MATERIAL' or node.type == 'OUTPUT_LAMP' or node.type == 'GROUP_OUTPUT':
        return 7

    return 0


def GetNodePriorityRE(node: bpy.types.Node):
    if node.type == 'GROUP_INPUT' or node.type == 'UVMAP':
        return -7
    if node.type == 'TEX_IMAGE' or node.type == 'TEX_MUSGRAVE' or node.type == 'TEX_BRICK' or\
            node.type == 'TEX_NOISE' or node.type == 'TEX_VORONOI':
        return -6
    if node.type == 'VALUE' or node.type == 'ATTRIBUTE':
        return -5
    if node.type == 'SEPXYZ':
        return -4
    if node.type == 'SEPHSV' or node.type == 'SEPRGB' or node.type == 'BLACKBODY':
        return -3
    if node.type == 'MATH' or node.type == 'VECT_MATH':
        return -2
    if node.type == 'COMBXYZ':
        return -1
    if node.type == 'NORMAL_MAP':
        return 1
    if node.type == 'COMBHSV' or node.type == 'COMBRGB':
        return 2
    if node.type == 'MIX_RGB' or node.type == 'HUE_SAT':
        return 3
    if node.type == 'NEW_GEOMETRY' or node.type == 'TEX_COORD':
        return 4
    if hasattr(node, 'bl_type') and node.bl_type.startswith("REE_NODE"):
        return 5
    if hasattr(node, 'bl_type') and  node.bl_type.startswith("REE_SHADER"):
        return 6
    if node.type == 'BSDF_DIFFUSE' or node.type == 'BSDF_PRINCIPLED' or node.type == 'EMISSION':
        return 7
    if node.type == 'HOLDOUT' or node.type == 'VOLUME_SCATTER' or node.type == 'VOLUME_ABSORPTION':
        return 8
    if node.type == 'MIX_SHADER':
        return 9
    if node.type == 'OUTPUT_MATERIAL' or node.type == 'OUTPUT_LAMP' or node.type == 'GROUP_OUTPUT':
        return 10

    return 0


def RearrangeNodesInEditorWindow(nodes: bpy.types.Nodes, priorityFunction: Callable = GetNodePriorityRE,
                                 paddingX: float = 0.0, paddingY: float = 0.0, wMaxThreshold: float = 0.5,
                                 hMaxThreshold: float = 1.0, wMult: float = 1.0, hMult: float = 1.0):
    wMaxThreshold *= wMult
    hMaxThreshold *= hMult
    depthNodes = {}
    for node in nodes:
        depth = priorityFunction(node)
        if depth in depthNodes:
            depthNodes[depth].append(node)
        else:
            depthNodes[depth] = [node]

    sumWidth = 0
    for depth in depthNodes:
        max_width = 0
        for node in depthNodes[depth]:
            if max_width < node.width:
                max_width = node.width
        sumWidth += max_width

    extentsW = (0.5 + paddingX) * sumWidth
    numNodes = len(depthNodes)
    if numNodes > 1:
        wMaxThreshold = (1.0 / (numNodes - 1)) * wMult

    depths = sorted(depthNodes.items())
    for i in range(numNodes):
        nodesCh = depths[i][1]
        wThreshold = i * wMaxThreshold
        x = LerpFloat(-extentsW, extentsW, wThreshold)

        numNodesCh = len(nodesCh)
        sumHeight = 0
        for node in nodesCh:
            node.hide = numNodesCh > 1 or node.name.endswith(" - NormalMap")
            sumHeight += node.height if not node.hide else node.bl_height_min

        extentsH = (0.5 + paddingY) * sumHeight
        if numNodesCh > 1:
            hMaxThreshold = (1.0 / (numNodesCh - 1)) * hMult

        for j in range(numNodesCh):
            node = nodesCh[j]
            hThreshold = j * hMaxThreshold
            y = LerpFloat(extentsH, -extentsH, hThreshold)
            xOffset = 450.0 if priorityFunction(node) >= 5 else 0.0
            node.location.xy = (x - 0.5 * node.width + xOffset, y - 0.5 * node.height)
