from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ldtk.world import World


class LayerInstance():
    def __init__(self) -> None:
        pass 

    def to_ldtk(self, world: 'World'):
        layer_instance =  LayerInstance()
        return layer_instance
        