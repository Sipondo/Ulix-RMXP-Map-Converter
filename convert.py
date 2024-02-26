from pathlib import Path
from PSDKDataLoader import PSDKDataLoader
from ldtk.Ldtk import Ldtk
import shutil
import os
import sys

WORLD_FILE = Path("ldtk/world.ldtk")
PROJECT_PATH = Path(sys.argv[1])

ldtk = Ldtk(WORLD_FILE)
ldtk._json.external_levels = True

# This is just for early stage debugging
to_dir = Path("world")
if to_dir.exists():
    shutil.rmtree(to_dir)
########################################

loader = PSDKDataLoader(PROJECT_PATH)

levels_done = 0
total_maps = len(loader.maps.keys())
for id, map in loader.maps.items():
    level = map.to_level()
    ldtk.add_level(level)

    levels_done += 1
    print(f"{levels_done}/{total_maps} maps imported")

print(f"Importing done. Writing files...")
ldtk.save(Path("world"))