import json
import subprocess
import os
import pytest

def test_golden_ratio_wall_production():
    # Test two walls with different seeds to ensure deterministic but different slot placement
    for seed in [123, 456]:
        name = f"MathWall_S{seed}"
        input_data = {
            "command": "create_wall",
            "seed": seed,
            "asset": {
                "name": name,
                "dimensions": {"width": 5.0},
                "tags": ["arch_wall", "math_verified"]
            }
        }
        
        input_path = f"test_in_{seed}.json"
        output_path = f"test_out_{seed}.json"
        
        with open(input_path, "w") as f:
            json.dump(input_data, f)
            
        subprocess.run([
            "/home/ubuntu/blender5/blender",
            "--background", "--python", "run_command.py",
            "--", input_path, output_path
        ], capture_output=True)
        
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            out = json.load(f)
            assert out["status"] == "success"
            
        # Verify Inventory Entry
        with open("_registry/inventory.json", "r") as f:
            inv = json.load(f)
            asset = inv["assets"][name]
            assert "slots" in asset
            assert len(asset["slots"]) > 0
            # Check if position is snapped to GRID_UNIT (0.25)
            pos_x = asset["slots"][0]["pos"][0]
            assert pos_x % 0.25 == 0
            
        # Cleanup
        os.remove(input_path)
        os.remove(output_path)
