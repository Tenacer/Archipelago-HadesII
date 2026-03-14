from typing import Dict, NamedTuple, Optional
from BaseClasses import Item, ItemClassification
from .Locations import setup_location_table_with_settings, location_table_prophecies

class ItemData(NamedTuple):
    code: Optional[int]
    item_classification: ItemClassification
    event: bool = False
    
# Sorry for the abomination of uppercase and underscore here, but I figured it was more 
# readable than `HadesIIItem`
class Hades_II_Item(Item):
    game = "Hades II"

    def __init__(self, name: str, player: int):
        item_data = item_table[name]
        super().__init__(name, item_data.item_classification, item_data.code, player)

hades_ii_base_item_id = 1

fears_base_item_id = hades_ii_base_item_id
item_table_fears: Dict[str, ItemData] = {
    "Item1": ItemData(hades_ii_base_item_id+1, ItemClassification.progression),
    "Item2": ItemData(hades_ii_base_item_id+2, ItemClassification.progression)
}

filler_base_item_id = fears_base_item_id + 2
item_table_filler: Dict[str, ItemData] = {
    "filler1": ItemData(filler_base_item_id+1, ItemClassification.filler),
    "filler2": ItemData(filler_base_item_id+2, ItemClassification.filler)
}

keepsakes_base_item_id  = filler_base_item_id + 2
item_table_keepsakes: Dict[str, ItemData] = {
    "Hecate Keepsake": ItemData(keepsakes_base_item_id + 1, ItemClassification.progression),
    "Odysseus Keepsake": ItemData(keepsakes_base_item_id + 2, ItemClassification.progression),
    "Schelemeus Keepsake": ItemData(keepsakes_base_item_id + 3, ItemClassification.progression),
    "Dora Keepsake": ItemData(keepsakes_base_item_id + 4, ItemClassification.progression),
    "Nemesis Keepsake": ItemData(keepsakes_base_item_id + 5, ItemClassification.progression),
    "Moros Keepsake": ItemData(keepsakes_base_item_id + 6, ItemClassification.progression),
    "Eris Keepsake": ItemData(keepsakes_base_item_id + 7, ItemClassification.progression),
    "Charon Keepsake": ItemData(keepsakes_base_item_id + 8, ItemClassification.progression),
    "Hermes Keepsake": ItemData(keepsakes_base_item_id + 9, ItemClassification.progression),
    "Artemis Keepsake": ItemData(keepsakes_base_item_id + 10, ItemClassification.progression),
    "Selene Keepsake": ItemData(keepsakes_base_item_id + 11, ItemClassification.progression),

    "Zeus Keepsake": ItemData(keepsakes_base_item_id + 12, ItemClassification.progression),
    "Hera Keepsake": ItemData(keepsakes_base_item_id + 13, ItemClassification.progression),
    "Poseidon Keepsake": ItemData(keepsakes_base_item_id + 14, ItemClassification.progression),
    "Demeter Keepsake": ItemData(keepsakes_base_item_id + 15, ItemClassification.progression),
    "Apollo Keepsake": ItemData(keepsakes_base_item_id + 16, ItemClassification.progression),
    "Aphrodite Keepsake": ItemData(keepsakes_base_item_id + 17, ItemClassification.progression),
    "Hephaestus Keepsake": ItemData(keepsakes_base_item_id + 18, ItemClassification.progression),
    "Hestia Keepsake": ItemData(keepsakes_base_item_id + 19, ItemClassification.progression),
    "Ares Keepsake": ItemData(keepsakes_base_item_id + 20, ItemClassification.progression),
    "Athena Keepsake": ItemData(keepsakes_base_item_id + 21, ItemClassification.progression),
    "Dionysus Keepsake": ItemData(keepsakes_base_item_id + 22, ItemClassification.progression),

    "Arachne Keepsake": ItemData(keepsakes_base_item_id + 23, ItemClassification.progression),
    "Narcissus Keepsake": ItemData(keepsakes_base_item_id + 24, ItemClassification.progression),
    "Echo Keepsake": ItemData(keepsakes_base_item_id + 25, ItemClassification.progression),
    "Heracles Keepsake": ItemData(keepsakes_base_item_id + 26, ItemClassification.progression),
    "Medea Keepsake": ItemData(keepsakes_base_item_id + 27, ItemClassification.progression),
    "Circe Keepsake": ItemData(keepsakes_base_item_id + 28, ItemClassification.progression),
    "Icarus Keepsake": ItemData(keepsakes_base_item_id + 29, ItemClassification.progression),

    "Hades/Persephone Keepsake": ItemData(keepsakes_base_item_id + 30, ItemClassification.progression),
    "Zagreus Keepsake": ItemData(keepsakes_base_item_id + 31, ItemClassification.progression),
    "Chronos Keepsake": ItemData(keepsakes_base_item_id + 32, ItemClassification.progression),

    "Chaos Keepsake": ItemData(keepsakes_base_item_id + 33, ItemClassification.progression),
}

weapons_base_item_id = keepsakes_base_item_id + 33
item_table_weapons: Dict[str, ItemData] = {
    "Staff Weapon Unlock Item": ItemData(weapons_base_item_id +1, ItemClassification.progression),
    "Daggers Weapon Unlock Item": ItemData(weapons_base_item_id + 2, ItemClassification.progression),
    "Torches Weapon Unlock Item": ItemData(weapons_base_item_id + 3, ItemClassification.progression),
    "Axe Weapon Unlock Item": ItemData(weapons_base_item_id + 4, ItemClassification.progression),
    "Skull Weapon Unlock Item": ItemData(weapons_base_item_id + 5, ItemClassification.progression),
    "Coat Weapon Unlock Item": ItemData(weapons_base_item_id + 6, ItemClassification.progression)
}

tools_base_item_id = weapons_base_item_id +6
item_table_tools: Dict[str, ItemData] = {
    "Crescent Pickaxe Tool Unlock Item": ItemData(tools_base_item_id + 1, ItemClassification.progression),
    "Tablet of Peace Tool Unlock Item": ItemData(tools_base_item_id + 1, ItemClassification.progression),
    "Silver Spade Tool Unlock Item": ItemData(tools_base_item_id+  1, ItemClassification.progression),
    "Rod of Fishing Tool Unlock Item": ItemData(tools_base_item_id + 1, ItemClassification.progression)

}

aspects_base_item_id = tools_base_item_id +4
item_table_aspects: Dict[str, ItemData] = {
    "X Weapon Y Aspect Unlock Item": ItemData(aspects_base_item_id+ 1 , ItemClassification.progression)
}

traps_base_item_id = aspects_base_item_id + 24
item_table_traps: Dict[str, ItemData] = {
    "trap1": ItemData(hades_ii_base_item_id+13, ItemClassification.trap)
}

helpers_base_item_id = traps_base_item_id + 1
item_table_helpers: Dict[str, ItemData] = {
    "helper1": ItemData(hades_ii_base_item_id+14, ItemClassification.progression | ItemClassification.useful)
}

# prophecies_base_item_id = helpers_base_item_id + 1
# item_table_prophecies_completion = {
#     "Melinoë, Help Us Reward": ItemData(prophecies_base_item_id+1, ItemClassification.progression, False),
#     "Melinoë, Remember Us Event": ItemData(prophecies_base_item_id+2, ItemClassification.progression, False),
#     "Melinoë, Seek Us Event": ItemData(prophecies_base_item_id+3, ItemClassification.progression, True),
#     "Melinoë, Find Us Event": ItemData(prophecies_base_item_id+4, ItemClassification.progression, True),
#     "Storm in the Heavens Event": ItemData(prophecies_base_item_id+5, ItemClassification.progression, True),
#     "Temporary Setback Event": ItemData(prophecies_base_item_id+6, ItemClassification.progression, True),
#     "Harbinger of Doom Event": ItemData(prophecies_base_item_id+7, ItemClassification.progression, True),
#     "Witch of the Crossroads Event": ItemData(prophecies_base_item_id+8, ItemClassification.progression, True),
#     "Natural Talent Event": ItemData(prophecies_base_item_id+9, ItemClassification.progression, True),
#     "Sword of the Night Event": ItemData(prophecies_base_item_id+10, ItemClassification.progression, True),
#     "Arcana of the Ages Event": ItemData(prophecies_base_item_id+11, ItemClassification.progression, True),
#     "Unrivaled Prowess Event": ItemData(prophecies_base_item_id+12, ItemClassification.progression, True),
#     "Bearing Dark Gifts Event": ItemData(prophecies_base_item_id+13, ItemClassification.progression, True),
#     "Den Mother Event": ItemData(prophecies_base_item_id+14, ItemClassification.progression, True),
#     "Family in Need Event": ItemData(prophecies_base_item_id+15, ItemClassification.progression, True),
#     "Visions of Victory Event": ItemData(prophecies_base_item_id+16, ItemClassification.progression, True),
#     "Unfinished Business Event": ItemData(prophecies_base_item_id+17, ItemClassification.progression, True),
#     "Haunted by the Past Event": ItemData(prophecies_base_item_id+18, ItemClassification.progression, True),
#     "Silk and Spitefulness Event": ItemData(prophecies_base_item_id+19, ItemClassification.progression, True),
#     "Voice and Vanity Event": ItemData(prophecies_base_item_id+20, ItemClassification.progression, True),
#     "Bitter Tears Event": ItemData(prophecies_base_item_id+21, ItemClassification.progression, True),
#     "Drowned Ambitions Event": ItemData(prophecies_base_item_id+22, ItemClassification.progression, True),
#     "The Jackal's Aspect Event": ItemData(prophecies_base_item_id+23, ItemClassification.progression, True),
#     "The Crow's Aspect Event": ItemData(prophecies_base_item_id+24, ItemClassification.progression, True),
#     "The Shadow's Aspect Event": ItemData(prophecies_base_item_id+25, ItemClassification.progression, True),
#     "The Warrior's Aspect Event": ItemData(prophecies_base_item_id+26, ItemClassification.progression, True),
#     "The Grave's Aspect Event": ItemData(prophecies_base_item_id+27, ItemClassification.progression, True),
#     "The Destroyer's Aspect Event": ItemData(prophecies_base_item_id+28, ItemClassification.progression, True),
#     "Nobody but Nobody Event": ItemData(prophecies_base_item_id+29, ItemClassification.progression, True),
#     "Born to Win Event": ItemData(prophecies_base_item_id+30, ItemClassification.progression, True),
#     "Improbable Outcomes Event": ItemData(prophecies_base_item_id+31, ItemClassification.progression, True),
#     "Soundest of Slumbers Event": ItemData(prophecies_base_item_id+32, ItemClassification.progression, True),
#     "Customary Gift Event": ItemData(prophecies_base_item_id+33, ItemClassification.progression, True),
#     "Mindful Craft Event": ItemData(prophecies_base_item_id+34, ItemClassification.progression, True),
#     "Blades of Pure Silver Event": ItemData(prophecies_base_item_id+35, ItemClassification.progression, True),
#     "The Arms of Night Event": ItemData(prophecies_base_item_id+36, ItemClassification.progression, True),
#     "The Unseen Sentinel Event": ItemData(prophecies_base_item_id+37, ItemClassification.progression, True),
#     "Awakened Aspect Event": ItemData(prophecies_base_item_id+38, ItemClassification.progression, True),
#     "Major Arcana Event": ItemData(prophecies_base_item_id+39, ItemClassification.progression, True),
#     "Familiar Confidant Event": ItemData(prophecies_base_item_id+40, ItemClassification.progression, True),
#     "Note to Self Event": ItemData(prophecies_base_item_id+41, ItemClassification.progression, True),
#     "The Invoker Event": ItemData(prophecies_base_item_id+42, ItemClassification.progression, True),
#     "Whims of Chaos Event": ItemData(prophecies_base_item_id+43, ItemClassification.progression, True),
#     "Breadth of Knowledge Event": ItemData(prophecies_base_item_id+44, ItemClassification.progression, True),
#     "Weight in Gold Event": ItemData(prophecies_base_item_id+45, ItemClassification.progression, True),
#     "Valued Customer Event": ItemData(prophecies_base_item_id+46, ItemClassification.progression, True),
#     "Close Companions Event": ItemData(prophecies_base_item_id+47, ItemClassification.progression, True),
#     "Beyond Familiar Event": ItemData(prophecies_base_item_id+48, ItemClassification.progression, True),
#     "Denizen of the Depths Event": ItemData(prophecies_base_item_id+49, ItemClassification.progression, True),
#     "Keeper of Shadows Event": ItemData(prophecies_base_item_id+50, ItemClassification.progression, True),
#     "Tools of the Unseen Event": ItemData(prophecies_base_item_id+51, ItemClassification.progression, True),
#     "Precision Instrument Event": ItemData(prophecies_base_item_id+52, ItemClassification.progression, True),
#     "Home in the Crossroads Event": ItemData(prophecies_base_item_id+53, ItemClassification.progression, True),
#     "Spectral Forms Event": ItemData(prophecies_base_item_id+54, ItemClassification.progression, True),
#     "Shadow of Death Event": ItemData(prophecies_base_item_id+55, ItemClassification.progression, True),
#     "Shadow of Doom Event": ItemData(prophecies_base_item_id+56, ItemClassification.progression, True),
#     "Gifts of the Moon Event": ItemData(prophecies_base_item_id+57, ItemClassification.progression, True),
#     "Godsent Favor Event": ItemData(prophecies_base_item_id+58, ItemClassification.progression, True),
#     "Master of the Dead Event": ItemData(prophecies_base_item_id+59, ItemClassification.progression, True),
#     "Master of the Heavens Event": ItemData(prophecies_base_item_id+60, ItemClassification.progression, True),
#     "Mistress of Wedlock Event": ItemData(prophecies_base_item_id+61, ItemClassification.progression, True),
#     "Master of the Sea Event": ItemData(prophecies_base_item_id+62, ItemClassification.progression, True),
#     "Mistress of Seasons Event": ItemData(prophecies_base_item_id+63, ItemClassification.progression, True),
#     "Master of Light Event": ItemData(prophecies_base_item_id+64, ItemClassification.progression, True),
#     "Mistress of Beauty Event": ItemData(prophecies_base_item_id+65, ItemClassification.progression, True),
#     "Master of the Forge Event": ItemData(prophecies_base_item_id+66, ItemClassification.progression, True),
#     "Mistress of the Hearth Event": ItemData(prophecies_base_item_id+67, ItemClassification.progression, True),
#     "Master of War Event": ItemData(prophecies_base_item_id+68, ItemClassification.progression, True),
#     "Mistress of the Hunt Event": ItemData(prophecies_base_item_id+69, ItemClassification.progression, True),
#     "Master of Swiftness Event": ItemData(prophecies_base_item_id+70, ItemClassification.progression, True),
#     "Mistress of Battle Event": ItemData(prophecies_base_item_id+71, ItemClassification.progression, True),
#     "Master of Revelry Event": ItemData(prophecies_base_item_id+72, ItemClassification.progression, True),
#     "Original Sins Event": ItemData(prophecies_base_item_id+73, ItemClassification.progression, True),
#     "Original Virtues Event": ItemData(prophecies_base_item_id+74, ItemClassification.progression, True),
#     "Power Beyond Legend Event": ItemData(prophecies_base_item_id+75, ItemClassification.progression, True),
#     "Combined Might Event": ItemData(prophecies_base_item_id+76, ItemClassification.progression, True),
#     "Weaver of Fineries Event": ItemData(prophecies_base_item_id+77, ItemClassification.progression, True),
#     "Denier of Suitors Event": ItemData(prophecies_base_item_id+78, ItemClassification.progression, True),
#     "Voice of Truth Event": ItemData(prophecies_base_item_id+79, ItemClassification.progression, True),
#     "Witch of Shadows Event": ItemData(prophecies_base_item_id+80, ItemClassification.progression, True),
#     "Witch of Changing Event": ItemData(prophecies_base_item_id+81, ItemClassification.progression, True),
#     "Wings of Freedom Event": ItemData(prophecies_base_item_id+82, ItemClassification.progression, True),
#     "Bared Fangs Event": ItemData(prophecies_base_item_id+83, ItemClassification.progression, True),
#     "The Witch's Staff Event": ItemData(prophecies_base_item_id+84, ItemClassification.progression, True),
#     "The Sister Blades Event": ItemData(prophecies_base_item_id+85, ItemClassification.progression, True),
#     "The Umbral Flames Event": ItemData(prophecies_base_item_id+86, ItemClassification.progression, True),
#     "The Moonstone Axe Event": ItemData(prophecies_base_item_id+87, ItemClassification.progression, True),
#     "The Argent Skull Event": ItemData(prophecies_base_item_id+88, ItemClassification.progression, True),
#     "The Black Coat Event": ItemData(prophecies_base_item_id+89, ItemClassification.progression, True)
# }

item_table = {
    **item_table_fears,
    # **item_table_prophecies_completion,
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
    # TODO: Fear
    
    # Keepsakes
    if self.options.keepsakesanity:
        pool.extend(self.create_item(name) for name in item_table_keepsakes)
    
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
            
    # Tools
    if self.options.toolsanity:
        pool.extend(self.create_item(name) for name in item_table_tools)

    # # Prophecies
    # if self.options.fatesanity:
    #     pool.extend(self.create_item(name) for name in item_table_prophecies_completion)
            
    # Handle fillers and traps
    handle_fillers(self, pool, local_location_table)

    # Place in boss event psuedo-items
    place_boss_events(self.world, self.player)
        
    # Add items to pool
    self.multiworld.itempool += pool

# General use function
def create_item(self, name: str) -> Item:
    return Hades_II_Item(name, self.player)

# Places boss event pseudo-items at each location
def place_boss_events(world, player) -> None:
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

# Calculates percentages of filler materials and traps    
def handle_fillers(self, pool, local_location_table):
    total_fillers_needed = len(local_location_table) - len(pool) - len(location_table_prophecies) 
    
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
    
    # For 100% safety to make sure negative numbers don't happen
    counts["bones"] = max(counts["bones"], 0)
    
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
        pool.extend(self.create_item(name) for _ in range(count))
            
    # Fill traps
    trap_pool = list(item_table_traps.keys())
    for i in range(counts["traps"]):
        item_name = trap_pool[i % len(trap_pool)]
        pool.append(Hades_II_Item(item_name, self.player))