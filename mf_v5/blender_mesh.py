"""Blender-specific mesh generation, UV mapping, and bmesh operations for Blender 4.3."""

import bpy
import bmesh
from typing import List, Iterable, Optional
from .datamodel import WallSegment, Rect
from .slabs import Slab
from .roof import RoofGeometry
from .config import TEXTURE_TILE_SIZE

def _add_box_with_uv(bm: bmesh.types.BMesh, x1, y1, z1, x2, y2, z2, uv_layer):
    """Helper to add a box with world-space UV projection."""
    v = []
    for z in [z1, z2]:
        v.append(bm.verts.new((x1, y1, z)))
        v.append(bm.verts.new((x2, y1, z)))
        v.append(bm.verts.new((x2, y2, z)))
        v.append(bm.verts.new((x1, y2, z)))
    
    faces = []
    try:
        faces.append(bm.faces.new(v[0:4])) # bottom
        faces.append(bm.faces.new(v[4:8])) # top
        faces.append(bm.faces.new((v[0], v[1], v[5], v[4]))) # front
        faces.append(bm.faces.new((v[1], v[2], v[6], v[5]))) # right
        faces.append(bm.faces.new((v[2], v[3], v[7], v[6]))) # back
        faces.append(bm.faces.new((v[3], v[0], v[4], v[7]))) # left
    except ValueError:
        pass
    
    for f in faces:
        for loop in f.loops:
            co = loop.vert.co
            if abs(f.normal.y) > 0.5:
                loop[uv_layer].uv = (co.x / TEXTURE_TILE_SIZE, co.z / TEXTURE_TILE_SIZE)
            else:
                loop[uv_layer].uv = (co.y / TEXTURE_TILE_SIZE, co.z / TEXTURE_TILE_SIZE)

def create_wall_mesh(segments: Iterable[WallSegment], name: str = "Walls", material: Optional[bpy.types.Material] = None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material: obj.data.materials.append(material)
    
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    for s in segments:
        half_t = s.thickness / 2
        dx, dy = s.x2 - s.x1, s.y2 - s.y1
        length = (dx**2 + dy**2)**0.5
        if length < 1e-4: continue
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        
        window = getattr(s, 'window_opening', None)
        if window:
            _add_box_with_uv(bm, s.x1 - nx * half_t, s.y1 - ny * half_t, 0, s.x2 + nx * half_t, s.y2 + ny * half_t, window.sill_height, uv_layer)
            _add_box_with_uv(bm, s.x1 - nx * half_t, s.y1 - ny * half_t, window.sill_height + window.height, s.x2 + nx * half_t, s.y2 + ny * half_t, s.height, uv_layer)
        else:
            _add_box_with_uv(bm, s.x1 - nx * half_t, s.y1 - ny * half_t, 0, s.x2 + nx * half_t, s.y2 + ny * half_t, s.height, uv_layer)

    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_slab_mesh(slabs: Iterable[Slab], name: str = "Slabs", material: Optional[bpy.types.Material] = None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material: obj.data.materials.append(material)
        
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    for s in slabs:
        r = s.rect
        if s.hole_rect:
            # Create slab with hole using 4 boxes around the hole
            h = s.hole_rect
            # Left box
            _add_box_with_uv(bm, r.min_x, r.min_y, s.z, h.min_x, r.max_y, s.z + s.thickness, uv_layer)
            # Right box
            _add_box_with_uv(bm, h.max_x, r.min_y, s.z, r.max_x, r.max_y, s.z + s.thickness, uv_layer)
            # Top box (middle part)
            _add_box_with_uv(bm, h.min_x, h.max_y, s.z, h.max_x, r.max_y, s.z + s.thickness, uv_layer)
            # Bottom box (middle part)
            _add_box_with_uv(bm, h.min_x, r.min_y, s.z, h.max_x, h.min_y, s.z + s.thickness, uv_layer)
        else:
            _add_box_with_uv(bm, r.min_x, r.min_y, s.z, r.max_x, r.max_y, s.z + s.thickness, uv_layer)
        
    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_roof_mesh(roof_geo: RoofGeometry, name: str = "Roof", material: Optional[bpy.types.Material] = None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material: obj.data.materials.append(material)
    
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in roof_geo.faces:
        verts = [bm.verts.new(v) for v in face.vertices]
        try:
            f = bm.faces.new(verts)
            for loop in f.loops:
                co = loop.vert.co
                loop[uv_layer].uv = (co.x / TEXTURE_TILE_SIZE, co.y / TEXTURE_TILE_SIZE)
        except ValueError: pass
    bm.to_mesh(mesh)
    bm.free()
    return obj

def final_merge_and_cleanup(objects: List[bpy.types.Object], merge_distance: float = 0.0005):
    if not objects: return None
    bpy.ops.object.select_all(action='DESELECT')
    valid_objs = [o for o in objects if o.type == 'MESH']
    if not valid_objs: return None
    for obj in valid_objs: obj.select_set(True)
    bpy.context.view_layer.objects.active = valid_objs[0]
    bpy.ops.object.join()
    merged_obj = bpy.context.active_object
    merged_obj.name = "Building_Final"
    bm = bmesh.new()
    bm.from_mesh(merged_obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    internal_faces = [f for f in bm.faces if all(len(e.link_faces) > 2 for e in f.edges)]
    if internal_faces: bmesh.ops.delete(bm, geom=internal_faces, context='FACES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(merged_obj.data)
    bm.free()
    return merged_obj
