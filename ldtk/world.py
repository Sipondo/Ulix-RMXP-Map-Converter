import json
from pathlib import Path


class Ldtk():
    def __init__(self, project_filepath: Path):
        with open(project_filepath, "r", encoding="utf-8") as infile:
            self.json = json.load(infile)