import csv
from functools import reduce
from typing import Dict, List, NamedTuple, Optional, Set

from BaseClasses import Item, ItemClassification

from . import data
from .Locations import setup_location_table_with_settings, should_ignore_weapon_location, \
    initial_aspect_item


_BOSS_VICTORY_NAMES = {
    "Hecate Victory", "Scylla Victory", "Cerberus Victory", "Chronos Victory",
    "Polyphemus Victory", "Eris Victory", "Prometheus Victory", "Typhon Victory",
}

# The two surface-unlock incantations are owned by lock_surface_incantations, never cauldronsanity.
SURFACE_LOCK_ITEMS = ("Permeation of Witching-Wards", "Unraveling a Fateful Bond")

# Incantations used in Rules.py logic gates; must be promoted to progression since `useful` items are invisible to state.has().
PROGRESSION_INCANTATION_ITEMS = frozenset({
    # Group 2 — underworld chain heads
    "Rise of Stygian Wells",
    "Revival of a Desecrating Pool",
    "Cleansing of Fountain-Waters",
    "Gathering of Ancient Bones",
    # Group 4 — Market chain head
    "Summoning of Mercantile Fortune",
    # Group 5 — Tools / Garden chain
    "Night's Craftwork",
    "Flourishing Soil",
    "Observance of Gaia's Secrets",
    "Rich Soil",
    "Verdant Soil",
    # Group 6 — Bounty / familiar heads
    "Abyssal Insight",
    "Faith of Familiar Spirits",
    # Group 2 — underworld prereq referenced by Group 3 surface chain
    "Exhumed Troves",   # Eyes of Night and Darkness needs both Arisen + Exhumed
    # Group 3 — surface-gated downstream-of-other-incantation links
    "Rush of Fresh Air",
    "Arisen Troves",
    "Circles of Protection",
    # Group 8 — Hypnos chain
    "End to Deepest Slumber",
    "End to Dearest Slumber",
    # Group 9
    "Forget-Me-Not",
    "Insight into Offerings",
    "Favored of All Keepsakes",
    # Group F — gates referenced by prophecy rules
    "Greater Favor of Gaia",
    "Necromantic Influence",
    "Rite of River-Fording",
    # Ingredient-logic gates (Rules.handle_ingredients / _has_hidden_aspect)
    "Aspects of Night and Darkness",
    "Bravery of Familiar Spirits",
})

# Prophecy items used as chain prereqs in Rules.py; promoted to progression for the same reason.
PROGRESSION_PROPHECY_ITEMS = frozenset({
    "Witch of the Crossroads Reward",   # QuestBeatHecate → Natural Talent
    "Temporary Setback Reward",          # QuestFirstUnderworldClear → Sword of the Night, Arcana of the Ages
    "Close Companions Reward",           # QuestRecruitFamiliars → Beyond Familiar
    "Tools of the Unseen Reward",        # QuestToolsUnlocks → Precision Instrument
    "The Unseen Sentinel Reward",        # QuestUnlockAllWeaponAspects → Bearing Dark Gifts
})

# (base item name, shrine_upgrade_name); vow items only enter the pool in reverse_fear mode.
_VOW_OPTIONS = [
    ("Vow of Pain",    "EnemyDamageShrineUpgrade"),
    ("Vow of Grit",    "EnemyHealthShrineUpgrade"),
    ("Vow of Wards",   "EnemyShieldShrineUpgrade"),
    ("Vow of Frenzy",  "EnemySpeedShrineUpgrade"),
    ("Vow of Hordes",  "EnemyCountShrineUpgrade"),
    ("Vow of Menace",  "NextBiomeEnemyShrineUpgrade"),
    ("Vow of Return",  "EnemyRespawnShrineUpgrade"),
    ("Vow of Fangs",   "EnemyEliteShrineUpgrade"),
    ("Vow of Scars",   "HealingReductionShrineUpgrade"),
    ("Vow of Debt",    "ShopPricesShrineUpgrade"),
    ("Vow of Shadow",  "MinibossCountShrineUpgrade"),
    ("Vow of Forfeit", "BoonSkipShrineUpgrade"),
    ("Vow of Time",    "BiomeSpeedShrineUpgrade"),
    ("Vow of Void",    "LimitGraspShrineUpgrade"),
    ("Vow of Hubris",  "BoonManaReserveShrineUpgrade"),
    ("Vow of Denial",  "BanUnpickedBoonsShrineUpgrade"),
    ("Vow of Rivals",  "BossDifficultyShrineUpgrade"),
]


class ItemData(NamedTuple):
    code: Optional[int]
    item_classification: ItemClassification
    groups: frozenset


# Sorry for the abomination of uppercase and underscore here, but I figured it was more
# readable than `HadesIIItem`
class Hades_II_Item(Item):
    game = "Hades II"

    def __init__(self, name: str, player: int):
        item_data = item_table[name]
        super().__init__(name, item_data.item_classification, item_data.code, player)


def _parse_classification(field: str) -> ItemClassification:
    # Comma-separated classifications (e.g. "progression,useful") combine via bitwise OR.
    parts = [ItemClassification[p.strip()] for p in field.split(",") if p.strip()]
    return reduce(lambda a, b: a | b, parts)


def _load_items_csv() -> Dict[str, ItemData]:
    try:
        from importlib.resources import files
    except ImportError:
        from importlib_resources import files  # type: ignore

    items: Dict[str, ItemData] = {}
    with files(data).joinpath("items.csv").open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = int(row["id"]) if row["id"] else None
            classification = _parse_classification(row["classification"])
            groups = frozenset(g.strip() for g in row["groups"].split(",") if g.strip())
            items[row["name"]] = ItemData(code, classification, groups)
    return items


item_table: Dict[str, ItemData] = _load_items_csv()


def _items_in_group(group: str) -> Dict[str, ItemData]:
    return {name: d for name, d in item_table.items() if group in d.groups}


# Exported subtables (consumed by Rules.py and create_items below)
item_table_fears       = _items_in_group("fears")
item_table_filler      = _items_in_group("fillers")
item_table_keepsakes   = _items_in_group("keepsakes")
item_table_post_ending_keepsakes = _items_in_group("post_ending_keepsakes")
item_table_weapons     = _items_in_group("weapons")
item_table_tools       = _items_in_group("tools")
item_table_hidden_aspects = _items_in_group("hidden_aspects")
item_table_base_aspects = _items_in_group("base_aspects")
item_table_standard_aspects = _items_in_group("standard_aspects")
item_table_familiars   = _items_in_group("familiars")
item_table_traps       = _items_in_group("traps")
item_table_helpers     = _items_in_group("helpers")
item_table_prophecies  = _items_in_group("prophecies")
item_table_incantations = _items_in_group("incantations")
item_table_true_ending_ingredients  = _items_in_group("true_ending_ingredients")

# Build item_name_groups by scanning every tag on every item.
def _build_name_groups(items: Dict[str, ItemData]) -> Dict[str, Set[str]]:
    groups: Dict[str, Set[str]] = {}
    for name, d in items.items():
        for g in d.groups:
            groups.setdefault(g, set()).add(name)
    return groups

item_name_groups: Dict[str, Set[str]] = _build_name_groups(item_table)


def create_items(self) -> None:
    local_location_table = setup_location_table_with_settings(self.options).copy()
    pool: List[Item] = []

    # Fear vows — only in reverse_fear; amounts from the randomly distributed vow_ranks.
    if self.options.fear_system.value == 1:
        vow_ranks = getattr(self, "vow_ranks", {})
        for base, shrine_name in _VOW_OPTIONS:
            for _ in range(vow_ranks.get(shrine_name, 0)):
                pool.append(self.create_item(base))

    # Keepsakes: 30 with checks plus 3 receive-only post-ending ones; promoted to progression when the goal counts them.
    if self.options.keepsakesanity:
        promote = self.options.keepsakes_needed.value > 0
        for name in item_table_keepsakes:
            item = self.create_item(name)
            if promote:
                item.classification = ItemClassification.progression
            pool.append(item)
        pool.extend(self.create_item(name) for name in item_table_post_ending_keepsakes)

    # Weapons
    if self.options.weaponsanity:
        for name in item_table_weapons:
            location_name = f"{name} Location"
            if should_ignore_weapon_location(location_name, self.options):
                continue
            pool.append(Hades_II_Item(name, self.player))

    # Hidden aspects — 1 per weapon, promoted to progression for the Rules.py gates.
    if self.options.hidden_aspectsanity:
        for name in item_table_hidden_aspects:
            item = self.create_item(name)
            item.classification = ItemClassification.progression
            pool.append(item)

    # Base + standard aspects — progression (gate wielding + the hidden reveal chain).
    # The starting weapon's Initial Aspect is granted at start, so it leaves the pool.
    if self.options.aspectsanity:
        skip = initial_aspect_item(self.options)
        for name in (*item_table_base_aspects, *item_table_standard_aspects):
            if name == skip:
                continue
            item = self.create_item(name)
            item.classification = ItemClassification.progression
            pool.append(item)

    # Tools — gated by toolsanity (otherwise tools stay vanilla)
    if self.options.toolsanity:
        pool.extend(self.create_item(name) for name in item_table_tools)

    # Familiars — promoted to progression for the Rules.py gathering and count gates.
    if self.options.familiarsanity:
        for name in item_table_familiars:
            item = self.create_item(name)
            item.classification = ItemClassification.progression
            pool.append(item)

    # Surface-unlock incantations — always progression so the surface predicates can see them.
    if self.options.lock_surface_incantations:
        for name in SURFACE_LOCK_ITEMS:
            item = self.create_item(name)
            item.classification = ItemClassification.progression
            pool.append(item)

    # Cauldronsanity covers the remaining incantations; Rivals T4 is skipped under true_ending (post-goal gate).
    if self.options.cauldronsanity:
        for name in item_table_incantations:
            if name in SURFACE_LOCK_ITEMS:
                continue
            if name == "Rivals of Old and Rot" and self.options.true_ending:
                continue
            # The Broker is free under unlock_broker, so its incantation leaves the pool.
            if name == "Summoning of Mercantile Fortune" and self.options.unlock_broker:
                continue
            item = self.create_item(name)
            if name in PROGRESSION_INCANTATION_ITEMS:
                item.classification = ItemClassification.progression
            pool.append(item)

    # True Ending goal items: one Zodiac Sand per Chronos kill and one Void Lens per Typhon kill; extras above the thresholds feed Arcana upgrades.
    if self.options.true_ending:
        for _ in range(self.options.chronos_kills_needed.value):
            pool.append(self.create_item("Zodiac Sand"))
        for _ in range(self.options.typhon_kills_needed.value):
            pool.append(self.create_item("Void Lens"))
        pool.append(self.create_item("Gigaros"))
        pool.append(self.create_item("Entropy"))

    # Prophecies — promoted to progression when the goal counts them or they gate another prophecy.
    if self.options.fatesanity:
        promote_all = self.options.fates_needed.value > 0
        for name in item_table_prophecies:
            item = self.create_item(name)
            if promote_all or name in PROGRESSION_PROPHECY_ITEMS:
                item.classification = ItemClassification.progression
            pool.append(item)

    # Handle fillers and traps
    handle_fillers(self, pool, local_location_table)

    # Place in boss event pseudo-items
    place_boss_events(self.multiworld, self.player, self.options)

    # Add items to pool
    self.multiworld.itempool += pool


# Places boss event pseudo-items at each location
def place_boss_events(world, player, options) -> None:
    names = set(_BOSS_VICTORY_NAMES)
    if options.true_ending:
        names.add("Chronos True Victory")
    for boss in names:
        location = world.get_location(boss, player)
        event_item = Item(boss, ItemClassification.progression, None, player)
        location.place_locked_item(event_item)


# Calculates percentages of filler materials and traps
def handle_fillers(self, pool, local_location_table):
    total_fillers_needed = len(local_location_table) - len(pool)

    trap_pct   = self.options.filler_trap_percentage   if self.options.enable_traps   else 0
    helper_pct = self.options.filler_helper_percentage if self.options.enable_helpers else 0

    # Outside vanilla fear the game only hands out Nightmare at the True Ending, so aspect
    # leveling would stall — guarantee at least a 5% Nightmare share from the filler pool.
    nightmare_pct = self.options.nightmare_pack_percentage.value
    if self.options.fear_system.value != 3:
        nightmare_pct = max(5, nightmare_pct)

    percentages = {
        "ash":         self.options.ash_pack_percentage,
        "bones":       self.options.bones_pack_percentage,
        "psyche":      self.options.psyche_pack_percentage,
        "nectar":      self.options.nectar_pack_percentage,
        "ambrosia":    self.options.ambrosia_pack_percentage,
        "nightmare":   nightmare_pct,
        "moon_dust":   self.options.moon_dust_pack_percentage,
        "fate_fabric": self.options.fate_fabric_pack_percentage,
        "traps":       trap_pct,
        "helpers":     helper_pct,
    }

    total_percentage = sum(percentages.values())
    if total_percentage == 0:
        percentages["bones"] = 100
        total_percentage = 100

    correction = 100 / total_percentage

    counts = {
        name: int(total_fillers_needed * pct * correction / 100)
        for name, pct in percentages.items()
    }

    # Populate the rest with bones for remainder safety
    counts["bones"] += total_fillers_needed - sum(counts.values())
    counts["bones"] = max(counts["bones"], 0)

    filler_counts = {
        "Ash":         counts["ash"],
        "Bones":       counts["bones"],
        "Psyche":      counts["psyche"],
        "Nectar":      counts["nectar"],
        "Ambrosia":    counts["ambrosia"],
        "Nightmare":   counts["nightmare"],
        "Moon Dust":   counts["moon_dust"],
        "Fate Fabric": counts["fate_fabric"],
    }

    for name, count in filler_counts.items():
        pool.extend(self.create_item(name) for _ in range(count))

    # Fill traps — cycle through the trap items so the count is split evenly.
    trap_pool = list(item_table_traps.keys())
    if trap_pool:
        for i in range(counts["traps"]):
            item_name = trap_pool[i % len(trap_pool)]
            pool.append(Hades_II_Item(item_name, self.player))
    else:
        pool.extend(self.create_item("Bones") for _ in range(counts["traps"]))

    # Fill helpers — split among MaxHealth / InitialMoney / BoonBoost; the remainder is boon-boost.
    helper_total = counts["helpers"]
    if helper_total > 0 and item_table_helpers:
        pct_mh = self.options.max_health_helper_percentage.value
        pct_im = min(self.options.initial_money_helper_percentage.value,
                     max(0, 100 - pct_mh))
        mh_count = helper_total * pct_mh // 100
        im_count = helper_total * pct_im // 100
        bb_count = helper_total - mh_count - im_count
        pool.extend(self.create_item("Max Health Helper")    for _ in range(mh_count))
        pool.extend(self.create_item("Initial Money Helper") for _ in range(im_count))
        pool.extend(self.create_item("Boon Boost Helper")    for _ in range(bb_count))
    else:
        pool.extend(self.create_item("Bones") for _ in range(helper_total))
