from typing import TYPE_CHECKING
from .Items import item_table_fears, item_table_keepsakes, item_table_prophecies
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import add_rule

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

# Used for keepsake logic
olympians = [
    "Zeus",
    "Hera",
    "Poseidon",
    "Demeter",
    "Apollo",
    "Aphrodite",
    "Hephaestus",
    "Hestia",
    "Ares",
    "Athena",
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
        for prop in item_table_prophecies:
            amount_props += self.count(prop, player) # type: ignore
        return amount_props >= amount
    
    # Checks if the player has defeated the boss with enough (depending on options):
    def _can_get_victory(self, player: int, options) -> bool:
        can_win = self._can_reach_endgame(player, options)
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
    
    # Checks if a specific biome boss has been defeated (used for region/keepsake logic)
    def _has_defeated_final_boss(self, boss_event: str, player: int, options=None) -> bool:
        return self.has(boss_event, player)  # type: ignore

    # Checks if the player has reached the end-game (Chronos or Typhon cleared)
    def _can_reach_endgame(self, player: int, options) -> bool:
        if options.location_system == "room_weapon_based":
            return sum(self.count(f"Boss Victory {w}", player) for w in weapons) > 0  # type: ignore
        else:
            return self.has("Chronos Victory", player) or self.has("Typhon Victory", player)  # type: ignore

    # Checks if the player has enough weapon wins for goal
    def _enough_weapons_victories(self, player: int, options, amount: int) -> bool:
        if options.location_system == "room_weapon_based":
            counter = sum(self.count("Boss Victory " + w, player) for w in weapons)  # type: ignore
            return counter >= amount
        else:
            return self._can_reach_endgame(player, options) and self._has_enough_weapons(player, options, amount)
    
    # Incantations not yet implemented — surface/moros always accessible for now
    def _has_surface_access(self, player: int) -> bool:
        return True

    def _has_moros_access(self, player: int) -> bool:
        return True

def set_rules(world, player: int, location_table: dict, options) -> None:    
    if options.location_system == "room_weapon_based":
        pass
        # for weapon in weapons:
            # set_weapon_region_rules(world, player, number_items, location_table, options, weapon)
    else:
        handle_area_logic(world, player)
    
    world.completion_condition[player] = lambda state: state._can_get_victory(player, options)
    
    # Keepsakes
    handle_keepsakes(world, player, options)
        
    # if options.weaponsanity:
    #     add_rule(world.get_entrance("Weapon Cache", player), lambda state: True)
        
    # if options.fatesanity:
    #     set_fates_rules(world, player, location_table, options, "")
        
    # set_fates_rules(world, player, location_table, options, " Event")

# Defines logic for each area / region
# TODO: Make these actual event "items" / make them work
def handle_area_logic(world, player):
    area_rules = [ # ("Region name", "Boss Victory")
    ("Erebus -> Oceanus", "Hecate Victory"),
    ("Oceanus -> Fields", "Scylla Victory"),
    ("Fields -> Tartarus", "Cerberus Victory"),
    
    ("Ephyra -> Thessaly", "Polyphemus Victory"),
    ("Thessaly -> Olympus", "Eris Victory"),
    ("Olympus -> Summit", "Prometheus Victory"),
    ]
    
    for entrance_name, victory_item in area_rules:
        add_rule(world.get_entrance(entrance_name, player), lambda state, v=victory_item: state.has(v, player))

# Defines logic for keepsakes, the logic doc lists NPCs in more detail
def handle_keepsakes(world, player, options):
    if options.keepsakesanity: # If randomized
        keepsake_rules = [ # ("Name Keepsake", "Boss Victory" {OR NONE}, Surface Needed [bool])
            ("Narcissus Keepsake", "Hecate Victory", False),
            ("Hermes Keepsake", "Hecate Victory", False),
            ("Echo Keepsake", "Scylla Victory", False),
            ("Medea Keepsake", None, True),
            ("Heracles Keepsake", None, True),
            ("Icarus Keepsake", "Polyphemus Victory", True),
            ("Circe Keepsake", "Polyphemus Victory", True),
            ("Eris Keepsake", "Eris Victory", True), # ! Eris is probably accessible earlier, here right now for safety.
            ("Dionysus Keepsake", "Eris Victory", True),        
        ]

        # Apply logic to each keepsake check
        # Location-based
        for person_keepsake, boss, surface in keepsake_rules:
            add_rule(
                world.get_location(person_keepsake, player),
                lambda state, boss=boss, surface=surface:
                    (boss is None or state._has_defeated_final_boss(boss, player, options)) # type: ignore
                    and (not surface or state._has_surface_access(player)) # type: ignore
            )
        
        # Olympians require their own keepsake to be logically checked
        for person in olympians:
            add_rule(
                world.get_location(f"{person} Keepsake", player),
                lambda state, person=person:
                    state.has(f"{person} Keepsake", player)
            )
        
        # Specifically Moros
        add_rule(
            world.get_location("Moros Keepsake", player),
            lambda state: state._has_moros_access(player) # type: ignore
            )
        
    # When keepsakesanity is off there are no keepsake locations, nothing to do.