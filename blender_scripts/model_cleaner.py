"""
Model Cleaner - Blender Script
Cleans and prepares 3D models for AR processing

Operations:
- Remove unused objects and hidden meshes
- Merge duplicate vertices
- Apply all transforms
- Recalculate normals
- Fix shading issues
- Auto-origin correction
- Enforce unit system

Usage:
    blender -b model.blend -P model_cleaner.py -- --input model.blend --output cleaned.blend
"""

import sys
import os

try:
    import bpy
    import bmesh
    from mathutils import Vector
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


class ModelCleaner:
    """Cleans 3D models for AR jewellery pipeline"""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.log = []
    
    def clean(self) -> dict:
        """
        Run all cleaning operations.
        
        Returns:
            Dictionary with cleaning results
        """
        if not IN_BLENDER:
            return {"success": False, "error": "Not in Blender environment"}
        
        if self.filepath:
            self._load_file()
        
        # Run cleaning operations
        self._remove_unused_data()
        self._delete_hidden_objects()
        self._merge_duplicate_vertices()
        self._apply_transforms()
        self._recalculate_normals()
        self._fix_shading()
        self._set_origin_to_center()
        self._enforce_unit_system()
        
        return {
            "success": True,
            "log": self.log,
            "objects_remaining": len([o for o in bpy.data.objects if o.type == 'MESH'])
        }
    
    def _load_file(self):
        """Load the 3D model file"""
        ext = os.path.splitext(self.filepath)[1].lower()
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        if ext == ".blend":
            bpy.ops.wm.open_mainfile(filepath=self.filepath)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=self.filepath)
        elif ext == ".obj":
            bpy.ops.import_scene.obj(filepath=self.filepath)
        elif ext in [".glb", ".gltf"]:
            bpy.ops.import_scene.gltf(filepath=self.filepath)
        
        self.log.append(f"Loaded: {self.filepath}")
    
    def _remove_unused_data(self):
        """Remove unused datablocks"""
        # Remove unused meshes
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        
        # Remove unused materials
        for mat in bpy.data.materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        
        # Remove unused images
        for img in bpy.data.images:
            if img.users == 0:
                bpy.data.images.remove(img)
        
        self.log.append("Removed unused data blocks")
    
    def _delete_hidden_objects(self):
        """Delete hidden and empty objects"""
        to_delete = []
        
        for obj in bpy.data.objects:
            # Delete if hidden in viewport
            if obj.hide_viewport or obj.hide_get():
                to_delete.append(obj)
            # Delete empty mesh objects
            elif obj.type == 'MESH' and len(obj.data.vertices) == 0:
                to_delete.append(obj)
            # Keep only mesh objects for AR (remove cameras, lights, etc.)
            elif obj.type not in ['MESH', 'EMPTY']:
                to_delete.append(obj)
        
        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
        
        self.log.append(f"Deleted {len(to_delete)} hidden/empty objects")
    
    def _merge_duplicate_vertices(self):
        """Merge duplicate vertices in all meshes"""
        merged_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                
                # Merge by distance (0.0001 units)
                bpy.ops.mesh.remove_doubles(threshold=0.0001)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                merged_count += 1
        
        self.log.append(f"Merged duplicate vertices in {merged_count} meshes")
    
    def _apply_transforms(self):
        """Apply all transforms (location, rotation, scale)"""
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                obj.select_set(False)
        
        self.log.append("Applied all transforms")
    
    def _recalculate_normals(self):
        """Recalculate normals for all meshes"""
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
        
        self.log.append("Recalculated normals")
    
    def _fix_shading(self):
        """Set smooth shading for all meshes"""
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                # Set smooth shading
                for poly in obj.data.polygons:
                    poly.use_smooth = True
                
                # Enable auto smooth for better normals
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = 1.0472  # 60 degrees
        
        self.log.append("Applied smooth shading with auto-smooth")
    
    def _set_origin_to_center(self):
        """Set origin to center of geometry for all meshes"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.ops.object.select_all(action='DESELECT')
        
        self.log.append("Set origin to geometry center")
    
    def _enforce_unit_system(self):
        """Set scene units to meters"""
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.length_unit = 'METERS'
        bpy.context.scene.unit_settings.scale_length = 1.0
        
        self.log.append("Set unit system to meters")
    
    def save(self, output_path: str):
        """Save the cleaned model"""
        ext = os.path.splitext(output_path)[1].lower()
        
        if ext == ".blend":
            bpy.ops.wm.save_as_mainfile(filepath=output_path)
        elif ext == ".fbx":
            bpy.ops.export_scene.fbx(filepath=output_path)
        elif ext in [".glb", ".gltf"]:
            bpy.ops.export_scene.gltf(filepath=output_path)
        
        self.log.append(f"Saved to: {output_path}")


def clean_model(input_path: str, output_path: str = None) -> dict:
    """
    Convenience function to clean a model.
    
    Args:
        input_path: Path to input model
        output_path: Path for cleaned output (optional)
    
    Returns:
        Cleaning results dictionary
    """
    cleaner = ModelCleaner(input_path)
    result = cleaner.clean()
    
    if output_path and result["success"]:
        cleaner.save(output_path)
    
    return result


if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Clean 3D model for AR")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output", required=True, help="Output cleaned model file")
    
    args = parser.parse_args(argv)
    
    result = clean_model(args.input, args.output)
    print(f"Cleaning complete: {result}")
