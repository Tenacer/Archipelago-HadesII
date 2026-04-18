from typing import Dict, NamedTuple, Optional
from BaseClasses import Item, ItemClassification
from .Locations import setup_location_table_with_settings, location_table_prophecies, should_ignore_weapon_location

_BOSS_VICTORY_NAMES = {
    "Hecate Victory", "Scylla Victory", "Cerberus Victory", "Chronos Victory",
    "Polyphemus Victory", "Eris Victory", "Prometheus Victory", "Typhon Victory",
}

class ItemData(NamedTuple):
    code: Optional[int]
    item_classification: ItemClassification
    event: bool = False
    # resource_id and amount are used by HadesIIClient to grant items via the mod
    resource_id: Optional[str] = None
    amount: int = 0
    
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
    "Ash":                  ItemData(filler_base_item_id + 1, ItemClassification.filler, False, "Ashes",          100),
    "Psyche":               ItemData(filler_base_item_id + 2, ItemClassification.useful, False, "Psyche",           1),
    "Nectar":               ItemData(filler_base_item_id + 3, ItemClassification.useful, False, "Nectar",           1),
    "Ambrosia":             ItemData(filler_base_item_id + 4, ItemClassification.useful, False, "Ambrosia",         1),
    "Nightmare":            ItemData(filler_base_item_id + 5, ItemClassification.useful, False, "Nightmare",        1),
    "Bones":                ItemData(filler_base_item_id + 6, ItemClassification.filler, False, "Bones",          100),
    "Fate Fabric":          ItemData(filler_base_item_id + 7, ItemClassification.useful, False, "FabricOfMemory",   1),
}

keepsakes_base_item_id  = filler_base_item_id + 7
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
    "Tablet of Peace Tool Unlock Item": ItemData(tools_base_item_id + 2, ItemClassification.progression),
    "Silver Spade Tool Unlock Item": ItemData(tools_base_item_id+  3, ItemClassification.progression),
    "Rod of Fishing Tool Unlock Item": ItemData(tools_base_item_id + 4, ItemClassification.progression)
}

aspects_base_item_id = tools_base_item_id +4
item_table_aspects: Dict[str, ItemData] = {
    "Staff Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 1, ItemClassification.progression),
    "Staff Weapon Circe Aspect Unlock Item": ItemData(aspects_base_item_id + 2, ItemClassification.progression),
    "Staff Weapon Momus Aspect Unlock Item": ItemData(aspects_base_item_id + 3, ItemClassification.progression),
    "Staff Weapon Anubis Aspect Unlock Item": ItemData(aspects_base_item_id + 4, ItemClassification.progression),

    "Daggers Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 5, ItemClassification.progression),
    "Daggers Weapon Pan Aspect Unlock Item": ItemData(aspects_base_item_id + 6, ItemClassification.progression),
    "Daggers Weapon Artemis Aspect Unlock Item": ItemData(aspects_base_item_id + 7, ItemClassification.progression),
    "Daggers Weapon Morrigan Aspect Unlock Item": ItemData(aspects_base_item_id + 8, ItemClassification.progression),

    "Torches Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 9, ItemClassification.progression),
    "Torches Weapon Moros Aspect Unlock Item": ItemData(aspects_base_item_id + 10, ItemClassification.progression),
    "Torches Weapon Eos Aspect Unlock Item": ItemData(aspects_base_item_id + 11, ItemClassification.progression),
    "Torches Weapon Supay Aspect Unlock Item": ItemData(aspects_base_item_id + 12, ItemClassification.progression),

    "Axe Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 13, ItemClassification.progression),
    "Axe Weapon Charon Aspect Unlock Item": ItemData(aspects_base_item_id + 14, ItemClassification.progression),
    "Axe Weapon Thanatos Aspect Unlock Item": ItemData(aspects_base_item_id + 15, ItemClassification.progression),
    "Axe Weapon Nergal Aspect Unlock Item": ItemData(aspects_base_item_id + 16, ItemClassification.progression),

    "Skull Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 17, ItemClassification.progression),
    "Skull Weapon Medea Aspect Unlock Item": ItemData(aspects_base_item_id + 18, ItemClassification.progression),
    "Skull Weapon Persephone Aspect Unlock Item": ItemData(aspects_base_item_id + 19, ItemClassification.progression),
    "Skull Weapon Hel Aspect Unlock Item": ItemData(aspects_base_item_id + 20, ItemClassification.progression),

    "Coat Weapon Melinoë Aspect Unlock Item": ItemData(aspects_base_item_id + 21, ItemClassification.progression),
    "Coat Weapon Selene Aspect Unlock Item": ItemData(aspects_base_item_id + 22, ItemClassification.progression),
    "Coat Weapon Nyx Aspect Unlock Item": ItemData(aspects_base_item_id + 23, ItemClassification.progression),
    "Coat Weapon Shiva Aspect Unlock Item": ItemData(aspects_base_item_id + 24, ItemClassification.progression),
}

traps_base_item_id = aspects_base_item_id + 24
item_table_traps: Dict[str, ItemData] = {
    "trap1": ItemData(hades_ii_base_item_id + 13, ItemClassification.trap)
}

helpers_base_item_id = traps_base_item_id + 1
item_table_helpers: Dict[str, ItemData] = {
    "helper1": ItemData(helpers_base_item_id + 1, ItemClassification.progression | ItemClassification.useful)
}

prophecies_base_item_id = helpers_base_item_id + 1
item_table_prophecies = {
    "Melinoë, Help Us Reward": ItemData(prophecies_base_item_id+1, ItemClassification.progression, False),
    "Melinoë, Remember Us Reward": ItemData(prophecies_base_item_id+2, ItemClassification.progression, False),
    "Melinoë, Seek Us Reward": ItemData(prophecies_base_item_id+3, ItemClassification.progression, True),
    "Melinoë, Find Us Reward": ItemData(prophecies_base_item_id+4, ItemClassification.progression, True),
    "Storm in the Heavens Reward": ItemData(prophecies_base_item_id+5, ItemClassification.progression, True),
    "Temporary Setback Reward": ItemData(prophecies_base_item_id+6, ItemClassification.progression, True),
    "Harbinger of Doom Reward": ItemData(prophecies_base_item_id+7, ItemClassification.progression, True),
    "Witch of the Crossroads Reward": ItemData(prophecies_base_item_id+8, ItemClassification.progression, True),
    "Natural Talent Reward": ItemData(prophecies_base_item_id+9, ItemClassification.progression, True),
    "Sword of the Night Reward": ItemData(prophecies_base_item_id+10, ItemClassification.progression, True),
    "Arcana of the Ages Reward": ItemData(prophecies_base_item_id+11, ItemClassification.progression, True),
    "Unrivaled Prowess Reward": ItemData(prophecies_base_item_id+12, ItemClassification.progression, True),
    "Bearing Dark Gifts Reward": ItemData(prophecies_base_item_id+13, ItemClassification.progression, True),
    "Den Mother Reward": ItemData(prophecies_base_item_id+14, ItemClassification.progression, True),
    "Family in Need Reward": ItemData(prophecies_base_item_id+15, ItemClassification.progression, True),
    "Visions of Victory Reward": ItemData(prophecies_base_item_id+16, ItemClassification.progression, True),
    "Unfinished Business Reward": ItemData(prophecies_base_item_id+17, ItemClassification.progression, True),
    "Haunted by the Past Reward": ItemData(prophecies_base_item_id+18, ItemClassification.progression, True),
    "Silk and Spitefulness Reward": ItemData(prophecies_base_item_id+19, ItemClassification.progression, True),
    "Voice and Vanity Reward": ItemData(prophecies_base_item_id+20, ItemClassification.progression, True),
    "Bitter Tears Reward": ItemData(prophecies_base_item_id+21, ItemClassification.progression, True),
    "Drowned Ambitions Reward": ItemData(prophecies_base_item_id+22, ItemClassification.progression, True),
    "The Jackal's Aspect Reward": ItemData(prophecies_base_item_id+23, ItemClassification.progression, True),
    "The Crow's Aspect Reward": ItemData(prophecies_base_item_id+24, ItemClassification.progression, True),
    "The Shadow's Aspect Reward": ItemData(prophecies_base_item_id+25, ItemClassification.progression, True),
    "The Warrior's Aspect Reward": ItemData(prophecies_base_item_id+26, ItemClassification.progression, True),
    "The Grave's Aspect Reward": ItemData(prophecies_base_item_id+27, ItemClassification.progression, True),
    "The Destroyer's Aspect Reward": ItemData(prophecies_base_item_id+28, ItemClassification.progression, True),
    "Nobody but Nobody Reward": ItemData(prophecies_base_item_id+29, ItemClassification.progression, True),
    "Born to Win Reward": ItemData(prophecies_base_item_id+30, ItemClassification.progression, True),
    "Improbable Outcomes Reward": ItemData(prophecies_base_item_id+31, ItemClassification.progression, True),
    "Soundest of Slumbers Reward": ItemData(prophecies_base_item_id+32, ItemClassification.progression, True),
    "Customary Gift Reward": ItemData(prophecies_base_item_id+33, ItemClassification.progression, True),
    "Mindful Craft Reward": ItemData(prophecies_base_item_id+34, ItemClassification.progression, True),
    "Blades of Pure Silver Reward": ItemData(prophecies_base_item_id+35, ItemClassification.progression, True),
    "The Arms of Night Reward": ItemData(prophecies_base_item_id+36, ItemClassification.progression, True),
    "The Unseen Sentinel Reward": ItemData(prophecies_base_item_id+37, ItemClassification.progression, True),
    "Awakened Aspect Reward": ItemData(prophecies_base_item_id+38, ItemClassification.progression, True),
    "Major Arcana Reward": ItemData(prophecies_base_item_id+39, ItemClassification.progression, True),
    "Familiar Confidant Reward": ItemData(prophecies_base_item_id+40, ItemClassification.progression, True),
    "Note to Self Reward": ItemData(prophecies_base_item_id+41, ItemClassification.progression, True),
    "The Invoker Reward": ItemData(prophecies_base_item_id+42, ItemClassification.progression, True),
    "Whims of Chaos Reward": ItemData(prophecies_base_item_id+43, ItemClassification.progression, True),
    "Breadth of Knowledge Reward": ItemData(prophecies_base_item_id+44, ItemClassification.progression, True),
    "Weight in Gold Reward": ItemData(prophecies_base_item_id+45, ItemClassification.progression, True),
    "Valued Customer Reward": ItemData(prophecies_base_item_id+46, ItemClassification.progression, True),
    "Close Companions Reward": ItemData(prophecies_base_item_id+47, ItemClassification.progression, True),
    "Beyond Familiar Reward": ItemData(prophecies_base_item_id+48, ItemClassification.progression, True),
    "Denizen of the Depths Reward": ItemData(prophecies_base_item_id+49, ItemClassification.progression, True),
    "Keeper of Shadows Reward": ItemData(prophecies_base_item_id+50, ItemClassification.progression, True),
    "Tools of the Unseen Reward": ItemData(prophecies_base_item_id+51, ItemClassification.progression, True),
    "Precision Instrument Reward": ItemData(prophecies_base_item_id+52, ItemClassification.progression, True),
    "Home in the Crossroads Reward": ItemData(prophecies_base_item_id+53, ItemClassification.progression, True),
    "Spectral Forms Reward": ItemData(prophecies_base_item_id+54, ItemClassification.progression, True),
    "Shadow of Death Reward": ItemData(prophecies_base_item_id+55, ItemClassification.progression, True),
    "Shadow of Doom Reward": ItemData(prophecies_base_item_id+56, ItemClassification.progression, True),
    "Gifts of the Moon Reward": ItemData(prophecies_base_item_id+57, ItemClassification.progression, True),
    "Godsent Favor Reward": ItemData(prophecies_base_item_id+58, ItemClassification.progression, True),
    "Master of the Dead Reward": ItemData(prophecies_base_item_id+59, ItemClassification.progression, True),
    "Master of the Heavens Reward": ItemData(prophecies_base_item_id+60, ItemClassification.progression, True),
    "Mistress of Wedlock Reward": ItemData(prophecies_base_item_id+61, ItemClassification.progression, True),
    "Master of the Sea Reward": ItemData(prophecies_base_item_id+62, ItemClassification.progression, True),
    "Mistress of Seasons Reward": ItemData(prophecies_base_item_id+63, ItemClassification.progression, True),
    "Master of Light Reward": ItemData(prophecies_base_item_id+64, ItemClassification.progression, True),
    "Mistress of Beauty Reward": ItemData(prophecies_base_item_id+65, ItemClassification.progression, True),
    "Master of the Forge Reward": ItemData(prophecies_base_item_id+66, ItemClassification.progression, True),
    "Mistress of the Hearth Reward": ItemData(prophecies_base_item_id+67, ItemClassification.progression, True),
    "Master of War Reward": ItemData(prophecies_base_item_id+68, ItemClassification.progression, True),
    "Mistress of the Hunt Reward": ItemData(prophecies_base_item_id+69, ItemClassification.progression, True),
    "Master of Swiftness Reward": ItemData(prophecies_base_item_id+70, ItemClassification.progression, True),
    "Mistress of Battle Reward": ItemData(prophecies_base_item_id+71, ItemClassification.progression, True),
    "Master of Revelry Reward": ItemData(prophecies_base_item_id+72, ItemClassification.progression, True),
    "Original Sins Reward": ItemData(prophecies_base_item_id+73, ItemClassification.progression, True),
    "Original Virtues Reward": ItemData(prophecies_base_item_id+74, ItemClassification.progression, True),
    "Power Beyond Legend Reward": ItemData(prophecies_base_item_id+75, ItemClassification.progression, True),
    "Combined Might Reward": ItemData(prophecies_base_item_id+76, ItemClassification.progression, True),
    "Weaver of Fineries Reward": ItemData(prophecies_base_item_id+77, ItemClassification.progression, True),
    "Denier of Suitors Reward": ItemData(prophecies_base_item_id+78, ItemClassification.progression, True),
    "Voice of Truth Reward": ItemData(prophecies_base_item_id+79, ItemClassification.progression, True),
    "Witch of Shadows Reward": ItemData(prophecies_base_item_id+80, ItemClassification.progression, True),
    "Witch of Changing Reward": ItemData(prophecies_base_item_id+81, ItemClassification.progression, True),
    "Wings of Freedom Reward": ItemData(prophecies_base_item_id+82, ItemClassification.progression, True),
    "Bared Fangs Reward": ItemData(prophecies_base_item_id+83, ItemClassification.progression, True),
    "The Witch's Staff Reward": ItemData(prophecies_base_item_id+84, ItemClassification.progression, True),
    "The Sister Blades Reward": ItemData(prophecies_base_item_id+85, ItemClassification.progression, True),
    "The Umbral Flames Reward": ItemData(prophecies_base_item_id+86, ItemClassification.progression, True),
    "The Moonstone Axe Reward": ItemData(prophecies_base_item_id+87, ItemClassification.progression, True),
    "The Argent Skull Reward": ItemData(prophecies_base_item_id+88, ItemClassification.progression, True),
    "The Black Coat Reward": ItemData(prophecies_base_item_id+89, ItemClassification.progression, True)
}

# TODO: Fill this up
incantations_base_item_id = prophecies_base_item_id + 89
item_table_incantations = {}

item_table = {
    **item_table_fears,
    **item_table_prophecies,
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
            # item name is e.g. "Staff Weapon Unlock Item"; location is "Staff Weapon Unlock Location"
            location_name = name.replace(" Item", " Location")
            if should_ignore_weapon_location(location_name, self.options):
                continue
            item = Hades_II_Item(name, self.player)
            pool.append(item)
            
    # Aspects
    if self.options.aspectsanity:
        for name in item_table_aspects:
            item = Hades_II_Item(name, self.player)
            pool.append(item)
            
    # Tools — always available (no toolsanity option yet)
    pool.extend(self.create_item(name) for name in item_table_tools)

    # # Prophecies
    # if self.options.fatesanity:
    #     pool.extend(self.create_item(name) for name in item_table_prophecies_completion)
            
    # Handle fillers and traps
    handle_fillers(self, pool, local_location_table)

    # Place in boss event pseudo-items
    place_boss_events(self.multiworld, self.player)
        
    # Add items to pool
    self.multiworld.itempool += pool

# General use function
def create_item(self, name: str) -> Item:
    return Hades_II_Item(name, self.player)

# Places boss event pseudo-items at each location
def place_boss_events(world, player) -> None:
    for boss in _BOSS_VICTORY_NAMES:
        location = world.get_location(boss, player)
        event_item = Item(boss, ItemClassification.progression, None, player)
        location.place_locked_item(event_item)

# Calculates percentages of filler materials and traps    
def handle_fillers(self, pool, local_location_table):
    total_fillers_needed = len(local_location_table) - len(pool)
    
    # Define the percentages in the pool based off options
    # ? Add F. Fabric to speed things up for the player?
    percentages = {
        "ash":         self.options.ash_pack_percentage,
        "bones":       self.options.bones_pack_percentage,
        "psyche":      self.options.psyche_pack_percentage,
        "nectar":      self.options.nectar_pack_percentage,
        "ambrosia":    self.options.ambrosia_pack_percentage,
        "nightmare":   self.options.nightmare_pack_percentage,
        "fate_fabric": self.options.fate_fabric_pack_percentage,
        "traps":       self.options.filler_trap_percentage,
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
    
    # Populate the pool with fillers
    filler_counts = {
        "Ash":         counts["ash"],
        "Bones":       counts["bones"],
        "Psyche":      counts["psyche"],
        "Nectar":      counts["nectar"],
        "Ambrosia":    counts["ambrosia"],
        "Nightmare":   counts["nightmare"],
        "Fate Fabric": counts["fate_fabric"],
    }

    for name, count in filler_counts.items():
        pool.extend(self.create_item(name) for _ in range(count))

    # Fill traps
    trap_pool = list(item_table_traps.keys())
    for i in range(counts["traps"]):
        item_name = trap_pool[i % len(trap_pool)]
        pool.append(Hades_II_Item(item_name, self.player))


# Maps item code → (resource_id, amount) for HadesIIClient to write to ap_in.json.
# Only includes items the Lua mod can grant via AddResource.
ITEM_CODE_TO_RESOURCE: Dict[int, tuple] = {
    data.code: (data.resource_id, data.amount)
    for data in item_table.values()
    if data.code is not None and data.resource_id is not None
}