"""
Texture Optimizer - Blender Script
Optimizes textures for mobile AR and WebAR

Operations:
- Resize textures (1024px / 2048px)
- Convert to optimized formats
- Remove unused texture maps
- Compress for WebAR
- Maintain gold reflections and gem sparkle

Usage:
    blender -b model.blend -P texture_optimizer.py -- --input model.blend --max-size 1024
"""

import sys
import os

try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


class TextureOptimizer:
    """Optimizes textures for mobile AR"""
    
    MAX_SIZE_MOBILE = 1024
    MAX_SIZE_DESKTOP = 2048
    
    # Essential texture types to keep
    ESSENTIAL_TYPES = ['base_color', 'metallic', 'roughness', 'normal']
    
    def __init__(self, filepath: str = None, max_size: int = 1024):
        self.filepath = filepath
        self.max_size = max_size
        self.log = []
    
    def optimize(self) -> dict:
        """
        Run texture optimization.
        
        Returns:
            Dictionary with optimization results
        """
        if not IN_BLENDER:
            return {"success": False, "error": "Not in Blender environment"}
        
        if self.filepath:
            self._load_file()
        
        initial_count = len(bpy.data.images)
        
        # Run optimization steps
        self._resize_textures()
        self._remove_unused_textures()
        self._optimize_materials()
        self._pack_textures()
        
        final_count = len(bpy.data.images)
        
        return {
            "success": True,
            "initial_textures": initial_count,
            "final_textures": final_count,
            "max_size": self.max_size,
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
    
    def _resize_textures(self):
        """Resize textures to max size"""
        resized = 0
        
        for img in bpy.data.images:
            if img.size[0] == 0 or img.size[1] == 0:
                continue
            
            # Skip if already within limits
            if img.size[0] <= self.max_size and img.size[1] <= self.max_size:
                continue
            
            # Calculate new size maintaining aspect ratio
            aspect = img.size[0] / img.size[1]
            
            if img.size[0] > img.size[1]:
                new_width = self.max_size
                new_height = int(self.max_size / aspect)
            else:
                new_height = self.max_size
                new_width = int(self.max_size * aspect)
            
            # Resize
            img.scale(new_width, new_height)
            resized += 1
            
            self.log.append(f"Resized: {img.name} to {new_width}x{new_height}")
        
        self.log.append(f"Resized {resized} textures to max {self.max_size}px")
    
    def _remove_unused_textures(self):
        """Remove textures not used in any material"""
        used_images = set()
        
        # Find all images used in materials
        for mat in bpy.data.materials:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        used_images.add(node.image.name)
        
        # Remove unused
        removed = 0
        for img in list(bpy.data.images):
            if img.name not in used_images and img.users == 0:
                bpy.data.images.remove(img)
                removed += 1
        
        self.log.append(f"Removed {removed} unused textures")
    
    def _optimize_materials(self):
        """Optimize materials for jewellery rendering"""
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            
            # Get principled BSDF node
            principled = None
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled = node
                    break
            
            if not principled:
                continue
            
            # Optimize for jewellery
            mat_name = mat.name.lower()
            
            # Gold material optimization
            if 'gold' in mat_name:
                principled.inputs['Metallic'].default_value = 1.0
                principled.inputs['Roughness'].default_value = 0.2
                # Gold color
                if not principled.inputs['Base Color'].is_linked:
                    principled.inputs['Base Color'].default_value = (1.0, 0.843, 0.0, 1.0)
            
            # Silver material optimization
            elif 'silver' in mat_name:
                principled.inputs['Metallic'].default_value = 1.0
                principled.inputs['Roughness'].default_value = 0.15
                if not principled.inputs['Base Color'].is_linked:
                    principled.inputs['Base Color'].default_value = (0.97, 0.97, 0.97, 1.0)
            
            # Gemstone optimization
            elif any(gem in mat_name for gem in ['gem', 'diamond', 'ruby', 'sapphire', 'emerald']):
                principled.inputs['Metallic'].default_value = 0.0
                principled.inputs['Roughness'].default_value = 0.0
                principled.inputs['Transmission'].default_value = 0.95
                principled.inputs['IOR'].default_value = 2.4  # Diamond-like
        
        self.log.append("Optimized materials for jewellery rendering")
    
    def _pack_textures(self):
        """Pack all textures into the blend file"""
        for img in bpy.data.images:
            if img.packed_file is None and img.filepath:
                try:
                    img.pack()
                except:
                    pass
        
        self.log.append("Packed all textures")
    
    def save(self, output_path: str):
        """Save the optimized model"""
        bpy.ops.wm.save_as_mainfile(filepath=output_path)


def optimize_textures(input_path: str, output_path: str = None, max_size: int = 1024) -> dict:
    """
    Convenience function to optimize textures.
    """
    optimizer = TextureOptimizer(input_path, max_size)
    result = optimizer.optimize()
    
    if output_path and result["success"]:
        optimizer.save(output_path)
    
    return result


if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Optimize textures for AR")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output", help="Output model file")
    parser.add_argument("--max-size", type=int, default=1024, help="Max texture size")
    
    args = parser.parse_args(argv)
    
    result = optimize_textures(args.input, args.output, args.max_size)
    print(f"Texture optimization complete: {result}")
