import csv
from typing import Dict, NamedTuple, Optional

from BaseClasses import Location

from . import data


hades_ii_base_location_id = 1


class LocationData(NamedTuple):
    code: Optional[int]
    region: str
    category: str


def _load_locations_csv() -> Dict[str, LocationData]:
    try:
        from importlib.resources import files
    except ImportError:
        from importlib_resources import files  # type: ignore

    locs: Dict[str, LocationData] = {}
    with files(data).joinpath("locations.csv").open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = int(row["id"]) if row["id"] else None
            locs[row["name"]] = LocationData(code, row["region"], row["category"])
    return locs


location_table: Dict[str, LocationData] = _load_locations_csv()


def _by_category(category: str) -> Dict[str, Optional[int]]:
    return {name: d.code for name, d in location_table.items() if d.category == category}


def _by_region(region: str, category: Optional[str] = None) -> Dict[str, Optional[int]]:
    return {
        name: d.code for name, d in location_table.items()
        if d.region == region and (category is None or d.category == category)
    }


# -- Exports consumed by Regions.py / HadesIIClient.py / Rules.py ---------------

# Score checks live in Menu and are always accessible.
location_table_score_checks: Dict[str, int] = _by_category("score")  # values are all int
SCORE_LOCATION_COUNT = len(location_table_score_checks)

# Per-biome event tables (victory events, no address).
location_table_erebus   = _by_region("Erebus",   "biome_victory")
location_table_oceanus  = _by_region("Oceanus",  "biome_victory")
location_table_fields   = _by_region("Fields",   "biome_victory")
location_table_tartarus = _by_region("Tartarus", "biome_victory")
location_table_ephyra   = _by_region("Ephyra",   "biome_victory")
location_table_thessaly = _by_region("Thessaly", "biome_victory")
location_table_olympus  = _by_region("Olympus",  "biome_victory")
location_table_summit   = _by_region("Summit",   "biome_victory")

# Crossroads (option-gated) tables
location_keepsakes          = _by_category("keepsake")
location_weapons            = _by_category("weapon")
location_hidden_aspects     = _by_category("hidden_aspect")
location_tools              = _by_category("tool")
location_incantations       = _by_category("incantation")
location_table_prophecies   = _by_category("prophecy")

# Boss kill reward locations — separate from biome-victory events above.
location_table_boss_rewards: Dict[str, int] = _by_category("boss_reward")

# Unused placeholder (kept for back-compat — no Crossroads-category locations
# live outside the specialised tables above).
location_table_crossroads: Dict[str, int] = {}

# Maps in-game boss room name → AP location ID (used by HadesIIClient)
BOSS_ROOM_TO_LOCATION_ID: Dict[str, int] = {
    "I_Boss01": location_table_boss_rewards["Chronos Kill Reward"],
    "Q_Boss01": location_table_boss_rewards["Typhon Kill Reward"],
    "Q_Boss02": location_table_boss_rewards["Typhon Kill Reward"],
}

# Location groups (exported as `location_name_groups` on the World class).
location_name_groups = {
    "keepsakes":    set(location_keepsakes),
    "weapons":      set(location_weapons),
    "tools":        set(location_tools),
    "prophecies":   set(location_table_prophecies),
    "incantations": set(location_incantations),
}


def give_all_locations_table() -> dict:
    """Flat name→id dict for every non-event location. Fed to World.location_name_to_id."""
    return {
        name: d.code for name, d in location_table.items() if d.code is not None
    }


def setup_location_table_with_settings(options) -> dict:
    """Returns the locations actually in play for this seed, filtered by options."""
    total: Dict[str, Optional[int]] = {}

    # Boss rewards always in play.
    total.update(location_table_boss_rewards)

    # Score checks only under score_based system; limited to first N.
    if options.location_system == "score_based":
        for i in range(1, options.score_rewards_amount.value + 1):
            name = f"Score Check {i}"
            total[name] = location_table_score_checks[name]

    # Tools are always available at the shop
    total.update(location_tools)

    if options.keepsakesanity.value == 1:
        total.update(location_keepsakes)

    if options.weaponsanity.value == 1:
        for name, code in location_weapons.items():
            if not should_ignore_weapon_location(name, options):
                total[name] = code

    if options.hidden_aspectsanity.value == 1:
        total.update(location_hidden_aspects)

    if options.cauldronsanity.value == 1:
        total.update(location_incantations)

    if options.fatesanity == 1:
        total.update(location_table_prophecies)

    return total


def should_ignore_weapon_location(weaponLocation: str, options) -> bool:
    mapping = {
        0: "Staff Weapon Unlock Location",
        1: "Daggers Weapon Unlock Location",
        2: "Torches Weapon Unlock Location",
        3: "Axe Weapon Unlock Location",
        4: "Skull Weapon Unlock Location",
        5: "Coat Weapon Unlock Location",
    }
    return mapping.get(options.initial_weapon.value) == weaponLocation


class HadesIILocation(Location):
    game: str = "Hades II"

    def __init__(self, player: int, name: str, address=None, parent=None):
        super().__init__(player, name, address, parent)
        if address is None:
            self.event = True
            self.locked = True
