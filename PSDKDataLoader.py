from pathlib import Path
from DataLoader import DataLoader

class PSDKDataLoader(DataLoader):
    def __init__(self, project_path: Path):
        DataLoader.__init__(self, project_path)

