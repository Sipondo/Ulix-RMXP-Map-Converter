from base64 import decode

from cx_Freeze import ConfigError
from rubymarshal.ruby import readruby, writeruby
import numpy as np
from pathlib import Path
import os
import json
import copy
from tilesetconverter import get_image_size, shrink_tileset

ROOT = Path("world/world")
LDTK_TEMPLATE = Path("./0000-Template.ldtkl")
WORLD_TEMPLATE = Path("./worldTemplate.ldtk")
FILE = "Roni"
ESSENTIALS_FOLDER = Path(r"C:\Pythonpaskaa\Pokemon Essentials")
CENTER_MAP = 2  # By id
# Convert coords into the single int pointer format
def coordToInt(coords, width):
    return coords[0] + coords[1] * width


# Take in a single int tile texture pointer and return the coordinate version of it
def tToSrc(value):
    x = value % 8 * 16
    y = value // 8 * 16
    return [x, y]


# Returns a list of all connections related to an ID
def id_to_connections(id):
    """
    Requires: CONNECTIONS, a list of connections
    in: map ID
    out: A list of all related connections
    """
    related_connections = []
    for connection in CONNECTIONS:
        if id == connection[0]:
            related_connections.append(connection)
        elif id == connection[3]:
            related_connections.append(connection[3:] + connection[:3])
    return related_connections


# Get level connections
# Returns a list of all connection lists
# 0: src    1:  edge    2: connected tile   3: dest     4: edge     5: connected tile
# https://essentialsdocs.fandom.com/wiki/Connecting_maps#PBS_file_connections.txt
def get_connections():
    """
    in: None
    out: A list of all connections
    """
    with open(Path(f"{ESSENTIALS_FOLDER}/PBS/connections.txt")) as connections_file:
        lines = connections_file.readlines()
    connections = []
    # Skip the header
    for line in lines[2:]:
        line = line.strip()
        if line.startswith("#"):
            continue
        values = line.split(",")
        values = list(map(lambda x: int(x) if x.isdecimal() else x, values))
        connections.append(values)
    return connections


def get_rmxp_tilesets():
    tileset_dict = {}
    tilesets = readruby(Path(f"{ESSENTIALS_FOLDER}/Data/Tilesets.rxdata"))
    for tileset in (t for t in tilesets if t is not None):
        tileset_name = tileset.attributes["@tileset_name"].decode("utf-8")
        id = tileset.attributes["@id"]
        tileset_dict[id] = tileset_name
    return tileset_dict


# Get all rmxp maps
# Returns a dict with map IDs as keys
def get_rmxp_maps():
    """in: None
    out : a dict of names, by ID"""
    rmxpMaps = {}
    for file in Path("./").glob("Map???.rxdata"):
        id = int(file.name.split("p")[1][:3])
        rmxpMaps[id] = file.name
    return rmxpMaps


# Takes in a dict with ID: map name
# Generate a dict of map tile sizes
def get_rmxp_map_sizes(maps):
    """in: A dict of names, by ID
    out: A dict of level sizes, by ID"""
    # Keys are map IDs
    level_sizes = {}
    for id, map in maps.items():
        # Open a ruby map
        rubyData = readruby(f"Map{id:0>3}.rxdata")

        heightTiles = rubyData.attributes["@height"]
        widthTiles = rubyData.attributes["@width"]
        level_sizes[id] = (widthTiles, heightTiles)
    return level_sizes


def create_level_filename(name):
    mapIndex = 0
    for file in ROOT.glob("*.ldtkl"):
        currNum = int(file.name.split("-")[0])
        if currNum >= mapIndex:
            mapIndex = currNum + 1
    tmpName = mapInfos[id].attributes["@name"].decode("utf-8")
    mapName = "".join(l for l in tmpName if l.isalnum())
    levelName = f"L{id}_{mapName}"
    levelFilename = f"{mapIndex:0>4}-{levelName}.ldtkl"
    return levelFilename


def get_level_locations(maps, level_sizes, mapInfos):
    """
    @maps: A dict of map names, by ID
    in 2: A dict of map sizes, by ID
    out: A dict of all known level locations, by ID
    """
    center_loc = tuple([0 - l // 2 for l in level_sizes[CENTER_MAP]] + [0])
    level_locations = {CENTER_MAP: center_loc}
    walk = True
    while walk:
        walk = False
        for id in maps.keys():
            if id in level_locations:
                continue
            for con in id_to_connections(id):
                if con[3] not in level_locations:
                    continue
                src_x, src_y, src_z = level_locations[con[3]]
                src_wid, src_hei = level_sizes[con[3]]
                dest_wid, dest_hei = level_sizes[id]
                if con[1] in ("S", "South"):
                    y = src_y - dest_hei
                    x = src_x - con[2] + con[5]
                if con[1] in ("W", "West"):
                    y = src_y - con[2] + con[5]
                    x = src_x + src_wid
                if con[1] in ("N", "North"):
                    y = src_y + src_hei
                    x = src_x - con[2] + con[5]
                if con[1] in ("E", "East"):
                    y = src_y - con[2] + con[5]
                    x = src_x - dest_wid
                level_locations[id] = x, y, src_z
                walk = True
            if not walk:
                if (
                    parent := mapInfos[id].attributes["@parent_id"]
                ) and parent in level_locations:
                    src_x, src_y, src_z = level_locations[parent]
                    level_locations[id] = src_x, src_y, src_z + 1
                    walk = True

    return level_locations


## Start doing stuff here
# Open world file for reading
with open(WORLD_TEMPLATE, "r", encoding="utf-8") as worldFile:
    world_template = json.load(worldFile)
    world_final = copy.deepcopy(world_template)

# Open a level template
with open(LDTK_TEMPLATE, "r", encoding="utf-8") as ldtkTemplate:
    level_template = json.load(ldtkTemplate)
    level_final = copy.deepcopy(level_template)

# Get info on all maps
# Index by map ID and .attributes[@attribute]
mapInfos = readruby(Path(f"{ESSENTIALS_FOLDER}/Data/Mapinfos.rxdata"))

# Get all connections from connections.txt
CONNECTIONS = get_connections()

# Get all map names
rmxpMaps = get_rmxp_maps()

# Get the sizes and pre-calculate locations
level_sizes = get_rmxp_map_sizes(rmxpMaps)
level_locations = get_level_locations(rmxpMaps, level_sizes, mapInfos)

# Find out what tilesets are needed
rmxp_tilesets = get_rmxp_tilesets()
ldtk_tilesets = {}

# Start for loop here

for id, rmxpMap in rmxpMaps.items():
    print("Importing level: ", rmxpMap)

    level = copy.deepcopy(level_template)

    # Open a ruby map
    rubyData = readruby(f"{rmxpMaps[id]}")

    # Grab numpy array of map
    rubyArray = rubyData.attributes["@data"].to_array()

    widthTiles, heightTiles = level_sizes[id]
    widthPx = widthTiles * 16
    heightPx = heightTiles * 16

    # [-1] is Ground layer
    level["layerInstances"][-1]["gridTiles"] = []
    for layer in range(3):
        for indexX in range(widthTiles):
            for indexY in range(heightTiles):
                t = int(rubyArray[layer][indexY][indexX])
                if t == 0:
                    continue

                # Adjust t to account for 384 RMXP autotiles and 8 empty ldtk tiles
                # Add +8 if importing legacy tilesets (empty line on top)
                t = t - 384
                src = tToSrc(t)
                level["layerInstances"][-1]["gridTiles"].append(
                    {
                        "px": [widthPx, heightPx],
                        "src": src,
                        "f": 0,
                        "t": t,
                        "d": [coordToInt((indexX, indexY), widthTiles)],
                    }
                )

    # Create an unique name for the new level
    level_name = mapInfos[id].attributes["@name"].decode("utf-8")
    level_filename = create_level_filename(level_name)

    # Make required changes to the level and save it

    # Set the correct uid
    uid = world_template["nextUid"]
    level["uid"] = uid
    for instance in level["layerInstances"]:
        instance["levelId"] = uid

    # Split out the 4 digit ID and file extension from filename (== L75_TiallRegion for example)
    level["identifier"] = level_filename.split("-")[1].split(".")[0]

    # Correct level size
    level["pxWid"] = widthPx
    level["pxHei"] = heightPx

    # Set correct world location. If not known, throw it out of the way
    if id in level_locations:
        level["worldX"] = level_locations[id][0] * 16
        level["worldY"] = level_locations[id][1] * 16
        level["worldDepth"] = level_locations[id][2]
    else:
        level["worldX"] = -1000
        level["worldY"] = 1000

    # Set the correct tileset
    curr_tileset_id = rubyData.attributes["@tileset_id"]
    curr_tileset_name = rmxp_tilesets[curr_tileset_id]
    if curr_tileset_name in ldtk_tilesets:
        level["layerInstances"][-1]["overrideTilesetUid"] = ldtk_tilesets[
            curr_tileset_name
        ]
    else:
        print(f"\nTileset {curr_tileset_name} does not exist. Trying to import...")
        try:
            img = next(
                Path(f"{ESSENTIALS_FOLDER}/Graphics/Tilesets/").glob(
                    f"*{curr_tileset_name}*"
                )
            )
        except StopIteration:
            print(
                f"Tileset '{curr_tileset_name} not found in Essentials folder! Skipping import."
            )
        if img:
            shrunk_img_name = shrink_tileset(img)
            tileset_template = copy.deepcopy(world_template["defs"]["tilesets"][0])

            # Find out the next uid
            try:
                tileset_uid += 1
            except NameError:
                tileset_uid = tileset_template["uid"]

            tileset_width, tileset_height = get_image_size(shrunk_img_name)
            tileset_template["identifier"] = curr_tileset_name
            tileset_template["uid"] = tileset_uid
            tileset_template[
                "relPath"
            ] = f"../resources/imported/graphics/tilesets/{shrunk_img_name}"
            tileset_template["pxWid"] = tileset_width
            tileset_template["pxHei"] = tileset_height
            tileset_template["enumTags"] = []
            tileset_template["tagsSourceEnumUid"] = None
            tileset_template["cachedPixelData"] = {}

            world_final["defs"]["tilesets"].append(tileset_template)

            # ldtk_raw[tileset_rmxp_name] = highest_uid + 1
            level["layerInstances"][-1]["overrideTilesetUid"] = tileset_uid

            # Add the tileset to known tileset list
            ldtk_tilesets[curr_tileset_name] = tileset_uid

    with open(Path(f"{ROOT}/{level_filename}"), "w", encoding="utf-8") as outfile:
        json.dump(level, outfile, indent=4)

    # Second part to write level into world file

    # Prepare level data to be added into the world file
    level["layerInstances"] = None
    level["externalRelPath"] = f"world/{level_filename}"
    level.pop("__header__")
    world_final["levels"].append(level)

    # Increment nextUid by 1
    world_template["nextUid"] += 1

# Save the final world file
with open(Path("world/world.ldtk"), "w", encoding="utf-8") as worldWrite:
    json.dump(world_final, worldWrite, indent=4)
