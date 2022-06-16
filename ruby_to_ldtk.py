from rubymarshal.ruby import readruby, writeruby
import numpy as np
from pathlib import Path
import json
import copy
import rmxpdataloader

from tilesetconverter import (
    get_image_size,
    import_tileset,
)

# TODO: Multiple different autotiles on one layer
# TODO: Fix animated tilesets
ROOT = Path("world/world")
LDTK_TEMPLATE = Path("./0000-Template.ldtkl")
WORLD_TEMPLATE = Path("./worldTemplate.ldtk")
ESSENTIALS_FOLDER = Path(r"C:\Pythonpaskaa\Pokemon Essentials v20")
# Convert coords into the single int pointer format
def coordToInt(coords, width):
    return coords[0] + coords[1] * width


# Take in a single int tile texture pointer and return the coordinate version of it
def tToSrc(value):
    x = value % 8 * 16
    y = value // 8 * 16
    return [x, y]


def where_value_is(origin, item, value):
    """
    @param: Indexable object
    @param: Item to search for
    @param: Value that item should be
    @returns: The item that contains the value"""
    for i in origin:
        if i[item] == value:
            return i


# Determine if the autotile should be a layer default tileset
def get_autotile_layer(autotile_name):
    """Checks the name against keywords to see if it should be the default tileset
    @param: The name of the autotileset
    @returns: The name of the autotile layer it should go on"""
    auto_water = ["Sea", "Flowers", "Flowers1"]
    auto_cliff = []
    auto_road = ["brick", "path", "Brick path"]
    if autotile_name in auto_water:
        return "Auto_Water_A"
    if autotile_name in auto_cliff:
        return "Auto_Cliff_A"
    if autotile_name in auto_road:
        return "Auto_Road_A"


def create_level_filename(name):
    mapIndex = 0
    for file in ROOT.glob("*.ldtkl"):
        currNum = int(file.name.split("-")[0])
        if currNum >= mapIndex:
            mapIndex = currNum + 1
    tmpName = data_loader.map_infos[id].attributes["@name"].decode("utf-8")
    mapName = "".join(l for l in tmpName if l.isalnum())
    levelName = f"L{id}_{mapName}"
    levelFilename = f"{mapIndex:0>4}-{levelName}.ldtkl"
    return levelFilename


## Start doing stuff here
# Open world file for reading
with open(WORLD_TEMPLATE, "r", encoding="utf-8") as worldFile:
    world_template = json.load(worldFile)
    world_final = copy.deepcopy(world_template)

# Open a level template
with open(LDTK_TEMPLATE, "r", encoding="utf-8") as ldtkTemplate:
    level_template = json.load(ldtkTemplate)
    level_final = copy.deepcopy(level_template)


data_loader = rmxpdataloader.RmxpDataLoader(ESSENTIALS_FOLDER)

# Get the sizes and pre-calculate locations
level_sizes = data_loader.get_rmxp_map_sizes()
level_locations = data_loader.get_level_locations(center_map_id=2)

# Find out what tilesets are needed
rmxp_tilesets = data_loader.get_rmxp_tilesets()
rmxp_autotilesets = data_loader.get_rmxp_autotilesets()
imported_tilesets = {}

# Start for loop here

for id, rmxp_map in data_loader.rmxp_maps.items():
    print("Importing level: ", rmxp_map)

    level = copy.deepcopy(level_template)

    # Open a ruby map
    rubyData = data_loader.read_rmxp_map(rmxp_map)

    # Grab numpy array of map
    rubyArray = rubyData.attributes["@data"].to_array()

    widthTiles, heightTiles = data_loader.rmxp_map_sizes[id]
    widthPx = widthTiles * 16
    heightPx = heightTiles * 16

    curr_tileset_id = rubyData.attributes["@tileset_id"]
    curr_tileset_name = rmxp_tilesets[curr_tileset_id]
    autotile_array = np.zeros((heightTiles, widthTiles), int)

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

                # Negative means an autotile
                if t < 0:
                    t += 384
                    autotile_index = t // 48 - 1
                    autotileset = rmxp_autotilesets[curr_tileset_id][autotile_index]
                    autotile_array[indexY][indexX] = 1

                else:
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
    # Write autotiles
    level["layerInstances"][-2]["intGridCsv"] = autotile_array.flatten().tolist()

    # Create an unique name for the new level
    level_name = data_loader.map_infos[id].attributes["@name"].decode("utf-8")
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

    # Set the correct ground tileset

    # Create a list of tilesets that are needed
    imports = []
    imports.append(curr_tileset_name)
    if curr_tileset_id in rmxp_autotilesets:
        for item in rmxp_autotilesets[curr_tileset_id]:
            imports.append(item)

    # Convert tilesets and add them to a list of converted tilesets
    # TODO: Maybe add a default tileset to layers
    # autotile_layer["tilesetDefUid"] = tileset_uid
    # autotile_layer["autoTilesetDefUid"] = tileset_uid
    for item in imports:
        # Check if working with an autotile
        at = False if item == curr_tileset_name else True

        # Convert the tilesets
        if item not in imported_tilesets:
            if tileset_path := import_tileset(item, autotile=at):
                try:
                    tileset_uid += 1
                except NameError:
                    # Arbitrary value that doesnt overlap with current uids
                    tileset_uid = 500

                # Prepare tileset data to the world file
                tileset_template = copy.deepcopy(world_template["defs"]["tilesets"][0])
                folder = "autotiles" if at else "tilesets"
                tileset_template[
                    "relPath"
                ] = f"../resources/imported/graphics/{folder}/{tileset_path}"
                tileset_width, tileset_height = get_image_size(
                    tileset_path, autotile=at
                )

                tileset_template["identifier"] = item
                tileset_template["uid"] = tileset_uid

                tileset_template["pxWid"] = tileset_width
                tileset_template["pxHei"] = tileset_height
                tileset_template["enumTags"] = []
                tileset_template["tagsSourceEnumUid"] = None
                tileset_template["cachedPixelData"] = {}

                # Save to known tilesets
                imported_tilesets[item] = tileset_uid

                # And append tileset to world file
                world_final["defs"]["tilesets"].append(tileset_template)
            else:
                print(f"Could not import tileset: {item}")

        if item in imported_tilesets:
            # Set UID into level
            ts_id = imported_tilesets[item]
            if at:
                if ldtk_layer := get_autotile_layer(item):
                    autotile_layer = where_value_is(
                        level["layerInstances"], "__identifier", ldtk_layer
                    )
                    autotile_layer["overrideTilesetUid"] = ts_id
            else:
                level["layerInstances"][-1]["overrideTilesetUid"] = ts_id

    with open(ROOT / level_filename, "w", encoding="utf-8") as outfile:
        json.dump(level, outfile, indent=4)

    # Second part to write level into world file

    # Prepare level data to be added into the world file
    level["layerInstances"] = None
    level["externalRelPath"] = f"world/{level_filename}"
    level.pop("__header__")
    world_final["levels"].append(level)

    # Increment nextUid by 1
    world_template["nextUid"] += 1

# Set world file default tilesets
for item in world_final["defs"]["layers"]:
    item_id = item["identifier"]

    try:
        if item_id == "Auto_Water_A":
            ts_id = imported_tilesets["Sea"]
        elif item_id == "Auto_Road_B":
            ts_id = imported_tilesets["Road"]
        elif item_id == "Auto_Cliff_A":
            ts_id = imported_tilesets["Cliff"]
    except KeyError:
        print("Could not set default tileset for layer:", item_id)
        continue
    item["tilesetDefUid"] = ts_id
    item["autoTilesetDefUid"] = ts_id

# Save the final world file
with open(Path("world/world.ldtk"), "w", encoding="utf-8") as worldWrite:
    json.dump(world_final, worldWrite, indent=4)
