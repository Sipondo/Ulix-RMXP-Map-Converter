from rubymarshal.ruby import readruby
from pathlib import Path


class RmxpDataLoader:
    def __init__(self, essentials_folder: Path):
        self.src = essentials_folder

        # Get info on all maps
        # Index by map ID and .attributes[@attribute]
        self.map_infos = readruby(self.src / "Data" / "Mapinfos.rxdata")

    # Get level connections
    # Returns a list of all connection lists
    # 0: src    1:  edge    2: connected tile   3: dest     4: edge     5: connected tile
    # https://essentialsdocs.fandom.com/wiki/Connecting_maps#PBS_file_connections.txt
    def get_connections(self):
        """
        in: None
        out: A list of all connections
        """
        for name in ("map_connections.txt", "connections.txt"):
            try:
                with open(self.src / "PBS" / name) as connections_file:
                    lines = connections_file.readlines()
            except FileNotFoundError:
                continue

        connections = []
        # Skip the line about wiki documentation and the divider
        for line in lines[2:]:
            line = line.strip()
            if line.startswith("#"):
                continue
            values = line.split(",")
            values = list(map(lambda x: int(x) if x.isdecimal() else x, values))
            connections.append(values)
        self._map_connections = connections

    @property
    def map_connections(self):
        if not hasattr(self, "_map_connections"):
            self.get_connections()
        return self._map_connections

    # Get all rmxp maps
    # Returns a dict with map IDs as keys
    def get_rmxp_maps(self):
        """in: None
        out : a dict of names, by ID"""
        rmxp_maps = {}
        for file in (self.src / "Data").glob("Map???.rxdata"):
            id = int(file.name.split("p")[1][:3])
            rmxp_maps[id] = file.name
        self._rmxp_maps = rmxp_maps

    # Takes in a dict with ID: map name
    # Generate a dict of map tile sizes
    def get_rmxp_map_sizes(self):
        """in: A dict of names, by ID
        out: A dict of level sizes, by ID"""
        # Keys are map IDs
        level_sizes = {}
        for id, map in self.rmxp_maps.items():
            # Open a ruby map
            rubyData = readruby(self.src / "Data" / map)
            heightTiles = rubyData.attributes["@height"]
            widthTiles = rubyData.attributes["@width"]
            level_sizes[id] = (widthTiles, heightTiles)
        self._rmxp_map_sizes = level_sizes

    @property
    def rmxp_maps(self):
        if not hasattr(self, "_rmxp_maps"):
            self.get_rmxp_maps()
        return self._rmxp_maps

    @property
    def rmxp_map_sizes(self):
        if not hasattr(self, "_rmxp_map_sizes"):
            self.get_rmxp_map_sizes()
        return self._rmxp_map_sizes

    def get_level_locations(self, center_map_id=1):
        """
        @maps: A dict of map names, by ID
        in 2: A dict of map sizes, by ID
        out: A dict of all known level locations, by ID
        """
        center_loc = tuple(
            [0 - l // 2 for l in self.rmxp_map_sizes[center_map_id]] + [0]
        )
        level_locations = {center_map_id: center_loc}
        walk = True
        while walk:
            walk = False
            for id in self.rmxp_maps.keys():
                if id in level_locations:
                    continue
                for con in self.id_to_connections(id):
                    if con[3] not in level_locations:
                        continue
                    src_x, src_y, src_z = level_locations[con[3]]
                    src_wid, src_hei = self.rmxp_map_sizes[con[3]]
                    dest_wid, dest_hei = self.rmxp_map_sizes[id]
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
                        parent := self.map_infos[id].attributes["@parent_id"]
                    ) and parent in level_locations:
                        src_x, src_y, src_z = level_locations[parent]
                        level_locations[id] = src_x, src_y, src_z + 1
                        walk = True

        return level_locations

    # Returns a list of all connections related to an ID
    def id_to_connections(self, id):
        """
        in: map ID
        out: A list of all related connections
        """
        related_connections = []
        for connection in self.map_connections:
            if id == connection[0]:
                related_connections.append(connection)
            elif id == connection[3]:
                related_connections.append(connection[3:] + connection[:3])
        return related_connections

    def read_rmxp_map(self, map_name):
        rubyData = readruby(self.src / "Data" / map_name)
        return rubyData

    # Get all used rmxp tilesets
    def get_rmxp_tilesets(self):
        tileset_dict = {}
        tilesets = readruby(self.src / "Data" / "Tilesets.rxdata")
        for tileset in (t for t in tilesets if t is not None):
            if tileset.attributes["@tileset_name"].decode("utf-8") == "":
                continue
            tileset_name = tileset.attributes["@tileset_name"].decode("utf-8")
            id = tileset.attributes["@id"]
            tileset_dict[id] = tileset_name
        return tileset_dict

    # Get all used rmxp autotilesets
    def get_rmxp_autotilesets(self):
        """@returns: Dict of autotile names, indexable by map ID"""
        autotileset_dict = {}
        tilesets = readruby(self.src / "Data" / "Tilesets.rxdata")
        for tileset in (t for t in tilesets if t is not None):
            if tileset.attributes["@tileset_name"].decode("utf-8") == "":
                continue
            id = tileset.attributes["@id"]
            autotiles = [
                t.decode("utf-8") for t in tileset.attributes["@autotile_names"]
            ]
            autotileset_dict[id] = autotiles
        return autotileset_dict
