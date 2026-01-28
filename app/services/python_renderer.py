"""
Python 3D Rendering Service
Alternative to Blender - pure Python rendering using PyVista and Trimesh
"""

import io
import asyncio
from typing import Optional, List, Tuple
from pathlib import Path
import tempfile
import os

try:
    import pyvista as pv
    import trimesh
    import numpy as np
    from PIL import Image
    RENDERING_AVAILABLE = True
except ImportError:
    RENDERING_AVAILABLE = False


class PythonRenderer:
    """
    Pure Python 3D model renderer.
    No Blender required - uses PyVista and Trimesh.
    """
    
    def __init__(self):
        if not RENDERING_AVAILABLE:
            raise ImportError(
                "Rendering libraries not installed. "
                "Run: pip install pyvista trimesh pillow numpy"
            )
    
    async def render_360(
        self,
        model_path: str,
        output_dir: str,
        angles: List[int] = None,
        resolution: Tuple[int, int] = (1920, 1080)
    ) -> List[str]:
        """
        Render 360° views of a 3D model.
        
        Args:
            model_path: Path to 3D model file
            output_dir: Directory to save renders
            angles: List of rotation angles (default: [0, 45, 90, 135, 180, 225, 270, 315])
            resolution: Image resolution (width, height)
        
        Returns:
            List of output file paths
        """
        if angles is None:
            angles = [0, 45, 90, 135, 180, 225, 270, 315]
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._render_360_sync,
            model_path,
            output_dir,
            angles,
            resolution
        )
    
    def _render_360_sync(
        self,
        model_path: str,
        output_dir: str,
        angles: List[int],
        resolution: Tuple[int, int]
    ) -> List[str]:
        """Synchronous 360° rendering"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Load model
        mesh = pv.read(model_path)
        
        # Center the mesh
        mesh.translate(-mesh.center, inplace=True)
        
        output_files = []
        
        for angle in angles:
            # Create plotter
            plotter = pv.Plotter(off_screen=True, window_size=resolution)
            
            # Add mesh with nice material
            plotter.add_mesh(
                mesh,
                color='gold',
                metallic=0.8,
                roughness=0.2,
                ambient=0.3
            )
            
            # Set camera position (rotate around Y-axis)
            radius = mesh.length * 2
            x = radius * np.sin(np.radians(angle))
            z = radius * np.cos(np.radians(angle))
            
            plotter.camera_position = [
                (x, 0, z),  # Camera position
                (0, 0, 0),  # Focal point
                (0, 1, 0)   # View up
            ]
            
            # Add lighting
            plotter.add_light(pv.Light(position=(10, 10, 10), intensity=0.8))
            plotter.add_light(pv.Light(position=(-10, 10, -10), intensity=0.5))
            
            # Render and save
            output_path = os.path.join(output_dir, f"render_{angle:03d}.png")
            plotter.screenshot(output_path)
            plotter.close()
            
            output_files.append(output_path)
        
        return output_files
    
    async def generate_thumbnail(
        self,
        model_path: str,
        output_path: str,
        resolution: Tuple[int, int] = (800, 800)
    ) -> str:
        """
        Generate a single thumbnail image.
        
        Args:
            model_path: Path to 3D model
            output_path: Output image path
            resolution: Image resolution
        
        Returns:
            Output file path
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._generate_thumbnail_sync,
            model_path,
            output_path,
            resolution
        )
    
    def _generate_thumbnail_sync(
        self,
        model_path: str,
        output_path: str,
        resolution: Tuple[int, int]
    ) -> str:
        """Synchronous thumbnail generation"""
        # Load model
        mesh = pv.read(model_path)
        mesh.translate(-mesh.center, inplace=True)
        
        # Create plotter
        plotter = pv.Plotter(off_screen=True, window_size=resolution)
        
        # Add mesh
        plotter.add_mesh(
            mesh,
            color='gold',
            metallic=0.8,
            roughness=0.2,
            ambient=0.3
        )
        
        # Set camera (45° angle for nice view)
        radius = mesh.length * 2
        plotter.camera_position = [
            (radius * 0.7, radius * 0.5, radius * 0.7),
            (0, 0, 0),
            (0, 1, 0)
        ]
        
        # Lighting
        plotter.add_light(pv.Light(position=(10, 10, 10), intensity=0.8))
        plotter.add_light(pv.Light(position=(-10, 10, -10), intensity=0.5))
        
        # Render
        plotter.screenshot(output_path)
        plotter.close()
        
        return output_path
    
    async def optimize_model(
        self,
        input_path: str,
        output_path: str,
        target_faces: int = 10000
    ) -> dict:
        """
        Optimize 3D model by reducing polygon count.
        
        Args:
            input_path: Input model path
            output_path: Output model path
            target_faces: Target number of faces
        
        Returns:
            Optimization statistics
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._optimize_model_sync,
            input_path,
            output_path,
            target_faces
        )
    
    def _optimize_model_sync(
        self,
        input_path: str,
        output_path: str,
        target_faces: int
    ) -> dict:
        """Synchronous model optimization"""
        # Load with trimesh
        mesh = trimesh.load(input_path)
        
        original_faces = len(mesh.faces)
        original_vertices = len(mesh.vertices)
        
        # Simplify if needed
        if original_faces > target_faces:
            # Calculate reduction ratio
            ratio = target_faces / original_faces
            mesh = mesh.simplify_quadric_decimation(target_faces)
        
        # Export as GLB (optimized format)
        mesh.export(output_path)
        
        return {
            "original_faces": original_faces,
            "original_vertices": original_vertices,
            "optimized_faces": len(mesh.faces),
            "optimized_vertices": len(mesh.vertices),
            "reduction_percentage": round((1 - len(mesh.faces) / original_faces) * 100, 2)
        }
    
    async def extract_dimensions(self, model_path: str) -> dict:
        """
        Extract model dimensions and metadata.
        
        Args:
            model_path: Path to model
        
        Returns:
            Model dimensions and stats
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._extract_dimensions_sync,
            model_path
        )
    
    def _extract_dimensions_sync(self, model_path: str) -> dict:
        """Synchronous dimension extraction"""
        mesh = trimesh.load(model_path)
        
        bounds = mesh.bounds
        extents = mesh.extents
        
        return {
            "width": float(extents[0]),
            "height": float(extents[1]),
            "depth": float(extents[2]),
            "volume": float(mesh.volume) if mesh.is_watertight else None,
            "surface_area": float(mesh.area),
            "center": mesh.center.tolist(),
            "bounds_min": bounds[0].tolist(),
            "bounds_max": bounds[1].tolist(),
            "faces": len(mesh.faces),
            "vertices": len(mesh.vertices),
            "is_watertight": mesh.is_watertight
        }


# Global renderer instance
_renderer: Optional[PythonRenderer] = None


def get_renderer() -> PythonRenderer:
    """Get or create renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = PythonRenderer()
    return _renderer


# ============ Convenience Functions ============

async def render_product_360(
    model_path: str,
    output_dir: str,
    angles: int = 8
) -> List[str]:
    """
    Render 360° product views.
    
    Args:
        model_path: Path to model
        output_dir: Output directory
        angles: Number of angles (default: 8)
    
    Returns:
        List of rendered image paths
    """
    renderer = get_renderer()
    angle_list = [int(360 / angles * i) for i in range(angles)]
    return await renderer.render_360(model_path, output_dir, angle_list)


async def create_product_thumbnail(
    model_path: str,
    output_path: str
) -> str:
    """Create product thumbnail"""
    renderer = get_renderer()
    return await renderer.generate_thumbnail(model_path, output_path)


async def optimize_for_ar(
    input_path: str,
    output_path: str
) -> dict:
    """Optimize model for AR (target: 10k faces)"""
    renderer = get_renderer()
    return await renderer.optimize_model(input_path, output_path, target_faces=10000)
