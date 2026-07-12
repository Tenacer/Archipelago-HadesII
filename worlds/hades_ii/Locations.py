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

# Score checks: one combined pool plus two route-named pools so the route is visible in the static datapackage.
location_table_score_checks: Dict[str, int] = _by_category("score")  # values are all int
location_table_underworld_score_checks: Dict[str, int] = _by_category("score_underworld")
location_table_surface_score_checks: Dict[str, int] = _by_category("score_surface")
SCORE_LOCATION_COUNT = len(location_table_score_checks)

# Lowest id of each route pool; the pools are contiguous so the client maps counts to [base, base+count).
UNDERWORLD_SCORE_BASE_ID = location_table_underworld_score_checks["Underworld Score Check 1"]
SURFACE_SCORE_BASE_ID = location_table_surface_score_checks["Surface Score Check 1"]
UNDERWORLD_SCORE_COUNT = len(location_table_underworld_score_checks)
SURFACE_SCORE_COUNT = len(location_table_surface_score_checks)


def score_check_split(score_rewards_amount: int, surface_score_ratio: int):
    """Return (underworld_budget, surface_budget); Regions.py, HadesIIClient.py and the game mod MUST all agree on this split."""
    surface_budget = score_rewards_amount * surface_score_ratio // 100
    underworld_budget = score_rewards_amount - surface_budget
    return underworld_budget, surface_budget


# -- Room-based location systems (room_based / room_weapon_based) --------------
# Per-route biome depth bounds as ordered (region, last_run_depth) pairs; each room check lives in the biome region owning its depth.
# TODO(confirm): boundaries are estimates — update from the mod's logged depths, then regenerate the room rows (scripts/gen_room_locations.py).
UNDERWORLD_BIOME_BOUNDS = [("Erebus", 11), ("Oceanus", 20), ("Fields", 25), ("Tartarus", 40)]
SURFACE_BIOME_BOUNDS    = [("Ephyra", 11), ("Thessaly", 19), ("Olympus", 29), ("Summit", 36)]

UNDERWORLD_ROOM_MAX = UNDERWORLD_BIOME_BOUNDS[-1][1]
SURFACE_ROOM_MAX    = SURFACE_BIOME_BOUNDS[-1][1]
# Run depth where Tartarus begins; the Chronos-kill auto-grant covers from here to the underworld max.
UNDERWORLD_AUTOGRANT_FROM = UNDERWORLD_BIOME_BOUNDS[-2][1] + 1


def room_region_for(bounds, depth: int) -> str:
    """Return the biome region that owns `depth` for a route's bounds list."""
    for region, last in bounds:
        if depth <= last:
            return region
    return bounds[-1][0]  # clamp into the final biome

# Weapon tokens for room_weapon_based suffixes; MUST match WEAPON_SHORT in the game mod.
ROOM_WEAPON_TOKENS = ["Staff", "Daggers", "Torches", "Axe", "Skull", "Coat"]


location_room_clears        = _by_category("room_clear")
location_room_weapon_clears = _by_category("room_weapon_clear")


def _room_clears_by_region(category: str) -> Dict[str, Dict[str, Optional[int]]]:
    """Group a room category's locations by the biome region in their CSV row."""
    grouped: Dict[str, Dict[str, Optional[int]]] = {}
    for name, d in location_table.items():
        if d.category == category:
            grouped.setdefault(d.region, {})[name] = d.code
    return grouped


location_room_clears_by_region        = _room_clears_by_region("room_clear")
location_room_weapon_clears_by_region = _room_clears_by_region("room_weapon_clear")


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
# Per-weapon final-boss clears (trackable filler checks, gated by weaponsanity).
location_weapon_clears      = _by_category("weapon_clear")
location_hidden_aspects     = _by_category("hidden_aspect")
location_base_aspects       = _by_category("base_aspect")
location_standard_aspects   = _by_category("standard_aspect")
location_tools              = _by_category("tool")
location_familiars          = _by_category("familiar")
# Familiar recruits live in the biome where the wild familiar appears.
location_familiars_by_region = {
    region: _by_region(region, "familiar")
    for region in ("Crossroads", "Erebus", "Oceanus", "Fields", "Olympus")
}
location_incantations       = _by_category("incantation")
location_table_prophecies   = _by_category("prophecy")

# The two surface-unlock incantation locations, owned by lock_surface_incantations.
SURFACE_LOCK_LOCATIONS = ("Permeation of Witching-Wards", "Unraveling a Fateful Bond")

# Boss kill reward locations ("Chronos Kill Reward N" / "Typhon Kill Reward N").
location_table_boss_rewards: Dict[str, int] = _by_category("boss_reward")

# Location groups (exported as `location_name_groups` on the World class).
location_name_groups = {
    "keepsakes":    set(location_keepsakes),
    "weapons":      set(location_weapons),
    "tools":        set(location_tools),
    "familiars":    set(location_familiars),
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

    # Boss kill rewards: only in True Ending mode.
    if options.true_ending:
        for i in range(1, options.chronos_kills_needed.value + 1):
            name = f"Chronos Kill Reward {i}"
            total[name] = location_table_boss_rewards[name]
        for i in range(1, options.typhon_kills_needed.value + 1):
            name = f"Typhon Kill Reward {i}"
            total[name] = location_table_boss_rewards[name]

    # Score checks: one combined pool, or the two route-named pools split by budget.
    if options.location_system == "score_based":
        if options.score_split_mode == 1:  # separate
            underworld_budget, surface_budget = score_check_split(
                options.score_rewards_amount.value, options.surface_score_ratio.value)
            for i in range(1, underworld_budget + 1):
                name = f"Underworld Score Check {i}"
                total[name] = location_table_underworld_score_checks[name]
            for i in range(1, surface_budget + 1):
                name = f"Surface Score Check {i}"
                total[name] = location_table_surface_score_checks[name]
        else:  # combined
            for i in range(1, options.score_rewards_amount.value + 1):
                name = f"Score Check {i}"
                total[name] = location_table_score_checks[name]

    # Room-based systems: per-route depth checks.
    elif options.location_system == "room_based":
        total.update(location_room_clears)
    elif options.location_system == "room_weapon_based":
        total.update(location_room_weapon_clears)

    # Tool unlocks at Schelmy's shop, gated by toolsanity
    if options.toolsanity.value == 1:
        total.update(location_tools)

    # Familiar recruits, gated by familiarsanity
    if options.familiarsanity.value == 1:
        total.update(location_familiars)

    if options.keepsakesanity.value == 1:
        total.update(location_keepsakes)

    if options.weaponsanity.value == 1:
        for name, code in location_weapons.items():
            if not should_ignore_weapon_location(name, options):
                total[name] = code
        total.update(location_weapon_clears)

    if options.hidden_aspectsanity.value == 1:
        total.update(location_hidden_aspects)

    # Base + standard aspects; the starting weapon's Initial Aspect has no check (granted at start).
    if options.aspectsanity.value == 1:
        for name, code in {**location_base_aspects, **location_standard_aspects}.items():
            if not should_ignore_aspect_location(name, options):
                total[name] = code

    # Cauldronsanity covers the non-surface incantation locations; Rivals T4 is excluded under true_ending (post-goal gate).
    if options.cauldronsanity.value == 1:
        for name, code in location_incantations.items():
            if name in SURFACE_LOCK_LOCATIONS:
                continue
            if name == "Rivals of Old and Rot" and options.true_ending.value == 1:
                continue
            # Broker granted for free at game start — drop its check.
            if name == "Summoning of Mercantile Fortune" and options.unlock_broker.value == 1:
                continue
            total[name] = code

    # lock_surface_incantations owns the two surface-unlock locations.
    if options.lock_surface_incantations.value == 1:
        for name in SURFACE_LOCK_LOCATIONS:
            total[name] = location_incantations[name]

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


# Per initial_weapon value: [base, first standard, second standard] — for aspect sanity.
# initial_aspect (0=base, 1=first standard, 2=second standard) picks the granted starting aspect.
ASPECT_BY_WEAPON_ITEM = {
    0: ["Staff Melinoe Aspect Unlock",   "Circe Aspect Unlock",    "Momus Aspect Unlock"],
    1: ["Daggers Melinoe Aspect Unlock", "Artemis Aspect Unlock",  "Pan Aspect Unlock"],
    2: ["Torches Melinoe Aspect Unlock", "Moros Aspect Unlock",    "Eos Aspect Unlock"],
    3: ["Axe Melinoe Aspect Unlock",     "Charon Aspect Unlock",   "Thanatos Aspect Unlock"],
    4: ["Skull Melinoe Aspect Unlock",   "Medea Aspect Unlock",    "Persephone Aspect Unlock"],
    5: ["Coat Melinoe Aspect Unlock",    "Nyx Aspect Unlock",      "Selene Aspect Unlock"],
}
ASPECT_BY_WEAPON_LOC = {
    0: ["Staff Weapon Melinoe Aspect Unlock Location",   "Staff Weapon Circe Aspect Unlock Location",    "Staff Weapon Momus Aspect Unlock Location"],
    1: ["Daggers Weapon Melinoe Aspect Unlock Location", "Daggers Weapon Artemis Aspect Unlock Location","Daggers Weapon Pan Aspect Unlock Location"],
    2: ["Torches Weapon Melinoe Aspect Unlock Location", "Torches Weapon Moros Aspect Unlock Location",  "Torches Weapon Eos Aspect Unlock Location"],
    3: ["Axe Weapon Melinoe Aspect Unlock Location",     "Axe Weapon Charon Aspect Unlock Location",     "Axe Weapon Thanatos Aspect Unlock Location"],
    4: ["Skull Weapon Melinoe Aspect Unlock Location",   "Skull Weapon Medea Aspect Unlock Location",    "Skull Weapon Persephone Aspect Unlock Location"],
    5: ["Coat Weapon Melinoe Aspect Unlock Location",    "Coat Weapon Nyx Aspect Unlock Location",       "Coat Weapon Selene Aspect Unlock Location"],
}


def initial_aspect_item(options):
    """AP item name for the granted starting aspect, or None when aspect sanity is off."""
    if options.aspectsanity.value != 1:
        return None
    return ASPECT_BY_WEAPON_ITEM[options.initial_weapon.value][options.initial_aspect.value]


def initial_aspect_location(options):
    """AP location name skipped because it is the granted starting aspect, or None."""
    if options.aspectsanity.value != 1:
        return None
    return ASPECT_BY_WEAPON_LOC[options.initial_weapon.value][options.initial_aspect.value]


def should_ignore_aspect_location(name: str, options) -> bool:
    return initial_aspect_location(options) == name


class HadesIILocation(Location):
    game: str = "Hades II"

    def __init__(self, player: int, name: str, address=None, parent=None):
        super().__init__(player, name, address, parent)
        if address is None:
            self.event = True
            self.locked = True
