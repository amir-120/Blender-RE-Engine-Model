from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup, Operator, Panel
from bpy_extras.io_utils import ImportHelper
import bpy

class UIProps(PropertyGroup):

    meshPath: StringProperty(
        name="Mesh",
        subtype='FILE_PATH',
        description="Path to the mesh file",
        default="",
        options={'TEXTEDIT_UPDATE'}
        )

    mdfPath: StringProperty(
        name="MDF",
        subtype='FILE_PATH',
        description="Path to the MDF file",
        default="",
        options={'TEXTEDIT_UPDATE'}
        )

    assetRootDir: StringProperty(
        name="Root",
        subtype='DIR_PATH',
        description="Root directory for assets (x64)",
        default="",
        options={'TEXTEDIT_UPDATE'}
    )

    importMDF: BoolProperty(
        name="Load Materials",
        description="Load the info saved inside the MDF file about materials",
        default=False
    )

    hqTextures: BoolProperty(
        name="High Quality Textures",
        description="Import streaming textures if present in the root",
        default=True
    )

    customRoot: BoolProperty(
        name="Use Custom Asset Root Dir",
        description="Use a manually set custom directory as the base of the game asset references",
        default=False
    )

    importArmature: BoolProperty(
        name="Load Armature",
        description="Import the bone structure and rig the mesh to it",
        default=True
    )

    importHQLODOnly: BoolProperty(
        name="Only Load HQ LOD",
        description="Only import the LOD group with the highest quality (LOD Group 1)",
        default=True
    )

    importShadowGeo: BoolProperty(
        name="Load Shadow Geometry",
        description="Import the geometry used to cast shadow if present in the file",
        default=False
    )

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)
        bpy.types.Scene.reProps = PointerProperty(type=cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)


class OBJECT_PT_REEModel(Panel):
    bl_category = "RE Engine Mesh"
    bl_idname = "OBJECT_PT_REEMesh"
    bl_label = "RE Engine Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw(self, context: bpy.types.Context):
        props = context.scene.reProps
        col1 = self.layout.column(align=True)

        modelBox = col1.box()
        col1ModelBox = modelBox.column(align=True)
        col1ModelBox.label(text="Model")
        modelRow = col1ModelBox.row(align=True)
        modelRow.separator(factor=1.0)
        modelRow.prop(props, "meshPath")

        col1.prop(props, "importMDF")
        if props.importMDF:
            mdfBox = col1.box()
            col1MDFBox = mdfBox.column(align=True)
            col1MDFBox.label(text="Material")
            materialRow = col1MDFBox.row(align=True)
            materialRow.separator(factor=1.0)
            materialRow.prop(props, "mdfPath")

            col1MDFBox.separator(factor=1.0)
            col1MDFBox.prop(props, "hqTextures")

            col1MDFBox.separator(factor=1.0)
            col1MDFBox.prop(props, "customRoot")
            if props.customRoot:
                rootRow = col1MDFBox.row(align=True)
                rootRow.separator(factor=1.0)
                rootRow.prop(props, "assetRootDir")

        importBox = col1.box()
        col1ImportBox = importBox.column(align=True)
        col1ImportBox.label(text="Import")

        armRow = col1ImportBox.row(align=True)
        armRow.separator(factor=1.0)
        armRow.prop(props, "importArmature")

        lodRow = col1ImportBox.row(align=True)
        lodRow.separator(factor=1.0)
        lodRow.prop(props, "importHQLODOnly")

        shadRow = col1ImportBox.row(align=True)
        shadRow.separator(factor=1.0)
        shadRow.prop(props, "importShadowGeo")

        importButtonRow = col1ImportBox.row()
        importButtonRow.alignment = 'CENTER'
        importButtonRow.operator(OBJECT_OT_REMeshImport.bl_idname)

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)


class OBJECT_OT_REMeshImport(Operator):
    bl_idname = "reengine.import_mesh"
    bl_label = "Import"
    bl_description = "Import the model"

    def execute(self, context: bpy.types.Context):
        from . import Import

        props = context.scene.reProps
        Import.LoadREModel(props.meshPath, props.mdfPath if props.importMDF else None, props.hqTextures,
                           props.assetRootDir if props.customRoot else None, props.importHQLODOnly,
                           not props.importShadowGeo, props.importArmature)

        return {'FINISHED'}

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

class IMPORT_OT_REModel(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.reemesh"
    bl_label = "Import RE Engine Model"
    bl_options = {'UNDO', 'PRESET'}
    bl_description = "Load an RE Engine mesh file"

    directory: StringProperty()

    filename_ext = ".1808282334"
    filter_glob: StringProperty(default="*.1808282334;*.10", options={'HIDDEN'})

    files: CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )

    def draw(self, context):
        layout = self.layout
        props = context.scene.reProps

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(props, "importArmature")
        layout.prop(props, "importHQLODOnly")
        layout.prop(props, "importShadowGeo")
        layout.prop(props, "hqTextures")

    def execute(self, context):
        from . import Import
        import os

        props = context.scene.reProps
        if self.files:
            ret = {'CANCELLED'}
            dirName = os.path.dirname(self.filepath)
            modelPath: tuple[str or None, str or None] = (None, None)
            for file in self.files:
                path = os.path.join(dirName, file.name)
                ext = os.path.splitext(file.name)[1]
                if ext == ".1808282334":
                    modelPath = (path, modelPath[1])
                elif ext == ".10":
                    modelPath = (modelPath[0], path)

            if modelPath[0] is None:
                if modelPath[1] is None:
                    self.report({'ERROR'}, "Select a file")
                    return {'CANCELLED'}

                self.report({'ERROR'}, "A mesh file must be selected")
                return {'CANCELLED'}

            Import.LoadREModel(modelPath[0], modelPath[1] if modelPath[1] is not None else None, props.hqTextures, None,
                                props.importHQLODOnly, not props.importShadowGeo, props.importArmature)
            ret = {'FINISHED'}

            return ret
        else:
            ret = {'CANCELLED'}

            if os.path.splitext(self.filepath)[1] == ".1808282334":
                Import.LoadREModel(props.filepath, None, props.hqTextures, None, props.importHQLODOnly,
                                   not props.importShadowGeo, props.importArmature)
                ret = {'FINISHED'}

            return ret

    @classmethod
    def Register(cls):
        bpy.utils.register_class(cls)

    @classmethod
    def Unregister(cls):
        bpy.utils.unregister_class(cls)

def MenuFuncImport(self, context: bpy.types.Context):
    self.layout.operator(IMPORT_OT_REModel.bl_idname, text="RE Engine Model (.mesh.1808282334/.mdf2.10)")

def Register():
    UIProps.Register()
    OBJECT_OT_REMeshImport.Register()
    OBJECT_PT_REEModel.Register()
    IMPORT_OT_REModel.Register()
    bpy.types.TOPBAR_MT_file_import.append(MenuFuncImport)

def Unregister():
    UIProps.Unregister()
    OBJECT_OT_REMeshImport.Unregister()
    OBJECT_PT_REEModel.Unregister()
    IMPORT_OT_REModel.Unregister()
    bpy.types.TOPBAR_MT_file_import.remove(MenuFuncImport)