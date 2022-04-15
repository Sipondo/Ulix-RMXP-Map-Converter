import json
from pathlib import Path

ROOT = Path("world/world")
FILE = "Roni"

with open(list(ROOT.glob(f"*{FILE}*"))[0], "r", encoding="utf-8") as infile:
    ldtk_raw = json.load(infile)

ldtk_raw["layerInstances"][-1]["gridTiles"]
ldtk_raw["layerInstances"][-1]["gridTiles"]

def coordToInt(coords, width):
    return coords[0] + coords[1] * width

ldtk_raw["layerInstances"][-1]["gridTiles"] = []
for wid in range(0, ldtk_raw["pxWid"], 16):
    for hei in range(0, ldtk_raw["pxHei"], 16):
        tileY = hei // 16
        tileX = wid // 16
        ldtk_raw["layerInstances"][-1]["gridTiles"].append({'px': [wid, hei], 'src': [32, 320], 'f': 0, 't': 162, 'd': [coordToInt((wid, hei), ldtk_raw["pxWid"])]})

with open(list(ROOT.glob(f"*{FILE}*"))[0], "w", encoding="utf-8") as outfile:
   json.dump(ldtk_raw, outfile, indent=4)
