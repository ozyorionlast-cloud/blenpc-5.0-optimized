"""Centralized configuration and logging for MF v5.1 generation pipeline."""

import logging
import os

# --- Generation Constants ---
GRID = 0.25
EPSILON = 1e-4

# Dimensions (meters)
WALL_THICKNESS = 0.20
WALL_HEIGHT = 3.0
FLOOR_THICKNESS = 0.20
CEILING_THICKNESS = 0.15
STORY_HEIGHT = 3.2  # WALL_HEIGHT + FLOOR_THICKNESS

DOOR_WIDTH = 0.9
DOOR_HEIGHT = 2.1

WINDOW_WIDTH = 1.2
WINDOW_HEIGHT = 1.0
WINDOW_SILL_HEIGHT = 1.0  # Height from floor to window bottom
TEXTURE_TILE_SIZE = 2.0  # UV tiling size in meters

CORRIDOR_WIDTH = 1.8
MIN_ROOM_SIZE = 2.5

# Roof
ROOF_HEIGHT = 1.2

# Cleanup
MERGE_DISTANCE = 5e-4
DISSOLVE_ANGLE = 0.01

# --- Logging Configuration ---
# Set MF_DEBUG=1 to enable debug logging
DEBUG_MODE = os.environ.get("MF_DEBUG", "0") == "1"

def setup_logger(name: str = "MFv5"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    return logger

logger = setup_logger()

def snap(value: float) -> float:
    """Snap a value to the global grid."""
    return round(value / GRID) * GRID
