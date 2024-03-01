from pathlib import Path
from DataLoader import DataLoader
from PIL import Image

class PSDKDataLoader(DataLoader):

    def __init__(self, project_path: Path):
        super().__init__(project_path)

        self.dir_tilesets = self.src / "graphics" / "tilesets"

    def get_tileset(self, tileset_name: str):
        # TODO: Uhh dunno if only png is allowed
        img_path = Path(self.dir_tilesets / f"{tileset_name}.png")
        return img_path

