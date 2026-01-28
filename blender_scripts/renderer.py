"""
Renderer - Blender Script
Renders preview images and animations for jewellery

Features:
- Preview image rendering (front, angled, close-up)
- 360° turntable animation
- Transparent background support
- Eevee for fast preview, Cycles for quality

Usage:
    blender -b model.blend -P renderer.py -- --input model.blend --output-dir ./renders --type preview
"""

import sys
import os
import math

try:
    import bpy
    from mathutils import Vector
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


class JewelleryRenderer:
    """Renders jewellery preview images and animations"""
    
    # Render resolutions
    PREVIEW_SIZE = (1024, 1024)
    TURNTABLE_SIZE = (720, 720)
    TURNTABLE_FRAMES = 36  # 10 degrees per frame
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.log = []
    
    def render_previews(self, output_dir: str, use_cycles: bool = False) -> dict:
        """
        Render preview images.
        
        Args:
            output_dir: Output directory for renders
            use_cycles: Use Cycles (slow but quality) vs Eevee (fast)
        
        Returns:
            Dictionary with render results
        """
        if not IN_BLENDER:
            return {"success": False, "error": "Not in Blender environment"}
        
        if self.filepath:
            self._load_file()
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup render settings
        self._setup_render(use_cycles)
        
        # Setup transparent background
        self._setup_transparent_background()
        
        # Import lighting
        from blender_scripts.lighting_rigs import setup_jewellery_lighting
        setup_jewellery_lighting()
        
        outputs = {}
        
        # Render front view
        self._setup_camera_front()
        front_path = os.path.join(output_dir, "preview_front.png")
        self._render_frame(front_path)
        outputs["preview_front"] = front_path
        
        # Render angled view
        self._setup_camera_angle()
        angle_path = os.path.join(output_dir, "preview_angle.png")
        self._render_frame(angle_path)
        outputs["preview_angle"] = angle_path
        
        # Render close-up (gemstone detail)
        self._setup_camera_closeup()
        detail_path = os.path.join(output_dir, "preview_detail.png")
        self._render_frame(detail_path)
        outputs["preview_detail"] = detail_path
        
        return {
            "success": True,
            "outputs": outputs,
            "log": self.log
        }
    
    def render_turntable(self, output_path: str, use_cycles: bool = False) -> dict:
        """
        Render 360° turntable animation.
        
        Args:
            output_path: Output video/gif path
            use_cycles: Use Cycles for quality
        
        Returns:
            Dictionary with render results
        """
        if not IN_BLENDER:
            return {"success": False, "error": "Not in Blender environment"}
        
        if self.filepath:
            self._load_file()
        
        # Setup render settings for animation
        self._setup_render(use_cycles, resolution=self.TURNTABLE_SIZE)
        self._setup_transparent_background()
        
        # Import lighting
        from blender_scripts.lighting_rigs import setup_jewellery_lighting
        setup_jewellery_lighting()
        
        # Setup camera
        self._setup_camera_front()
        
        # Setup turntable animation
        self._setup_turntable_animation()
        
        # Setup output format
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.filepath = output_path
        
        # Render animation
        bpy.ops.render.render(animation=True)
        
        return {
            "success": True,
            "output": output_path,
            "frames": self.TURNTABLE_FRAMES,
            "log": self.log
        }
    
    def _load_file(self):
        """Load the 3D model file"""
        ext = os.path.splitext(self.filepath)[1].lower()
        
        # Keep only mesh objects when loading
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        if ext == ".blend":
            bpy.ops.wm.open_mainfile(filepath=self.filepath)
        elif ext in [".glb", ".gltf"]:
            bpy.ops.import_scene.gltf(filepath=self.filepath)
    
    def _setup_render(self, use_cycles: bool = False, resolution: tuple = None):
        """Configure render settings"""
        resolution = resolution or self.PREVIEW_SIZE
        
        scene = bpy.context.scene
        
        if use_cycles:
            scene.render.engine = 'CYCLES'
            scene.cycles.samples = 128
            scene.cycles.use_denoising = True
        else:
            scene.render.engine = 'BLENDER_EEVEE'
            scene.eevee.taa_render_samples = 64
        
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]
        scene.render.resolution_percentage = 100
        
        self.log.append(f"Setup render: {'Cycles' if use_cycles else 'Eevee'} at {resolution}")
    
    def _setup_transparent_background(self):
        """Enable transparent background"""
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    
    def _get_scene_center(self) -> Vector:
        """Get center of all mesh objects"""
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        
        if not meshes:
            return Vector((0, 0, 0))
        
        center = Vector((0, 0, 0))
        for obj in meshes:
            center += obj.location
        center /= len(meshes)
        
        return center
    
    def _get_scene_radius(self) -> float:
        """Get radius to encompass all objects"""
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        
        max_dist = 0
        center = self._get_scene_center()
        
        for obj in meshes:
            for v in obj.data.vertices:
                world_co = obj.matrix_world @ v.co
                dist = (world_co - center).length
                max_dist = max(max_dist, dist)
        
        return max_dist if max_dist > 0 else 1
    
    def _create_camera(self) -> bpy.types.Object:
        """Create and return camera"""
        # Remove existing cameras
        for cam in [o for o in bpy.data.objects if o.type == 'CAMERA']:
            bpy.data.objects.remove(cam)
        
        # Create new camera
        cam_data = bpy.data.cameras.new("RenderCamera")
        cam_obj = bpy.data.objects.new("RenderCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        bpy.context.scene.camera = cam_obj
        
        return cam_obj
    
    def _setup_camera_front(self):
        """Setup camera for front view"""
        camera = self._create_camera()
        center = self._get_scene_center()
        radius = self._get_scene_radius()
        
        # Position camera in front
        camera.location = (0, -radius * 3, center.z)
        camera.rotation_euler = (math.radians(90), 0, 0)
        
        self.log.append("Camera: front view")
    
    def _setup_camera_angle(self):
        """Setup camera for 3/4 angle view"""
        camera = self._create_camera()
        center = self._get_scene_center()
        radius = self._get_scene_radius()
        
        # Position camera at angle
        dist = radius * 3
        angle = math.radians(45)
        
        camera.location = (
            dist * math.sin(angle),
            -dist * math.cos(angle),
            center.z + radius * 0.5
        )
        
        # Point at center
        direction = center - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        
        self.log.append("Camera: angled view")
    
    def _setup_camera_closeup(self):
        """Setup camera for close-up detail view"""
        camera = self._create_camera()
        center = self._get_scene_center()
        radius = self._get_scene_radius()
        
        # Closer position
        camera.location = (radius * 0.5, -radius * 1.5, center.z + radius * 0.3)
        
        direction = center - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        
        self.log.append("Camera: close-up view")
    
    def _setup_turntable_animation(self):
        """Setup turntable rotation animation"""
        scene = bpy.context.scene
        
        scene.frame_start = 1
        scene.frame_end = self.TURNTABLE_FRAMES
        
        # Create empty at center to rotate objects around
        empty = bpy.data.objects.new("TurntableEmpty", None)
        bpy.context.collection.objects.link(empty)
        
        # Parent all meshes to empty
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.parent = empty
        
        # Animate rotation
        empty.rotation_euler = (0, 0, 0)
        empty.keyframe_insert(data_path="rotation_euler", frame=1)
        
        empty.rotation_euler = (0, 0, math.radians(360))
        empty.keyframe_insert(data_path="rotation_euler", frame=self.TURNTABLE_FRAMES + 1)
        
        # Set linear interpolation
        for fcurve in empty.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'
        
        self.log.append(f"Setup turntable animation: {self.TURNTABLE_FRAMES} frames")
    
    def _render_frame(self, output_path: str):
        """Render single frame"""
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        self.log.append(f"Rendered: {output_path}")


def render_previews(input_path: str, output_dir: str, use_cycles: bool = False) -> dict:
    """Convenience function to render previews"""
    renderer = JewelleryRenderer(input_path)
    return renderer.render_previews(output_dir, use_cycles)


def render_turntable(input_path: str, output_path: str, use_cycles: bool = False) -> dict:
    """Convenience function to render turntable"""
    renderer = JewelleryRenderer(input_path)
    return renderer.render_turntable(output_path, use_cycles)


if __name__ == "__main__" and IN_BLENDER:
    import argparse
    
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description="Render jewellery previews")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--type", choices=["preview", "turntable", "all"], default="preview")
    parser.add_argument("--cycles", action="store_true", help="Use Cycles renderer")
    
    args = parser.parse_args(argv)
    
    renderer = JewelleryRenderer(args.input)
    
    if args.type in ["preview", "all"]:
        result = renderer.render_previews(args.output_dir, args.cycles)
        print(f"Preview render: {result}")
    
    if args.type in ["turntable", "all"]:
        turntable_path = os.path.join(args.output_dir, "turntable.mp4")
        result = renderer.render_turntable(turntable_path, args.cycles)
        print(f"Turntable render: {result}")
