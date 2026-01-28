"""
AR Alignment - Blender Script
Aligns jewellery models for AR wrist try-on

Operations:
- Center bangle at origin
- Align rotation with wrist axis
- Detect inner diameter
- Calculate wrist-fit radius
- Generate AR metadata

Usage:
    blender -b model.blend -P ar_alignment.py -- --input model.blend --output ar_config.json
"""

import json
import sys
import os
import math

try:
    import bpy
    from mathutils import Vector, Matrix
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


class ARAligner:
    """Aligns jewellery for AR wrist try-on"""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.log = []
        self.ar_config = {}
    
    def align(self) -> dict:
        """
        Run AR alignment.
        
        Returns:
            AR configuration dictionary
        """
        if not IN_BLENDER:
            return self._mock_config()
        
        if self.filepath:
            self._load_file()
        
        # Run alignment steps
        self._center_at_origin()
        self._align_to_wrist_axis()
        
        # Analyze geometry
        dimensions = self._analyze_dimensions()
        
        # Generate AR config
        self.ar_config = {
            "scale": self._calculate_scale(dimensions),
            "rotation": self._get_alignment_rotation(),
            "offset": [0, 0, 0],
            "wrist_diameter": dimensions.get("inner_diameter", 6.5),
            "bangle_thickness": dimensions.get("thickness", 0.5),
            "center_point": [0, 0, 0],
            "bounding_box": dimensions.get("bounding_box", [0, 0, 0])
        }
        
        return {
            "success": True,
            "ar_config": self.ar_config,
            "log": self.log
        }
    
    def _load_file(self):
        """Load the 3D model file"""
        ext = os.path.splitext(self.filepath)[1].lower()
        
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        if ext == ".blend":
            bpy.ops.wm.open_mainfile(filepath=self.filepath)
        elif ext in [".glb", ".gltf"]:
            bpy.ops.import_scene.gltf(filepath=self.filepath)
    
    def _center_at_origin(self):
        """Center all geometry at world origin"""
        # Get all mesh objects
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        
        if not meshes:
            return
        
        # Calculate combined bounds center
        min_co = Vector((float('inf'), float('inf'), float('inf')))
        max_co = Vector((float('-inf'), float('-inf'), float('-inf')))
        
        for obj in meshes:
            for v in obj.data.vertices:
                world_co = obj.matrix_world @ v.co
                min_co.x = min(min_co.x, world_co.x)
                min_co.y = min(min_co.y, world_co.y)
                min_co.z = min(min_co.z, world_co.z)
                max_co.x = max(max_co.x, world_co.x)
                max_co.y = max(max_co.y, world_co.y)
                max_co.z = max(max_co.z, world_co.z)
        
        center = (min_co + max_co) / 2
        
        # Move all objects to center
        for obj in meshes:
            obj.location -= center
        
        self.log.append("Centered geometry at origin")
    
    def _align_to_wrist_axis(self):
        """Align bangle to wrist axis (Y-axis)"""
        # For bangles, the hole should align with Y-axis (wrist direction)
        # This assumes the bangle is circular in XZ plane
        
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        
        for obj in meshes:
            # Get bounding box dimensions
            dims = obj.dimensions
            
            # If X and Z are similar (circular) and Y is thinner, it's aligned
            # If Y and Z are similar and X is thinner, rotate 90° on Z
            # If X and Y are similar and Z is thinner, rotate 90° on X
            
            xy_ratio = min(dims.x, dims.y) / max(dims.x, dims.y) if max(dims.x, dims.y) > 0 else 1
            xz_ratio = min(dims.x, dims.z) / max(dims.x, dims.z) if max(dims.x, dims.z) > 0 else 1
            yz_ratio = min(dims.y, dims.z) / max(dims.y, dims.z) if max(dims.y, dims.z) > 0 else 1
            
            # The circular face should be in XZ plane (hole goes through Y)
            if xz_ratio > 0.8:
                # Already aligned - XZ is the circular face
                pass
            elif xy_ratio > 0.8 and dims.z < dims.x * 0.5:
                # XY is circular, rotate to make XZ circular
                obj.rotation_euler.x = math.radians(90)
            elif yz_ratio > 0.8 and dims.x < dims.y * 0.5:
                # YZ is circular, rotate to make XZ circular
                obj.rotation_euler.z = math.radians(90)
        
        # Apply rotations
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(rotation=True)
        
        self.log.append("Aligned to wrist axis (Y)")
    
    def _analyze_dimensions(self) -> dict:
        """Analyze bangle dimensions"""
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        
        if not meshes:
            return {}
        
        # Get combined dimensions
        min_co = Vector((float('inf'), float('inf'), float('inf')))
        max_co = Vector((float('-inf'), float('-inf'), float('-inf')))
        
        for obj in meshes:
            for v in obj.data.vertices:
                world_co = obj.matrix_world @ v.co
                min_co.x = min(min_co.x, world_co.x)
                min_co.y = min(min_co.y, world_co.y)
                min_co.z = min(min_co.z, world_co.z)
                max_co.x = max(max_co.x, world_co.x)
                max_co.y = max(max_co.y, world_co.y)
                max_co.z = max(max_co.z, world_co.z)
        
        dims = max_co - min_co
        
        # Estimate inner diameter (outer diameter minus estimated thickness)
        outer_diameter = max(dims.x, dims.z)
        thickness = dims.y  # Bangle thickness/width
        
        # Rough estimate: inner diameter is about 85% of outer for typical bangles
        inner_diameter = outer_diameter * 0.85
        
        # Convert to cm (assuming model is in meters)
        result = {
            "bounding_box": [dims.x, dims.y, dims.z],
            "outer_diameter": outer_diameter * 100,  # to cm
            "inner_diameter": inner_diameter * 100,  # to cm
            "thickness": thickness * 100  # to cm
        }
        
        self.log.append(f"Dimensions: {result}")
        return result
    
    def _calculate_scale(self, dimensions: dict) -> float:
        """Calculate appropriate scale for AR"""
        # Target inner diameter for average wrist: ~6.5cm
        target_diameter = 6.5
        current_diameter = dimensions.get("inner_diameter", 6.5)
        
        if current_diameter > 0:
            scale = target_diameter / current_diameter
        else:
            scale = 1.0
        
        return round(scale, 4)
    
    def _get_alignment_rotation(self) -> list:
        """Get final rotation values"""
        # Return rotation in degrees for WebAR
        return [0, 0, 0]
    
    def _mock_config(self) -> dict:
        """Return mock config when not in Blender"""
        return {
            "success": True,
            "ar_config": {
                "scale": 1.0,
                "rotation": [0, 0, 0],
                "offset": [0, 0, 0],
                "wrist_diameter": 6.5,
                "bangle_thickness": 0.5,
                "center_point": [0, 0, 0]
            },
            "log": ["Mock config generated (Blender not available)"]
        }
    
    def save_config(self, output_path: str):
        """Save AR config to JSON file"""
        with open(output_path, "w") as f:
            json.dump(self.ar_config, f, indent=2)
        self.log.append(f"Saved AR config to: {output_path}")
    
    def save_model(self, output_path: str):
        """Save aligned model"""
        bpy.ops.wm.save_as_mainfile(filepath=output_path)


def align_for_ar(input_path: str, config_output: str = None) -> dict:
    """
    Convenience function to align model for AR.
    """
    aligner = ARAligner(input_path)
    result = aligner.align()
    
    if config_output and result["success"]:
        aligner.save_config(config_output)
    
    return result


if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Align model for AR")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output", help="Output AR config JSON")
    
    args = parser.parse_args(argv)
    
    result = align_for_ar(args.input, args.output)
    print(json.dumps(result, indent=2))
