from typing import TYPE_CHECKING
from .Items import item_table_fears, item_table_keepsakes, item_table_prophesy_completion
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule, add_rule, add_item_rule

# NOTE: All the `# type: ignore` blocks are to clear the unknown property error sometimes caused by state stuff

if TYPE_CHECKING:
    from . import HadesIIWorld

weapons = [
    "Staff Weapon",
    "Daggers Weapon",
    "Torches Weapon",
    "Axe Weapon",
    "Skull Weapon",
    "Coat Weapon",
]

class HadesIILogic(LogicMixin):
    # Checks if the player has enough of a given item 
    # TODO: Use this for max grasp logic?
    def _has_enough_of_item(self, player: int, amount: int, item: str) -> bool:
        return self.count(item, player) >= amount  # type: ignore
    
    # Checks if the player has enough weapons for defeat boss with N individual weapons
    def _has_enough_weapons(self, player: int, options, amount: int) -> bool:
        if not options.weaponsanity:
            return True
        count = 0
        count = sum(self._has_weapon(w, player, options) for w in weapons)
        return count >= amount
    
    # Checks if the player has a given weapon
    def _has_weapon(self, weaponName: str, player: int, options) -> bool:
        if not options.weaponsanity:
            return True
        idx = weapons.index(weaponName)
        return (options.initial_weapon == idx or self.has(f"{weaponName} Unlock Item", player)) # type: ignore
    
    # Checks if the player has enough keepsakes for goal
    def _has_enough_keepsakes(self, player: int, amount: int) -> bool:
        amount_keepsakes = 0
        for keepsake_name in item_table_keepsakes:
            amount_keepsakes += self.count(keepsake_name, player) # type: ignore
        return amount_keepsakes >= amount
    
    # Checks if the player has enough prophecies completed for goal
    def _has_enough_prophecies_done(self, player: int, amount: int) -> bool:
        amount_props = 0 
        for prop_name in item_table_prophesy_completion:
            amount_props += self.count(prop_name, player) # type: ignore
        return amount_props >= amount
    
    # Checks if the player has defeated the boss with enough (depending on options):
    def _can_get_victory(self, player: int, options) -> bool:
        can_win = self._has_defeated_boss("Boss Victory", player, options)
        # Weapons cleared
        if options.weaponsanity:
            weapons_temp = options.weapons_clears_needed.value
            can_win = (can_win) and (self._enough_weapons_victories(player, options, weapons_temp))
        
        # Keepsakes owned
        if options.keepsakesanity:
            keepsakes = options.keepsakes_needed.value
            can_win = (can_win) and (self._has_enough_keepsakes(player, keepsakes))
        
        # Prophecies cleared
        if options.fatesanity:
            fates = options.fates_needed.value
            can_win = (can_win) and (self._has_enough_prophecies_done(player, fates))
            
        return can_win
    
    # Checks if the player has defeated bosses 
    def _has_defeated_boss(self, bossVictory : str, player: int, options) -> bool:
        if options.location_system == "room_weapon_based":
            return sum(self.count(f"{bossVictory} {w}", player) for w in weapons) > 0 # type: ignore
        else:
            return self.has(bossVictory, player) # type: ignore
    
    # Checks if the player has enough weapon wins for goal
    def _enough_weapons_victories(self, player: int, options, amount: int) -> bool:
        if options.location_system == "room_weapon_based":
            counter = sum(self.count("Boss Victory " + w, player) for w in weapons) # type: ignore
            return counter >= amount
        else:
            return self.has("Boss Victory", player) and self._has_enough_weapons(player, options, amount) # type: ignore
    
    # Checks if the player has the 2 incantations needed to permanently access the surface
    def _has_surface_access(self, player: int) -> bool:
        return (
            self.has("Permeation of Witching-Wards", player) and # type: ignore
            self.has("Unraveling of a Fateful Bond", player) # type: ignore
        )  
        
    def _has_moros_access(self, player: int) -> bool:
        return self.has("Doomed Beckoning", player)  # type: ignore

def set_rules(world, player: int, number_items: int, location_table: dict, options) -> None:    
    if options.location_system == "room_weapon_based":
        for weapon in weapons:
            set_weapon_region_rules(world, player, number_items, location_table, options, weapon) # type: ignore
    else:
        handle_area_logic(world, player)
    
    world.completion_condition[player] = lambda state: state._can_get_victory(player, options)
    
    # Keepsakes
    if options.keepsakesanity:
        handle_keepsakes(world)
        
    # if options.weaponsanity:
    #     add_rule(world.get_entrance("Weapon Cache", player), lambda state: True)
        
    # if options.fatesanity:
    #     set_fates_rules(world, player, location_table, options, "")
        
    # set_fates_rules(world, player, location_table, options, " Event")

# Defines logic for each area / region
# TODO: Make these actual event "items" / make them work
def handle_area_logic(world, player):
    area_rules = [ # ("Region name", "Boss Victory", Final boss? [Bool])
    ("Oceanus", "Hecate Victory", True),
    ("Fields", "Scylla Victory", True),
    ("Tartarus", "Cerberus Victory", True),
    ("Chronos", "Chronos Victory", False), 
    
    ("Ephyra", "Polyphemus Victory", True),
    ("Thessaly", "Eris Victory", True),
    ("Olympus", "Prometheus Victory", True),
    ("Surface", "Typhon Victory", False),
    ]
    
    for area_name, victory_item, is_entrance in area_rules:
        target = world.get_entrance(area_name) if is_entrance else world.get_location(area_name)
        add_rule(target, lambda state, victory_item=victory_item: state.has(victory_item, player))

# Defines logic for keepsakes, the logic doc lists NPCs in more detail
def handle_keepsakes(world):
    add_rule(world.get_entrance("NPCS"), lambda state: True)
    keepsake_rules = [ # ("Name Keepsake", "Boss Victory" {OR NONE}, Surface Needed [bool])
        ("Narcissus Keepsake", "Hecate Victory", False),
        ("Hermes Keepsake", "Hecate Victory", False),
        ("Echo Keepsake", "Scylla Victory", False),
        ("Medea Keepsake", None, True),
        ("Hera Keepsake", None, True),
        ("Heracles Keepsake", None, True),
        ("Icarus Keepsake", "Polyphemus Victory", True),
        ("Circe Keepsake", "Polyphemus Victory", True),
        ("Eris Keepsake", "Eris Victory", True), # ! Eris is probably accessible earlier, here right now for safety.
        ("Athena Keepsake", "Eris Victory", True),
        ("Dionysus Keepsake", "Eris Victory", True),
        ("Ares Keepsake", "Prometheus Victory", True),
        
    ]

    # Apply logic to each keepsake
    for person, boss, surface in keepsake_rules:
        add_rule(
            world.get_location(person),
            lambda state, boss=boss, surface=surface:
                (boss is None or state._has_defeated_boss(boss, player, options))  # type: ignore
                and (not surface or state._has_surface_access(player))  # type: ignore
        )
    
    # Specifically Moros
    add_rule(
        world.get_location("Moros Keepsake"),
        lambda state: state._has_moros_access(player)  # type: ignore
        )