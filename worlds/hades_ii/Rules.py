from typing import TYPE_CHECKING
from .Items import item_table_fears, item_table_keepsakes, item_table_prophecies
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import add_rule, add_item_rule

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
        return (options.initial_weapon == idx or self.has(f"{weaponName} Unlock", player)) # type: ignore
    
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
        if options.true_ending:
            can_win = self._has_true_ending_requirements(player, options)
        else:
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

    # True Ending: both final bosses, ingredient counts, Gigaros, Entropy,
    # both goal incantations, and a *final* Chronos kill performed after
    # Dissolution of Time has been cast (represented by the
    # `Chronos True Victory` event).
    def _has_true_ending_requirements(self, player: int, options) -> bool:
        return (
            self.has("Chronos True Victory", player)  # type: ignore
            and self.has("Typhon Victory", player)  # type: ignore
            and self.has("Gigaros", player)  # type: ignore
            and self.has("Entropy", player)  # type: ignore
            and self.has("Dissolution of Time", player)  # type: ignore
            and self.has("Disintegration of Monstrosity", player)  # type: ignore
            and self.count("Zodiac Sand", player) >= options.zodiac_sand_needed.value  # type: ignore
            and self.count("Void Lens", player) >= options.void_lens_needed.value  # type: ignore
        )
    
    # Checks if a specific biome boss has been defeated (used for region/keepsake logic)
    def _has_defeated_final_boss(self, boss_event: str, player: int, options=None) -> bool:
        return self.has(boss_event, player)  # type: ignore

    # Checks if the player has reached the end-game.
    # Combined mode: either Chronos or Typhon cleared (kill counts enforced
    # client-side via the BossDefeatsNeeded victory signal).
    # Separate mode: both Chronos AND Typhon cleared (per-boss kill counts
    # enforced client-side via the Chronos/TyphonKillsNeeded victory signal).
    def _can_reach_endgame(self, player: int, options) -> bool:
        if options.boss_defeats_mode == 1:  # separate
            return self.has("Chronos Victory", player) and self.has("Typhon Victory", player)  # type: ignore
        return self.has("Chronos Victory", player) or self.has("Typhon Victory", player)  # type: ignore

    # Checks if the player has enough weapon wins for goal
    def _enough_weapons_victories(self, player: int, options, amount: int) -> bool:
        return self._can_reach_endgame(player, options) and self._has_enough_weapons(player, options, amount)
    
    # Surface access: the two surface-gating incantations.
    # Permeation of Witching-Wards (WorldUpgradeAltRunDoor) opens the surface
    # run door at the Crossroads. Unraveling a Fateful Bond
    # (WorldUpgradeSurfacePenaltyCure) cures the surface penalty so runs are
    # actually viable. Gated solely by lock_surface_incantations — these two
    # incantations are intentionally independent of cauldronsanity. When the
    # lock is off, the player brews them naturally and they aren't AP items.
    def _has_surface_door(self, player: int, options) -> bool:
        if not options.lock_surface_incantations:
            return True
        return self.has("Permeation of Witching-Wards", player)  # type: ignore

    def _has_surface_access(self, player: int, options) -> bool:
        if not options.lock_surface_incantations:
            return True
        return (
            self.has("Permeation of Witching-Wards", player)  # type: ignore
            and self.has("Unraveling a Fateful Bond", player)  # type: ignore
        )

    def _has_moros_access(self, player: int) -> bool:
        return True

def _restrict_score_check_progression(world, player: int, options) -> None:
    """Block progression items from score checks.

    Score checks are intended for filler/useful (CLAUDE.md). Marking them
    EXCLUDED forced filler-only and biased filler to the lowest-numbered
    checks. A per-location item rule preserves the no-progression
    constraint while letting AP's shuffled fill place useful + filler
    uniformly across all score checks.
    """
    if options.location_system.value != 0:  # score_based only
        return
    for loc in world.get_locations(player):
        if loc.name.startswith("Score Check "):
            add_item_rule(loc, lambda item: not item.advancement)


def set_rules(world, player: int, location_table: dict, options) -> None:
    handle_area_logic(world, player, options)
    _restrict_score_check_progression(world, player, options)
    world.completion_condition[player] = lambda state: state._can_get_victory(player, options)

    # Keepsakes
    handle_keepsakes(world, player, options)

    # Hidden aspects: require the weapon to be in logic before the chant can happen.
    handle_hidden_aspects(world, player, options)

    # Cauldronsanity: gate surface incantation brewing on the surface unlock items.
    handle_surface_incantations(world, player, options)

    # True Ending: the final Chronos kill can only happen after the first
    # Chronos kill AND the Dissolution of Time ritual (Zodiac Sand + Entropy);
    # Gigaros is required because the True-Ending run also needs Disintegration
    # of Monstrosity brewed.
    if options.true_ending:
        add_rule(
            world.get_location("Chronos True Victory", player),
            lambda state: (
                state.has("Chronos Victory", player)
                and state.has("Dissolution of Time", player)
                and state.has("Gigaros", player)
                and state.has("Entropy", player)
                and state.count("Zodiac Sand", player) >= options.zodiac_sand_needed.value
            ),
        )
        
    # if options.weaponsanity:
    #     add_rule(world.get_entrance("Weapon Cache", player), lambda state: True)
        
    # if options.fatesanity:
    #     set_fates_rules(world, player, location_table, options, "")
        
    # set_fates_rules(world, player, location_table, options, " Event")

# Defines logic for each area / region
# TODO: Make these actual event "items" / make them work
def handle_area_logic(world, player, options):
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

    # Surface biome entrance: both surface-unlock incantations are needed for
    # a viable run (Permeation opens the door; Unraveling cures the penalty).
    # Requiring both here prevents either item from being placed at any
    # surface-chain location (Ephyra → Summit), including Typhon Kill Rewards.
    # No-op when lock_surface_incantations is off.
    add_rule(
        world.get_entrance("Crossroads -> Ephyra", player),
        lambda state: state._has_surface_access(player, options),  # type: ignore
    )

# Each hidden aspect can only be unlocked once the player has the corresponding weapon.
def handle_hidden_aspects(world, player, options):
    if not options.hidden_aspectsanity:
        return
    hidden_aspect_rules = [
        ("Staff Weapon Anubis Aspect Unlock Location",    "Staff Weapon"),
        ("Daggers Weapon Morrigan Aspect Unlock Location","Daggers Weapon"),
        ("Torches Weapon Supay Aspect Unlock Location",   "Torches Weapon"),
        ("Axe Weapon Nergal Aspect Unlock Location",      "Axe Weapon"),
        ("Skull Weapon Hel Aspect Unlock Location",       "Skull Weapon"),
        ("Coat Weapon Shiva Aspect Unlock Location",      "Coat Weapon"),
    ]
    for location_name, weapon_name in hidden_aspect_rules:
        add_rule(
            world.get_location(location_name, player),
            lambda state, w=weapon_name: state._has_weapon(w, player, options),
        )


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
                    and (not surface or state._has_surface_door(player, options)) # type: ignore
            )
        
        # Specifically Moros
        add_rule(
            world.get_location("Moros Keepsake", player),
            lambda state: state._has_moros_access(player) # type: ignore
            )

    # When keepsakesanity is off there are no keepsake locations, nothing to do.


# Incantations whose cauldron recipes transitively require the surface door
# (Permeation of Witching-Wards) AND the surface penalty cure
# (Unraveling a Fateful Bond) to be brewable in-game. Sourced from
# WorldUpgradeData.lua GameStateRequirements chains.
_SURFACE_GATED_INCANTATIONS = (
    "Summoning a Colony of Bats",     # WorldUpgradeEphyraZoomOut
    "Rush of Fresh Air",              # WorldUpgradeSurfaceShops
    "Surge of Fresh Air",             # WorldUpgradePostBossSurfaceShops
    "Sandy Lifespring",               # WorldUpgradeThessalyReprieve
    "Frozen Lifespring",              # WorldUpgradeOlympusReprieve
    "Rage of the Elements",           # WorldUpgradeOlympusStatues
    "Arisen Troves",                  # WorldUpgradeChallengeSwitchesSurface1
    "Eyes of Night and Darkness",     # WorldUpgradeChallengeSwitchesExtra1
    "Bounties of the Infinite Abyss", # WorldUpgradeMetaRewardStands
    "Circles of Protection",          # WorldUpgradeErebusSafeZones
    "Circles of the Moon",            # WorldUpgradeSafeZoneSpellCharge
)


def handle_surface_incantations(world, player, options):
    """Logic for surface-gated incantation brew locations.

    In-game the cauldron only reveals an incantation once its prerequisite
    chain is satisfied. Surface incantations all root at Permeation of
    Witching-Wards (opens the surface door) and Unraveling a Fateful Bond
    (cures the surface penalty so Moros's recipes unlock). Without these
    encoded as logical gates AP fill can place progression items behind
    incantations the player cannot brew yet.

    Two independent location sets are gated here:
    - The two surface-unlock incantation locations themselves, which exist
      only when lock_surface_incantations is on. "Unraveling a Fateful Bond"
      requires the surface door to have been opened (Moros appears only after
      a surface run).
    - The 11 cauldronsanity surface-gated incantation locations, which exist
      only when cauldronsanity is on AND need an AP gate only when
      lock_surface_incantations is also on. When cauldronsanity is on but the
      lock is off, the player brews the unlock 2 trivially and the 11 are
      reachable in-game by normal play (over-permissive but not soft-locking).
    """
    if options.lock_surface_incantations:
        add_rule(
            world.get_location("Unraveling a Fateful Bond", player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    if options.cauldronsanity and options.lock_surface_incantations:
        for loc_name in _SURFACE_GATED_INCANTATIONS:
            add_rule(
                world.get_location(loc_name, player),
                lambda state: state._has_surface_access(player, options),  # type: ignore
            )