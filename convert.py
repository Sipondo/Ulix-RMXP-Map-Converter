from pathlib import Path
from PSDKDataLoader import PSDKDataLoader
from ldtk.Ldtk import TilesetDefinition, World
import shutil
import os
import sys

WORLD_FILE = Path("ldtk/world.ldtk")
PROJECT_PATH = Path(sys.argv[1])

# This is just for early stage debugging
to_dir = Path("world")
if to_dir.exists():
    shutil.rmtree(to_dir)
########################################

world = World(WORLD_FILE)
world._json.external_levels = True
loader = PSDKDataLoader(PROJECT_PATH)

dst_project = Path("world")
dst_tilesets = dst_project / "assets" / "tilesets"
os.makedirs(dst_tilesets, exist_ok=True)

levels_done = 0
total_maps = len(loader.maps.keys())
imported_tilesets = {}
for id, map in loader.maps.items():

    # Import the tileset if it isnt already
    tileset = loader.tilesets[map.tileset_id]
    if tileset.tileset_name and tileset.id not in imported_tilesets:
        t = tileset.add_to_ldtk(dst_tilesets, world)
        imported_tilesets[tileset.id] = t

    tileset_definition = imported_tilesets.get(tileset.id)
    level = map.add_to_ldtk(world, tileset_definition)

    levels_done += 1
    print(f"{levels_done}/{total_maps} maps imported")

print(f"Importing done. Writing files...")
world.save(dst_project)