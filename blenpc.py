import click
import os
import sys
import json
import yaml
import platform
import subprocess
import time
import multiprocessing
from typing import Optional, List, Dict
from pathlib import Path

# Expert Fix: Add src/ to path for CLI to find the blenpc package
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(PROJECT_ROOT, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from blenpc import config

def run_blender_task(input_data: Dict, input_file: str, output_file: str, preview: bool = False) -> Dict:
    """Helper to run a single Blender task using the standardized run_command.py."""
    with open(input_file, 'w') as f:
        json.dump(input_data, f)
        
    # Expert Fix: Correct path to run_command.py inside src/blenpc
    run_cmd_path = os.path.join(PROJECT_ROOT, "src", "blenpc", "run_command.py")
    
    blender_cmd = [config.BLENDER_PATH]
    if not preview:
        blender_cmd.append("--background")
    
    blender_cmd.extend(["--python", run_cmd_path, "--", input_file, output_file])
    
    try:
        # Expert Fix: Capture stderr for debugging
        result = subprocess.run(blender_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                return json.load(f)
        else:
            return {"status": "error", "message": f"Blender did not produce output. Stderr: {result.stderr}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Blender process failed: {e.stderr}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)

@click.group()
@click.version_option(version="5.1.1")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose logging.")
@click.option('--blender-path', type=click.Path(exists=True), help="Custom path to Blender executable.")
def cli(verbose, blender_path):
    """BlenPC v5.1.1 - Expert-Driven Procedural Building Generator"""
    if verbose:
        os.environ["MF_LOG_LEVEL"] = "DEBUG"
    if blender_path:
        os.environ["BLENDER_PATH"] = blender_path

@cli.command()
@click.option('--width', '-w', type=float, help="Building width in meters.")
@click.option('--depth', '-d', type=float, help="Building depth in meters.")
@click.option('--floors', '-f', type=int, help="Number of floors.")
@click.option('--seed', '-s', type=int, default=0, help="Random seed.")
@click.option('--roof', '-r', type=click.Choice(['flat', 'gabled', 'hip', 'shed'], case_sensitive=False), default='flat', help="Roof type.")
@click.option('--output', '-o', type=click.Path(), default='./output', help="Output directory.")
@click.option('--spec', type=click.Path(exists=True), help="Path to YAML/JSON spec file.")
@click.option('--preview', is_flag=True, help="Open in Blender GUI after generation.")
def generate(width, depth, floors, seed, roof, output, spec, preview):
    """Generate a procedural building."""
    if spec:
        with open(spec, 'r') as f:
            spec_data = yaml.safe_load(f) if spec.endswith(('.yaml', '.yml')) else json.load(f)
        b_spec = spec_data.get('building', spec_data)
        width = width or b_spec.get('width', 20.0)
        depth = depth or b_spec.get('depth', 16.0)
        floors = floors or b_spec.get('floors', 1)
        seed = seed or b_spec.get('seed', 0)
        roof = roof or b_spec.get('roof', {}).get('type', 'flat')
        output = output or b_spec.get('output', {}).get('directory', './output')

    input_data = {
        "command": "generate_building",
        "seed": seed,
        "spec": {"width": width or 20.0, "depth": depth or 16.0, "floors": floors or 1, "roof": roof, "output_dir": output}
    }
    
    click.echo(f"Generating building (Seed: {seed})...")
    res = run_blender_task(input_data, f"gen_{seed}.json", f"out_{seed}.json", preview)
    
    if res.get("status") == "success":
        click.secho(f"✓ Success: {res['result']['glb_path']}", fg="green")
    else:
        click.secho(f"✗ Error: {res.get('message')}", fg="red")

@cli.command()
@click.option('--spec', type=click.Path(exists=True), required=True, help="Path to batch spec file.")
def batch(spec):
    """Run batch production."""
    with open(spec, 'r') as f:
        spec_data = yaml.safe_load(f)
    
    batch_list = spec_data.get('batch', {}).get('buildings', [])
    common_output = spec_data.get('batch', {}).get('output', {}).get('directory', './output')
    
    click.echo(f"Starting batch of {len(batch_list)} buildings...")
    with click.progressbar(batch_list, label='Processing') as bar:
        for b in bar:
            seed = b.get('seed', 1000)
            input_data = {
                "command": "generate_building", "seed": seed,
                "spec": {
                    "width": b.get('width', 20.0), "depth": b.get('depth', 16.0),
                    "floors": b.get('floors', 1), "roof": b.get('roof', {}).get('type', 'flat'),
                    "output_dir": common_output
                }
            }
            run_blender_task(input_data, f"batch_{seed}.json", f"out_{seed}.json")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def inspect(path):
    """Inspect a GLB/Blend file."""
    click.echo(f"File: {path} ({os.path.getsize(path)/1024:.1f} KB)")

@click.group()
def registry():
    """Manage the asset registry."""
    pass

@registry.command(name='list')
def list_assets():
    """List registered assets."""
    if os.path.exists(config.INVENTORY_FILE):
        with open(config.INVENTORY_FILE, 'r') as f:
            inv = json.load(f)
        for name in inv.get('assets', {}):
            click.echo(f"  - {name}")
    else:
        click.echo("Registry empty.")

cli.add_command(registry)

@cli.command()
def version():
    """Display version info."""
    click.echo(f"blenpc v5.1.1 (Expert Edition)")
    click.echo(f"Blender: {config.BLENDER_PATH}")
    click.echo(f"Platform: {platform.system()}")

if __name__ == '__main__':
    cli()
