from pathlib import Path
from PSDKDataLoader import PSDKDataLoader
from ldtk.Ldtk import Ldtk
import sys

WORLD_FILE = Path("ldtk/world.ldtk")
PROJECT_PATH = Path(sys.argv[1])

ldtk = Ldtk(WORLD_FILE)
ldtk._json.external_levels = True

loader = PSDKDataLoader(PROJECT_PATH)

for id, map in loader.maps.items():
    level = map.to_level()
    ldtk.add_level(level)

ldtk.save(Path("world"))