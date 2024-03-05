from pathlib import Path
from rmxp.psdkdataloader import PSDKDataLoader
from ldtk.world import Level, World
import shutil
import os
import sys

PROJECT_PATH = Path(sys.argv[1])

# This is just for early stage debugging
to_dir = Path("world")
if to_dir.exists():
    shutil.rmtree(to_dir)
########################################

world = World()
loader = PSDKDataLoader(PROJECT_PATH)

for id, map in loader.maps.items():
    level = map.to_level()
    world.add_level(level)
world.to_ldtk(Path("world"))


# dst_project = Path("world")
# dst_tilesets = dst_project / "assets" / "tilesets"
# os.makedirs(dst_tilesets, exist_ok=True)

# # Create the needed layers. Lowest layer is last
# layers = []
# for identifier in ["Ground", "Above_A", "Above B"]:
#     layers.append(world.add_layer_definition(
#         identifier=identifier,
#         grid_size=16
#     ))

# levels_done = 0
# total_maps = len(loader.maps.keys())
# imported_tilesets = {}
# # Import the maps
# for id, map in loader.maps.items():

#     # Import the tileset if it isnt already
#     tileset = loader.tilesets[map.tileset_id]
#     if tileset.tileset_name and tileset.id not in imported_tilesets:
#         t = tileset.add_to_ldtk(dst_tilesets, world)
#         imported_tilesets[tileset.id] = t

#     tileset_definition = imported_tilesets.get(tileset.id)
#     level = map.add_to_ldtk(world, layers, tileset_definition)

#     levels_done += 1
#     # print(f"{levels_done}/{total_maps} maps imported")

# # Then do final cleanup
# world._json.defs.layers.sort(key=lambda x: x.uid, reverse=True) # Easier to reverse in the end instead of importing in reverse

# print(f"Importing done. Writing files...")
# world.save(dst_project)