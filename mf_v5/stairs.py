"""Stairwell generation and stair geometry for multi-story buildings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import bpy
import bmesh
from .datamodel import Rect, Room
from .config import STORY_HEIGHT, TEXTURE_TILE_SIZE

@dataclass(frozen=True)
class Stairwell:
    rect: Rect          # Position of the stairwell hole
    floor_from: int
    floor_to: int
    stair_type: str = "straight" # "straight", "spiral" (planned)

def generate_stairwell(rooms: List[Room], corridor_rect: Rect) -> Optional[Stairwell]:
    """
    Place a stairwell at the end of the corridor.
    Ensures vertical alignment across all floors.
    """
    if not corridor_rect:
        return None
    
    # Place stairwell at the 'north' end of the corridor
    # Size: 2.5m x 4.0m for a standard straight stair
    stair_width = 2.0
    stair_depth = 4.0
    
    # Center it on the corridor width
    cx = (corridor_rect.min_x + corridor_rect.max_x) / 2
    
    stair_rect = Rect(
        min_x = cx - stair_width / 2,
        min_y = corridor_rect.max_y - stair_depth,
        max_x = cx + stair_width / 2,
        max_y = corridor_rect.max_y
    )
    
    return Stairwell(stair_rect, 0, 99) # Spans all floors

def build_stair_mesh(stairwell: Stairwell, total_floors: int, name: str = "Stairs", material: Optional[bpy.types.Material] = None) -> bpy.types.Object:
    """Create a mesh for the stairs connecting all floors."""
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    if material:
        obj.data.materials.append(material)
        
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    r = stairwell.rect
    num_steps = 16 # Steps per floor
    step_height = STORY_HEIGHT / num_steps
    step_depth = (r.max_y - r.min_y) / num_steps
    
    for f_idx in range(total_floors - 1):
        base_z = f_idx * STORY_HEIGHT
        
        for i in range(num_steps):
            z_start = base_z + i * step_height
            y_start = r.min_y + i * step_depth
            
            # Create a box for each step
            v = []
            # Bottom 4
            v.append(bm.verts.new((r.min_x, y_start, z_start)))
            v.append(bm.verts.new((r.max_x, y_start, z_start)))
            v.append(bm.verts.new((r.max_x, y_start + step_depth, z_start)))
            v.append(bm.verts.new((r.min_x, y_start + step_depth, z_start)))
            # Top 4
            v.append(bm.verts.new((r.min_x, y_start, z_start + step_height)))
            v.append(bm.verts.new((r.max_x, y_start, z_start + step_height)))
            v.append(bm.verts.new((r.max_x, y_start + step_depth, z_start + step_height)))
            v.append(bm.verts.new((r.min_x, y_start + step_depth, z_start + step_height)))
            
            try:
                faces = [
                    bm.faces.new(v[0:4]), bm.faces.new(v[4:8]),
                    bm.faces.new((v[0], v[1], v[5], v[4])),
                    bm.faces.new((v[1], v[2], v[6], v[5])),
                    bm.faces.new((v[2], v[3], v[7], v[6])),
                    bm.faces.new((v[3], v[0], v[4], v[7]))
                ]
                # UVs
                for face in faces:
                    for loop in face.loops:
                        co = loop.vert.co
                        loop[uv_layer].uv = (co.x / TEXTURE_TILE_SIZE, co.z / TEXTURE_TILE_SIZE)
            except ValueError:
                pass
                
    bm.to_mesh(mesh)
    bm.free()
    return obj
