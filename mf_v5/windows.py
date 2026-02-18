"""Window placement and carving logic for procedural buildings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple, DefaultDict
from collections import defaultdict

from .config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SILL_HEIGHT, EPSILON
from .datamodel import WallSegment, Room


@dataclass(frozen=True)
class WindowOpening:
    room_id: int
    side: str
    center: Tuple[float, float]
    width: float = WINDOW_WIDTH
    height: float = WINDOW_HEIGHT
    sill_height: float = WINDOW_SILL_HEIGHT


def generate_window_placements(rooms: Iterable[Room]) -> List[WindowOpening]:
    """Generate window placements for rooms on exterior walls."""
    openings: List[WindowOpening] = []
    for room in rooms:
        # Simple heuristic: one window per exterior-facing side (not corridor)
        # In a real implementation, we'd check if the side is truly exterior.
        # For now, let's place windows on North/South walls of rooms.
        min_x, min_y, max_x, max_y = room.rect.min_x, room.rect.min_y, room.rect.max_x, room.rect.max_y
        
        # Add a window to North and South walls for testing
        openings.append(WindowOpening(room.id, "north", ((min_x + max_x) / 2, max_y)))
        openings.append(WindowOpening(room.id, "south", ((min_x + max_x) / 2, min_y)))
    return openings


def _split_horizontal(seg: WallSegment, cx: float, width: float) -> List[WallSegment]:
    left_end = cx - width / 2
    right_start = cx + width / 2
    x_min, x_max = sorted((seg.x1, seg.x2))

    pieces: List[WallSegment] = []
    if left_end - x_min > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, x_min, seg.y1, left_end, seg.y2, seg.height, seg.thickness))
    if x_max - right_start > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, right_start, seg.y1, x_max, seg.y2, seg.height, seg.thickness))
    return pieces


def _split_vertical(seg: WallSegment, cy: float, width: float) -> List[WallSegment]:
    bottom_end = cy - width / 2
    top_start = cy + width / 2
    y_min, y_max = sorted((seg.y1, seg.y2))

    pieces: List[WallSegment] = []
    if bottom_end - y_min > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, seg.x1, y_min, seg.x2, bottom_end, seg.height, seg.thickness))
    if y_max - top_start > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, seg.x1, top_start, seg.x2, y_max, seg.height, seg.thickness))
    return pieces


def carve_windows(
    wall_segments: Dict[int, List[WallSegment]],
    openings: Iterable[WindowOpening],
) -> Dict[int, List[WallSegment]]:
    """
    Carve windows into walls. 
    NOTE: Unlike doors, windows create multiple segments vertically too.
    To keep the manifold-safe segment approach simple, we split horizontally 
    and then handle the Z-opening in the mesh generation phase (blender_mesh.py).
    """
    openings_by_room_side: DefaultDict[tuple, List[WindowOpening]] = defaultdict(list)
    for w in openings:
        openings_by_room_side[(w.room_id, w.side)].append(w)
        
    carved: Dict[int, List[WallSegment]] = {}

    for room_id, segments in wall_segments.items():
        out: List[WallSegment] = []
        for seg in segments:
            room_openings = openings_by_room_side.get((room_id, seg.side), [])
            if not room_openings:
                out.append(seg)
                continue

            current_pieces = [seg]
            for opening in room_openings:
                next_pieces = []
                for p in current_pieces:
                    # Mark the piece that contains the window for special mesh handling
                    is_horizontal = seg.side in ("north", "south")
                    coord = opening.center[0] if is_horizontal else opening.center[1]
                    p_min, p_max = sorted((p.x1, p.x2)) if is_horizontal else sorted((p.y1, p.y2))
                    
                    if coord > p_min + EPSILON and coord < p_max - EPSILON:
                        # Split and keep track of the 'window' segment
                        if is_horizontal:
                            left_end = opening.center[0] - opening.width / 2
                            right_start = opening.center[0] + opening.width / 2
                            
                            if left_end - p_min > EPSILON:
                                next_pieces.append(WallSegment(p.room_id, p.side, p_min, p.y1, left_end, p.y2, p.height, p.thickness))
                            
                            # The middle piece (window area)
                            win_seg = WallSegment(p.room_id, p.side, left_end, p.y1, right_start, p.y2, p.height, p.thickness)
                            # Tag for blender_mesh.py
                            win_seg.__dict__['window_opening'] = opening
                            next_pieces.append(win_seg)
                            
                            if p_max - right_start > EPSILON:
                                next_pieces.append(WallSegment(p.room_id, p.side, right_start, p.y1, p_max, p.y2, p.height, p.thickness))
                        else:
                            bottom_end = opening.center[1] - opening.width / 2
                            top_start = opening.center[1] + opening.width / 2
                            
                            if bottom_end - p_min > EPSILON:
                                next_pieces.append(WallSegment(p.room_id, p.side, p.x1, p_min, p.x2, bottom_end, p.height, p.thickness))
                            
                            win_seg = WallSegment(p.room_id, p.side, p.x1, bottom_end, p.x2, top_start, p.height, p.thickness)
                            win_seg.__dict__['window_opening'] = opening
                            next_pieces.append(win_seg)
                            
                            if p_max - top_start > EPSILON:
                                next_pieces.append(WallSegment(p.room_id, p.side, p.x1, top_start, p.x2, p_max, p.height, p.thickness))
                    else:
                        next_pieces.append(p)
                current_pieces = next_pieces
            out.extend(current_pieces)
        carved[room_id] = out

    return carved
