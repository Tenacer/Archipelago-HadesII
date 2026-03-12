import typing
import settings

from ..AutoWorld import World
from .Options import hades_ii_option_groups, HadesIIOptions

from .Items import item_table, item_name_groups, Hades_II_Item, create_trap_pool
from .Items import item_table_keepsakes, item_table_weapons, item_table_aspects

from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings
from .Locations import location_table_prophecies_events

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
    options_dataclass = HadesIIOptions
    game: str = "Hades II"
    topology_present: bool = False
    settings: typing.ClassVar[HadesIISettings]
    # TODO: Web world eventually
    required_client_version: tuple = (0, 6, 4)
    
    item_name_to_id = {name: data.code for name, data in item_table.items() if data.code is not None}
    location_name_to_id = give_all_locations_table()
    
    # Type conversion for proper assignment / get rid of errors
    # Realistically idk if this matters a ton, but here we ares
    item_name_groups = {name: set(group) for name, group in item_name_groups.items()}
    location_name_groups = {name: set(group) for name, group in location_name_groups.items()}
    
    def create_items(self) -> None:
        local_location_table = setup_location_table_with_settings(self.options).copy()
        pool = []
        
        # Data is included but never used, not sure if it breaks anything to remove it, I'll test later
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
        total_fillers_needed = len(local_location_table) - len(pool) - len(location_table_prophecies_events) 
        
        # Define the percentages in the pool based off options
        # ? Add F. Fabric to speed things up for the player?
        percentages = {
            "ash": self.options.ash_pack_percentage,
            "bones": self.options.bones_pack_percentage,
            "psyche": self.options.psyche_pack_percentage,
            "nectar": self.options.nectar_pack_percentage,
            "ambrosia": self.options.ambrosia_pack_percentage,
            "nightmare": self.options.nightmare_pack_percentage,
            "helpers": self.options.filler_helper_percentage,
            "traps": self.options.filler_trap_percentage,
        }

        total_percentage = sum(percentages.values())

        if total_percentage == 0:
            percentages["bones"] = 100
            total_percentage = 100
            
        correction = 100/total_percentage
        
        # Calculate the needed amounts
        counts = {
            name: int(total_fillers_needed * pct * correction / 100)
            for name, pct in percentages.items()
        }

        # Populate the rest with bones for remainder safety
        counts["bones"] += total_fillers_needed - sum(counts.values())
        
        # Helpers
        health_helpers = int(counts["helpers"] * self.options.max_health_helper_percentage / 100)
        money_helpers = counts["helpers"] - health_helpers
        
        trap_pool = create_trap_pool()

        # Populate the pool with fillers
        items = {
            "Ash": counts["ash"],
            "Bones": counts["bones"],
            "Psyche": counts["psyche"],
            "Nectar": counts["nectar"],
            "Ambrosia": counts["ambrosia"],
            "Nightmare": counts["nightmare"],
            "Max Health Helper": health_helpers,
            "Initial Money Helper": money_helpers,
        }

        for name, count in items.items():
            for _ in range(count):
                pool.append(Hades_II_Item(name, self.player))
        
        # Fill traps
        for i in range(counts["traps"]):
            item_name = trap_pool[i % len(trap_pool)]
            pool.append(Hades_II_Item(item_name, self.player))
            
        # Add items to pool
        self.multiworld.itempool += pool
        
    # Rules
    def apply_rules(self):
        local_location_table = setup_location_table_with_settings(self.options).copy()
        set_rules(
                self.multiworld, self.player, self.calculate_number_of_pact_items(), 
                local_location_table, self.options
        )