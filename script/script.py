import bpy
import os

# ---------- Main Export Operator Class ----------

class ExportSelectedMeshesOperator(bpy.types.Operator):
    # Blender identifier for the operator (used in buttons/menus)
    bl_idname = "export.custom_gltf_batch"
    bl_label = "Export Selected Meshes (GLTF)"
    bl_description = "Export each selected mesh to its own folder inside chosen directory"

    # Property to let the user choose a folder using Blender's file browser
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Folder to export meshes to",
        subtype='DIR_PATH'
    )

    def execute(self, context):
        export_path = self.directory  # Get the folder chosen by the user

        if not export_path:
            self.report({'ERROR'}, "No directory selected.")
            return {'CANCELLED'}  # Cancel the operation if no path is provided

        # Loop through all selected objects
        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue  # Skip non-mesh objects

            # Create folder structure: <SelectedFolder>/<ObjectName>/Models/
            object_folder = os.path.join(export_path, obj.name)
            models_folder = os.path.join(object_folder, "3DModels")
            os.makedirs(models_folder, exist_ok=True)  # Make directories if they don't exist

            # Create filename for the exported object (GLB format)
            filename = f"{obj.name}.glb"
            full_export_path = os.path.join(models_folder, filename)

            # Select only the current object for export
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            # Try exporting the object to GLTF/GLB
            try:
                bpy.ops.export_scene.gltf(filepath=full_export_path, use_selection=True)
                self.report({'INFO'}, f"Exported {obj.name}")
            except Exception as e:
                self.report({'WARNING'}, f"Failed to export {obj.name}: {e}")

            # Deselect the object after export
            obj.select_set(False)

        return {'FINISHED'}  # Signal successful completion

    def invoke(self, context, event):
        # Open file browser to choose folder when operator is invoked
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ---------- Register Operator in Blender UI ----------

def menu_func(self, context):
    # Add this operator to Blender's Export menu (File > Export)
    self.layout.operator(ExportSelectedMeshesOperator.bl_idname)

def register():
    # Register the custom operator and add it to the UI menu
    bpy.utils.register_class(ExportSelectedMeshesOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    # Remove operator and UI menu entry on unregister
    bpy.utils.unregister_class(ExportSelectedMeshesOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

# ---------- Enable script execution when run directly ----------
if __name__ == "__main__":
    register()
