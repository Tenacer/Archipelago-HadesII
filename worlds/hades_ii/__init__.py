import typing
import settings

from ..AutoWorld import World
from .Options import HadesIIOptions
from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings
from .Regions import create_regions
from .Items import item_table, item_name_groups, create_items
from .Rules import set_rules

# Probably needs to be re-done, mostly copied from H1 AP
# https://github.com/NaixGames/Polycosmos/

class HadesIISettings(settings.Group):
    class StyxScribePath(settings.UserFilePath):
        """Path to the StyxScribe install"""

    styx_scribe_path: StyxScribePath = StyxScribePath(
        "C:/Program Files/Steam/steamapps/common/Hades/StyxScribe.py")

class HadesIIWorld(World):
    options: HadesIIOptions
    # options_dataclass = HadesIIOptions
    game: str = "Hades II"
    topology_present: bool = False
    settings: typing.ClassVar[HadesIISettings]
    # TODO: Web world eventually
    required_client_version: tuple = (0, 6, 4)
    
    item_name_to_id = {name: data.code for name, data in item_table.items() if data.code is not None}
    location_name_to_id = give_all_locations_table()
    
    item_name_groups = {name: set(group) for name, group in item_name_groups.items()}
    location_name_groups = {name: set(group) for name, group in location_name_groups.items()}
    
    # Rules
    def create_regions(self):
        create_regions(self.player, self.multiworld, self.location_name_to_id)
        
    # Items
    def create_items(self):
        create_items(self)
       
    # Rules
    def set_rules(self):
        local_location_table = setup_location_table_with_settings(self.options).copy()
        set_rules( self.multiworld, self.player, local_location_table, self.options)