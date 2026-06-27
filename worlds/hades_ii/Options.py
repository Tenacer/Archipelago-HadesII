from dataclasses import dataclass
from typing import Dict, Any
from Options import Range, Toggle, DeathLink, Choice, StartInventoryPool, PerGameCommonOptions, OptionGroup, \
    DefaultOnToggle


# -----------------------Settings for Gameplay decisions ---------------


class InitialWeapon(Choice):
    """
    Chooses an initial weapon to start with.
    Set to "random" to have Archipelago roll a weapon for you at generation time.
    """
    display_name = "Initial Weapon"
    option_Staff = 0
    option_Daggers = 1
    option_Torches = 2
    option_Axe = 3
    option_Skull = 4
    option_Coat = 5
    default = "random"

class LocationSystem(Choice):
    """
    Chooses how the game gives you items. Currently only score_based is supported.
    Room-based modes are reserved for a future update.
    """
    display_name = "Location System"
    option_score_based = 0
    default = 0
    

class ScoreRewardsAmount(Range):
    """
    When using score based system, this sets how many checks are available based on the score.
    Each room in hades gives "its depth" in score when completed, and each new check needs one more
    point to be unlocked (so check 10 needs 10 points, which can be obtained, for example,
    by completing rooms 5 and 6)
    """
    display_name = "Score Rewards Amount"
    range_start = 72
    range_end = 500
    default = 150


class ScoreSplitMode(Choice):
    """
    Choose how room-clear score earns score checks.
    Combined: a single score pool — every room feeds the same budget (any route
    can earn all of the score checks on its own).
    Separate: the underworld route (Erebus, Oceanus, Mourning Fields, Tartarus —
    the Chronos path) and the surface route (Ephyra, Thessaly, Olympus, Summit —
    the Typhon path) accumulate score independently, each capped at its own share
    of the total Score Rewards Amount (see Surface Score Ratio), so clearing all
    score checks requires playing both routes.
    """
    display_name = "Score Split Mode"
    option_combined = 0
    option_separate = 1
    default = 1


class SurfaceScoreRatio(Range):
    """
    Only used when Score Split Mode is "separate". Percentage of the score-check
    budget allocated to the surface route (the Typhon path); the remainder goes
    to the underworld route (the Chronos path). The surface is accessed later in
    the game, so a lower value (fewer surface checks) is the intended default.
    """
    display_name = "Surface Score Ratio"
    range_start = 0
    range_end = 100
    default = 40


class KeepsakeSanity(DefaultOnToggle):
    """
    Shuffles NPCs' keepsakes into the item pool, and makes each keepsake location a check. 
    For simplicity this does not affect post TrueEnding characters (Zagreus, Chronos and Hades/Persephone).
    """
    display_name = "Keepsake Sanity"

class WeaponSanity(DefaultOnToggle):
    """
    Shuffles weapons (except your initial weapon) into the item pool, and makes obtaining
    each weapon at the Training Grounds a check.
    Need to be sent the weapon item to gain the skill to equip them.
    """
    display_name = "Weapon Sanity"

class ToolSanity(DefaultOnToggle):
    """
    Shuffles the four gathering tools (Crescent Pickaxe, Silver Spade, Tablet of Peace,
    Rod of Fishing) into the item pool, and makes unlocking each one at Schelmy's shop a check.
    Need to be sent the tool item to actually gain the tool.
    """
    display_name = "Tool Sanity"

class HiddenAspectSanity(DefaultOnToggle):
    """
    Shuffles weapon aspects into the item pool, and makes obtaining each aspect a check
    (which needs to be unlocked before being able to be bought).
    """
    display_name = "Hidden Aspect Sanity"

class FamiliarSanity(DefaultOnToggle):
    """
    Shuffles the five animal familiars (Frinos, Raki, Toula, Hecuba, Gale) into the item
    pool, and makes recruiting each one a check. Need to be sent the familiar item to
    actually gain the companion. Every familiar check sits behind the familiar-system
    unlock, which requires the Tablet of Peace, Crescent Pickaxe and Silver Spade.
    """
    display_name = "Familiar Sanity"

class CauldronSanity(DefaultOnToggle):
    """
    Shuffles incantations from the Cauldron in the item pool.
    Need to be sent the items to gain the different perks that make runs easier.
    Note: the two surface-unlock incantations (Permeation of Witching-Wards and
    Unraveling a Fateful Bond) are NOT part of this pool — they are controlled
    independently by LockSurfaceIncantations.
    """
    display_name = "Cauldron Sanity"

class LockSurfaceIncantations(DefaultOnToggle):
    """
    Locks the two surface-unlock incantations (Permeation of Witching-Wards and
    Unraveling a Fateful Bond) behind AP item checks. While locked, neither
    incantation appears in the Cauldron until the matching AP item is received;
    once received, the entry appears and brewing it normally fires the AP check
    and applies the vanilla effect (opens the Crossroads surface door / cures
    the surface penalty).

    Independent of Cauldron Sanity: these two incantations are always handled
    by this option, never by Cauldron Sanity.
    """
    display_name = "Lock Surface Incantations"

class FateSanity(Toggle):
    """
    Shuffles most rewards from the Fated List of Prophecies into the item pool,
    and makes the corresponding items from the list a check.
    Can make the games significantly longer.
    Off by default (matches the Normal presets); the Hard presets turn it on.
    """
    display_name = "Fate Sanity"

# -- Completion

class TrueEnding(DefaultOnToggle):
    """
    When enabled (the default), the goal is to complete the True Ending ritual: defeat
    both Chronos and Typhon, and collect the required Zodiac Sand, Void Lenses, Gigaros,
    and Entropy. The goal incantations (Dissolution of Time, Disintegration of Monstrosity)
    are NOT randomized — you brew them in-game once you have the ingredients; only their
    Zodiac Sand / Void Lens costs are adjusted (ZodiacSandNeeded / VoidLensNeeded).
    When disabled, the goal follows BossDefeatsNeeded and the other count options.
    """
    display_name = "True Ending"


class ZodiacSandNeeded(Range):
    """
    How many Zodiac Sand items are required to brew Dissolution of Time and
    complete the True Ending goal. Must be <= ChronosKillsNeeded, which now
    controls how many Zodiac Sands actually appear in the item pool
    (one per Chronos kill reward). Extras above this threshold are free to
    spend on Arcana cards that consume Zodiac Sand. Ignored when True
    Ending is off.
    """
    display_name = "Zodiac Sand Needed"
    range_start = 0
    range_end = 15
    default = 4


class VoidLensNeeded(Range):
    """
    How many Void Lens items are required to brew Disintegration of
    Monstrosity and complete the True Ending goal. Must be <=
    TyphonKillsNeeded, which now controls how many Void Lenses actually
    appear in the item pool (one per Typhon kill reward). Extras above
    this threshold are free to spend on Arcana cards that consume Void
    Lens. Ignored when True Ending is off.
    """
    display_name = "Void Lens Needed"
    range_start = 0
    range_end = 7
    default = 2

class BossDefeatsNeeded(Range):
    """
    BossDefeats goal mode (combined counting): how many total Chronos+Typhon
    kills are required to win the world. Ignored when TrueEnding is on, or
    when BossDefeatsMode is set to separate.
    """
    display_name = "Boss Defeats Needed"
    range_start = 1
    range_end = 20
    default = 5

class BossDefeatsMode(Choice):
    """
    In BossDefeats goal mode, choose whether Chronos and Typhon kills are
    counted together (combined) or independently (separate).
    Combined: BossDefeatsNeeded total Chronos+Typhon kills wins the world.
    Separate: requires ChronosKillsNeeded Chronos kills AND TyphonKillsNeeded
    Typhon kills.
    Ignored when TrueEnding is on.
    """
    display_name = "Boss Defeats Counting Mode"
    option_combined = 0
    option_separate = 1
    default = 0

class ChronosKillsNeeded(Range):
    """
    How many Chronos kills are required. In TrueEnding mode, kills 1..N each
    drop an AP location reward (past N, drops Nightmare/Gemstones). In
    BossDefeats mode with separate counting, this is the per-boss goal
    threshold.
    """
    display_name = "Chronos Kills Needed"
    range_start = 1
    range_end = 15
    default = 7

class TyphonKillsNeeded(Range):
    """
    How many Typhon kills are required. In TrueEnding mode, kills 1..N each
    drop an AP location reward (past N, drops Nightmare/Gemstones). In
    BossDefeats mode with separate counting, this is the per-boss goal
    threshold.
    """
    display_name = "Typhon Kills Needed"
    range_start = 1
    range_end = 15
    default = 5

class WeaponsClearsNeeded(Range):
    """
    How many different weapons clears are needed to win the world.
    """
    display_name = "Weapon Clears Needed"
    range_start = 1
    range_end = 6
    default = 1
    
class KeepsakesNeeded(Range):
    """
    How many different keepsake ITEMS are needed to win the world.
    Post-ending keepsakes (Hades/Persephone, Zagreus, Chronos) do not count
    toward this threshold — only the 30 keepsakes that have corresponding checks.
    """
    display_name = "Keepsakes Needed"
    range_start = 0
    range_end = 30
    default = 0

class FatesNeeded(Range):
    """
    How many different Fated List CHECKS you need to finish in order to win the world.
    Note that larger amounts can make the game significantly longer.
    """
    display_name = "Fates Needed"
    range_start = 0
    range_end = 84  # one per randomizable prophecy (Fated List check)
    default = 0
    
# -- Fear 

class FearSystem(Choice):
    """
    Choose either reverse_fear (1), minimal_fear (2) or vanilla_fear (3) for the game.
    In reverse_fear you start with randomly distributed Fear vows that are locked on until
    you receive the corresponding vow items from the AP world.
    In minimal_fear the game starts with randomly distributed vows that act as a permanent
    floor — the shrine is hidden and levels never change.
    vanilla_fear leaves all vow control to the player (shrine works normally).
    The total shrine points distributed is set by InitialFearLevel / MinimalFearLevel.
    Maximum possible fear level is 67 (all vows at max rank).
    """
    display_name = "Fear System"
    option_reverse_fear = 1
    option_minimal_fear = 2
    option_vanilla_fear = 3
    default = 1


class InitialFearLevel(Range):
    """
    Total shrine points to randomly distribute across vows at game start (reverse_fear only).
    The points are spread randomly — individual vow ranks are not configurable.
    Maximum is 67 (all vows at max rank). Unused points if no affordable rank remains.
    """
    display_name = "Initial Fear Level"
    range_start = 0
    range_end = 67
    default = 32


class MinimalFearLevel(Range):
    """
    Total shrine points to randomly distribute as the permanent vow floor (minimal_fear only).
    The shrine is hidden; these levels never change during the run.
    Maximum is 67 (all vows at max rank). Unused points if no affordable rank remains.
    """
    display_name = "Minimal Fear Level"
    range_start = 0
    range_end = 67
    default = 11


# -- Filler config: single place to tune all filler defaults
#    value      = how much of the resource each pack grants
#    percentage = share of the filler pool (treated as proportions if they don't sum to 100)
FILLER_CONFIG = {
    "ash":         {"value": 10,  "percentage": 24},
    "bones":       {"value": 50,  "percentage": 40},
    "psyche":      {"value": 30,  "percentage": 20},
    "nectar":      {"value": 1,   "percentage": 5},
    "ambrosia":    {"value": 1,   "percentage": 2},
    "moon_dust":   {"value": 1,   "percentage": 5},
    "nightmare":   {"value": 1,   "percentage": 1},
    "fate_fabric": {"value": 2,   "percentage": 3},
}

class AshPackValue(Range):
    """Choose the value (amount of ash) of each ash pack. 693 ash unlocks all arcana cards."""
    display_name = "Ash Pack Value"
    range_start = 0
    range_end = 200
    default = FILLER_CONFIG["ash"]["value"]

class AshPackPercentage(Range):
    """Percentage of filler slots that will be ash packs."""
    display_name = "Ash Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["ash"]["percentage"]

class BonesPackValue(Range):
    """Choose the value (amount of bones) of each bones pack."""
    display_name = "Bones Pack Value"
    range_start = 0
    range_end = 1000
    default = FILLER_CONFIG["bones"]["value"]

class BonesPackPercentage(Range):
    """Percentage of filler slots that will be bones packs."""
    display_name = "Bones Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["bones"]["percentage"]

class PsychePackValue(Range):
    """Choose the value (amount of psyche) of each psyche pack. 2595 psyche maxes all arcana levels."""
    display_name = "Psyche Pack Value"
    range_start = 0
    range_end = 3200
    default = FILLER_CONFIG["psyche"]["value"]

class PsychePackPercentage(Range):
    """Percentage of filler slots that will be psyche packs."""
    display_name = "Psyche Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["psyche"]["percentage"]

class NectarPackValue(Range):
    """Choose the value (amount of nectar) of each nectar pack. 32 nectar unlocks all keepsake checks."""
    display_name = "Nectar Pack Value"
    range_start = 0
    range_end = 50
    default = FILLER_CONFIG["nectar"]["value"]

class NectarPackPercentage(Range):
    """Percentage of filler slots that will be nectar packs."""
    display_name = "Nectar Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["nectar"]["percentage"]

class AmbrosiaPackValue(Range):
    """Choose the value (amount of ambrosia) of each ambrosia pack."""
    display_name = "Ambrosia Pack Value"
    range_start = 0
    range_end = 50
    default = FILLER_CONFIG["ambrosia"]["value"]

class AmbrosiaPackPercentage(Range):
    """Percentage of filler slots that will be ambrosia packs."""
    display_name = "Ambrosia Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["ambrosia"]["percentage"]

class MoonDustPackValue(Range):
    """Choose the value of each Moon Dust pack."""
    display_name = "Moon Dust Pack Value"
    range_start = 0
    range_end = 50
    default = FILLER_CONFIG["moon_dust"]["value"]

class MoonDustPackPercentage(Range):
    """Percentage of filler slots that will be Moon Dust packs."""
    display_name = "Moon Dust Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["moon_dust"]["percentage"]

class FateFabricPackValue(Range):
    """Choose the value of each Fate Fabric pack. """
    display_name = "Fate Fabric Pack Value"
    range_start = 0
    range_end = 50
    default = FILLER_CONFIG["fate_fabric"]["value"]

class FateFabricPackPercentage(Range):
    """Percentage of filler slots that will be Fate Fabric packs."""
    display_name = "Fate Fabric Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["fate_fabric"]["percentage"]

class NightmarePackValue(Range):
    """Choose the value of each Nightmare pack. A rare meta resource. 118 nightmare upgrades all aspects."""
    display_name = "Nightmare Pack Value"
    range_start = 0
    range_end = 10
    default = FILLER_CONFIG["nightmare"]["value"]

class NightmarePackPercentage(Range):
    """Percentage of filler slots that will be Nightmare packs. Recommended to keep low."""
    display_name = "Nightmare Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["nightmare"]["percentage"]

# -- Traps

class EnableTraps(DefaultOnToggle):
    """
    When enabled (the default), the filler pool contains trap items (Money
    Punishment, Health Punishment). The share is set by FillerTrapPercentage;
    this toggle simply gates whether traps are included at all. The Easy presets
    turn it off.
    """
    display_name = "Enable Traps"

class FillerTrapPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be traps instead.
    Traps diminish your money or health during a run.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    Ignored when EnableTraps is off.
    """
    display_name = "Filler Trap Percentage"
    range_start = 0
    range_end = 100
    default = 5

# -- Helpers

class EnableHelpers(DefaultOnToggle):
    """
    When enabled, the filler pool contains helper items (Max Health Helper,
    Initial Money Helper, Boon Boost Helper). The share is set by
    FillerHelperPercentage; this toggle simply gates whether helpers are
    included at all.
    """
    display_name = "Enable Helpers"

class FillerHelperPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be helpers instead.
    Helpers give a boost to your max health, your starting money, or your boon rarity.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    Ignored when EnableHelpers is off.
    """
    display_name = "Filler Helper Percentage"
    range_start = 0
    range_end = 100
    default = 10

class MaxHealthHelperPercentage(Range):
    """
    Choose the percentage of helper items that will boost your max health by 5 (permanently).
    The remaining percentage is split between initial-money helpers and boon-boost helpers.
    """
    display_name = "Max Health Helper Percentage"
    range_start = 0
    range_end = 100
    default = 50

class InitialMoneyHelperPercentage(Range):
    """
    Choose the percentage of helper items that will boost your starting money by 25 each run.
    This is capped by the percentage left after MaxHealthHelpers.
    What's left after both becomes Boon Boost helpers, each adding +1% to rare and epic
    boon rolls.
    """
    display_name = "Initial Money Helper Percentage"
    range_start = 0
    range_end = 100
    default = 35

# -----------------------Settings for QoL -------------------------

class ReverseOrderRivals(DefaultOnToggle):
    """
    When true the order in which Rival fights are applied is reverse 
    so level 1 is applied to Chronos/Typhon, instead of Hecate/Polyphemus). 
    For a more balanced experience.
    """
    display_name = "Reverse Order Rivals"


class IgnoreWinDeaths(Toggle):
    """
    If deaths after a completed run count for Deathlink. 
    Turn on for the memes.
    """
    display_name = "Win-Deaths Count for DeathLink"


class CauldronGiveHints(DefaultOnToggle):
    """
    If seeing an item on the Cauldron/Fated List of Prophecies
    should give a hint for it on the multiworld.
    """
    display_name = "Cauldron/FatedList Give Hints"


class UnlockBroker(DefaultOnToggle):
    """
    Unlocks the Broker at the Crossroads from the start of the game.
    When enabled, the Summoning of Mercantile Fortune incantation is removed from
    the Cauldron Sanity pool (you no longer have to earn it), and any incantations
    that normally require the Broker become brewable right away.
    """
    display_name = "Unlock Broker"


class DeathLinkAmnesty(Range):
    """
    Choose the amount of deaths it takes to send a deathlink. 
    A value of 1 functions as normal deathlink.
    """
    display_name = "Death Link Amnesty"
    range_start = 1
    range_end = 10
    default = 1

    
# -- Building dict

@dataclass
class HadesIIOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    initial_weapon: InitialWeapon
    location_system: LocationSystem
    score_rewards_amount: ScoreRewardsAmount
    score_split_mode: ScoreSplitMode
    surface_score_ratio: SurfaceScoreRatio

    keepsakesanity: KeepsakeSanity
    weaponsanity: WeaponSanity
    toolsanity: ToolSanity
    hidden_aspectsanity: HiddenAspectSanity
    familiarsanity: FamiliarSanity
    cauldronsanity: CauldronSanity
    lock_surface_incantations: LockSurfaceIncantations
    fatesanity: FateSanity

    true_ending: TrueEnding
    zodiac_sand_needed: ZodiacSandNeeded
    void_lens_needed: VoidLensNeeded
    boss_defeats_needed: BossDefeatsNeeded
    boss_defeats_mode: BossDefeatsMode
    chronos_kills_needed: ChronosKillsNeeded
    typhon_kills_needed: TyphonKillsNeeded
    weapons_clears_needed: WeaponsClearsNeeded
    keepsakes_needed: KeepsakesNeeded
    fates_needed: FatesNeeded

    fear_system: FearSystem
    initial_fear_level: InitialFearLevel
    minimal_fear_level: MinimalFearLevel

    ash_pack_value: AshPackValue
    ash_pack_percentage: AshPackPercentage
    bones_pack_value: BonesPackValue
    bones_pack_percentage: BonesPackPercentage
    psyche_pack_value: PsychePackValue
    psyche_pack_percentage: PsychePackPercentage
    nectar_pack_value: NectarPackValue
    nectar_pack_percentage: NectarPackPercentage
    ambrosia_pack_value: AmbrosiaPackValue
    ambrosia_pack_percentage: AmbrosiaPackPercentage
    nightmare_pack_value: NightmarePackValue
    nightmare_pack_percentage: NightmarePackPercentage
    moon_dust_pack_value: MoonDustPackValue
    moon_dust_pack_percentage: MoonDustPackPercentage
    fate_fabric_pack_value: FateFabricPackValue
    fate_fabric_pack_percentage: FateFabricPackPercentage

    enable_traps: EnableTraps
    filler_trap_percentage: FillerTrapPercentage
    enable_helpers: EnableHelpers
    filler_helper_percentage: FillerHelperPercentage
    max_health_helper_percentage: MaxHealthHelperPercentage
    initial_money_helper_percentage: InitialMoneyHelperPercentage

    reverse_order_rivals: ReverseOrderRivals
    ignore_win_deaths: IgnoreWinDeaths
    cauldron_give_hints: CauldronGiveHints
    unlock_broker: UnlockBroker
    death_link: DeathLink
    death_link_amnesty: DeathLinkAmnesty

hades_ii_option_groups = [
    OptionGroup("Game Options", [
        InitialWeapon,
        LocationSystem,
        ScoreRewardsAmount,
        ScoreSplitMode,
        SurfaceScoreRatio,
        KeepsakeSanity,
        WeaponSanity,
        ToolSanity,
        HiddenAspectSanity,
        FamiliarSanity,
        CauldronSanity,
        LockSurfaceIncantations,
        FateSanity,
        DeathLink,
        DeathLinkAmnesty,
    ]),
    OptionGroup("Goal Options", [
        TrueEnding,
        ZodiacSandNeeded,
        VoidLensNeeded,
        ChronosKillsNeeded,
        TyphonKillsNeeded,
        BossDefeatsMode,
        BossDefeatsNeeded,
        WeaponsClearsNeeded,
        KeepsakesNeeded,
        FatesNeeded,
    ]),
    OptionGroup("Fear Options", [
        FearSystem,
        InitialFearLevel,
        MinimalFearLevel,
    ]),
    OptionGroup("Filler Options", [
        AshPackValue,
        AshPackPercentage,
        BonesPackValue,
        BonesPackPercentage,
        PsychePackValue,
        PsychePackPercentage,
        NectarPackValue,
        NectarPackPercentage,
        AmbrosiaPackValue,
        AmbrosiaPackPercentage,
        NightmarePackValue,
        NightmarePackPercentage,
        MoonDustPackValue,
        MoonDustPackPercentage,
        FateFabricPackValue,
        FateFabricPackPercentage,
    ]),
    OptionGroup("Trap & Helper Options", [
        EnableTraps,
        FillerTrapPercentage,
        EnableHelpers,
        FillerHelperPercentage,
        MaxHealthHelperPercentage,
        InitialMoneyHelperPercentage,
    ]),
    OptionGroup("Quality of Life Options", [
        ReverseOrderRivals,
        IgnoreWinDeaths,
        CauldronGiveHints,
        UnlockBroker,
    ])
]

# ------------------------------ Presets
#
# Six presets: Easy / Normal / Hard for each goal mode (Boss Defeats and True
# Ending). Each preset is the difficulty knobs (resource generosity, fear,
# traps, scope — shared across goal modes) merged with the goal configuration.
# "True Ending Normal" is the recommended default and mirrors the bare option
# defaults, so loading it is a no-op.

# Shared difficulty knobs — identical regardless of goal mode.
_DIFFICULTY: Dict[str, Dict[str, Any]] = {
    "Easy": {
        "score_rewards_amount": 100,
        "hidden_aspectsanity": False,
        "fatesanity": False,
        "fear_system": "reverse_fear",
        "initial_fear_level": 12,
        "ash_pack_value": 20,
        "bones_pack_value": 100,
        "psyche_pack_value": 50,
        "nectar_pack_value": 2,
        "ambrosia_pack_value": 2,
        "moon_dust_pack_value": 2,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 3,
        "enable_traps": False,
        "filler_trap_percentage": 0,
    },
    "Normal": {
        "score_rewards_amount": 150,
        "hidden_aspectsanity": True,
        "fatesanity": False,
        "fear_system": "reverse_fear",
        "initial_fear_level": 32,
        "ash_pack_value": 10,
        "bones_pack_value": 50,
        "psyche_pack_value": 30,
        "nectar_pack_value": 1,
        "ambrosia_pack_value": 1,
        "moon_dust_pack_value": 1,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 2,
        "enable_traps": True,
        "filler_trap_percentage": 5,
    },
    "Hard": {
        "score_rewards_amount": 250,
        "hidden_aspectsanity": True,
        "fatesanity": True,
        "unlock_broker": False,
        "fear_system": "reverse_fear",
        "initial_fear_level": 57,
        "ash_pack_value": 5,
        "bones_pack_value": 25,
        "psyche_pack_value": 15,
        "nectar_pack_value": 1,
        "ambrosia_pack_value": 1,
        "moon_dust_pack_value": 1,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 1,
        "enable_traps": True,
        "filler_trap_percentage": 10,
    },
}

# Boss Defeats goal. Easy counts combined kills; Normal and Hard count each boss
# separately (Chronos and Typhon thresholds tracked independently).
_BOSS_GOAL: Dict[str, Dict[str, Any]] = {
    "Easy":   {"true_ending": False, "boss_defeats_mode": "combined", "boss_defeats_needed": 3},
    "Normal": {"true_ending": False, "boss_defeats_mode": "separate",
               "chronos_kills_needed": 3, "typhon_kills_needed": 2},
    "Hard":   {"true_ending": False, "boss_defeats_mode": "separate",
               "chronos_kills_needed": 5, "typhon_kills_needed": 3},
}

# True Ending goal: scale ingredient costs and per-boss kill counts by difficulty.
_TRUE_ENDING_GOAL: Dict[str, Dict[str, Any]] = {
    "Easy": {
        "true_ending": True, "boss_defeats_mode": "combined",
        "zodiac_sand_needed": 2, "void_lens_needed": 1,
        "chronos_kills_needed": 4, "typhon_kills_needed": 3,
        "weapons_clears_needed": 1, "keepsakes_needed": 0, "fates_needed": 0,
    },
    "Normal": {
        "true_ending": True, "boss_defeats_mode": "combined",
        "zodiac_sand_needed": 4, "void_lens_needed": 2,
        "chronos_kills_needed": 7, "typhon_kills_needed": 5,
        "weapons_clears_needed": 1, "keepsakes_needed": 0, "fates_needed": 0,
    },
    "Hard": {
        "true_ending": True, "boss_defeats_mode": "combined",
        "zodiac_sand_needed": 6, "void_lens_needed": 3,
        "chronos_kills_needed": 9, "typhon_kills_needed": 7,
        "weapons_clears_needed": 3, "keepsakes_needed": 0, "fates_needed": 0,
    },
}


def _make_preset(difficulty: str, goal: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return {**_DIFFICULTY[difficulty], **goal[difficulty]}


# Recommended default (True Ending Normal) listed first.
hades_ii_option_presets: Dict[str, Dict[str, Any]] = {
    "True Ending Normal": _make_preset("Normal", _TRUE_ENDING_GOAL),
    "True Ending Easy":   _make_preset("Easy",   _TRUE_ENDING_GOAL),
    "True Ending Hard":   _make_preset("Hard",   _TRUE_ENDING_GOAL),
    "Boss Defeats Easy":   _make_preset("Easy",   _BOSS_GOAL),
    "Boss Defeats Normal": _make_preset("Normal", _BOSS_GOAL),
    "Boss Defeats Hard":   _make_preset("Hard",   _BOSS_GOAL),
}