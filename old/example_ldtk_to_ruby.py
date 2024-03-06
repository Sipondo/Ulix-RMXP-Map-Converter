import json
import math
import numpy as np

from ldtk import ldtkjson
from pathlib import Path


from rubymarshal.ruby import readruby, writeruby

root = Path("world")

# First: read ldtk files + all ldtkl level subfiles
with open(root / "world.ldtk", "r", encoding="utf-8") as infile:
    ldtk_raw = json.load(infile)

if ldtk_raw["externalLevels"]:
    for i, level in enumerate(ldtk_raw["levels"]):
        if level["externalRelPath"]:
            with open(root / level["externalRelPath"], "r", encoding="utf-8") as infile:
                ldtk_raw["levels"][i] = json.load(infile)

# Parse the ldtk json
ldtk = ldtkjson.ldtk_json_from_dict(ldtk_raw)

# Iterate over level (map)
for level in ldtk.levels:
    # Only consider L17
    if "L1_Happy" not in level.identifier:
        continue

    width = level.px_wid // 16
    height = level.px_hei // 16

    print("\n", "-" * 50, f"LEVEL: {level.identifier}", "-" * 50)

    tile_array = np.zeros((3, height, width, 2), dtype=np.dtype("uint16"))

    # Iterate over layers
    # We need go from top to bottom, so first index we check is 3 (-1)
    depth = 3
    for layer in level.layer_instances:
        # We are looking for ground A, B and C
        if "Ground" not in layer.identifier:
            continue

        if layer.type == "Tiles":
            depth -= 1
            for tile in layer.grid_tiles:
                loc = (tile.px[0] // 16, tile.px[1] // 16)
                tile_array[depth, loc[1], loc[0]] = (
                    tile.src[0] // 16,
                    tile.src[1] // 16,
                )
        print(layer.identifier)


def f(coords):
    return coords[0] + 8 * coords[1]


# tile_array contains the tiles in grid coordinate format (x, y). We need them in single coordinate format for Ruby.

# tile_array_flat should correspond to the tile ids as found in LDTK
tile_array_flat = np.apply_along_axis(f, 3, tile_array)

# To convert to ruby we first need to get rid of the first (empty) row. We do this by subtracting 8 (one row) from all values.
# Because this can bring some tiles into the negative (which is bad) we have to bring any negatives back to 0.

tile_array_flat -= 8
tile_array_flat[tile_array_flat <= 0] = 0

# The first row contains the RMXP autotiles, which are 48 tiles long and there are 8 of them: 8x48 = 384
# If the tile is 0 then keep it 0. If larger than 0 we have to skip over the 384 autotile tiles.
tile_array_flat[tile_array_flat > 0] += 384

# Useful scripting help: check what unique tiles we have (in the map/on a layer, here: layer Ground_B)
np.unique(tile_array_flat[1])


RUBY_MAPNAME = "Map022.rxdata"
# Open a ruby map
data = readruby(RUBY_MAPNAME)

# # Grab numpy array of map
# array = data.attributes["@data"].to_array()
# array

# Write array to map
data.attributes["@data"].from_array(tile_array_flat)

# Save to a new file
writeruby(data, f"altered_{RUBY_MAPNAME}")

