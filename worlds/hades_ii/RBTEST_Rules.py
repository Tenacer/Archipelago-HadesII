import dataclasses
from typing import TYPE_CHECKING, override
from BaseClasses import CollectionState
from rule_builder.rules import Has, HasAll, HasAny, Rule, True_
from worlds.hades_ii import HadesIIWorld
from .Options import WeaponSanity, KeepsakeSanity, FateSanity

if TYPE_CHECKING:
    from . import HadesIIWorld

surface_access = (
    Has("Permeation of Witching-Wards"),
    Has("Unraveling of a Fateful Bond")
)

# Screw you, Moros
moros_access = (
    Has("Doomed Beckoning")
)

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

@dataclasses.dataclass()
class CanVictory(Rule["HadesIIWorld"], game = "Hades II"):
    @override
    def _instantiate(self, world: HadesIIWorld) -> Rule.Resolved:
        return self.Resolved(
            player = world.player,
            
            boss_defeats_needed = world.options.boss_defeats_needed.value,
            weapons_clears_needed = world.options.weapons_clears_needed.value,
            keepsakes_needed = world.options.keepsakes_needed.value,
            fates_needed = world.options.fates_needed.value,
            
            weaponsanity = bool(world.options.weaponsanity),
            keepsakesanity = bool(world.options.keepsakesanity),
            fatesanity = bool(world.options.fatesanity),
        )
    
    class Resolved(Rule.Resolved):
        boss_defeats_needed: int
        weapons_clears_needed: int
        keepsakes_needed: int
        fates_needed: int
        weaponsanity: bool
        keepsakesanity: bool
        fatesanity: bool
        
        @override
        def _evaluate(self, state: CollectionState) -> bool:
            defeats = (
                state.count("Chronos Victory", self.player) +
                state.count("Typhon Victory", self.player)
            )
            # Number of boss defeats
            if defeats < self.boss_defeats_needed:
                return False
            
            # TODO: Weapon clears here
            # if self.weaponsanity:
            #     distinct_clears = 0 # per-weapon victory events
            #     if distinct_clears < self.weapons_clears_needed:
            #         return False
            
            # Needs amount of keepsakes
            if self.keepsakesanity:
                keepsakes = sum(
                    state.count(k, self.player)
                    for k in state.prog_items[self.player] 
                    if k in _keepsake_names
                )
                if keepsakes < self.keepsakes_needed:
                    return False
            
            # Needs amount of fates
            if self.fatesanity:
                fates = sum(
                    state.count(f, self.player)
                    for f in state.prog_items[self.player]
                    if f in _fates_names
                )
                if fates < self.fates_needed:
                    return False
                
            # Only hits if player has all conditions to clear
            return True
        
def _load_names():
    from .Items import item_table_keepsakes, item_table_prophecies
    global _keepsake_names, _fates_names
    _keepsake_names = frozenset(item_table_keepsakes.keys())
    _fates_names = frozenset(item_table_prophecies.keys())
 
_keepsake_names: frozenset = frozenset()
_fates_names: frozenset = frozenset()