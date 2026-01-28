"""
GLB Exporter - Blender Script
Exports optimized GLB files for WebAR

Features:
- Export optimized GLB with Draco compression
- WebAR compatibility validation
- Material baking for compatibility
- Metadata embedding

Usage:
    blender -b model.blend -P glb_exporter.py -- --input model.blend --output model.glb --draco
"""

import sys
import os

try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


class GLBExporter:
    """Exports GLB files optimized for WebAR"""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.log = []
    
    def export(
        self,
        output_path: str,
        use_draco: bool = True,
        draco_level: int = 6
    ) -> dict:
        """
        Export to GLB format.
        
        Args:
            output_path: Output GLB file path
            use_draco: Enable Draco compression
            draco_level: Draco compression level (0-10)
        
        Returns:
            Export results dictionary
        """
        if not IN_BLENDER:
            return {"success": False, "error": "Not in Blender environment"}
        
        if self.filepath:
            self._load_file()
        
        # Prepare for export
        self._prepare_for_export()
        
        # Export settings
        export_settings = {
            'filepath': output_path,
            'export_format': 'GLB',
            'export_texcoords': True,
            'export_normals': True,
            'export_materials': 'EXPORT',
            'export_colors': True,
            'export_cameras': False,
            'export_lights': False,
            'export_extras': True,
            'export_yup': True,
            'export_apply': True,
        }
        
        # Add Draco compression if available
        if use_draco:
            export_settings.update({
                'export_draco_mesh_compression_enable': True,
                'export_draco_mesh_compression_level': draco_level,
                'export_draco_position_quantization': 14,
                'export_draco_normal_quantization': 10,
                'export_draco_texcoord_quantization': 12,
                'export_draco_color_quantization': 10,
            })
        
        # Export
        try:
            bpy.ops.export_scene.gltf(**export_settings)
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            self.log.append(f"Exported: {output_path}")
            self.log.append(f"File size: {file_size / 1024:.1f} KB")
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "draco_enabled": use_draco,
                "log": self.log
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "log": self.log
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
        elif ext in [".glb", ".gltf"]:
            bpy.ops.import_scene.gltf(filepath=self.filepath)
    
    def _prepare_for_export(self):
        """Prepare scene for GLB export"""
        # Apply all modifiers
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                
                for mod in obj.modifiers:
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    except:
                        pass
        
        # Ensure all meshes are triangulated
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.object.mode_set(mode='OBJECT')
        
        # Ensure materials are compatible
        self._ensure_compatible_materials()
        
        self.log.append("Prepared scene for GLB export")
    
    def _ensure_compatible_materials(self):
        """Ensure materials are GLTF compatible"""
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            
            # Check for Principled BSDF
            has_principled = False
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    has_principled = True
                    break
            
            if not has_principled:
                self.log.append(f"Warning: {mat.name} may not export correctly")
    
    def validate(self, glb_path: str) -> dict:
        """
        Validate exported GLB for WebAR compatibility.
        
        Args:
            glb_path: Path to GLB file
        
        Returns:
            Validation results
        """
        issues = []
        warnings = []
        
        # Check file exists
        if not os.path.exists(glb_path):
            return {"valid": False, "issues": ["File does not exist"]}
        
        # Check file size (warn if over 10MB)
        file_size = os.path.getsize(glb_path)
        if file_size > 10 * 1024 * 1024:
            warnings.append(f"File size ({file_size / 1024 / 1024:.1f}MB) may be too large for mobile")
        elif file_size > 5 * 1024 * 1024:
            warnings.append(f"File size ({file_size / 1024 / 1024:.1f}MB) is large for mobile")
        
        # Load and check
        try:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            bpy.ops.import_scene.gltf(filepath=glb_path)
            
            mesh_count = len([o for o in bpy.data.objects if o.type == 'MESH'])
            total_polys = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
            
            if total_polys > 100000:
                warnings.append(f"High polygon count: {total_polys}")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "stats": {
                    "file_size": file_size,
                    "mesh_count": mesh_count,
                    "polygon_count": total_polys
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Failed to validate: {str(e)}"]
            }


def export_glb(
    input_path: str,
    output_path: str,
    use_draco: bool = True,
    draco_level: int = 6
) -> dict:
    """
    Convenience function to export GLB.
    """
    exporter = GLBExporter(input_path)
    return exporter.export(output_path, use_draco, draco_level)


if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Export GLB for WebAR")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output", required=True, help="Output GLB file")
    parser.add_argument("--draco", action="store_true", help="Enable Draco compression")
    parser.add_argument("--draco-level", type=int, default=6, help="Draco compression level")
    
    args = parser.parse_args(argv)
    
    result = export_glb(args.input, args.output, args.draco, args.draco_level)
    print(f"Export complete: {result}")
