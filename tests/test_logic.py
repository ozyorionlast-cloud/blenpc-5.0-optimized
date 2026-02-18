import pytest
from mf_v5.floorplan import generate_floorplan
from mf_v5.doors import carve_doors, DoorOpening
from mf_v5.datamodel import WallSegment, Rect
from mf_v5.config import MIN_ROOM_SIZE, EPSILON

def test_floorplan_minimum_room_size():
    """Ensure all generated rooms respect the minimum room size."""
    rooms, corridor = generate_floorplan(20, 20, 42, 0)
    for room in rooms:
        assert room.rect.max_x - room.rect.min_x >= MIN_ROOM_SIZE - EPSILON
        assert room.rect.max_y - room.rect.min_y >= MIN_ROOM_SIZE - EPSILON

def test_corridor_placement():
    """Ensure the corridor is correctly centered in the floorplan."""
    width, depth = 20, 16
    rooms, corridor = generate_floorplan(width, depth, 42, 0)
    # Corridor should be centered vertically if split horizontally (spine)
    # In current BSP, it's a vertical spine: (width - corridor_width) / 2
    # The value is snapped to the grid (0.25). 
    # (20 - 1.8) / 2 = 9.1 -> snapped to 0.25 grid = 9.0
    from mf_v5.config import snap
    corridor_width = 1.8
    expected_min_x = snap((width - corridor_width) / 2)
    assert abs(corridor.rect.min_x - expected_min_x) < EPSILON

def test_door_carving_split_logic():
    """Verify that door carving correctly splits a wall segment into multiple pieces."""
    # 5m long wall
    wall = WallSegment(room_id=1, side="north", x1=0, y1=0, x2=5, y2=0, height=3.0, thickness=0.2)
    # 1m wide door in the middle
    door = DoorOpening(room_id=1, side="north", center=(2.5, 0), width=1.0, height=2.0)
    
    carved_map = carve_doors({1: [wall]}, [door])
    carved_segments = carved_map[1]
    
    # Should result in 2 segments (left and right of the door)
    assert len(carved_segments) == 2
    
    # Total length should be 5 - 1 = 4m
    total_length = sum(abs(s.x2 - s.x1) for s in carved_segments)
    assert abs(total_length - 4.0) < EPSILON

def test_no_overlapping_rooms():
    """Ensure no two rooms overlap in the generated floorplan."""
    rooms, corridor = generate_floorplan(30, 30, 123, 0)
    all_rects = [r.rect for r in rooms] + [corridor.rect]
    
    for i, r1 in enumerate(all_rects):
        for r2 in all_rects[i+1:]:
            # Check for overlap (intersection area > epsilon)
            overlap_x = max(0, min(r1.max_x, r2.max_x) - max(r1.min_x, r2.min_x))
            overlap_y = max(0, min(r1.max_y, r2.max_y) - max(r1.min_y, r2.min_y))
            assert overlap_x * overlap_y < EPSILON
