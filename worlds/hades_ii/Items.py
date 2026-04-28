import csv
from functools import reduce
from typing import Dict, List, NamedTuple, Optional, Set

from BaseClasses import Item, ItemClassification

from . import data
from .Locations import setup_location_table_with_settings, should_ignore_weapon_location


_BOSS_VICTORY_NAMES = {
    "Hecate Victory", "Scylla Victory", "Cerberus Victory", "Chronos Victory",
    "Polyphemus Victory", "Eris Victory", "Prometheus Victory", "Typhon Victory",
}

# (base item name, is_multi_rank, shrine_upgrade_name)
# Multi-rank vows add N items (ranks 1..N); single-rank vows add 1 item when rank >= 1.
# Vow items only enter the pool in reverse_Fear mode; amounts come from world.vow_ranks.
_VOW_OPTIONS = [
    ("Vow of Pain",    True,  "EnemyDamageShrineUpgrade"),
    ("Vow of Grit",    True,  "EnemyHealthShrineUpgrade"),
    ("Vow of Wards",   True,  "EnemyShieldShrineUpgrade"),
    ("Vow of Frenzy",  True,  "EnemySpeedShrineUpgrade"),
    ("Vow of Hordes",  True,  "EnemyCountShrineUpgrade"),
    ("Vow of Menace",  True,  "NextBiomeEnemyShrineUpgrade"),
    ("Vow of Return",  True,  "EnemyRespawnShrineUpgrade"),
    ("Vow of Fangs",   True,  "EnemyEliteShrineUpgrade"),
    ("Vow of Scars",   True,  "HealingReductionShrineUpgrade"),
    ("Vow of Debt",    True,  "ShopPricesShrineUpgrade"),
    ("Vow of Shadow",  False, "MinibossCountShrineUpgrade"),
    ("Vow of Forfeit", False, "BoonSkipShrineUpgrade"),
    ("Vow of Time",    True,  "BiomeSpeedShrineUpgrade"),
    ("Vow of Void",    True,  "LimitGraspShrineUpgrade"),
    ("Vow of Hubris",  True,  "BoonManaReserveShrineUpgrade"),
    ("Vow of Denial",  False, "BanUnpickedBoonsShrineUpgrade"),
    ("Vow of Rivals",  True,  "BossDifficultyShrineUpgrade"),
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
item_table_traps       = _items_in_group("traps")
item_table_helpers     = _items_in_group("helpers")
item_table_prophecies  = _items_in_group("prophecies")
item_table_incantations = _items_in_group("incantations")
item_table_true_ending_ingredients  = _items_in_group("true_ending_ingredients")
item_table_true_ending_incantations = _items_in_group("true_ending_incantations")

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

    # Fear vows — only in reverse_Fear (1); amounts from the randomly distributed vow_ranks.
    # minimal_Fear (2) and vanilla_Fear (3) add no vow items to the pool.
    if self.options.fear_system.value == 1:
        vow_ranks = getattr(self, "vow_ranks", {})
        for base, is_multi, shrine_name in _VOW_OPTIONS:
            amount = vow_ranks.get(shrine_name, 0)
            if is_multi:
                for rank in range(1, amount + 1):
                    pool.append(self.create_item(f"{base} Rank {rank}"))
            elif amount >= 1:
                pool.append(self.create_item(base))

    # Keepsakes (canonical 30 as checks, plus 3 post-ending keepsakes as
    # receive-only items — they have no corresponding checks since the player
    # cannot reach those NPCs under the randomizer's goal).
    # Promote to progression when the goal actually counts keepsakes; otherwise
    # the CSV's `useful` classification stands.
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
            # item name is e.g. "Staff Weapon Unlock Item"; location is "Staff Weapon Unlock Location"
            location_name = name.replace(" Item", " Location")
            if should_ignore_weapon_location(location_name, self.options):
                continue
            pool.append(Hades_II_Item(name, self.player))

    # Hidden aspects — 1 per weapon; visible aspects ride along with the weapon unlock.
    if self.options.hidden_aspectsanity:
        pool.extend(self.create_item(name) for name in item_table_hidden_aspects)

    # Tools — always available (no toolsanity option yet)
    pool.extend(self.create_item(name) for name in item_table_tools)

    # Incantations — gated by cauldronsanity
    if self.options.cauldronsanity:
        pool.extend(self.create_item(name) for name in item_table_incantations)

    # True Ending goal items: Zodiac Sand (N), Void Lens (M), Gigaros (1),
    # and the two goal incantations (items only — no locations).
    if self.options.true_ending:
        for _ in range(self.options.zodiac_sand_needed.value):
            pool.append(self.create_item("Zodiac Sand"))
        for _ in range(self.options.void_lens_needed.value):
            pool.append(self.create_item("Void Lens"))
        pool.append(self.create_item("Gigaros"))
        for name in item_table_true_ending_incantations:
            pool.append(self.create_item(name))

    # Prophecies — 89 items paired 1:1 with Fated List check locations.
    # Promote to progression when the goal actually counts prophecies.
    if self.options.fatesanity:
        promote = self.options.fates_needed.value > 0
        for name in item_table_prophecies:
            item = self.create_item(name)
            if promote:
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

    percentages = {
        "ash":         self.options.ash_pack_percentage,
        "bones":       self.options.bones_pack_percentage,
        "psyche":      self.options.psyche_pack_percentage,
        "nectar":      self.options.nectar_pack_percentage,
        "ambrosia":    self.options.ambrosia_pack_percentage,
        "nightmare":   self.options.nightmare_pack_percentage,
        "moon_dust":   self.options.moon_dust_pack_percentage,
        "fate_fabric": self.options.fate_fabric_pack_percentage,
        "traps":       self.options.filler_trap_percentage,
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

    # Fill traps — only if any trap items are defined. The trap implementation
    # isn't in place yet; when it is, repopulate the `traps` group in items.csv.
    trap_pool = list(item_table_traps.keys())
    if trap_pool:
        for i in range(counts["traps"]):
            item_name = trap_pool[i % len(trap_pool)]
            pool.append(Hades_II_Item(item_name, self.player))
    else:
        # No traps available — backfill the shortfall with bones.
        pool.extend(self.create_item("Bones") for _ in range(counts["traps"]))
