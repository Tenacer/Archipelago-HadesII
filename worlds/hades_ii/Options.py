from dataclasses import dataclass
from typing import Dict, Any
from Options import Range, Toggle, DeathLink, Choice, StartInventoryPool, PerGameCommonOptions,  OptionGroup, \
    DefaultOnToggle

class InitialWeapon(Choice):
    """Chooses an initial weapon to start with."""
    display_name = "Weapon"
    option_Staff = 0
    option_Daggers = 1
    option_Flames = 2
    option_Axe = 3
    option_Skull = 4
    option_Coat = 5
    
class LocationSystem(Choice):
    """
    Chooses how the game gives you items. RoomBased gives items on every new room completed.
    """
    display_name = "Location System"
    option_room_based = 0
    option_room_weapon_based = 1
    option_score_based = 2
    default = 2
    
class KeepsakeSanity(DefaultOnToggle):
    """
    Shuffles NPCs' keepsakes into the item pool, and makes each keepsake location a check. 
    For simplicity this does not affects Hades and Persephone.
    """
    display_name = "KeepsakeSanity"

class WeaponSanity(DefaultOnToggle):
    """
    Shuffles weapons (except your initial weapon) into the item pool, and makes obtaining
    each weapon at the House Contractor's shop a check.
    Need to be sent the weapon item to gain the skill to equip them.
    """
    display_name = "WeaponSanity"

class AspectSanity(DefaultOnToggle):
    """
    Shuffles weapon aspects into the item pool, and makes obtaining each aspect a check 
    (which needs to be unlocked before being able to be bought).
    """
    display_name = "AspectSanity"

class FateSanity(DefaultOnToggle):
    """
    Shuffles most rewards from the Fated List of Prophecies into the item pool, 
    and makes the corresponding items from the list a check. 
    Can make the games significantly longer.
    """
    display_name = "FateSanity"

# -- Completion

class BossDefeatsNeeded(Range):
    """
    How many times you need to defeat Chronos or Typhon (combined) to win the world.
    """
    display_name = "BossDefeatsNeeded"
    range_start = 1
    range_end = 20
    default = 5

class WeaponsClearsNeeded(Range):
    """
    How many different weapons clears are needed to win the world.
    """
    display_name = "WeaponsClearsNeeded"
    range_start = 1
    range_end = 6
    default = 1
    
class KeepsakesNeeded(Range):
    """
    How many different keepsake ITEMS are needed to win the world.
    """
    display_name = "KeepsakesNeeded"
    range_start = 0
    range_end = 33
    default = 0

class FatesNeeded(Range):
    """
    How many different Fated List CHECKS you need to finish in order to win the world.
    Note that larger amounts can make the game significantly longer.
    """
    display_name = "FatesNeeded"
    range_start = 0
    range_end = 89
    default = 0
    
# -- Fear NOT IMPLEMENTED YET

# -- Filler config: single place to tune all filler defaults
#    value      = how much of the resource each pack grants
#    percentage = share of the filler pool (treated as proportions if they don't sum to 100)
FILLER_CONFIG = {
    "ash":         {"value": 10,  "percentage": 10},
    "bones":       {"value": 50, "percentage": 10},
    "psyche":      {"value": 30,  "percentage": 10},
    "nectar":      {"value": 1,    "percentage": 10},
    "ambrosia":    {"value": 1,    "percentage": 10},
    "nightmare":   {"value": 1,   "percentage": 10},
    "fate_fabric": {"value": 1,    "percentage": 3},
}

class AshPackValue(Range):
    """Choose the value (amount of ash) of each ash pack. 693 ash unlocks all arcana cards."""
    display_name = "Ash Pack Value"
    range_start = 0
    range_end = 2000
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
    range_end = 10000
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

class NightmarePackValue(Range):
    """Choose the value (amount of nightmare) of each nightmare pack. 118 nightmare upgrades all aspects."""
    display_name = "Nightmare Pack Value"
    range_start = 0
    range_end = 50
    default = FILLER_CONFIG["nightmare"]["value"]

class NightmarePackPercentage(Range):
    """Percentage of filler slots that will be nightmare packs."""
    display_name = "Nightmare Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["nightmare"]["percentage"]

class FateFabricPackValue(Range):
    """Choose the value (amount of Fate Fabric) of each Fate Fabric pack. A rare meta resource."""
    display_name = "Fate Fabric Pack Value"
    range_start = 0
    range_end = 10
    default = FILLER_CONFIG["fate_fabric"]["value"]

class FateFabricPackPercentage(Range):
    """Percentage of filler slots that will be Fate Fabric packs. Recommended to keep low."""
    display_name = "Fate Fabric Pack Percentage"
    range_start = 0
    range_end = 100
    default = FILLER_CONFIG["fate_fabric"]["percentage"]

# -- Traps

class FillerTrapPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be traps instead. 
    Traps diminish your money or health during a run.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Filler Trap Percentage"
    range_start = 0
    range_end = 100
    default = 5
    
# -- Etc.

class IgnoreWinDeaths(Toggle):
    """
    If deaths after a completed run count for Deathlink. 
    Turn on for the memes.
    """
    display_name = "Win Deaths Count"
    
# -- Building dict

@dataclass
class HadesIIOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    initial_weapon: InitialWeapon
    location_system: LocationSystem
    
    keepsakesanity: KeepsakeSanity
    weaponsanity: WeaponSanity
    aspectsanity: AspectSanity
    fatesanity: FateSanity
    
    boss_defeats_needed: BossDefeatsNeeded
    weapons_clears_needed: WeaponsClearsNeeded
    keepsakes_needed: KeepsakesNeeded
    fates_needed: FatesNeeded
    
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
    fate_fabric_pack_value: FateFabricPackValue
    fate_fabric_pack_percentage: FateFabricPackPercentage

    filler_trap_percentage: FillerTrapPercentage
    
    ignore_win_deaths: IgnoreWinDeaths
    death_link: DeathLink

hades_ii_option_groups = [
    OptionGroup("Game Options", [
        InitialWeapon, LocationSystem,
        KeepsakeSanity,
        WeaponSanity,
        AspectSanity,
        FateSanity,
        DeathLink,
    ]),
    OptionGroup("Goal Options", [
        BossDefeatsNeeded,
        WeaponsClearsNeeded,
        KeepsakesNeeded,
        FatesNeeded,
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
        FateFabricPackValue,
        FateFabricPackPercentage,
    ]),
    OptionGroup("Trap Options", [
        FillerTrapPercentage,
    ]),
    OptionGroup("Quality of Life Options", [
        IgnoreWinDeaths,
    ]),
]