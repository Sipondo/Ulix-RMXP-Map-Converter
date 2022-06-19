import numpy as np
from pathlib import Path
import json
import copy
import rmxpdataloader
import string

from tilesetconverter import (
    get_image_size,
    import_tileset,
)

# TODO: Multiple different autotiles on one layer
#   - Kind of done
#   - Slow and autotile borders are funky
# TODO: Add extry layers on all levels in the code so ldtk doesnt have to do it
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


# Checks the autotileset name to determine what layer to put it on
def get_autotile_layer(autotile_name):
    """
    @param: The name of the autotileset
    @returns: The name of the autotile layer it should go on"""
    lower = autotile_name.lower()

    for i in ["water", "fountain", "sea", "flowers", "flowers1"]:
        if i in lower:
            return "Auto_Water_"

    for i in ["cliff"]:
        if i in lower:
            return "Auto_Cliff_"

    for i in ["brick", "path"]:
        if i in lower:
            return "Auto_Road_"


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


class Level:
    def __init__(self, level_filepath, world):
        with open(level_filepath, "r", encoding="utf-8") as infile:
            self.json = json.load(infile)

        # Create some useful attributes
        self.layers = {
            x["__identifier"]: x for x in self.json["layerInstances"]
        }  # TODO: Maybe make it a property
        self.name = self.json["identifier"]
        self.filepath = level_filepath
        self.world = world

    def layer_exists(self, layer_name):
        for k in self.layers:
            if k == layer_name:
                return True
        return False

    def next_layer_name(self, layer_type):
        for l in string.ascii_uppercase:
            if not self.layer_exists(name := layer_type + l):
                return name
        return None

    def fill_autotile_layer(self, layer, needed):
        for i in range(needed):
            lc = copy.deepcopy(self.layers["Auto_Water_A"])
            lc["intGridCsv"][lc["intGridCsv"] == 1] = 0
            lc["__identifier"] = id = self.next_layer_name(layer)
            lc["layerDefUid"] = self.world.layer_uids[id]

            # Add it to the class
            self.layers[id] = lc
            self.json["layerInstances"].append(lc)

    def write(self):
        with open(self.filepath, "w", encoding="utf-8") as outfile:
            json.dump(self.json, outfile, indent=4)


class World:
    def __init__(self, world_filepath):
        with open(world_filepath, "r", encoding="utf-8") as infile:
            self.json = json.load(infile)

        # Create some useful attributes
        self.filepath = world_filepath

    @property
    def layer_uids(self):
        return {x["identifier"]: x["uid"] for x in self.json["defs"]["layers"]}


def fill_empty_autotile_layers(level, layers_nd_fx):
    with open(Path("world/world") / level, "r", encoding="utf-8") as infile:
        lvl = json.load(infile)
    layer_copy = copy.deepcopy(
        where_value_is(lvl["layerInstances"], "__identifier", "Auto_Water_A")
    )
    # Zero out all values
    layer_copy["intGridCsv"][layer_copy["intGridCsv"] == 1] = 0
    for k, v in layers_nd_fx.items():
        for i in range(v):
            layer_append = copy.deepcopy(layer_copy)
            ab = string.ascii_uppercase[i + 1]
            layer_append["__identifier"] = k + ab
            lvl["layerInstances"].append(layer_append)
            # TODO: Set correct layer uid also
            # TODO: Also start incrementing alphabet at the correct index

    # Write the level with the added levels
    with open(Path("world/world") / level, "w", encoding="utf-8") as outfile:
        json.dump(lvl, outfile, indent=4)


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
levels_layers_added = {}

# Start for loop here

for id, rmxp_map in data_loader.rmxp_maps.items():
    # if id != 7:
    #     continue
    print("Importing level: ", rmxp_map)

    level = copy.deepcopy(level_template)

    # Open a ruby map
    rubyData = data_loader.read_rmxp_map(rmxp_map)

    # Grab numpy array of map
    rubyArray = rubyData.attributes["@data"].to_array()

    # Calculate the level dimensions in tiles and pixels
    widthTiles, heightTiles = data_loader.rmxp_map_sizes[id]
    widthPx = widthTiles * 16
    heightPx = heightTiles * 16

    # Get the ID number and name of the current level
    curr_tileset_id = rubyData.attributes["@tileset_id"]
    curr_tileset_name = rmxp_tilesets[curr_tileset_id]

    # Clear the ground layer tiles
    # [-1] is Ground layer
    level["layerInstances"][-1]["gridTiles"] = []

    # Create an empty dict to hold autotile arrays
    autotile_arrays = {}
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

                    # Create a zeros array the size of the level for the current autotileset
                    if autotileset not in autotile_arrays:
                        autotile_arrays[autotileset] = np.zeros(
                            (heightTiles, widthTiles), int
                        )

                    # Add arrays to a dict, to be written into the level later
                    autotile_arrays[autotileset][indexY][indexX] = 1

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

    # Create a list of tilesets that are needed for this level
    imports = []
    imports.append(curr_tileset_name)
    if curr_tileset_id in rmxp_autotilesets:
        for item in rmxp_autotilesets[curr_tileset_id]:
            imports.append(item)

    # A list of already added tilesets
    added_to_level = {
        "Ground": [],
        "Auto_Water_": [],
        "Auto_Road_": [],
        "Auto_Cliff_": [],
    }
    # For every tileset (normal and autotile) that are used in the rmxp tileset
    for item in imports:
        # Check if working with an autotile
        at = False if item == curr_tileset_name else True

        # If the autotile is not being used in the current level
        if at and item not in autotile_arrays:
            continue

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

        # Set tileset UID into level
        if item in imported_tilesets:
            ts_id = imported_tilesets[item]

            # If not an autotile, write to ground layer
            if not at:
                ldtk_layer = "Ground"
                level["layerInstances"][-1]["overrideTilesetUid"] = ts_id

            # Do lots of stuff if it is an autotile
            else:
                # Decide what layer to put the tileset on
                if not (ldtk_layer := get_autotile_layer(item)):

                    # We dont know where to put the autotile. Skip it and hopefully improve the function
                    print(
                        f"Couldn't decide a layer for {item}. Make the deciding function better"
                    )
                    continue

                # Layer is known, start work
                else:
                    ab_index = len(added_to_level[ldtk_layer])
                    layer_with_ab = ldtk_layer + string.ascii_uppercase[ab_index]

                    # Check if layers already exist
                    autotile_layer = where_value_is(
                        level["layerInstances"], "__identifier", layer_with_ab
                    )
                    world_autotile_layer = where_value_is(
                        world_final["defs"]["layers"], "identifier", layer_with_ab
                    )

                    # If layer doesn't exist yet in the world file
                    if world_autotile_layer is None:
                        try:
                            world_layer_uid += 1
                        except NameError:
                            # Arbitrary value that doesnt overlap with current uids
                            world_layer_uid = 700

                        # Make a copy of the original autotileset layer in the world file
                        world_layer_copy = copy.deepcopy(
                            where_value_is(
                                world_final["defs"]["layers"],
                                "identifier",
                                ldtk_layer + "A",
                            )
                        )
                        world_layer_copy["uid"] = world_layer_uid
                        world_layer_copy["identifier"] = layer_with_ab
                        world_final["defs"]["layers"].append(world_layer_copy)

                    # If layer doesn't exist in the level file
                    if autotile_layer is None:
                        # Make a copy of the original autotileset layer
                        layer_copy = copy.deepcopy(
                            where_value_is(
                                level["layerInstances"],
                                "__identifier",
                                ldtk_layer + "A",
                            )
                        )
                        world_autotile_layer = where_value_is(
                            world_final["defs"]["layers"], "identifier", layer_with_ab
                        )

                        # Set the correct data for the level
                        layer_copy["__identifier"] = layer_with_ab
                        layer_copy["layerDefUid"] = world_autotile_layer["uid"]
                        layer_copy["overrideTilesetUid"] = ts_id
                        layer_copy["intGridCsv"] = (
                            autotile_arrays[item].flatten().tolist()
                        )
                        level["layerInstances"].append(layer_copy)

                    # This is the A layer, just write to it
                    else:
                        autotile_layer["overrideTilesetUid"] = ts_id
                        autotile_layer["intGridCsv"] = (
                            autotile_arrays[item].flatten().tolist()
                        )

            # Append current tileset to list of tilesets that exist in the level
            added_to_level[ldtk_layer].append(item)

            # Save what layers where added to each level, so we can fill in empty ones later
            levels_layers_added[level_filename] = added_to_level

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

# Final fixes before we write the world file
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

# Fill missing autotile layers with empty ones
# Calculate how many of each layer is needed
highest_layers = {}
for level in levels_layers_added.values():
    for k, v in level.items():
        try:
            highest_layers[k] = max(len(v), highest_layers[k])
        except KeyError:
            highest_layers[k] = len(v)
# Check what levels need fixing and where
needs_fixing = {}
for level_id, layers in levels_layers_added.items():
    needs_fixing[level_id] = {}
    for k, v in layers.items():
        v.append(
            "def_layer"
        )  # One of each layer always exist, but isnt on "added" list
        if len(v) < highest_layers[k]:
            needs_fixing[level_id][k] = highest_layers[k] - len(v)

# Save the final world file
with open(Path("world/world.ldtk"), "w", encoding="utf-8") as worldWrite:
    json.dump(world_final, worldWrite, indent=4)

# Now apply the fixes
world = World("world/world.ldtk")
for level_filename, v in needs_fixing.items():
    level = Level(Path("world/world") / level_filename, world)
    for l_type, l_needed in v.items():
        level.fill_autotile_layer(l_type, l_needed)
        level.write()
