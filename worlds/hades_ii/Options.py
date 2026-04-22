from dataclasses import dataclass
from typing import Dict, Any
from Options import Range, Toggle, DeathLink, Choice, StartInventoryPool, PerGameCommonOptions,  OptionGroup, \
    DefaultOnToggle


# -----------------------Settings for Gameplay decisions ---------------


class InitialWeapon(Choice):
    """
    Chooses an initial weapon to start with.
    """
    display_name = "Weapon"
    option_Staff = 0
    option_Daggers = 1
    option_Torches = 2
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
    

class ScoreRewardsAmount(Range):
    """
    When using score based system, this sets how many checks are available based on the score.
    Each room in hades gives "its depth" in score when completed, and each new check needs one more
    point to be unlocked (so check 10 needs 10 points, which can be obtained, for example,
    by completing rooms 5 and 6)
    """
    display_name = "ScoreRewardsAmount"
    range_start = 72
    range_end = 500
    default = 150


class KeepsakeSanity(DefaultOnToggle):
    """
    Shuffles NPCs' keepsakes into the item pool, and makes each keepsake location a check. 
    For simplicity this does not affect post TrueEnding characters (Zagreus, Chronos and Hades/Persephone).
    """
    display_name = "KeepsakeSanity"

class WeaponSanity(DefaultOnToggle):
    """
    Shuffles weapons (except your initial weapon) into the item pool, and makes obtaining
    each weapon at the Training Grounds a check.
    Need to be sent the weapon item to gain the skill to equip them.
    """
    display_name = "WeaponSanity"

class HiddenAspectSanity(DefaultOnToggle):
    """
    Shuffles weapon aspects into the item pool, and makes obtaining each aspect a check 
    (which needs to be unlocked before being able to be bought).
    """
    display_name = "HiddenAspectSanity"

class CauldronSanity(DefaultOnToggle):
    """
    Shuffles incantations from the Cauldron in the item pool.
    Need to be sent the items to gain the different perks that make runs easier.
    """
    display_name = "CauldronSanity"

class FateSanity(DefaultOnToggle):
    """
    Shuffles most rewards from the Fated List of Prophecies into the item pool, 
    and makes the corresponding items from the list a check. 
    Can make the games significantly longer.
    """
    display_name = "FateSanity"

# -- Completion

class TrueEnding(Toggle):
    """
    When enabled, the goal is to complete the True Ending ritual: defeat both Chronos
    and Typhon, and collect the required Zodiac Sand, Void Lenses, Gigaros, and both
    goal incantations (Dissolution of Time, Disintegration of Monstrosity).
    When disabled, the goal follows BossDefeatsNeeded and the other count options.
    """
    display_name = "True Ending"


class ZodiacSandNeeded(Range):
    """
    How many Zodiac Sand items are required when True Ending is enabled.
    Ignored when True Ending is off.
    """
    display_name = "Zodiac Sand Needed"
    range_start = 0
    range_end = 15
    default = 4


class VoidLensNeeded(Range):
    """
    How many Void Lens items are required when True Ending is enabled.
    Ignored when True Ending is off.
    """
    display_name = "Void Lens Needed"
    range_start = 0
    range_end = 7
    default = 2

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
    Post-ending keepsakes (Hades/Persephone, Zagreus, Chronos) do not count
    toward this threshold — only the 30 keepsakes that have corresponding checks.
    """
    display_name = "KeepsakesNeeded"
    range_start = 0
    range_end = 30
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
    
# -- Fear 

class FearSystem(Choice):
    """
    Choose either ReverseFear (1), MinimalFear (2) or VanillaFear(3) for the game.
    In ReverseFear you start with Fear vows that cannot be disabled until you get the corresponding vow item.
    In Minimal the settings for the VowAmounts below set your minimal Fear to be set, and cannot go below that level.
    If not wanting to have one of this Fear systems on, chose Vanilla Fear
    (then the following options related to vows do nothing).
    """
    display_name = "Fear System"
    option_reverse_Fear = 1
    option_minimal_Fear = 2
    option_vanilla_Fear = 3
    default = 1


class PainVowAmount(Range):
    """
    Choose the amount of Vow of Pain ranks in the pool.
    Enemies deal more damage (3 ranks).
    """
    display_name = "Vow of Pain Amount"
    range_start = 0
    range_end = 3
    default = 1


class GritVowAmount(Range):
    """
    Choose the amount of Vow of Grit ranks in the pool.
    Enemies have more health (3 ranks).
    """
    display_name = "Vow of Grit Amount"
    range_start = 0
    range_end = 3
    default = 1


class WardsVowAmount(Range):
    """
    Choose the amount of Vow of Wards ranks in the pool.
    Enemies have barrier defenses (2 ranks).
    """
    display_name = "Vow of Wards Amount"
    range_start = 0
    range_end = 2
    default = 1


class FrenzyVowAmount(Range):
    """
    Choose the amount of Vow of Frenzy ranks in the pool.
    Enemies move and attack faster (3 ranks).
    """
    display_name = "Vow of Frenzy Amount"
    range_start = 0
    range_end = 2
    default = 1


class HordesVowAmount(Range):
    """
    Choose the amount of Vow of Hordes ranks in the pool.
    Encounters have more enemies (3 ranks).
    """
    display_name = "Vow of Hordes Amount"
    range_start = 0
    range_end = 3
    default = 1


class MenaceVowAmount(Range):
    """
    Choose the amount of Vow of Menace ranks in the pool.
    Foes have a chance to be from the next region (2 ranks).
    """
    display_name = "Vow of Menace Amount"
    range_start = 0
    range_end = 2
    default = 1


class ReturnVowAmount(Range):
    """
    Choose the amount of Vow of Return ranks in the pool.
    Slain foes have a chance to become revenants (2 ranks).
    """
    display_name = "Vow of Return Amount"
    range_start = 0
    range_end = 2
    default = 1


class FangsVowAmount(Range):
    """
    Choose the amount of Vow of Fangs ranks in the pool.
    Armored enemies gain additional perks (2 ranks).
    """
    display_name = "Vow of Fangs Amount"
    range_start = 0
    range_end = 2
    default = 0


class ScarsVowAmount(Range):
    """
    Choose the amount of Vow of Scars ranks in the pool.
    Healing items are less effective (3 ranks).
    """
    display_name = "Vow of Scars Amount"
    range_start = 0
    range_end = 3
    default = 1


class DebtVowAmount(Range):
    """
    Choose the amount of Vow of Debt ranks in the pool.
    Items in the shops are more expensive (2 ranks).
    """
    display_name = "Vow of Debt Amount"
    range_start = 0
    range_end = 2
    default = 1


class ShadowVowAmount(Range):
    """
    Choose the amount of Vow of Shadow ranks in the pool.
    Shadow Servants appear in mini-boss encounters (1 rank).
    """
    display_name = "Vow of Shadow Amount"
    range_start = 0
    range_end = 1
    default = 0


class ForfeitVowAmount(Range):
    """
    Choose the amount of Vow of Forfeit ranks in the pool.
    First boon in each region becomes an onion (1 rank).
    """
    display_name = "Vow of Forfeit Amount"
    range_start = 0
    range_end = 1
    default = 0


class TimeVowAmount(Range):
    """
    Choose the amount of Vow of Time ranks in the pool.
    Limits the time you can use to clear each region before
     starting to take damage (3 ranks).
    """
    display_name = "Vow of Time Amount"
    range_start = 0
    range_end = 3
    default = 0


class VoidVowAmount(Range):
    """
    Choose the amount of Vow of Void ranks in the pool.
    Arcana Grasp is reduced (4 ranks).
    """
    display_name = "Vow of Void Amount"
    range_start = 0
    range_end = 4
    default = 0


class HubrisVowAmount(Range):
    """
    Choose the amount of Vow of Hubris ranks in the pool.
    Prime magick after choosing boons above common (2 ranks).
    """
    display_name = "Vow of Hubris Amount"
    range_start = 0
    range_end = 2
    default = 0


class DenialVowAmount(Range):
    """
    Choose the amount of Vow of Denial ranks in the pool.
    After choosing a boon, the unpicked choices will no longer be available (1 rank).
    """
    display_name = "Vow of Denial Amount"
    range_start = 0
    range_end = 1
    default = 0


class RivalsVowAmount(Range):
    """
    Choose the amount of Vow of Rivals ranks in the pool.
    Boss encounters are enhanced (4 ranks).
    """
    display_name = "Vow of Rivals Amount"
    range_start = 0
    range_end = 4
    default = 0


# -- Filler config: single place to tune all filler defaults
#    value      = how much of the resource each pack grants
#    percentage = share of the filler pool (treated as proportions if they don't sum to 100)
FILLER_CONFIG = {
    "ash":         {"value": 10,  "percentage": 30},
    "bones":       {"value": 50,  "percentage": 40},
    "psyche":      {"value": 30,  "percentage": 20},
    "nectar":      {"value": 1,   "percentage": 5},
    "ambrosia":    {"value": 1,   "percentage": 1},
    "moon_dust":   {"value": 1,   "percentage": 3},
    "nightmare":   {"value": 1,   "percentage": 1},
    "fate_fabric": {"value": 1,   "percentage": 0},
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
    display_name = "Nightmare Pack Value"
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

# -- Helpers

# class FillerHelperPercentage(Range):
#     """
#     Choose the percentage of filler items in the pool that will be helpers instead. 
#     Helpers give a boost to your max Health or starting money.
#     Note if filler percentage doesn't sum up to 100 the system will treat them as proportions.
#     """
#     display_name = "Filler Helper Percentage"
#     range_start = 0
#     range_end = 100
#     default = 10

# class MaxHealthHelperPercentage(Range):
#     """
#     Choose the percentage of helper items that will boost your max health.
#     The remaning percentage will go towards initial money helpers, which boost initial money by X AMOUNT.
#     """
#     display_name = "Max Health Helper Percentage"
#     range_start = 0
#     range_end = 100
#     default = 50

# class InitialMoneyHelperPercentage(Range):
#     """
#     Choose the percentage of helper items that will boost your initial money by 25 each run.
#     This gets capped by the percentage being left from the MaxHealthHelpers. 
#     What percentage remains from this and the MaxHealthHelpers will give you items that boost the 
#     rarity of the boons obtained in runs.
#     """
#     display_name = "Initial Money Helper Percentage"
#     range_start = 0
#     range_end = 100
#     default = 35

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
    display_name = "Win Deaths Count"


class CauldronGiveHints(DefaultOnToggle):
    """
    If seeing an item on the Cauldron/Fated List of Prophecies 
    should give a hint for it on the multiworld.
    """
    display_name = "Cauldron/FatedList Give Hints"


# class AutomaticRoomsFinishOnHadesDefeat(Toggle):
#     """
#     If defeating Hades should give all room clears on Room based location mode 
#     or all rooms clears with the equipped weapon on Room weapon based location mode. 
#     """
#     display_name = "Automatic Room Finish On Hades Defeat"
#     default = 0

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

    keepsakesanity: KeepsakeSanity
    weaponsanity: WeaponSanity
    hidden_aspectsanity: HiddenAspectSanity
    cauldronsanity: CauldronSanity
    fatesanity: FateSanity

    true_ending: TrueEnding
    zodiac_sand_needed: ZodiacSandNeeded
    void_lens_needed: VoidLensNeeded
    boss_defeats_needed: BossDefeatsNeeded
    weapons_clears_needed: WeaponsClearsNeeded
    keepsakes_needed: KeepsakesNeeded
    fates_needed: FatesNeeded

    fear_system: FearSystem
    pain_vow_amount: PainVowAmount
    grit_vow_amount: GritVowAmount
    wards_vow_amount: WardsVowAmount
    frenzy_vow_amount: FrenzyVowAmount
    hordes_vow_amount: HordesVowAmount
    menace_vow_amount: MenaceVowAmount
    return_vow_amount: ReturnVowAmount
    fangs_vow_amount: FangsVowAmount
    scars_vow_amount: ScarsVowAmount
    debt_vow_amount: DebtVowAmount
    shadow_vow_amount: ShadowVowAmount
    forfeit_vow_amount: ForfeitVowAmount
    time_vow_amount: TimeVowAmount
    void_vow_amount: VoidVowAmount
    hubris_vow_amount: HubrisVowAmount
    denial_vow_amount: DenialVowAmount
    rivals_vow_amount: RivalsVowAmount

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

    filler_trap_percentage: FillerTrapPercentage

    reverse_order_rivals: ReverseOrderRivals
    ignore_win_deaths: IgnoreWinDeaths
    cauldron_give_hints: CauldronGiveHints
    death_link: DeathLink
    death_link_amnesty: DeathLinkAmnesty

hades_ii_option_groups = [
    OptionGroup("Game Options", [
        InitialWeapon,
        LocationSystem,
        ScoreRewardsAmount,
        KeepsakeSanity,
        WeaponSanity,
        HiddenAspectSanity,
        CauldronSanity,
        FateSanity,
        DeathLink,
        DeathLinkAmnesty,
    ]),
    OptionGroup("Goal Options", [
        TrueEnding,
        ZodiacSandNeeded,
        VoidLensNeeded,
        BossDefeatsNeeded,
        WeaponsClearsNeeded,
        KeepsakesNeeded,
        FatesNeeded,
    ]),
    OptionGroup("Fear Options", [
        FearSystem,
        PainVowAmount,
        GritVowAmount,
        WardsVowAmount,
        FrenzyVowAmount,
        HordesVowAmount,
        MenaceVowAmount,
        ReturnVowAmount,
        FangsVowAmount,
        ScarsVowAmount,
        DebtVowAmount,
        ShadowVowAmount,
        ForfeitVowAmount,
        TimeVowAmount,
        VoidVowAmount,
        HubrisVowAmount,
        DenialVowAmount,
        RivalsVowAmount,
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
    OptionGroup("Trap Options", [
        FillerTrapPercentage,
    ]),
    OptionGroup("Quality of Life Options", [
        ReverseOrderRivals,
        IgnoreWinDeaths,
        CauldronGiveHints,
    ])
]

# ------------------------------ Presets

hades_ii_option_presets: Dict[str, Dict[str, Any]] = {
    "Easy": {
        "score_rewards_amount": 100,
        "hidden_aspectsanity": False,
        "fatesanity": False,
        "fear_system": "reverse_Fear",
        "pain_vow_amount": 1,
        "grit_vow_amount": 1,
        "wards_vow_amount": 1,
        "frenzy_vow_amount": 1,
        "hordes_vow_amount": 1,
        "menace_vow_amount": 1,
        "return_vow_amount": 1,
        "fangs_vow_amount": 0,
        "scars_vow_amount": 1,
        "debt_vow_amount": 1,
        "shadow_vow_amount": 0,
        "forfeit_vow_amount": 0,
        "time_vow_amount": 0,
        "void_vow_amount": 0,
        "hubris_vow_amount": 0,
        "denial_vow_amount": 0,
        "rivals_vow_amount": 0,
        "ash_pack_value": 20,
        "bones_pack_value": 100,
        "psyche_pack_value": 50,
        "nectar_pack_value": 2,
        "ambrosia_pack_value": 2,
        "moon_dust_pack_value": 1,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 1,
        "filler_trap_percentage": 0,
    },
    "Normal": {
        "score_rewards_amount": 150,
        "hidden_aspectsanity": True,
        "fatesanity": False,
        "fear_system": "reverse_Fear",
        "pain_vow_amount": 2,
        "grit_vow_amount": 2,
        "wards_vow_amount": 1,
        "frenzy_vow_amount": 2,
        "hordes_vow_amount": 2,
        "menace_vow_amount": 1,
        "return_vow_amount": 1,
        "fangs_vow_amount": 1,
        "scars_vow_amount": 2,
        "debt_vow_amount": 1,
        "shadow_vow_amount": 1,
        "forfeit_vow_amount": 0,
        "time_vow_amount": 1,
        "void_vow_amount": 1,
        "hubris_vow_amount": 1,
        "denial_vow_amount": 0,
        "rivals_vow_amount": 1,
        "ash_pack_value": 10,
        "bones_pack_value": 50,
        "psyche_pack_value": 30,
        "nectar_pack_value": 1,
        "ambrosia_pack_value": 1,
        "moon_dust_pack_value": 1,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 1,
        "filler_trap_percentage": 5,
    },
    "Hard": {
        "score_rewards_amount": 150,
        "hidden_aspectsanity": True,
        "fatesanity": True,
        "fear_system": "reverse_Fear",
        "pain_vow_amount": 3,
        "grit_vow_amount": 3,
        "wards_vow_amount": 2,
        "frenzy_vow_amount": 3,
        "hordes_vow_amount": 3,
        "menace_vow_amount": 2,
        "return_vow_amount": 2,
        "fangs_vow_amount": 2,
        "scars_vow_amount": 3,
        "debt_vow_amount": 2,
        "shadow_vow_amount": 1,
        "forfeit_vow_amount": 1,
        "time_vow_amount": 2,
        "void_vow_amount": 2,
        "hubris_vow_amount": 2,
        "denial_vow_amount": 1,
        "rivals_vow_amount": 3,
        "ash_pack_value": 5,
        "bones_pack_value": 25,
        "psyche_pack_value": 15,
        "nectar_pack_value": 1,
        "ambrosia_pack_value": 1,
        "moon_dust_pack_value": 1,
        "nightmare_pack_value": 1,
        "fate_fabric_pack_value": 1,
        "filler_trap_percentage": 10,
    },
}