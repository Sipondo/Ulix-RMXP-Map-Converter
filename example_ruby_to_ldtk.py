from base64 import decode

from cx_Freeze import ConfigError
from rubymarshal.ruby import readruby, writeruby
import numpy as np
from pathlib import Path
import os
import json

ROOT = Path("world/world")
LDTK_TEMPLATE = Path("./0000-Template.ldtkl")
FILE = "Roni"
ESSENTIALS_FOLDER = Path("C:/Pythonpaskaa/Pokemon Essentials")
CENTER_MAP = 2  # By id

# Convert coords into the single int pointer format
def coordToInt(coords, width):
    return coords[0] + coords[1] * width


# Take in a single int tile texture pointer and return the coordinate version of it
def tToSrc(value):
    x = value % 8 * 16
    y = value // 8 * 16
    return [x, y]


def id_to_connections(id, connections):
    related_connections = []
    for connection in connections:
        if id == int(connection[0]):
            related_connections.append(connection)
        elif id == int(connection[3]):
            related_connections.append(connection[3:] + connection[:3])
    return related_connections


# Get level connections
# https://essentialsdocs.fandom.com/wiki/Connecting_maps#PBS_file_connections.txt
with open(Path(f"{ESSENTIALS_FOLDER}/PBS/connections.txt")) as connections_file:
    lines = connections_file.readlines()
    connections = []
    # Skip the header
    for line in lines[2:]:
        line = line.strip()
        if line.startswith("#"):
            continue
        values = line.split(",")
        connections.append(values)

# Get all rmxp maps
rmxpMaps = {}
for file in Path("./").glob("Map???.rxdata"):
    id = file.name.split("p")[1][:3]
    rmxpMaps[id] = file.name

# Get info on all maps
# Index by map ID and .attributes[@attribute]
mapInfos = readruby(Path(f"{ESSENTIALS_FOLDER}/Data/Mapinfos.rxdata"))

# Open world file for reading
with open(Path("world/world.ldtk"), "r", encoding="utf-8") as worldFile:
    world_raw = json.load(worldFile)

# Generate a dict of sizes
level_sizes = {}
for id, map in rmxpMaps.items():
    # Open a ruby map
    rubyData = readruby(f"Map{id:0>3}.rxdata")

    heightTiles = rubyData.attributes["@height"]
    widthTiles = rubyData.attributes["@width"]
    level_sizes[int(id)] = [widthTiles, heightTiles]

level_locations = {CENTER_MAP: (0, 0)}
walk = True
while walk:
    walk = False
    for id in rmxpMaps.keys():
        id = int(id)
        if id in level_locations:
            continue
        for con in id_to_connections(id, connections):
            if int(con[3]) not in level_locations:
                continue
            source = level_locations[int(con[3])]
            source_size = level_sizes[int(con[3])]
            dest_size = level_sizes[id]
            if con[1] == "S":
                y = source[1] - dest_size[1]
                x = source[0] - int(con[2]) + int(con[5])
            if con[1] == "W":
                y = source[1] - int(con[2]) + int(con[5])
                x = source[0] + source_size[0]
            if con[1] == "N":
                y = source[1] + source_size[1]
                x = source[0] - int(con[2]) + int(con[5])
            if con[1] == "E":
                y = source[1] - int(con[2]) + int(con[5])
                x = source[0] - dest_size[1]
            level_locations[id] = x, y
            walk = True


# Start for loop here

for id, map in rmxpMaps.items():

    # Open a level template
    with open(LDTK_TEMPLATE, "r", encoding="utf-8") as ldtkTemplate:
        ldtk_raw = json.load(ldtkTemplate)

    # Open a ruby map
    rubyData = readruby(f"Map{id:0>3}.rxdata")

    # Grab numpy array of map
    rubyArray = rubyData.attributes["@data"].to_array()

    heightTiles = rubyData.attributes["@height"]
    widthTiles = rubyData.attributes["@width"]
    widthPx = widthTiles * 16
    heightPx = heightTiles * 16

    # Set the correct ui
    uid = world_raw["nextUid"]
    ldtk_raw["uid"] = uid
    for instance in ldtk_raw["layerInstances"]:
        instance["levelId"] = uid

    ldtk_raw["layerInstances"][-1]["gridTiles"] = []
    for layer in range(3):
        for indexX in range(widthTiles):
            for indexY in range(heightTiles):
                t = int(rubyArray[layer][indexY][indexX])
                if t == 0:
                    continue

                # Adjust t to account for 384 RMXP autotiles and 8 empty ldtk tiles
                t = t - 384 + 8
                src = tToSrc(t)
                ldtk_raw["layerInstances"][-1]["gridTiles"].append(
                    {
                        "px": [widthPx, heightPx],
                        "src": src,
                        "f": 0,
                        "t": t,
                        "d": [coordToInt((indexX, indexY), widthTiles)],
                    }
                )

    # Create an unique name for the new level
    mapIndex = 0
    for file in ROOT.glob("*.ldtkl"):
        currNum = int(file.name.split("-")[0])
        if currNum >= mapIndex:
            mapIndex = currNum + 1
    tmpName = mapInfos[int(id)].attributes["@name"].decode("utf-8")
    mapName = "".join(l for l in tmpName if l.isalnum())
    levelName = f"L{int(id)}_{mapName}"
    levelFilename = f"{mapIndex:0>4}-{levelName}.ldtkl"

    # Make required changes to the level and save it
    ldtk_raw["identifier"] = levelName
    ldtk_raw["pxWid"] = widthPx
    ldtk_raw["pxHei"] = heightPx
    if int(id) in level_locations:
        ldtk_raw["worldX"] = level_locations[int(id)][0] * 16
        ldtk_raw["worldY"] = level_locations[int(id)][1] * 16
    with open(Path(f"{ROOT}/{levelFilename}"), "w", encoding="utf-8") as outfile:
        json.dump(ldtk_raw, outfile, indent=4)

    # Second part to write level into world file

    # Prepare level data to be added into the world file
    level = ldtk_raw
    level["layerInstances"] = None
    level["externalRelPath"] = f"world/{levelFilename}"
    level.pop("__header__")

    # Increment nextUid by 1 and append level into the world
    world_raw["nextUid"] += 1
    world_raw["levels"].append(level)

    # Save the world file
    with open(Path("world/world.ldtk"), "w", encoding="utf-8") as worldWrite:
        json.dump(world_raw, worldWrite, indent=4)
