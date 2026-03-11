import typing
import settings

from ..AutoWorld import World
from .Options import hades_ii_option_groups, HadesIIOptions
from .Items import item_table, item_name_groups, Hades_II_Item

from .Items import item_table_keepsakes, item_table_weapons, item_table_aspects

from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings

# Probably needs to be re-done, mostly copied from H1 AP
# https://github.com/NaixGames/Polycosmos/

class HadesIISettings(settings.Group):
    class StyxScribePath(settings.UserFilePath):
        """Path to the StyxScribe install"""

    styx_scribe_path: StyxScribePath = StyxScribePath(
        "C:/Program Files/Steam/steamapps/common/Hades/StyxScribe.py")

class HadesIIWorld(World):
    options: HadesIIOptions
    options_dataclass = HadesIIOptions
    game = "Hades II"
    topology_present = False
    settings: typing.ClassVar[HadesIISettings]
    # TODO: Web world eventually
    required_client_version = (0, 6, 4)
    
    item_name_to_id = {name: data.code for name, data in item_table.items() if data.code is not None}
    location_name_to_id = give_all_locations_table()
    
    # Type conversion for proper assignment / get rid of errors
    # Realistically idk if this matters a ton, but here we ares
    item_name_groups = {name: set(group) for name, group in item_name_groups.items()}
    location_name_groups = {name: set(group) for name, group in location_name_groups.items()}
    
    def create_items(self) -> None:
        local_location_table = setup_location_table_with_settings(self.options).copy()
        pool = []
        
        # Data is included but never used, not sure if it breaks anything to remove it, I'll test later4
        # TODO: Fear
        
        # Keepsakes
        if self.options.keepsakesanity:
            for name in item_table_keepsakes:
                item = Hades_II_Item(name, self.player)
                pool.append(item)
        
        # Weapons
        if self.options.weaponsanity:
            for name in item_table_weapons:
                if self.should_ignore_weapon(name):
                    continue
                item = Hades_II_Item(name, self.player)
                pool.append(item)
                
        if self.options.aspectsanity:
            for name in item_table_aspects:
                item = Hades_II_Item(name, self.player)
                pool.append(item)