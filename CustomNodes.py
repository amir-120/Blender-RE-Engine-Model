from nodeitems_utils import NodeCategory, NodeItem
from typing import Literal
from bpy.props import EnumProperty
from bpy.types import Operator, ShaderNodeCustomGroup
import nodeitems_utils
import bpy
import os

RENodeTreeEnum = Literal['Alba Shader', 'Albedo Wrinkles', 'Default Shader', 'Eye Shader', 'EyeOuter Shader',
                         'Hair Shader', 'Head MSK 4', 'Normal Wrinkles', 'Transparent Shader',
                         'Wrinkle Map']

REShaderNodeTreeEnum = Literal['Alba Shader', 'Default Shader', 'Eye Shader', 'EyeOuter Shader', 'Hair Shader',
                               'Transparent Shader']

RENodeNodeTreeEnum = Literal['Albedo Wrinkles', 'Head MSK 4', 'Normal Wrinkles', 'Wrinkle Map']

def AppendRENodeTree(reShaderName: RENodeTreeEnum) -> bpy.types.ShaderNodeTree:
    path = os.path.join(os.path.dirname(__file__), "ShaderStorage.blend")
    bpy.ops.wm.append(
        filepath=os.path.join(path, 'NodeTree', reShaderName),
        directory=os.path.join(path, 'NodeTree'),
        filename=reShaderName
    )

    return bpy.data.node_groups.get(reShaderName)


def AppendAllRENodeTrees():
    AppendRENodeTree('Default Shader')
    #AppendRENodeTree('Skin Shader')
    AppendRENodeTree('Wrinkle Map')
    AppendRENodeTree('Transparent Shader')
    AppendRENodeTree('Hair Shader')
    AppendRENodeTree('EyeOuter Shader')
    AppendRENodeTree('Eye Shader')
    AppendRENodeTree('Alba Shader')


def CleanNodeTree(nodeTree: bpy.types.NodeTree):
    if nodeTree is not None:
        for node in nodeTree.nodes:
            if node is not None and hasattr(node, 'node_tree'):
                CleanNodeTree(node.node_tree)
        bpy.data.node_groups.remove(nodeTree, do_unlink=True)


def DeepCopyNodeTree(nodeTree: bpy.types.NodeTree) -> bpy.types.NodeTree or None:
    if nodeTree is not None:
        nodeTree = nodeTree.copy()
        for node in nodeTree.nodes:
            if node is not None and hasattr(node, 'node_tree'):
                node.node_tree = DeepCopyNodeTree(node.node_tree)
        return nodeTree
    return None


def GetRENodeNoCopy(reShaderName: RENodeTreeEnum) -> bpy.types.ShaderNodeTree:
    reNode: bpy.types.ShaderNodeTree or None = bpy.data.node_groups.get(reShaderName)
    return AppendRENodeTree(reShaderName) if reNode is None else reNode


def GetRENodeCopy(reShaderName: RENodeTreeEnum) -> bpy.types.ShaderNodeTree or None:
    nodeTree = GetRENodeNoCopy(reShaderName)

    return DeepCopyNodeTree(nodeTree)


def AutoconnectRENodes(shaderNode: bpy.types.Node, mdfNode: bpy.types.Node = None, reNodes: list[bpy.types.Node] = None,
                       materialOuput: bpy.types.Node = None):
    nodeTree = shaderNode.id_data
    mdfInfoNode: bpy.types.Node or None = mdfNode
    reExtraNodes: list[bpy.types.Node] or None = reNodes
    materialOutput: bpy.types.Node or None = materialOuput

    if mdfInfoNode is None:
        for node in nodeTree.nodes:
            if node.name == 'Group' and node.node_tree.name.endswith(" - RE Material Properties"):
                mdfInfoNode = node
                continue

    if reExtraNodes is None:
        reExtraNodes = []
        for node in nodeTree.nodes:
            if hasattr(node, 'bl_type') and node.bl_type.startswith("REE_NODE"):
                reExtraNodes.append(node)

    topLeft = (shaderNode.location[0] - shaderNode.width - shaderNode.width * 0.5, shaderNode.location[1])
    botLeft = (shaderNode.location[0] - shaderNode.width - shaderNode.width * 0.5, shaderNode.location[1] - 45.0)
    if materialOutput is None:
        for node in nodeTree.nodes:
            xy = node.location

            if node.type != 'UVMAP':
                topLeft = (min([xy[0] - node.width - node.width * 0.5, topLeft[0]]), max([xy[1], topLeft[1]]))

            if node.type == 'TEX_IMAGE':
                botLeft = (min([xy[0], botLeft[0]]), min([xy[1], botLeft[1] - 45.0]))

            if node.type == 'OUTPUT_MATERIAL':
                materialOutput = node
                break

    shaderInputNames: list[str] = [socket.name for socket in shaderNode.inputs]
    mdfOutputNames: list[str] = [socket.name for socket in mdfInfoNode.outputs] if mdfInfoNode is not None else None
    mdfInputNames: list[str] = [socket.name for socket in mdfInfoNode.inputs] if mdfInfoNode is not None else None

    if mdfInfoNode is not None:
        # Add a Wrinkle Map or uv node if needed
        hasWrinkleMap = "WrinkleDiffuseMap1" in mdfOutputNames and "WrinkleDiffuseMap2" in mdfOutputNames and \
                            "WrinkleDiffuseMap3" in mdfOutputNames and "WrinkleNormalMap1" in mdfOutputNames and \
                            "WrinkleNormalMap2" in mdfOutputNames and "WrinkleNormalMap3" in mdfOutputNames

        wrinkleMapExists = False
        for node in reExtraNodes:
            if node.bl_type == "REE_NODE_WRINKLE_MAP":
                wrinkleMapExists = True
                continue

        if hasWrinkleMap and not wrinkleMapExists:
            wmNode: REENodeWrinkleMap = nodeTree.nodes.new(type='REENodeWrinkleMap')
            wmNode.location = (shaderNode.location[0] - shaderNode.width - 100.0, shaderNode.location[1])
            nodeTree.links.new(shaderNode.inputs["BaseMetalMap"], wmNode.outputs["BaseMetalMap"])
            nodeTree.links.new(shaderNode.inputs["NormalRoughnessMap"], wmNode.outputs["NormalRoughnessMap"])
            reExtraNodes.append(wmNode)

    # Add second UV textures if needed
    secondUVUsers: list[str] = []
    for input in shaderInputNames:
        if input.startswith("UV2 - "):
            secondUVUsers.append(input)

    secondUVUsers = list(dict.fromkeys(secondUVUsers))

    secondUVNode: bpy.types.Node or None = None
    for node in nodeTree.nodes:
        if node.type == 'UVMAP' and node.uv_map == "UV_1":
            secondUVNode = node

    if secondUVUsers and secondUVNode is None:
        secondUVNode = nodeTree.nodes.new(type='ShaderNodeUVMap')
        secondUVNode.uv_map = "UV_1"
        secondUVNode.location = topLeft

    if mdfInfoNode is not None:
        for shaderInSocket in secondUVUsers:
            mdfNodeInSocketName = shaderInSocket[6:]
            if mdfNodeInSocketName in mdfInputNames:
                mdfInSocket = mdfInfoNode.inputs.get(mdfNodeInSocketName)
                if mdfInSocket is not None:
                    sourceNodes = [link.from_node for link in mdfInSocket.links]
                    for sourceNode in list(dict.fromkeys(sourceNodes)):
                        if sourceNode.type == 'TEX_IMAGE':
                            newUV2TexNode = nodeTree.nodes.get("2nd UV - " + sourceNode.name)

                            if newUV2TexNode is None:
                                newUV2TexNode = nodeTree.nodes.new(type='ShaderNodeTexImage')

                                newUV2TexNode.image = sourceNode.image
                                newUV2TexNode.extension = sourceNode.extension
                                newUV2TexNode.interpolation = sourceNode.interpolation
                                newUV2TexNode.projection = sourceNode.projection
                                newUV2TexNode.projection_blend = sourceNode.projection_blend

                            newUV2TexNode.name = "2nd UV - " + sourceNode.name
                            newUV2TexNode.label = "2nd UV - " + sourceNode.label
                            newUV2TexNode.hide = True
                            newUV2TexNode.location = botLeft
                            botLeft = (botLeft[0], botLeft[1] - 17.0)
                            nodeTree.links.new(secondUVNode.outputs['UV'], newUV2TexNode.inputs['Vector'])
                            if shaderInSocket.endswith(" - Alpha"):
                                nodeTree.links.new(newUV2TexNode.outputs['Alpha'],
                                                   shaderNode.inputs[shaderInSocket])
                            else:
                                nodeTree.links.new(newUV2TexNode.outputs['Color'], shaderNode.inputs[shaderInSocket])

    if materialOutput is not None:
        nodeTree.links.new(shaderNode.outputs["BSDF"], materialOutput.inputs["Surface"])

    for shaderInputName in shaderInputNames:
        # Connect RE nodes to the RE shader
        for reExtraNode in reExtraNodes:
            for reExtraNodeOutput in reExtraNode.outputs:
                if reExtraNodeOutput.name in shaderInputNames:
                    nodeTree.links.new(reExtraNodeOutput, shaderNode.inputs[reExtraNodeOutput.name])

        if mdfInfoNode is not None:
            # Connect the MDF node to the RE shader
            if shaderInputName in mdfOutputNames:
                if not shaderNode.inputs[shaderInputName].is_linked:
                    nodeTree.links.new(mdfInfoNode.outputs[shaderInputName], shaderNode.inputs[shaderInputName])

            # Connect the MDF node to the RE nodes
            for reExtraNode in reExtraNodes:
                for reExtraNodeInput in reExtraNode.inputs:
                    if reExtraNodeInput.name in mdfOutputNames:
                        nodeTree.links.new(mdfInfoNode.outputs[reExtraNodeInput.name], reExtraNodeInput)

class NodeHelper:
    @staticmethod
    def __path_resolve__(obj, path):
        if "." in path:
            extraPath, path = path.rsplit(".", 1)
            obj = obj.path_resolve(extraPath)
        return obj, path

    def _value_set(self, obj, path, val):
        obj, path = self.__path_resolve__(obj, path)
        setattr(obj, path, val)

    def AddNodes(self, nodes: list[tuple[str, dict]]):
        for nodeItem in nodes:
            node = self.node_tree.nodes.new(type=nodeItem[0])
            for attr in nodeItem[1]:
                self._value_set(node, attr, nodeItem[1][attr])

    def SetInternalNodeTree(self, nodeName: str, node_tree: bpy.types.NodeTree or bpy.types.ID):
        node = self.node_tree.nodes.get(nodeName)
        if node is not None:
            node.node_tree = node_tree

    def AddLinks(self, links: list[tuple[str, str]]):
        for link in links:
            if isinstance(link[0], str):
                if link[0].startswith('inputs'):
                    socketFrom = self.node_tree.path_resolve(
                        'nodes["Group Input"].outputs' + link[0][link[0].rindex('['):])
                else:
                    socketFrom = self.node_tree.path_resolve(link[0])
            else:
                socketFrom = link[0]
            if isinstance(link[1], str):
                if link[1].startswith('outputs'):
                    socketTo = self.node_tree.path_resolve(
                        'nodes["Group Output"].inputs' + link[1][link[1].rindex('['):])
                else:
                    socketTo = self.node_tree.path_resolve(link[1])
            else:
                socketTo = link[1]
            self.node_tree.links.new(socketFrom, socketTo)

    def AddInputs(self, inputs: list[tuple[str, dict]]):
        for inputItem in inputs:
            name = inputItem[1].pop('name')
            socketInterface = self.node_tree.inputs.new(inputItem[0], name)
            socket = self.path_resolve(socketInterface.path_from_id())
            for attr in inputItem[1]:
                if attr in ['default_value', 'hide', 'hide_value', 'enabled']:
                    self._value_set(socket, attr, inputItem[1][attr])
                else:
                    self._value_set(socketInterface, attr, inputItem[1][attr])

    def AddOutputs(self, outputs: list[tuple[str, dict]]):
        for outputItem in outputs:
            name = outputItem[1].pop('name')
            socketInterface = self.node_tree.outputs.new(outputItem[0], name)
            socket = self.path_resolve(socketInterface.path_from_id())
            for attr in outputItem[1]:
                if attr in ['default_value', 'hide', 'hide_value', 'enabled']:
                    self._value_set(socket, attr, outputItem[1][attr])
                else:
                    self._value_set(socketInterface, attr, outputItem[1][attr])

class REEShaderAlba(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderAlba'
    bl_label = "RE Engine Alba Shader"
    bl_description = "Alba Shader"
    bl_type = 'REE_SHADER_ALBA'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Alba Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REEShaderDefaultShader(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderDefaultShader'
    bl_label = "RE Engine Default Shader"
    bl_description = "Default Shader"
    bl_type = 'REE_SHADER_DEFAULT'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Default Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REEShaderEyeShader(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderEyeShader'
    bl_label = "RE Engine Eye Shader"
    bl_description = "Eye Shader"
    bl_type = 'REE_SHADER_EYE'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Eye Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REEShaderEyeOuterShader(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderEyeOuterShader'
    bl_label = "RE Engine Eye Outer Shader"
    bl_type = 'REE_SHADER_EYE_OUTER'

    def init(self, context):
        self.node_tree = GetRENodeCopy('EyeOuter Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REEShaderHairShader(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderHairShader'
    bl_label = "RE Engine Hair Shader"
    bl_description = "Hair Shader"
    bl_type = 'REE_SHADER_HAIR'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Hair Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

#class REEShaderSkinShader(ShaderNodeCustomGroup, NodeHelper):
#    bl_name = 'REEShaderSkinShader'
#    bl_label = "RE Engine Skin Shader"
#    bl_description = "Skin Shader"
#    bl_type = 'REE_SHADER_SKIN'
#
#    def init(self, context):
#        self.node_tree = GetRENodeCopy('Skin Shader')
#        self.width = 240.0
#
#    def draw_label(self):
#        return self.bl_label
#
#    def copy(self, node):
#        self.node_tree = DeepCopyNodeTree(node.node_tree)
#
#    def free(self):
#        CleanNodeTree(self.node_tree)
#        self.node_tree = None
#
#    @classmethod
#    def Register(cls):
#        bpy.utils.register_class(cls)
#
#    @classmethod
#    def Unregister(cls):
#        bpy.utils.unregister_class(cls)

class REEShaderTransparentShader(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderTransparentShader'
    bl_label = "RE Engine Transparent Shader"
    bl_description = "Transparent Shader"
    bl_type = 'REE_SHADER_TRANSPARENT'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Transparent Shader')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REEShaderDynamic(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REEShaderDynamic'
    bl_label = "RE Engine Dynamic Shader"
    bl_description = "Changeable shader"
    bl_type = 'REE_SHADER_DYNAMIC'

    reShaderDict = {
        'DefS': "Default Shader",
        #'Skin': "Skin Shader",
        'Tran': "Transparent Shader",
        'Hair': "Hair Shader",
        'EyeO': "EyeOuter Shader",
        'EyeS': "Eye Shader",
        'Alba': "Alba Shader",
    }

    def _ChangeTypeEnum(self, context: bpy.types.Context):
        self.free()
        self._NewNodeTree(REEShaderDynamic.reShaderDict[self.reShaderType])

    reShaderType: EnumProperty(
        name="Type",
        description="Type of REE shader to use",
        items= [
            ('DefS', "Default Shader", "Generic REE shader"),
            #('Skin', "Skin Shader", "Can use a wrinkle map as input"),
            ('Tran', "Transparent Shader", "Has transparency"),
            ('Hair', "Hair Shader", "Hair"),
            ('EyeO', "Eye Outer Shader", "Used for the outer mesh of the eye"),
            ('EyeS', "Eye Shader", "Eyeball"),
            ('Alba', "Alba Shader", "ALBA texture"),
        ],
        default="DefS",
        update=_ChangeTypeEnum,
    )

    def _NewNodeTree(self, reShaderType: REShaderNodeTreeEnum):
        self.node_tree = GetRENodeCopy(reShaderType)

    def ChangeType(self, reShaderType: REShaderNodeTreeEnum):
        self.free()
        self._NewNodeTree(reShaderType)
        self.reShaderType = list(self.reShaderDict.keys())[list(self.reShaderDict.values()).index(reShaderType)]

    def init(self, context):
        self._NewNodeTree('Default Shader')
        self.width = 240.0

    def draw_buttons(self, context, layout):
        isActive =  context.active_node == self

        row1 = layout.row(align=True)
        row1.prop(self, "reShaderType")
        if self.reShaderType == 'DefS':
            row2 = layout.row(align=True)
            row2.operator(NODE_OT_AddWrinkleMap.bl_idname if isActive else NODE_OT_AddWrinkleMap_Disable.bl_idname)
        row3 = layout.row(align=True)
        row3.operator(NODE_OT_AutoconnectREShader.bl_idname if isActive else
                      NODE_OT_AutoconnectREShader_Disable.bl_idname)

    def draw_buttons_ext(self, context, layout):
        isActive = context.active_node == self

        row1 = layout.row(align=True)
        row1.prop(self, "reShaderType")
        if self.reShaderType == 'DefS':
            row2 = layout.row(align=True)
            row2.operator(NODE_OT_AddWrinkleMap.bl_idname if isActive else NODE_OT_AddWrinkleMap_Disable.bl_idname)
        row3 = layout.row(align=True)
        row3.operator(NODE_OT_AutoconnectREShader.bl_idname if isActive else
                      NODE_OT_AutoconnectREShader_Disable.bl_idname)

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        if node.node_tree:
            self.node_tree = DeepCopyNodeTree(node.node_tree)
        else:
            self._NewNodeTree('Default Shader')

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeWrinkleMap(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REENodeWrinkleMap'
    bl_label = "RE Engine Wrinkle Map"
    bl_description = "Wrinkle Map"
    bl_type = 'REE_NODE_WRINKLE_MAP'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Wrinkle Map')
        self.width = 240.0

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "reShaderType")

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeHeadMSK4(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REENodeHeadMSK4'
    bl_label = "RE Engine Head MSK 4"
    bl_description = "Head MSK 4"
    bl_type = 'REE_NODE_HEAD_MSK4'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Head MSK 4')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeNormalWrinkles(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REENodeNormalWrinkles'
    bl_label = "RE Engine Normal Wrinkles"
    bl_description = "Normal Wrinkles"
    bl_type = 'REE_NODE_NORMAL_WRINKLES'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Normal Wrinkles')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        self.node_tree = DeepCopyNodeTree(node.node_tree)

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeAlbedoWrinkles(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REENodeAlbedoWrinkles'
    bl_label = "RE Engine Albedo Wrinkles"
    bl_description = "Albedo Wrinkles"
    bl_type = 'REE_NODE_ALBEDO_WRINKLES' 'REE_SHADER_DYNAMIC' 'REE_NODE_DYNAMIC'

    def init(self, context):
        self.node_tree = GetRENodeCopy('Albedo Wrinkles')
        self.width = 240.0

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        if node.node_tree:
            self.node_tree = DeepCopyNodeTree(self.node_tree)
        else:
            self.node_tree = GetRENodeCopy('Default Shader')

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeDynamic(ShaderNodeCustomGroup, NodeHelper):
    bl_name = 'REENodeDynamic'
    bl_label = "RE Engine Dynamic Node"
    bl_description = "Changeable Nodes"
    bl_type = 'REE_NODE_DYNAMIC'

    reShaderDict = {
        'AlbW': "Albedo Wrinkles",
        'HMS4': "Head MSK 4",
        'NrmW': "Normal Wrinkles",
        'WriM': "Wrinkle Map"
    }

    def _ChangeTypeEnum(self, context: bpy.types.Context):
        self.free()
        self._NewNodeTree(REENodeDynamic.reShaderDict[self.reShaderType])

    reShaderType: EnumProperty(
        name="Type",
        description="Type of REE shader to use",
        items= [
            ('AlbW', "Albedo Wrinkles", "Wrinkle colormap"),
            ('HMS4', "Head MSK 4", "Head MSK 4 values"),
            ('NrmW', "Normal Wrinkles", "Wrinkle normalmap"),
            ('WriM', "Wrinkle Map", "Used to translate values from wrinkle maps to shader"),
        ],
        default="AlbW",
        update=_ChangeTypeEnum,
    )

    def ChangeType(self, reShaderType: REShaderNodeTreeEnum):
        self.free()
        self._NewNodeTree(reShaderType)
        self.reShaderType = list(self.reShaderDict.keys())[list(self.reShaderDict.values()).index(reShaderType)]

    def _NewNodeTree(self, reNodeType: RENodeNodeTreeEnum):
        self.node_tree = GetRENodeCopy(reNodeType)

    def init(self, context):
        self._NewNodeTree('Default Shader')
        self.width = 240.0

    def draw_buttons(self, context, layout):
        layout.prop(self, "reShaderType")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "reShaderType")

    def draw_label(self):
        return self.bl_label

    def copy(self, node):
        if node.node_tree:
            self.node_tree = DeepCopyNodeTree(node.node_tree)
        else:
            self._NewNodeTree('Default Shader')

    def free(self):
        CleanNodeTree(self.node_tree)
        self.node_tree = None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class NODE_OT_AutoconnectREShader(Operator):
    bl_idname = "reengine.auto_connect_shader_node"
    bl_label = "Auto Connect"
    bl_description = "Automatically connect nodes"

    def execute(self, context: bpy.types.Context):
        node: bpy.types.Node = context.active_node

        if node is None:
            return {'CANCELLED'}

        AutoconnectRENodes(node)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_node is not None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class NODE_OT_AddWrinkleMap(Operator):
    bl_idname = "reengine.add_wrinkle_map_node"
    bl_label = "Add Wrinkle Map"
    bl_description = "Add a Wrinkle Map node"

    def execute(self, context: bpy.types.Context):
        node: bpy.types.Node = context.active_node

        if node is None:
            return {'CANCELLED'}

        currNode = node
        wmNode: REENodeWrinkleMap = currNode.id_data.nodes.new(type='REENodeWrinkleMap')
        wmNode.location = (currNode.location[0] - currNode.width - 100.0, currNode.location[1])
        currNode.id_data.links.new(currNode.inputs["BaseMetalMap"], wmNode.outputs["BaseMetalMap"])
        currNode.id_data.links.new(currNode.inputs["NormalRoughnessMap"], wmNode.outputs["NormalRoughnessMap"])
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_node is not None

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

# Stupid workarounds to show a disabled button
class NODE_OT_AutoconnectREShader_Disable(Operator):
    bl_idname = NODE_OT_AutoconnectREShader.bl_idname.__add__("_disable")
    bl_label = NODE_OT_AutoconnectREShader.bl_label
    bl_description = NODE_OT_AutoconnectREShader.bl_description

    def execute(self, context: bpy.types.Context):
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return False

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

# Stupid workarounds to show a disabled button
class NODE_OT_AddWrinkleMap_Disable(Operator):
    bl_idname = NODE_OT_AddWrinkleMap.bl_idname.__add__("_disable")
    bl_label = NODE_OT_AddWrinkleMap.bl_label
    bl_description = NODE_OT_AddWrinkleMap.bl_description

    def execute(self, context: bpy.types.Context):
        return {'FINISHED'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return False

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class REENodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'

customShaderClasses = [
    REEShaderAlba, REEShaderDefaultShader, REEShaderEyeShader, REEShaderEyeOuterShader, REEShaderHairShader,
    REEShaderTransparentShader, REEShaderDynamic
]

customNodeClasses = [ REENodeAlbedoWrinkles, REENodeHeadMSK4, REENodeNormalWrinkles, REENodeWrinkleMap, REENodeDynamic]

customNodeCategories = [
    REENodeCategory('REEngineShaders', "RE Engine Shader",
        items=[
            NodeItem(custom.bl_name) for custom in customShaderClasses
        ]
    ),
    REENodeCategory('REEngineNodes', "RE Engine Node",
        items=[
            NodeItem(custom.bl_name) for custom in customNodeClasses
        ]
    ),
]

def Register():
    NODE_OT_AutoconnectREShader.Register()
    NODE_OT_AddWrinkleMap.Register()
    NODE_OT_AutoconnectREShader_Disable.Register()
    NODE_OT_AddWrinkleMap_Disable.Register()
    for customNodeClass in customShaderClasses + customNodeClasses:
        customNodeClass.Register()

    nodeitems_utils.register_node_categories('REECustomShaderNodes', customNodeCategories)


def Unregister():
    nodeitems_utils.unregister_node_categories('REECustomShaderNodes')

    NODE_OT_AutoconnectREShader.Unregister()
    NODE_OT_AddWrinkleMap.Unregister()
    NODE_OT_AutoconnectREShader_Disable.Unregister()
    NODE_OT_AddWrinkleMap_Disable.Unregister()
    for customNodeClass in customNodeClasses:
        customNodeClass.Unregister()