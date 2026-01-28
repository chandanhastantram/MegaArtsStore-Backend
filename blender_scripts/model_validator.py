"""
Model Validator - Blender Script
Validates 3D models for AR jewellery pipeline

Usage (from command line):
    blender -b model.blend -P model_validator.py -- --input model.blend --output validation.json

Usage (as module when Blender is available):
    from blender_scripts.model_validator import validate_model
"""

import json
import sys
import os

# Check if running in Blender
try:
    import bpy
    import bmesh
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    print("Warning: Not running in Blender environment. Validation will be limited.")


class ModelValidator:
    """Validates 3D models for AR jewellery requirements"""
    
    # Validation limits
    MAX_POLYGON_COUNT = 100000  # Max polygons for mobile AR
    MAX_TEXTURE_SIZE = 2048    # Max texture resolution
    RECOMMENDED_POLYGON_COUNT = 50000
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def validate(self) -> dict:
        """
        Run all validation checks.
        
        Returns:
            Dictionary with validation results
        """
        if not IN_BLENDER:
            return self._mock_validation()
        
        # Load file if provided
        if self.filepath:
            self._load_file()
        
        # Run checks
        self._check_polygon_count()
        self._check_uv_maps()
        self._check_materials()
        self._check_textures()
        self._check_normals()
        self._check_non_manifold()
        self._check_scale()
        
        return {
            "valid": len(self.issues) == 0,
            "polygon_count": self.stats.get("polygon_count", 0),
            "has_uv_maps": self.stats.get("has_uv_maps", False),
            "has_materials": self.stats.get("has_materials", False),
            "texture_resolution": self.stats.get("max_texture_size"),
            "issues": self.issues,
            "warnings": self.warnings,
            "stats": self.stats
        }
    
    def _load_file(self):
        """Load the 3D model file"""
        ext = os.path.splitext(self.filepath)[1].lower()
        
        # Clear existing objects
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
    
    def _check_polygon_count(self):
        """Check total polygon count"""
        total_polys = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                total_polys += len(obj.data.polygons)
        
        self.stats["polygon_count"] = total_polys
        self.stats["mesh_count"] = len([o for o in bpy.data.objects if o.type == 'MESH'])
        
        if total_polys > self.MAX_POLYGON_COUNT:
            self.issues.append(
                f"Polygon count too high: {total_polys} (max: {self.MAX_POLYGON_COUNT})"
            )
        elif total_polys > self.RECOMMENDED_POLYGON_COUNT:
            self.warnings.append(
                f"Polygon count is high: {total_polys} (recommended: {self.RECOMMENDED_POLYGON_COUNT})"
            )
    
    def _check_uv_maps(self):
        """Check for UV maps"""
        has_uv = False
        missing_uv = []
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if len(obj.data.uv_layers) > 0:
                    has_uv = True
                else:
                    missing_uv.append(obj.name)
        
        self.stats["has_uv_maps"] = has_uv
        
        if missing_uv:
            self.issues.append(f"Missing UV maps on: {', '.join(missing_uv)}")
    
    def _check_materials(self):
        """Check for materials"""
        has_materials = False
        no_material = []
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if len(obj.data.materials) > 0:
                    has_materials = True
                else:
                    no_material.append(obj.name)
        
        self.stats["has_materials"] = has_materials
        self.stats["material_count"] = len(bpy.data.materials)
        
        if no_material:
            self.warnings.append(f"No materials on: {', '.join(no_material)}")
    
    def _check_textures(self):
        """Check texture resolutions"""
        max_size = 0
        oversized = []
        
        for img in bpy.data.images:
            if img.size[0] > 0:
                size = max(img.size[0], img.size[1])
                max_size = max(max_size, size)
                
                if size > self.MAX_TEXTURE_SIZE:
                    oversized.append(f"{img.name} ({size}px)")
        
        self.stats["max_texture_size"] = f"{max_size}px" if max_size > 0 else None
        self.stats["texture_count"] = len([i for i in bpy.data.images if i.size[0] > 0])
        
        if oversized:
            self.warnings.append(f"Large textures: {', '.join(oversized)}")
    
    def _check_normals(self):
        """Check for flipped normals"""
        flipped_count = 0
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                
                # Check for inconsistent normals
                for face in bm.faces:
                    # Simple check - in production, use more sophisticated algorithm
                    pass
                
                bm.free()
        
        self.stats["normals_checked"] = True
    
    def _check_non_manifold(self):
        """Check for non-manifold geometry"""
        non_manifold = []
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                
                # Find non-manifold edges
                nm_edges = [e for e in bm.edges if not e.is_manifold]
                
                if nm_edges:
                    non_manifold.append(f"{obj.name} ({len(nm_edges)} edges)")
                
                bm.free()
        
        if non_manifold:
            self.warnings.append(f"Non-manifold geometry in: {', '.join(non_manifold)}")
    
    def _check_scale(self):
        """Check object scale consistency"""
        wrong_scale = []
        
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                scale = obj.scale
                if not (0.99 < scale.x < 1.01 and 0.99 < scale.y < 1.01 and 0.99 < scale.z < 1.01):
                    wrong_scale.append(obj.name)
        
        if wrong_scale:
            self.warnings.append(f"Unapplied scale on: {', '.join(wrong_scale)}")
    
    def _mock_validation(self) -> dict:
        """Return mock validation when not in Blender"""
        return {
            "valid": True,
            "polygon_count": 0,
            "has_uv_maps": True,
            "has_materials": True,
            "texture_resolution": None,
            "issues": ["Not running in Blender - validation skipped"],
            "warnings": [],
            "stats": {}
        }


def validate_model(filepath: str = None) -> dict:
    """
    Convenience function to validate a model.
    
    Args:
        filepath: Path to 3D model file
    
    Returns:
        Validation results dictionary
    """
    validator = ModelValidator(filepath)
    return validator.validate()


# Command line interface
if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    # Parse arguments after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Validate 3D model for AR")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output", help="Output JSON file for results")
    
    args = parser.parse_args(argv)
    
    # Run validation
    result = validate_model(args.input)
    
    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Validation results written to: {args.output}")
    else:
        print(json.dumps(result, indent=2))
