from typing import Dict, NamedTuple, Optional
from BaseClasses import Item, ItemClassification
from .Locations import setup_location_table_with_settings, location_table_prophecies_events

class ItemData(NamedTuple):
    code: Optional[int]
    item_classification: ItemClassification
    event: bool = False
    
# Sorry for the abomination of uppercase and underscore here, but I figured it was more 
# readable than `HadesIIItem`
class Hades_II_Item(Item):
    game = "Hades"

    def __init__(self, name, player: int):
        item_data = item_table[name]
        itemClass = item_data.item_classification
            
        super(Hades_II_Item, self).__init__(name, itemClass, item_data.code, player)

hades_ii_base_item_id = 1

item_table_fears: Dict[str, ItemData] = {
    "Item1": ItemData(hades_ii_base_item_id, ItemClassification.progression),
    "Item2": ItemData(hades_ii_base_item_id+1, ItemClassification.progression)
}

item_table_prophesy_completion: Dict[str, ItemData] = {
    "prophesy | Event Item": ItemData(None, ItemClassification.progression, True)
}

item_table_filler: Dict[str, ItemData] = {
    "filler1": ItemData(hades_ii_base_item_id+3, ItemClassification.filler)
}

item_table_keepsakes: Dict[str, ItemData] = {
    "Hecate Keepsake": ItemData(hades_ii_base_item_id +4, ItemClassification.progression),
    "Odysseus Keepsake": ItemData(hades_ii_base_item_id +5, ItemClassification.progression),
    "Schelemeus Keepsake": ItemData(hades_ii_base_item_id +6, ItemClassification.progression),
    "Dora Keepsake": ItemData(hades_ii_base_item_id +7, ItemClassification.progression),
    "Nemesis Keepsake": ItemData(hades_ii_base_item_id +8, ItemClassification.progression),
    "Moros Keepsake": ItemData(hades_ii_base_item_id +9, ItemClassification.progression),
    "Eris Keepsake": ItemData(hades_ii_base_item_id +10, ItemClassification.progression),
    "Charon Keepsake": ItemData(hades_ii_base_item_id +11, ItemClassification.progression),
    "Hermes Keepsake": ItemData(hades_ii_base_item_id +12, ItemClassification.progression),
    "Artemis Keepsake": ItemData(hades_ii_base_item_id +13, ItemClassification.progression),
    "Selene Keepsake": ItemData(hades_ii_base_item_id +14, ItemClassification.progression),
    
    "Zeus Keepsake": ItemData(hades_ii_base_item_id +15, ItemClassification.progression),
    "Hera Keepsake": ItemData(hades_ii_base_item_id +16, ItemClassification.progression),
    "Poseidon Keepsake": ItemData(hades_ii_base_item_id +17, ItemClassification.progression),
    "Demeter Keepsake": ItemData(hades_ii_base_item_id +18, ItemClassification.progression),
    "Apollo Keepsake": ItemData(hades_ii_base_item_id +19, ItemClassification.progression),
    "Aphrodite Keepsake": ItemData(hades_ii_base_item_id +20, ItemClassification.progression),
    "Hephaestus Keepsake": ItemData(hades_ii_base_item_id +21, ItemClassification.progression),
    "Hestia Keepsake": ItemData(hades_ii_base_item_id +22, ItemClassification.progression),
    "Ares Keepsake": ItemData(hades_ii_base_item_id +23, ItemClassification.progression),
    "Athena Keepsake": ItemData(hades_ii_base_item_id +24, ItemClassification.progression),
    "Dionysus Keepsake": ItemData(hades_ii_base_item_id +25, ItemClassification.progression),
    
    "Arachne Keepsake": ItemData(hades_ii_base_item_id +26, ItemClassification.progression),
    "Narcissus Keepsake": ItemData(hades_ii_base_item_id +27, ItemClassification.progression),
    "Echo Keepsake": ItemData(hades_ii_base_item_id +28, ItemClassification.progression),
    "Heracles Keepsake": ItemData(hades_ii_base_item_id +29, ItemClassification.progression),
    "Medea Keepsake": ItemData(hades_ii_base_item_id +30, ItemClassification.progression),
    "Circe Keepsake": ItemData(hades_ii_base_item_id +31, ItemClassification.progression),
    "Icarus Keepsake": ItemData(hades_ii_base_item_id +32, ItemClassification.progression),
    
    "Hades/Persephone Keepsake": ItemData(hades_ii_base_item_id +33, ItemClassification.progression),
    "Zagreus Keepsake": ItemData(hades_ii_base_item_id +34, ItemClassification.progression),
    "Chronos Keepsake": ItemData(hades_ii_base_item_id +35, ItemClassification.progression),
    
    "Chaos Keepsake": ItemData(hades_ii_base_item_id +36, ItemClassification.progression),
}

item_table_weapons: Dict[str, ItemData] = {
    "Staff Weapon Unlock Item": ItemData(hades_ii_base_item_id+37, ItemClassification.progression),
    "Daggers Weapon Unlock Item": ItemData(hades_ii_base_item_id+38, ItemClassification.progression),
    "Torches Weapon Unlock Item": ItemData(hades_ii_base_item_id+39, ItemClassification.progression),
    "Axe Weapon Unlock Item": ItemData(hades_ii_base_item_id+40, ItemClassification.progression),
    "Skull Weapon Unlock Item": ItemData(hades_ii_base_item_id+41, ItemClassification.progression),
    "Coat Weapon Unlock Item": ItemData(hades_ii_base_item_id+42, ItemClassification.progression)
}

item_table_tools: Dict[str, ItemData] = {
    "X Tool Unlock Item": ItemData(hades_ii_base_item_id+11, ItemClassification.progression)
}

item_table_aspects: Dict[str, ItemData] = {
    "X Weapon Y Aspect Unlock Item": ItemData(hades_ii_base_item_id+12, ItemClassification.progression)
}

item_table_traps: Dict[str, ItemData] = {
    "trap1": ItemData(hades_ii_base_item_id+13, ItemClassification.trap)
}

item_table_helpers: Dict[str, ItemData] = {
    "helper1": ItemData(hades_ii_base_item_id+14, ItemClassification.progression | ItemClassification.useful)
}

item_table = {
    **item_table_fears,
    **item_table_prophesy_completion,
    **item_table_filler,
    **item_table_keepsakes,
    **item_table_weapons,
    **item_table_tools,
    **item_table_aspects,
    **item_table_traps,
    **item_table_helpers,
}

group_fears = {"fears": item_table_fears.keys()}
group_fillers = {"fillers": item_table_filler.keys()}
group_weapons = {"weapons": item_table_weapons.keys()}
group_tools = {"tools": item_table_tools.keys()}
group_aspects = {"aspects": item_table_aspects.keys()}
group_keepsakes = {"keepsakes": item_table_keepsakes.keys()}

item_name_groups = {
    **group_fears,
    **group_fillers,
    **group_tools,
    **group_weapons,
    **group_aspects,
    **group_keepsakes,
}

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
        trap_pool = create_trap_pool()
        for i in range(counts["traps"]):
            item_name = trap_pool[i % len(trap_pool)]
            pool.append(Hades_II_Item(item_name, self.player))
            
        # Place in boss events
        place_boss_events(self.world, self.player)
            
        # Add items to pool
        self.multiworld.itempool += pool

def create_trap_pool():
    return [trap for trap in item_table_traps.keys()]

# Places boss event pseudo-items at each location
def place_boss_events(world, player):
    bosses = [
        "Hecate Victory",
        "Scylla Victory",
        "Cerberus Victory",
        "Chronos Victory",
        "Polyphemus Victory",
        "Eris Victory",
        "Prometheus Victory",
        "Typhon Victory",
    ]

    for boss in bosses:
        location = world.get_location(boss, player)
        item = world.create_event(boss)
        location.place_locked_item(item)