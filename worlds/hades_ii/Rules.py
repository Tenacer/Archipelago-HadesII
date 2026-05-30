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

    # True Ending: both final bosses, ingredient counts, Gigaros, Entropy, and a
    # *final* Chronos kill performed after Dissolution of Time has been cast
    # (represented by the `Chronos True Victory` event). The incantations
    # themselves are brewed in-game (vanilla, not AP items); having the
    # ingredients here is what makes them brewable, so they need no `has()` gate.
    def _has_true_ending_requirements(self, player: int, options) -> bool:
        return (
            self.has("Chronos True Victory", player)  # type: ignore
            and self.has("Typhon Victory", player)  # type: ignore
            and self.has("Gigaros", player)  # type: ignore
            and self.has("Entropy", player)  # type: ignore
            and self.count("Zodiac Sand", player) >= options.zodiac_sand_needed.value  # type: ignore
            and self.count("Void Lens", player) >= options.void_lens_needed.value  # type: ignore
        )
    
    # Checks if a specific biome boss has been defeated (used for region/keepsake logic)
    def _has_defeated_final_boss(self, boss_event: str, player: int, options=None) -> bool:
        return self.has(boss_event, player)  # type: ignore

    # Sugar over `_has_defeated_final_boss` that takes the boss base name
    # ("Hecate", "Scylla", …) and appends " Victory". Used by the unified
    # handle_keepsakes / handle_incantations / handle_prophecies handlers.
    def _has_boss(self, boss: str, player: int) -> bool:
        return self.has(f"{boss} Victory", player)  # type: ignore

    # True when cauldronsanity is OFF (player brews the incantation freely)
    # or the AP item for that incantation has been received. Used for
    # incantation→incantation prerequisite chains in handle_incantations and
    # handle_prophecies. The surface-unlock 2 are NOT routed through this —
    # they have their own _has_surface_door / _has_surface_access predicates.
    def _has_incantation(self, name: str, player: int, options) -> bool:
        if not options.cauldronsanity:
            return True
        # The Broker is granted for free at game start when unlock_broker is on,
        # so its incantation is removed from the pool — treat it as satisfied so
        # the chains that depend on it (Deathly/Kinship/Earthly Fortune, Long Arm
        # of the Unseen, Night's Craftwork → garden chain) stay reachable.
        if name == "Summoning of Mercantile Fortune" and options.unlock_broker:
            return True
        return self.has(name, player)  # type: ignore

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

    # Moros only appears at the Crossroads after Melinoë's first surface run,
    # which requires `Permeation of Witching-Wards`. The Penalty Cure is not
    # required to meet him — just to *survive* a real surface run.
    def _has_moros_access(self, player: int, options) -> bool:
        return self._has_surface_door(player, options)

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

    # Each sanity gets one unified handler. Surface gating is folded into each
    # handler per the per-entry tables, not a separate pass.
    handle_keepsakes(world, player, options)
    handle_hidden_aspects(world, player, options)
    handle_incantations(world, player, options)
    handle_prophecies(world, player, options)

    # True Ending: the final Chronos kill can only happen after the first
    # Chronos kill AND the Dissolution of Time ritual (Zodiac Sand + Entropy);
    # Gigaros is required because the True-Ending run also needs Disintegration
    # of Monstrosity brewed.
    if options.true_ending:
        add_rule(
            world.get_location("Chronos True Victory", player),
            lambda state: (
                state.has("Chronos Victory", player)
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


# ── Keepsake gates ───────────────────────────────────────────────────────────
# One unified `handle_keepsakes` replaces the previous boss-only +
# surface-only split. Each keepsake is gated on the NPC's reachability:
# Crossroads-only (no rule), boss-locked Crossroads (Hermes), surface (every
# Ephyra / Thessaly / Olympus NPC), or surface-door (Moros only appears post-
# first-surface-run).
#
# Rows marked `[VERIFY]` in the planning doc are encoded as written; revisit
# when the underlying TextLine gates have been cross-checked against the
# NPCData/KeepsakeData source.

_KEEPSAKE_RULES_BOSS = (
    # (AP location, boss base name)
    ("Hermes Keepsake", "Hecate"),
)

_KEEPSAKE_RULES_SURFACE_ACCESS = (
    # Ephyra NPCs
    "Medea Keepsake",
    "Heracles Keepsake",
    # Thessaly NPCs
    "Circe Keepsake",
    "Eris Keepsake",          # [VERIFY] ErisGift01 may pre-date the Eris boss room
    # Olympus / surface NPCs
    "Icarus Keepsake",
    "Dionysus Keepsake",
    "Athena Keepsake",
    # Olympians whose first-pickup requires a surface trip
    "Hera Keepsake",          # RequirementsData.lua:108 — HeraUnlocked needs WorldUpgradeSurfacePenaltyCure
    "Ares Keepsake",          # AresUnlocked needs RoomsEntered.Q_Boss01 >= 1
)

_KEEPSAKE_RULES_SURFACE_DOOR = (
    "Moros Keepsake",         
)


def handle_keepsakes(world, player, options):
    """Gate every keepsake location on its NPC's reachability.

    Crossroads-only NPCs (Hecate, Odysseus, Schelemeus, Charon, Nemesis, Dora,
    Selene, Artemis, Zeus, Poseidon, Demeter, Apollo, Aphrodite, Hephaestus,
    Hestia, Chaos) have no rule — they're available as soon as
    keepsakesanity is on. Underworld-biome NPCs (Arachne in F, Narcissus in G,
    Echo in H) also have no rule — gifting them doesn't require a surface run.
    """
    if not options.keepsakesanity:
        return

    for loc_name, boss in _KEEPSAKE_RULES_BOSS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    for loc_name in _KEEPSAKE_RULES_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    for loc_name in _KEEPSAKE_RULES_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )


# ── Incantation gates ────────────────────────────────────────────────────────
# Sourced from WorldUpgradeData.lua GameStateRequirements chains. Surface
# 2 (Permeation + Unraveling) are owned by `lock_surface_incantations`, the
# remaining 84 cauldronsanity-controlled entries (we excluded Rivals of Old
# and Rot under true_ending) are owned by `cauldronsanity`.

# Cauldronsanity entries with no prereq (always reachable when the location
# exists). Listed for completeness; no add_rule call needed.
#
# Tier-1 set documented in the plan file under "Group 1" / "Group 2" /
# parts of "Group 4" / etc. Intentionally not enumerated in code.

# Cauldronsanity entries that need one or more prereq incantations to be
# brewable. Format: (location, [incantation prereqs]). Each prereq is
# resolved via _has_incantation (inert when cauldronsanity is off).
_INCANTATION_CHAIN_RULES = (
    # Group 2 — underworld biome reprieves / Erebus shops
    ("Surge of Stygian Wells",       ("Rise of Stygian Wells",)),
    ("Surge of Desecrating Pools",   ("Revival of a Desecrating Pool",)),
    ("Purification of Fountain-Waters", ("Cleansing of Fountain-Waters",)),
    ("Gathering of Subterranean Riches", ("Gathering of Ancient Bones",)),
    # Group 4 — Olympian market hub
    ("Deathly Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Kinship Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Earthly Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Long Arm of the Unseen",
        ("Summoning of Mercantile Fortune", "Night's Craftwork")),
    # Group 5 — Tools / Garden chain
    ("Night's Craftwork",        ("Summoning of Mercantile Fortune",)),
    ("Greater Favor of Gaia",    ("Night's Craftwork",)),
    ("Flourishing Soil",         ("Night's Craftwork",)),
    ("Observance of Gaia's Secrets", ("Flourishing Soil",)),
    ("Rich Soil",                ("Observance of Gaia's Secrets",)),
    ("Verdant Soil",             ("Rich Soil",)),
    ("Green Hand of Gaia",       ("Observance of Gaia's Secrets",)),
    ("Greater Sowing of Gardens", ("Rich Soil",)),
    ("Greatest Gift of Gaia",
        ("Verdant Soil", "Observance of Gaia's Secrets")),
    # Group 6 — Bounty / familiar systems
    ("Abyssal Reflection",       ("Abyssal Insight",)),
    ("Bravery of Familiar Spirits", ("Faith of Familiar Spirits",)),
    # Group 8 — Hypnos chain
    ("End to Dearest Slumber",   ("End to Deepest Slumber",)), 
    # Group 9 — Misc
    ("Path to Desired Blessings",
        ("Forget-Me-Not", "Insight into Offerings")),
    ("Kindred Keepsakes",        ("Favored of All Keepsakes",)),  # [VERIFY]
)

# Cauldronsanity entries that need a boss victory (post-Hecate dialogue,
# post-Chronos dialogue, etc.). Format: (location, boss base name).
_INCANTATION_BOSS_RULES = (
    ("Necromantic Influence",   "Hecate"),
    ("Abyssal Insight",         "Hecate"),
    ("Faith of Familiar Spirits", "Hecate"),
)

# Cauldronsanity entries gated purely on surface access (no intra-cauldron
# prereq besides the surface-unlock 2, which `_has_surface_access` already
# enforces).
_INCANTATION_SURFACE_ACCESS = (
    # Group 1 tail
    "Greater Removal of Rubbish",
    # Group 3 — surface-gated proper
    "Summoning a Colony of Bats",
    "Rush of Fresh Air",
    "Sandy Lifespring",
    "Frozen Lifespring",
    "Rage of the Elements",
    "Arisen Troves",
    "Bounties of the Infinite Abyss",
    "Circles of Protection",
    # Group 8 — surface NPC-quest incantations
    "Purification of Crystal Clarity",
    "Return of Latent Memories",
    "Essence of Sorrow",
)

# Cauldronsanity entries gated on surface access AND a prereq incantation.
# Format: (location, [incantation prereqs]).
_INCANTATION_SURFACE_ACCESS_AND_CHAIN = (
    ("Surge of Fresh Air",           ("Rush of Fresh Air",)),
    ("Eyes of Night and Darkness",   ("Arisen Troves", "Exhumed Troves",)), 
    ("Circles of the Moon",          ("Circles of Protection",)),
    ("Alteration of Familiar Forms", ("Faith of Familiar Spirits",)),  # [VERIFY]
)

# Cauldronsanity entries gated on the surface door (Permeation only — Moros
# appears post-first-surface-run, doesn't need the penalty cure).
_INCANTATION_SURFACE_DOOR = (
    "Doomed Beckoning",         # MorosUnlock
)

# Rivals chain: each tier needs the relevant bosses cleared AND (T2+) surface
# access. Format: (location, [bosses], requires_surface).
# [VERIFY] vanilla boss triples for T2/T3.
# T4 ("Rivals of Old and Rot") is EXCLUDED from the pool under true_ending —
# handled in Locations.py.setup_location_table_with_settings + Items.py.
_INCANTATION_RIVALS_RULES = (
    ("Rivals of Depth and Sea",   ("Scylla", "Eris"),             True),
    ("Rivals of Plain and Peak",  ("Prometheus", "Cerberus"),     True),
    ("Rivals of Old and Rot",     ("Chronos", "Typhon"),          True),
)


def handle_incantations(world, player, options):
    """Gate cauldron-incantation locations on their in-game prerequisites.

    Two independent option toggles drive what gets added:
      • `lock_surface_incantations` owns the two surface-unlock locations
        (Permeation, Unraveling). Permeation has no gate. Unraveling needs
        the surface door (Moros must have appeared).
      • `cauldronsanity` owns the 84+ remaining locations. Each gets the rule
        from one of the tables above.
    """
    # Surface-unlock 2 — owned by lock_surface_incantations.
    if options.lock_surface_incantations:
        add_rule(
            world.get_location("Unraveling a Fateful Bond", player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    if not options.cauldronsanity:
        return

    # Intra-cauldron prereq chains.
    for loc_name, prereqs in _INCANTATION_CHAIN_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: all(
                state._has_incantation(p, player, options) for p in ps  # type: ignore
            ),
        )

    # Boss-victory gates.
    for loc_name, boss in _INCANTATION_BOSS_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    # Surface-access-only gates.
    for loc_name in _INCANTATION_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    # Surface-access AND prereq incantation.
    for loc_name, prereqs in _INCANTATION_SURFACE_ACCESS_AND_CHAIN:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: (
                state._has_surface_access(player, options)  # type: ignore
                and all(state._has_incantation(p, player, options) for p in ps)  # type: ignore
            ),
        )

    # Surface-door only.
    for loc_name in _INCANTATION_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    # Rivals tiers — boss list + optional surface gate.
    for loc_name, bosses, requires_surface in _INCANTATION_RIVALS_RULES:
        # T4 is removed from the pool under true_ending; skip if not present.
        try:
            location = world.get_location(loc_name, player)
        except KeyError:
            continue
        add_rule(
            location,
            lambda state, bs=bosses, surf=requires_surface: (
                all(state._has_boss(b, player) for b in bs)  # type: ignore
                and (state._has_surface_access(player, options) if surf else True)  # type: ignore
            ),
        )


# ── Prophecy gates ───────────────────────────────────────────────────────────
# Mirrors handle_incantations. Sourced from QuestData.lua
# UnlockGameStateRequirements + CompleteGameStateRequirements. Surface-NPC
# dialogue triggers map to _has_surface_access; coarse boss grinds map to
# _has_boss; system-unlock prophecies map to _has_incantation.

_PROPHECY_BOSS_RULES = (
    # Group A — boss-defeat
    ("Witch of the Crossroads",  "Hecate"),
    ("Temporary Setback",        "Chronos"),
    ("Storm in the Heavens",     "Typhon"),
    ("Den Mother",               "Hecate"),   # [VERIFY] coarse — also requires 2 cleared runs
    # Group F — system unlocks gated post-Hecate
    ("Visions of Victory",       "Hecate"),   # [VERIFY] ChaosGrantsBountyBoard01
    ("Whims of Chaos",           "Hecate"),   # [VERIFY] coarse — BountyBoard already viewed
    ("Familiar Confidant",       "Hecate"),   # [VERIFY] HecateHideAndSeek03
    ("Close Companions",         "Hecate"),   # [VERIFY] HecateBossGrantsFamiliarSystem01
    ("Keeper of Shadows",        "Hecate"),
    ("Improbable Outcomes",      "Hecate"),   # [VERIFY] coarse — ChaosGift06 + bounty board
)

# Prophecies whose UnlockGameStateRequirements chain off a *prereq prophecy*
# being cashed out (QuestStatus IsAny CashedOut / QuestsCompleted HasAll).
# Format: (AP location, boss base name, (prereq "X Reward" item names)).
# The prereq item names follow items.csv naming — they are AP items, not
# locations. Each prereq listed here must also be in
# Items.PROGRESSION_PROPHECY_ITEMS so state.has(...) can see it.
_PROPHECY_BOSS_AND_CHAIN_RULES = (
    ("Natural Talent",      "Hecate",  ("Witch of the Crossroads Reward",)),  # QuestBeatHecateWithoutArcana → QuestBeatHecate
    ("Arcana of the Ages",  "Chronos", ("Temporary Setback Reward",)),         # QuestBeatChronosWithArcana → QuestFirstUnderworldClear
    ("Beyond Familiar",     "Hecate",  ("Close Companions Reward",)),          # QuestUpgradeFamiliars → QuestRecruitFamiliars
)

# Boss A OR boss B (Chronos or Typhon — either route can complete).
_PROPHECY_BOSS_OR_RULES = (
    ("Born to Win",        ("Chronos", "Typhon")),
)

# Surface-access only.
_PROPHECY_SURFACE_ACCESS = (
    # Group A
    "Unrivaled Prowess",      # [VERIFY] also wants BossEris02 etc. EM2 grind
    "Shadow of Doom",
    # Group B — surface-only Olympians
    "Mistress of Battle",     # [VERIFY] Athena
    "Master of Revelry",      # [VERIFY] Dionysus
    # Group C — NPC-bond on surface
    "Haunted by the Past",
    "Voice and Vanity",
    "Bitter Tears",           # [VERIFY] MedeaAboutConcoctionQuest01
    "Weaver of Fineries",
    "Denier of Suitors",
    "Voice of Truth",
    "Witch of Shadows",
    "Witch of Changing",
    "Wings of Freedom",
    # Group D — hidden-aspect deliveries through surface NPCs
    "The Jackal's Aspect",    # [VERIFY] Anubis path
    "The Shadow's Aspect",    # [VERIFY] Supay path
    "The Grave's Aspect",     # [VERIFY] Hel path
)

# Surface-access AND a specific boss.
_PROPHECY_SURFACE_ACCESS_AND_BOSS = (
    ("Silk and Spitefulness", "Hecate"),
    ("Drowned Ambitions",     "Scylla"),    # [VERIFY] CirceAboutScyllaQuest01
    ("Nobody but Nobody",     "Polyphemus"),
)

# Surface-door only (Moros).
_PROPHECY_SURFACE_DOOR = (
    "Harbinger of Doom",      # QuestUnlockMoros
)

# Incantation-system gates (Group F-ish).
_PROPHECY_INCANTATION_RULES = (
    ("Tools of the Unseen",   ("Night's Craftwork",)),
    ("Note to Self",          ("Forget-Me-Not",)),
    ("Valued Customer",       ("Rise of Stygian Wells",)),
    ("Spectral Forms",        ("Necromantic Influence",)),
    ("Denizen of the Depths", ("Rite of River-Fording",)),  # [VERIFY] FishingPoint
)

# Sword of the Night needs Typhon Victory AND every weapon unlocked AND the
# `Temporary Setback Reward` prereq prophecy (QuestFirstUnderworldClear).
def _sword_of_the_night_rule(state, player, options):
    if not state._has_boss("Typhon", player):  # type: ignore
        return False
    if not state._has_enough_weapons(player, options, 6):  # type: ignore
        return False
    return state.has("Temporary Setback Reward", player)  # type: ignore


# Bearing Dark Gifts: (Chronos OR Typhon) AND The Unseen Sentinel Reward
# (QuestClearedWithAllAspects chain on QuestUnlockAllWeaponAspects).
def _bearing_dark_gifts_rule(state, player, options):
    if not (state._has_boss("Chronos", player) or state._has_boss("Typhon", player)):  # type: ignore
        return False
    return state.has("The Unseen Sentinel Reward", player)  # type: ignore


# Precision Instrument: incantation prereq (Greater Favor of Gaia, the tool
# upgrade system) AND prereq prophecy `Tools of the Unseen Reward`
# (QuestToolsUpgrades chains on QuestToolsUnlocks).
def _precision_instrument_rule(state, player, options):
    if not state._has_incantation("Greater Favor of Gaia", player, options):  # type: ignore
        return False
    return state.has("Tools of the Unseen Reward", player)  # type: ignore


def handle_prophecies(world, player, options):
    """Gate every prophecy location on its in-game completion prerequisites.

    Crossroads-NPC bond prophecies, Olympian boon prophecies (route-agnostic
    Olympians), Chaos blessings/curses, Selene duos, and pure-grind prophecies
    have no AP gate. Surface NPCs, post-boss systems, and incantation-system
    prophecies are gated here.
    """
    if not options.fatesanity:
        return

    for loc_name, boss in _PROPHECY_BOSS_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    # Boss-victory AND prereq prophecy cashed out (chain on another quest).
    for loc_name, boss, prereqs in _PROPHECY_BOSS_AND_CHAIN_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss, ps=prereqs: (
                state._has_boss(b, player)  # type: ignore
                and all(state.has(p, player) for p in ps)  # type: ignore
            ),
        )

    for loc_name, bosses in _PROPHECY_BOSS_OR_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, bs=bosses: any(
                state._has_boss(b, player) for b in bs  # type: ignore
            ),
        )

    for loc_name in _PROPHECY_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    for loc_name, boss in _PROPHECY_SURFACE_ACCESS_AND_BOSS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: (
                state._has_surface_access(player, options)  # type: ignore
                and state._has_boss(b, player)  # type: ignore
            ),
        )

    for loc_name in _PROPHECY_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    for loc_name, prereqs in _PROPHECY_INCANTATION_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: all(
                state._has_incantation(p, player, options) for p in ps  # type: ignore
            ),
        )

    add_rule(
        world.get_location("Sword of the Night", player),
        lambda state: _sword_of_the_night_rule(state, player, options),
    )
    add_rule(
        world.get_location("Bearing Dark Gifts", player),
        lambda state: _bearing_dark_gifts_rule(state, player, options),
    )
    add_rule(
        world.get_location("Precision Instrument", player),
        lambda state: _precision_instrument_rule(state, player, options),
    )