import json
import math
import numpy as np

from ldtk import ldtkjson
from pathlib import Path

root = Path("world")

with open(root / "world.ldtk", "r", encoding="utf-8") as infile:
    ldtk_raw = json.load(infile)

if ldtk_raw["externalLevels"]:
    for i, level in enumerate(ldtk_raw["levels"]):
        if level["externalRelPath"]:
            with open(root / level["externalRelPath"], "r", encoding="utf-8") as infile:
                ldtk_raw["levels"][i] = json.load(infile)

ldtk = ldtkjson.ldtk_json_from_dict(ldtk_raw)

for level in ldtk.levels:
    # Only consider L1
    if "Happy" not in level.identifier:
        continue

    width = level.px_wid // 16
    height = level.px_hei // 16

    print("\n", "-" * 50, f"LEVEL: {level.identifier}", "-" * 50)

    tile_array = np.zeros((3, height, width, 2), dtype=np.dtype("uint16"))

    depth = -1
    for layer in level.layer_instances:
        # We are looking for ground A, B and C
        if "Ground" not in layer.identifier:
            continue

        if layer.type == "Tiles":
            depth += 1
            for tile in layer.grid_tiles:
                loc = (tile.px[0] // 16, tile.px[1] // 16)
                tile_array[depth, loc[1], loc[0]] = (
                    tile.src[0] // 16 + 1,
                    tile.src[1] // 16,
                )
        print(layer.identifier)

tile_array
