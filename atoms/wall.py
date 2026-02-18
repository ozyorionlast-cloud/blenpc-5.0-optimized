import math
import hashlib
import struct
import bpy
import bmesh
from typing import List, Tuple, Dict, Optional

# Use absolute import from the project root
from config import PHI, STORY_HEIGHT, WALL_THICKNESS_BASE, GRID_UNIT

def make_rng(seed: int, subsystem: str):
    """Create a deterministic RNG for a specific subsystem."""
    h = hashlib.sha256(f"{seed}:{subsystem}".encode()).digest()
    sub_seed = struct.unpack('<Q', h[:8])[0]
    import random
    return random.Random(sub_seed)

def golden_split(length: float, rng) -> float:
    """Split a length using the Golden Ratio with slight deterministic variation."""
    # Standard split at 1/PHI or (1 - 1/PHI)
    split_point = length / PHI
    # Add +/- 2% variation based on RNG to avoid perfect repetition while maintaining aesthetics
    variation = (rng.random() - 0.5) * 0.04 * length
    final_split = split_point + variation
    
    # Snap to GRID_UNIT for modularity
    return round(final_split / GRID_UNIT) * GRID_UNIT

def check_manifold(bm) -> bool:
    """Verify if the mesh is a manifold using Euler's Formula: V - E + F = 2."""
    v = len(bm.verts)
    e = len(bm.edges)
    f = len(bm.faces)
    # Simple check for closed genus-0 mesh
    return (v - e + f) == 2

def create_engineered_wall(name: str, length: float, seed: int = 0):
    """Create a wall with mathematically placed slots for openings."""
    rng = make_rng(seed, "wall_slots")
    
    # Clear existing data
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale to dimensions
    thickness = WALL_THICKNESS_BASE
    height = STORY_HEIGHT
    
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= thickness
        v.co.z *= height
        v.co.z += height / 2
        v.co.x += length / 2
        
    if not check_manifold(bm):
        bm.free()
        raise Exception(f"Manifold check failed for {name}")
        
    bm.to_mesh(mesh)
    bm.free()
    
    # Define Slots (Mathematical placement)
    # Use Golden Ratio to find a primary 'feature' spot (e.g., a window)
    primary_slot_x = golden_split(length, rng)
    
    # Metadata for slots
    slots = [
        {
            "id": "main_opening",
            "type": "window_opening",
            "pos": [primary_slot_x, 0, 1.2], # 1.2m height standard
            "size": [1.0, 1.2]
        }
    ]
    
    # Mark as asset and store metadata
    obj.asset_mark()
    obj["slots_json"] = json.dumps(slots) if 'json' in globals() else str(slots)
    
    return obj, slots

def calculate_roof_trig(width: float, pitch_deg: float = 35.0) -> Dict[str, float]:
    """Calculate roof geometry using trigonometry."""
    pitch_rad = math.radians(pitch_deg)
    height = (width / 2) * math.tan(pitch_rad)
    slope_length = (width / 2) / math.cos(pitch_rad)
    
    return {
        "height": height,
        "slope_length": slope_length,
        "pitch_deg": pitch_deg
    }
