import sys
import json
import os
import time
import bpy

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from atoms.wall import create_engineered_wall
from engine.inventory_manager import InventoryManager

def run():
    try:
        if '--' in sys.argv:
            args = sys.argv[sys.argv.index('--') + 1:]
            input_file = args[0]
            output_file = args[1]
        else:
            sys.exit(1)
    except (ValueError, IndexError):
        sys.exit(1)

    if not os.path.exists(input_file):
        result = {"status": "error", "message": "Input not found"}
    else:
        try:
            with open(input_file, 'r') as f:
                command_data = json.load(f)
            
            cmd = command_data.get("command")
            seed = command_data.get("seed", 0)
            
            if cmd == "create_wall":
                wall_data = command_data.get("asset", {})
                name = wall_data.get("name", "GenWall")
                length = wall_data.get("dimensions", {}).get("width", 4.0)
                
                # Create engineered mesh with slots
                obj, slots = create_engineered_wall(name, length, seed)
                
                # Register in inventory with slots
                asset_info = {
                    "name": name,
                    "tags": wall_data.get("tags", ["arch_wall"]),
                    "dimensions": {"width": length, "height": 3.0, "depth": 0.2},
                    "slots": slots,
                    "blend_file": f"_library/{name}.blend",
                    "seed": seed
                }
                InventoryManager.register_asset(asset_info)
                
                # Save
                if not os.path.exists("_library"): os.makedirs("_library")
                lib_path = os.path.join("_library", f"{name}.blend")
                bpy.ops.wm.save_as_mainfile(filepath=lib_path)
                
                result = {
                    "status": "success",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "result": {"asset_name": name, "slots_count": len(slots)}
                }
            else:
                result = {"status": "error", "message": f"Unknown command: {cmd}"}
                
        except Exception as e:
            import traceback
            result = {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run()
