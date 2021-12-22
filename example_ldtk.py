import json

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
    print("\n", "-" * 50, f"LEVEL: {level.identifier}", "-" * 50)

    for layer in level.layer_instances:
        # We are looking for ground A, B and C
        print(layer.identifier)
