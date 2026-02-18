"""Simplified collider generation for procedural buildings."""

import bpy
import bmesh

def create_simplified_collider(building_obj: bpy.types.Object, name: str = "Building_Collider") -> bpy.types.Object:
    """
    Create a simplified collider object from the building mesh.
    Uses decimation and remove doubles to reduce complexity for physics engines.
    """
    if not building_obj or building_obj.type != 'MESH':
        return None
        
    # Create a copy of the building object
    collider_mesh = building_obj.data.copy()
    collider_obj = bpy.data.objects.new(name, collider_mesh)
    bpy.context.collection.objects.link(collider_obj)
    
    # Process the mesh for simplification
    bm = bmesh.new()
    bm.from_mesh(collider_mesh)
    
    # 1. Aggressive remove doubles (0.1m threshold)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.1)
    
    # 2. Delete internal faces (already done in building mesh, but let's be sure)
    bm.edges.ensure_lookup_table()
    internal_faces = [f for f in bm.faces if all(len(e.link_faces) > 2 for e in f.edges)]
    if internal_faces:
        bmesh.ops.delete(bm, geom=internal_faces, context='FACES')
        
    # 3. Planar dissolve to merge coplanar faces (e.g., floor slabs)
    bmesh.ops.dissolve_limit(bm, angle_limit=0.01, verts=bm.verts, edges=bm.edges)
    
    bm.to_mesh(collider_mesh)
    bm.free()
    
    # Optional: Apply a decimate modifier if still too complex
    # modifier = collider_obj.modifiers.new(name="Decimate", type='DECIMATE')
    # modifier.ratio = 0.5
    # bpy.context.view_layer.objects.active = collider_obj
    # bpy.ops.object.modifier_apply(modifier="Decimate")
    
    return collider_obj
