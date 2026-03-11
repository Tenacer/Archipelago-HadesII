import typing
import settings

from ..AutoWorld import World
from .Options import hades_ii_option_groups, HadesIIOptions

from .Items import item_table, item_name_groups, Hades_II_Item, create_trap_pool
from .Items import item_table_keepsakes, item_table_weapons, item_table_aspects

from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings
from .Locations import location_table_prophecies_events

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
                
        # Aspects
        if self.options.aspectsanity:
            for name in item_table_aspects:
                item = Hades_II_Item(name, self.player)
                pool.append(item)
                
        # Filler Stuff
        # There's probably a more efficient way to do this with for loops or other iterables
        total_fillers_needed = len(local_location_table)- len(pool)- len(location_table_prophecies_events) 
        # Not 100% sure why the prophecies are in here, just copied and pasted, I'll figure it out later
        
        ash_pack_percentage = self.options.ash_pack_percentage
        bones_pack_percentage = self.options.bones_pack_percentage
        psyche_pack_percentage = self.options.psyche_pack_percentage
        nightmare_pack_percentage = self.options.nightmare_pack_percentage
        nectar_pack_percentage = self.options.nectar_pack_percentage
        ambrosia_pack_percentage = self.options.ambrosia_pack_percentage
        helper_percentage = self.options.filler_helper_percentage
        trap_percentage = self.options.filler_trap_percentage

        total_percentage = sum([ash_pack_percentage, bones_pack_percentage, psyche_pack_percentage, nightmare_pack_percentage, 
                                nectar_pack_percentage, ambrosia_pack_percentage, helper_percentage, trap_percentage])

        if total_percentage == 0:
            bones_pack_percentage = 100
            
        correction = 100/total_percentage
        
        ash_needed = int(total_fillers_needed * ash_pack_percentage * correction / 100)
        psyche_needed = int(total_fillers_needed * psyche_pack_percentage * correction / 100)
        nectar_needed = int(total_fillers_needed * nectar_pack_percentage * correction / 100)
        ambrosia_needed = int(total_fillers_needed * ambrosia_pack_percentage * correction / 100)
        nightmare_needed = int(total_fillers_needed * nightmare_pack_percentage * correction / 100)
        traps_needed = int(total_fillers_needed * trap_percentage * correction / 100)
        helpers_needed = int(total_fillers_needed * helper_percentage * correction / 100)
        
        bones_needed = (total_fillers_needed - psyche_needed - ash_needed - nightmare_needed
                        - nectar_needed - ambrosia_needed - traps_needed - helpers_needed)
        
        trap_pool = create_trap_pool()

        # Populate the pool with fillers
        # Again could probably be done with nested for loops, but I'll explore that later
        for _ in range(bones_needed):
            item = Hades_II_Item("Bones", self.player)
            pool.append(item)
            
        for _ in range(ash_needed):
            item = Hades_II_Item("Ash", self.player)
            pool.append(item)
            
        for _ in range(psyche_needed):
            item = Hades_II_Item("Psyche", self.player)
            pool.append(item)
            
        for _ in range(nectar_needed):
            item = Hades_II_Item("Nectar", self.player)
            pool.append(item)
        
        for _ in range(ambrosia_needed):
            item = Hades_II_Item("Ambrosia", self.player)
            pool.append(item)
            
        for _ in range(nectar_needed):
            item = Hades_II_Item("Nightmare", self.player)
            pool.append(item)
            
        # Helpers
        health_helpers_needed = int(helpers_needed * self.options.max_health_helper_percentage / 100)
        money_helpers_needed = int(100-health_helpers_needed)
        
        for _ in range(health_helpers_needed):
            item = Hades_II_Item("Max Health Helper", self.player)
            pool.append(item)
            
        for _ in range(money_helpers_needed):
            item = Hades_II_Item("Initial Money Helper", self.player)
            pool.append(item)
        
        
        # Fill traps
        # Having the separate index seems redundant, once again I'll figure it out later
        index = 0
        for _ in range(0, traps_needed):
            item_name = trap_pool[index]
            item = Hades_II_Item(item_name, self.player)
            pool.append(item)
            index = (index + 1) % len(trap_pool)