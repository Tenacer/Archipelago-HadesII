from typing import TYPE_CHECKING
from .Items import item_table_fears, item_table_keepsakes, item_table_prophesy_completion
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import set_rule, add_rule, add_item_rule

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
    def _has_enough_of_item(self, player: int, amount: int, item: str) -> bool:
        return self.count(item, player) >= amount  # type: ignore
    
    
    def _has_enough_weapons(self, player: int, options, amount: int) -> bool:
        if not options.weaponsanity:
            return True
        count = 0
        count = sum(self._has_weapon(w, player, options) for w in weapons)
        return count >= amount
    
    
    def _has_weapon(self, weaponSubfix : str, player: int, option) -> bool:
        if not option.weaponsanity:
            return True
        weapon_index = {
            "Staff Weapon": 0,
            "Daggers Weapon": 1,
            "Torches Weapon": 2,
            "Axe Weapon": 3,
            "Skull Weapon": 4,
            "Coat Weapon": 5,
        }
        idx = weapon_index[weaponSubfix]
        return (option.initial_weapon == idx or self.has(f"{weaponSubfix} Unlock Item", player)) # type: ignore
    
    
    def _has_enough_keepsakes(self, player: int, amount: int, options) -> bool:
        amount_keepsakes = 0
        for keepsake_name in item_table_keepsakes:
            amount_keepsakes += self.count(keepsake_name, player) # type: ignore
        return amount_keepsakes >= amount
    
    
    def _has_enough_prophecies_done(self, player: int, amount: int, options) -> bool:
        amount_props = 0 
        for prop_name in item_table_prophesy_completion:
            amount_props += self.count(prop_name, player) # type: ignore
        return amount_props >= amount
    
    
    def _can_get_victory(self, player: int, options) -> bool:
        can_win = self._has_defeated_boss("Hades Victory", player, options)
        if options.weaponsanity:
            weapons_temp = options.weapons_clears_needed.value
            can_win = (can_win) and (self._enough_weapons_victories(player, options, weapons_temp))
        if options.keepsakesanity:
            keepsakes = options.keepsakes_needed.value
            can_win = (can_win) and (self._has_enough_keepsakes(player, keepsakes, options))
        fates = options.fates_needed.value
        can_win = (can_win) and (self._has_enough_prophecies_done(player, fates, options))
        return can_win
    
    
    def _has_defeated_boss(self, bossVictory : str, player: int, options) -> bool:
        if options.location_system == "room_weapon_based":
            return sum(self.count(f"{bossVictory} {w}", player) for w in weapons) > 0 # type: ignore
        else:
            return self.has(bossVictory, player) # type: ignore
    
    
    def _enough_weapons_victories(self, player: int, options, amount: int) -> bool:
        if options.location_system == "room_weapon_based":
            counter = sum(self.count("Boss Victory " + w, player) for w in weapons) # type: ignore
            return counter >= amount
        else:
            return self.has("Boss Victory", player) and self._has_enough_weapons(player, options, amount) # type: ignore
        
    def _has_surface_access(self, player: int) -> bool:
        return (
            self.has("Permeation of Witching-Wards", player) and # type: ignore
            self.has("Unraveling of a Fateful Bond", player) # type: ignore
        )  
        
    def _has_moros_access(self, player: int) -> bool:
        return self.has("Doomed Beckoning", player)  # type: ignore

def set_rules(world, player: int, number_items: int, location_table: dict, options) -> None:
    # Locations
    if options.location_system == "room_weapon_based":
        for weapon in weapons:
            set_weapon_region_rules(world, player, number_items, location_table, options, weapon) # type: ignore
    else:
        add_rule(world.get_entrance("Exit Erebus"),
    lambda state:
        state.has("Hecate Victory", player)
        and state._has_enough_weapons(player, options, 2)) # type: ignore

    add_rule(world.get_entrance("Exit Oceanus"),
        lambda state:
            state.has("Scylla Victory", player)
            and state._has_enough_weapons(player, options, 3)) # type: ignore

    add_rule(world.get_entrance("Exit Fields"),
        lambda state:
            state.has("Cerberus Victory", player)
            and state._has_enough_weapons(player, options, 5)) # type: ignore

    add_rule(world.get_location("Beat Chronos"),
        lambda state:
            state._has_enough_weapons(player, options, 6)) # type: ignore
    
    world.completion_condition[player] = \
        lambda state: state._can_get_victory(player, options)
    
    # Keepsakes
    if options.keepsakesanity:
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
            ("Eris Keepsake", "Eris Victory", True),
            ("Athena Keepsake", "Eris Victory", True),
            ("Dionysus Keepsake", "Eris Victory", True),
            ("Ares Keepsake", "Prometheus Victory", True),
            
        ]

        for location, boss, surface in keepsake_rules:
            add_rule(
                world.get_location(location),
                lambda state, boss=boss, surface=surface:
                    (boss is None or state._has_defeated_boss(boss, player, options))  # type: ignore
                    and (not surface or state._has_surface_access(player))  # type: ignore
            )
        
        # Specifically Moros
        add_rule(
            world.get_location("Moros Keepsake"),
            lambda state: state._has_moros_access(player)  # type: ignore
        )
        
    # if options.weaponsanity:
    #     add_rule(world.get_entrance("Weapon Cache", player), lambda state: True)
        
    # if options.fatesanity:
    #     set_fates_rules(world, player, location_table, options, "")
        
    # set_fates_rules(world, player, location_table, options, " Event")