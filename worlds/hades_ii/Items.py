from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification

class ItemData(NamedTuple):
    code: Optional[int]
    item_classification: ItemClassification
    event: bool = False
    
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
    "Hecate Keepsake": ItemData(hades_ii_base_item_id +4, ItemClassification.useful),
    "Odysseus Keepsake": ItemData(hades_ii_base_item_id +5, ItemClassification.useful),
    "Schelemeus Keepsake": ItemData(hades_ii_base_item_id +6, ItemClassification.useful),
    "Dora Keepsake": ItemData(hades_ii_base_item_id +7, ItemClassification.useful),
    "Nemisis Keepsake": ItemData(hades_ii_base_item_id +8, ItemClassification.useful),
    "Moros Keepsake": ItemData(hades_ii_base_item_id +9, ItemClassification.useful),
    "Eris Keepsake": ItemData(hades_ii_base_item_id +10, ItemClassification.useful),
    "Charon Keepsake": ItemData(hades_ii_base_item_id +11, ItemClassification.useful),
    "Hermes Keepsake": ItemData(hades_ii_base_item_id +12, ItemClassification.useful),
    "Artemis Keepsake": ItemData(hades_ii_base_item_id +13, ItemClassification.useful),
    "Selene Keepsake": ItemData(hades_ii_base_item_id +14, ItemClassification.useful),
    
    "Zeus Keepsake": ItemData(hades_ii_base_item_id +15, ItemClassification.useful),
    "Hera Keepsake": ItemData(hades_ii_base_item_id +16, ItemClassification.useful),
    "Poseidon Keepsake": ItemData(hades_ii_base_item_id +17, ItemClassification.useful),
    "Demeter Keepsake": ItemData(hades_ii_base_item_id +18, ItemClassification.useful),
    "Apollo Keepsake": ItemData(hades_ii_base_item_id +19, ItemClassification.useful),
    "Aphrodite Keepsake": ItemData(hades_ii_base_item_id +20, ItemClassification.useful),
    "Hephaestus Keepsake": ItemData(hades_ii_base_item_id +21, ItemClassification.useful),
    "Hestia Keepsake": ItemData(hades_ii_base_item_id +22, ItemClassification.useful),
    "Ares Keepsake": ItemData(hades_ii_base_item_id +23, ItemClassification.useful),
    "Athena Keepsake": ItemData(hades_ii_base_item_id +24, ItemClassification.useful),
    "Dionysus Keepsake": ItemData(hades_ii_base_item_id +25, ItemClassification.useful),
    
    "Arachne Keepsake": ItemData(hades_ii_base_item_id +26, ItemClassification.useful),
    "Narcissus Keepsake": ItemData(hades_ii_base_item_id +27, ItemClassification.useful),
    "Echo Keepsake": ItemData(hades_ii_base_item_id +28, ItemClassification.useful),
    "Heracles Keepsake": ItemData(hades_ii_base_item_id +29, ItemClassification.useful),
    "Medea Keepsake": ItemData(hades_ii_base_item_id +30, ItemClassification.useful),
    "Circe Keepsake": ItemData(hades_ii_base_item_id +31, ItemClassification.useful),
    "Icarus Keepsake": ItemData(hades_ii_base_item_id +32, ItemClassification.useful),
    
    "Hades/Persephone Keepsake": ItemData(hades_ii_base_item_id +33, ItemClassification.useful),
    "Zagreus Keepsake": ItemData(hades_ii_base_item_id +34, ItemClassification.useful),
    "Chronos Keepsake": ItemData(hades_ii_base_item_id +35, ItemClassification.useful),
    
    "Chaos Keepsake": ItemData(hades_ii_base_item_id +36, ItemClassification.useful),
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

def create_trap_pool():
    return [trap for trap in item_table_traps.keys()]

# Sorry for the abomination of uppercase and underscore here, but I figured it was more 
# readable than `HadesIIItem`
class Hades_II_Item(Item):
    game = "Hades"

    def __init__(self, name, player: int):
        item_data = item_table[name]
        itemClass = item_data.item_classification
            
        super(Hades_II_Item, self).__init__(
            name,
            itemClass,
            item_data.code, player
        )
        
        def is_progression(self): # idk if this is needed, copied/pasted
            return self.classification == ItemClassification.progression