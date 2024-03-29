from .REEMeshFile import *
from .REEMDFFile import *
from . import Shader
from . import CustomNodes
import mathutils
import bpy
import os.path

# Transformation matrix
transformMatrix = mathutils.Matrix([ [1.0, 0.0,  0.0, 0.0],
                                     [0.0, 0.0, -1.0, 0.0],
                                     [0.0, 1.0,  0.0, 0.0],
                                     [0.0, 0.0,  0.0, 0.0] ])


def GetMDFRoot(path: str) -> str:
    from pathlib import Path
    parts = Path(path).parts

    # Look for the x64 folder and return its directory if present
    for idx, part in enumerate(parts):
        if part.lower() == "x64":
            root = parts[0]
            for i in range(1, idx + 1):
                root = os.path.join(root, parts[i])

            return root

    # Return the directory of the mdf file itself if not x64 folder was found
    return os.path.dirname(path)


def ReadMDFFile(path: str) -> MDF:
    mdfBuffer = None
    with open(path, 'rb') as reMDFFile:
        mdfBuffer = reMDFFile.read(-1)

    if mdfBuffer is None:
        raise RuntimeError(f"Failed to open \"{path}\"")

    return MDF(mdfBuffer)

def ReadREModel(path: str) -> REEMesh:
    meshBuffer = None
    with open(path, 'rb') as reModelFile:
        meshBuffer = reModelFile.read(-1)

    if meshBuffer is None:
        raise RuntimeError(f"Failed to open \"{path}\"")

    return REEMesh(meshBuffer)

def LoadREModel(meshPath: str, mdfPath: str or None = None, useHQTex: bool = True, assetRoot: str or None = None,
                hqLODOnly: bool = False, mainGeoOnly: bool = False, loadArmature: bool = True):
    # Open the model file and read it
    reModel = ReadREModel(meshPath)

    loadArmature = loadArmature and reModel.hasArmature

    # Make collection
    modelCollection = bpy.data.collections.new(os.path.splitext(os.path.splitext(os.path.basename(meshPath))[0])[0])
    bpy.context.scene.collection.children.link(modelCollection)

    # Get the name string buffer from the file
    nameBuffer: list[str] = reModel.nameTable.nameList

    # Set up the armature
    armature = bpy.data.armatures.new("Armature")
    armatureObject = bpy.data.objects.new("Armature", armature)
    armature.show_axes = False
    armature.display_type = 'OCTAHEDRAL'

    modelCollection.objects.link(armatureObject)
    bpy.context.view_layer.objects.active = armatureObject
    armatureObject.select_set(True)

    # Storing the mode before changing it, so we can restore it when we are done
    modeBefore = bpy.context.object.mode

    # Keep a list of the material
    meshMaterials: list[bpy.types.Material] = []

    # Create the materials
    mdf: MDF or None = None
    if mdfPath is not None:
        mdf = ReadMDFFile(mdfPath)

    for matNameIdx in reModel.materialNameIndexBuffer:
        matName = nameBuffer[matNameIdx]
        mat = Shader.CreateMaterial(matName)

        if len(mat.node_tree.links) == 0 and len(mat.node_tree.nodes) == 0:
            meshMaterials.append(mat)

            mdfNode: bpy.types.Node or None = None
            texNodes: list[bpy.types.Node] = []

            outShader: CustomNodes.REEShaderDynamic = mat.node_tree.nodes.new(type='REEShaderDynamic')

            if mdf is not None:
                mdfMat = mdf[matName]
                mdfNode = Shader.AddMDFNode(mat, mdfMat)

                reShaderType = Shader.GuessREShaderType(mat.name, mdfNode)
                if reShaderType == "Skin WM":
                    outShader.ChangeType('Default Shader')
                else:
                    outShader.ChangeType(reShaderType)

                for tex in mdfMat.textureInfo:
                    lqTexPath = tex.filePath
                    hqTexPath = os.path.join("Streaming", tex.filePath)

                    lqTexPath = os.path.join(assetRoot, lqTexPath + ".11") if assetRoot is not None else\
                        os.path.join(GetMDFRoot(mdfPath), lqTexPath + ".11")

                    hqTexPath = os.path.join(assetRoot, hqTexPath + ".11") if assetRoot is not None else\
                        os.path.join(GetMDFRoot(mdfPath), hqTexPath + ".11")

                    texPath:str or None = None

                    if useHQTex and os.path.isfile(hqTexPath):
                        texPath = hqTexPath
                    elif os.path.isfile(lqTexPath):
                        texPath = lqTexPath

                    if texPath is not None:
                        texNode = Shader.AddRETextureToMaterial(mat, texPath)
                        mat.node_tree.links.new(texNode.outputs['Color'], mdfNode.inputs[tex.type])
                        mat.node_tree.links.new(texNode.outputs['Alpha'], mdfNode.inputs[f"{tex.type} - Alpha"])
                        texNodes.append(texNode)

                flags = mdfMat.flags

                mat.shadow_method = 'OPAQUE'

                #flags & int(MaterialFlags.AlphaMaskUsed) or\
                if mdfMat.shaderType == ShaderType.Transparent or mdfMat.shaderType == ShaderType.GUIMeshTransparent or\
                        mdfMat.shaderType == ShaderType.ExpensiveTransparent or\
                        flags & int(MaterialFlags.AlphaTestEnable) or\
                        flags & int(MaterialFlags.BaseAlphaTestEnable) or\
                        flags & int(MaterialFlags.ForcedAlphaTestEnable):
                    mat.blend_method = 'HASHED' if reShaderType == 'Hair Shader' else 'BLEND'
                    mat.shadow_method = 'HASHED'

                if flags & int(MaterialFlags.TwoSideEnable) or flags & int(MaterialFlags.BaseTwoSideEnable) or\
                    flags & int(MaterialFlags.ForcedTwoSideEnable):
                    mat.use_backface_culling = False
                else:
                    mat.use_backface_culling = True

                if flags & MaterialFlags.ShadowCastDisable:
                    mat.shadow_method = 'NONE'

                useSSS = False

                for matProp in mdfMat.properties:
                    if matProp.name == 'SSS_Channel':
                        useSSS =matProp.parameters[0] == 1.0

                mat.use_sss_translucency = useSSS
                mat.use_screen_refraction = reShaderType == 'EyeOuter Shader'

            matOut = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            outShader.label = f"{mat.name} - Output Shader"
            mat.node_tree.links.new(outShader.outputs[0], matOut.inputs[0])

            Shader.RearrangeNodesInEditorWindow(mat.node_tree.nodes)
            if texNodes:
                topNodeY = max(node.location.xy[1] for node in texNodes)

                offset =  (mdfNode.location.xy[1]) - topNodeY
                for node in texNodes:
                    xy = node.location.xy
                    node.location.xy = (xy[0], xy[1] + offset)

            if mdfNode is not None:
                mdfSockets = [socket.name for socket in mdfNode.outputs]
                for inputSocket in outShader.inputs:
                    socketName = inputSocket.name
                    if socketName in mdfSockets:
                        mat.node_tree.links.new(mdfNode.outputs[socketName], outShader.inputs[socketName])

                CustomNodes.AutoconnectRENodes(outShader)

    bpy.ops.object.mode_set(mode='EDIT')

    if loadArmature:
        # Set up bones
        bones = reModel.armature.globalBoneTransforms  # From the file
        bone_index_buffer = reModel.boneNameIndexBuffer

        # First we add all the bones to blender scene because we might need to index bones that need to be there later
        for i in range(reModel.armature.boneCount):
            bone_from_file = bones[i]
            bone = armature.edit_bones.new(nameBuffer[bone_index_buffer[i]])
            bone.matrix = bone_from_file.transformMatrix
            bone.use_relative_parent = True

        # Then we set the parents for the bones
        for i in range(reModel.armature.boneCount):
            bone_parent_index = reModel.armature.boneHierarchy[i].parent
            bone = armature.edit_bones[i]

            if bone_parent_index != -1:
                bone.parent = armature.edit_bones[bone_parent_index]
                #bone.head += bone.parent.head # For local bone transforms


        # Calculate the bone tails
        for bone in armature.edit_bones:
            children = bone.children

            if children:
                childrenPosAverage = mathutils.Vector([.0, .0, .0])

                for c in children:
                    childrenPosAverage += c.head

                childrenPosAverage /= len(children)

                bone.tail = childrenPosAverage.lerp(bone.head, .5 if len(children) > 1 else 0.)

            else:
                bone.tail = bone.head + (bone.head - bone.parent.head) * 0.5

        # Getting around blender being ass and not letting 0 length bones
        for bone in armature.edit_bones:
            if bone.length <= 0.00005:
                bone.tail += mathutils.Vector([0.005, 0.0, 0.0])

    for geoIdx in range(1 if mainGeoOnly else 2):
        # idx == 0: main geometry
        # idx == 1: shadow geometry
        geo = None
        geoCollection = None

        if geoIdx == 0:
            geoCollection = bpy.data.collections.new("Main Geometry")
            modelCollection.children.link(geoCollection)
            geo = reModel.mainModel
        elif reModel.hasShadowGeo:
            geoCollection = bpy.data.collections.new("Shadow Geometry")
            modelCollection.children.link(geoCollection)
            geo = reModel.shadowModel

        if geo is None:
            continue

        # Import all the meshes within a lod group
        for lodIdx, lodGroup in (enumerate(geo.lodGroups[0:1]) if hqLODOnly else enumerate(geo.lodGroups) ):
            lodCollection = bpy.data.collections.new(f"LOD Group - {lodIdx} ({geoIdx} {lodIdx})")
            geoCollection.children.link(lodCollection)

            for mmIdx, mainmesh in enumerate(lodGroup.mainmeshes):
                mainMeshCollection = bpy.data.collections.new(f"Mainmesh - {mmIdx} ({geoIdx} {lodIdx} {mmIdx})")
                lodCollection.children.link(mainMeshCollection)

                for smIdx, submesh in enumerate(mainmesh.submeshes):
                    # Fetching the name of the material
                    materialName = nameBuffer[reModel.materialNameIndexBuffer[submesh.materialID]]

                    # Create the meshes
                    mesh = bpy.data.meshes.new(f"LODGroup_{lodIdx}_Mainmesh_{mmIdx}_Submesh{smIdx} - {materialName}")
                    mesh.from_pydata(submesh.vertexBuffer, [], submesh.faces)
                    mesh.update()

                    # Make object from mesh
                    submeshObject = bpy.data.objects.new(f"Submesh - {smIdx} ({geoIdx} {lodIdx} {mmIdx} {smIdx})", mesh)

                    # Apply uvs (Horizontally flipped)
                    # First layer:
                    if submesh.uv0s.any():
                        mesh.uv_layers.new(name='UV_0')
                        uv0Data = mesh.uv_layers[0].data

                        for u in range(len(uv0Data)):
                            uv = submesh.uv0s[mesh.loops[u].vertex_index]
                            uv0Data[u].uv = (uv[0], 1.0 - uv[1])

                    # Second layer:
                    if submesh.uv1s.any():
                        mesh.uv_layers.new(name='UV_1')
                        uv1Data = mesh.uv_layers[1].data

                        for u in range(len(uv1Data)):
                            uv = submesh.uv1s[mesh.loops[u].vertex_index]
                            uv1Data[u].uv = (uv[0], 1.0 - uv[1])

                        mesh.update()

                    # Apply normals and calculate tangents
                    normal_data: list[mathutils.Vector] = []

                    for face in mesh.polygons:
                        for vert_index in face.vertices:
                            n_and_t = submesh.normalsTangents[vert_index]
                            normal = mathutils.Vector(
                                [n_and_t.normalX,
                                 n_and_t.normalY,
                                 n_and_t.normalZ]
                            )
                            normal.normalize()
                            normal_data.append(normal)

                    # Enable smooth for polygons
                    mesh.polygons.foreach_set("use_smooth", np.full(len(mesh.polygons), True, dtype=bool))

                    # Setting the normals
                    mesh.normals_split_custom_set(normal_data)
                    mesh.use_auto_smooth = True
                    if submesh.uv0s.any():
                        mesh.calc_tangents(uvmap="UV_0")
                    mesh.update()

                    if loadArmature:
                        # Create vertex groups for each bone
                        for i in range(reModel.armature.boneCount):
                            submeshObject.vertex_groups.new(name=nameBuffer[reModel.boneNameIndexBuffer[i]])

                        # Assign vertices to vertex groups
                        for vert in mesh.vertices:
                            v = vert.index
                            boneIndices = submesh.boneInfo[v].indices
                            weights = submesh.boneInfo[v].weights

                            for boneIdx, boneIndex in enumerate(boneIndices):
                                if weights[boneIdx] > 0.0:
                                    vgroup = submeshObject.vertex_groups[reModel.armature.skinBoneMap[boneIndex]]
                                    vgroup.add([v], weights[boneIdx], "REPLACE")

                        # Assign the Armature modifier to the model
                        modifier = submeshObject.modifiers.new(type='ARMATURE', name="Armature")
                        modifier.object = armatureObject

                    # Apply transformation
                    mesh.transform(transformMatrix)
                    mesh.update()

                    # Apply material
                    submeshObject.data.materials.append(bpy.data.materials.get(materialName))

                    # Add the object to collection
                    mainMeshCollection.objects.link(submeshObject)

    if loadArmature:
        # Apply the transformation matrix to the armature in pose mode
        armature.transform(transformMatrix)

    # Restore to the mode before we changed it
    bpy.ops.object.mode_set(mode=modeBefore)

    # Rename the materials to be unique, so they don't conflict with next imports
    for mat in meshMaterials:
        mat.name = f"{os.path.splitext(os.path.basename(meshPath))[0]} - {mat.name}"