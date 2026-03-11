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
    option_room_based = 1
    
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
    How many different keepsake unlocks are needed to win the world.
    """
    display_name = "KeepsakesNeeded"
    range_start = 0
    range_end = 33
    default = 0

class FatesNeeded(Range):
    """
    How many different Fated List completions are needed to win the world.
    Note that larger amounts can make the game significantly longer.
    """
    display_name = "FatesNeeded"
    range_start = 0
    range_end = 89
    default = 0
    
# -- Fear NOT IMPLEMENTED YET

# -- Filler
class AshPackValue(Range):
    """
    Choose the value (amount of ash) of each ash pack in the pool. 
    If set to 0, ash will not appear in the pool.
    693 ash is needed to unlock all arcana cards.
    """
    display_name = "Ash Pack Value"
    range_start = 0
    range_end = 2000
    default = 200
    
class AshPackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be ash packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Ash Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10
    

class BonesPackValue(Range):
    """
    Choose the value (amount of bones) of each bones pack in the pool. 
    If set to 0, bones will not appear in the pool.
    """
    display_name = "Bones Pack Value"
    range_start = 0
    range_end = 10000
    default = 1000
    
class BonesPackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be bone packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Bones Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10
    

class PsychePackValue(Range):
    """
    Choose the value (amount of psyche) of each psyche pack in the pool. 
    If set to 0, psyche will not appear in the pool.
    2595 Psyche is needed to max all arcana levels
    """
    display_name = "Psyche Pack Value"
    range_start = 0
    range_end = 3200
    default = 650
    
class PsychePackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be psyche packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Psyche Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10


class NectarPackValue(Range):
    """
    Choose the value (amount of nectar) of each nectar pack in the pool. 
    If set to 0, nectar will not appear in the pool.
    32 nectar is needed to unlock all keepsake checks
    """
    display_name = "Nectar Pack Value"
    range_start = 0
    range_end = 50
    default = 4
    
class NectarPackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be nectar packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Nectar Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10
    

class AmbrosiaPackValue(Range):
    """
    Choose the value (amount of Ambrosia) of each Ambrosia pack in the pool. 
    If set to 0, Ambrosia will not appear in the pool.
    """
    display_name = "Ambrosia Pack Value"
    range_start = 0
    range_end = 50
    default = 4
    
class AmbrosiaPackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be Ambrosia packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Ambrosia Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10


class NightmarePackValue(Range):
    """
    Choose the value (amount of Nightmare) of each Nightmare pack in the pool. 
    If set to 0, Nightmare will not appear in the pool.
    118 Nightmare is needed to upgrade all aspects.
    """
    display_name = "Nightmare Pack Value"
    range_start = 0
    range_end = 50
    default = 15
    
class NightmarePackPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be Nightmare packs.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Nightmare Pack Percentage"
    range_start = 0
    range_end = 100
    default = 10
    
# -- Helpers

class FillerHelperPercentage(Range):
    """
    Choose the percentage of filler items in the pool that will be helpers instead. 
    Helpers give a boost to your max Health or starting money.
    Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
    """
    display_name = "Filler Helper Percentage"
    range_start = 0
    range_end = 100
    default = 10


class MaxHealthHelperPercentage(Range):
    """
    Choose the percentage of helper items that will boost your max health.
    The remaning percentage will go towards initial money helpers, which boost initial money by X AMOUNT.
    """
    display_name = "Max Health Helper Percentage"
    range_start = 0
    range_end = 100
    default = 50
    
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
    
    filler_helper_percentage: FillerHelperPercentage
    max_health_helper_percentage: MaxHealthHelperPercentage
    
    filler_trap_percentage: FillerTrapPercentage
    
    ignore_win_deaths: IgnoreWinDeaths
    death_link: DeathLink

hades_ii_option_groups = [
    OptionGroup("Game Options", [
        InitialWeapon,
        LocationSystem,
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
        NightmarePackPercentage
    ]),
    OptionGroup("Helpers and Trap Options", [
        FillerHelperPercentage,
        MaxHealthHelperPercentage,
        FillerTrapPercentage,
    ]),
    OptionGroup("Quality of Life Options", [
        IgnoreWinDeaths,
    ]),
]