"""
Lighting Rigs - Blender Script
Professional lighting setups for jewellery rendering

Presets:
- Studio soft light
- Jewellery reflection rig
- Gem sparkle highlights
- Gold realism lighting

Usage:
    from blender_scripts.lighting_rigs import setup_jewellery_lighting
    setup_jewellery_lighting()
"""

import math

try:
    import bpy
    from mathutils import Vector
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


def clear_lights():
    """Remove all existing lights"""
    if not IN_BLENDER:
        return
    
    for light in [o for o in bpy.data.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(light)


def create_light(
    name: str,
    light_type: str,
    location: tuple,
    rotation: tuple = (0, 0, 0),
    energy: float = 100,
    color: tuple = (1, 1, 1),
    size: float = 1.0
) -> bpy.types.Object:
    """Create a light with specified parameters"""
    if not IN_BLENDER:
        return None
    
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = energy
    light_data.color = color
    
    if light_type == 'AREA':
        light_data.size = size
    elif light_type == 'SPOT':
        light_data.spot_size = math.radians(45)
        light_data.spot_blend = 0.5
    
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    
    light_obj.location = location
    light_obj.rotation_euler = tuple(math.radians(r) for r in rotation)
    
    return light_obj


def setup_studio_soft():
    """
    Studio soft light setup.
    Creates a three-point lighting system with soft shadows.
    """
    if not IN_BLENDER:
        return
    
    clear_lights()
    
    # Key light - main illumination from front-left
    create_light(
        name="Key_Light",
        light_type="AREA",
        location=(-2, -3, 2.5),
        rotation=(45, 0, -30),
        energy=500,
        color=(1.0, 0.98, 0.95),
        size=2.0
    )
    
    # Fill light - softer from front-right
    create_light(
        name="Fill_Light",
        light_type="AREA",
        location=(2, -2, 1.5),
        rotation=(60, 0, 30),
        energy=200,
        color=(0.95, 0.95, 1.0),
        size=3.0
    )
    
    # Back light - rim lighting from behind
    create_light(
        name="Back_Light",
        light_type="AREA",
        location=(0, 3, 2),
        rotation=(-45, 0, 0),
        energy=300,
        color=(1.0, 1.0, 1.0),
        size=1.5
    )
    
    # Enable soft shadows
    bpy.context.scene.eevee.use_soft_shadows = True


def setup_jewellery_reflection():
    """
    Jewellery reflection rig.
    Optimized for metallic surfaces with strong reflections.
    """
    if not IN_BLENDER:
        return
    
    clear_lights()
    
    # Large overhead softbox
    create_light(
        name="Overhead_Softbox",
        light_type="AREA",
        location=(0, 0, 4),
        rotation=(0, 0, 0),
        energy=800,
        color=(1.0, 0.99, 0.97),
        size=4.0
    )
    
    # Front fill for face visibility
    create_light(
        name="Front_Fill",
        light_type="AREA",
        location=(0, -3, 1),
        rotation=(75, 0, 0),
        energy=200,
        color=(1.0, 1.0, 1.0),
        size=2.0
    )
    
    # Left accent for edge definition
    create_light(
        name="Left_Accent",
        light_type="AREA",
        location=(-3, 0, 0.5),
        rotation=(90, 0, -90),
        energy=300,
        color=(1.0, 0.95, 0.9),
        size=1.0
    )
    
    # Right accent mirror
    create_light(
        name="Right_Accent",
        light_type="AREA",
        location=(3, 0, 0.5),
        rotation=(90, 0, 90),
        energy=300,
        color=(0.95, 0.95, 1.0),
        size=1.0
    )
    
    # Setup world for reflections
    world = bpy.context.scene.world
    if world:
        world.use_nodes = True
        bg = world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1)
            bg.inputs['Strength'].default_value = 0.5


def setup_gem_sparkle():
    """
    Gem sparkle highlight setup.
    Creates point lights for diamond-like sparkle effects.
    """
    if not IN_BLENDER:
        return
    
    # Add sparkle lights to existing setup
    # Small bright points for gem highlights
    
    sparkle_positions = [
        (-1, -2, 2),
        (1, -2, 2),
        (0, -1.5, 3),
        (-0.5, -2.5, 1.5),
        (0.5, -2.5, 1.5),
    ]
    
    for i, pos in enumerate(sparkle_positions):
        create_light(
            name=f"Sparkle_{i+1}",
            light_type="POINT",
            location=pos,
            energy=50,
            color=(1.0, 1.0, 1.0)
        )


def setup_gold_realism():
    """
    Gold realism lighting.
    Warm tones to enhance gold material appearance.
    """
    if not IN_BLENDER:
        return
    
    clear_lights()
    
    # Warm key light
    create_light(
        name="Warm_Key",
        light_type="AREA",
        location=(-2, -2.5, 3),
        rotation=(45, 0, -30),
        energy=600,
        color=(1.0, 0.92, 0.8),  # Warm gold tone
        size=2.5
    )
    
    # Cool fill for contrast
    create_light(
        name="Cool_Fill",
        light_type="AREA",
        location=(2, -1.5, 1.5),
        rotation=(60, 0, 45),
        energy=150,
        color=(0.9, 0.95, 1.0),  # Cool blue tint
        size=2.0
    )
    
    # Warm rim light
    create_light(
        name="Warm_Rim",
        light_type="AREA",
        location=(0, 2.5, 2),
        rotation=(-50, 0, 0),
        energy=400,
        color=(1.0, 0.9, 0.75),
        size=1.5
    )
    
    # Bottom reflection bounce
    create_light(
        name="Bottom_Bounce",
        light_type="AREA",
        location=(0, 0, -1),
        rotation=(180, 0, 0),
        energy=100,
        color=(1.0, 0.95, 0.9),
        size=3.0
    )


def setup_jewellery_lighting(preset: str = "reflection"):
    """
    Main function to setup jewellery lighting.
    
    Args:
        preset: One of 'studio', 'reflection', 'sparkle', 'gold'
    """
    if not IN_BLENDER:
        return {"success": False, "error": "Not in Blender environment"}
    
    if preset == "studio":
        setup_studio_soft()
    elif preset == "reflection":
        setup_jewellery_reflection()
    elif preset == "sparkle":
        setup_jewellery_reflection()
        setup_gem_sparkle()
    elif preset == "gold":
        setup_gold_realism()
    else:
        # Default to reflection rig
        setup_jewellery_reflection()
    
    return {"success": True, "preset": preset}


# Convenience exports
__all__ = [
    'setup_jewellery_lighting',
    'setup_studio_soft',
    'setup_jewellery_reflection',
    'setup_gem_sparkle',
    'setup_gold_realism',
    'clear_lights',
    'create_light'
]
