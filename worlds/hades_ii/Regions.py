from BaseClasses import Region, Entrance
from .Locations import (
    HadesIILocation,
    SURFACE_LOCK_LOCATIONS,
    location_table_score_checks,
    location_table_underworld_score_checks,
    location_table_surface_score_checks,
    score_check_split,
    location_room_clears_by_region,
    location_room_weapon_clears_by_region,
    location_table_boss_rewards,
    location_keepsakes,
    location_weapons,
    location_weapon_clears,
    location_hidden_aspects,
    location_base_aspects,
    location_standard_aspects,
    location_tools,
    location_familiars_by_region,
    location_incantations,
    location_table_prophecies,
    location_table_erebus,
    location_table_oceanus,
    location_table_fields,
    location_table_tartarus,
    location_table_ephyra,
    location_table_thessaly,
    location_table_olympus,
    location_table_summit,
    should_ignore_weapon_location,
    should_ignore_aspect_location,
)

# Biome → (event location table, boss reward base name or None); rewards are emitted in True Ending mode only.
_biome_data = {
    "Erebus":    (location_table_erebus,   None),
    "Oceanus":   (location_table_oceanus,  None),
    "Fields":    (location_table_fields,   None),
    "Tartarus":  (location_table_tartarus, ("Chronos Kill Reward", "chronos_kills_needed")),
    "Ephyra":    (location_table_ephyra,   None),
    "Thessaly":  (location_table_thessaly, None),
    "Olympus":   (location_table_olympus,  None),
    "Summit":    (location_table_summit,   ("Typhon Kill Reward", "typhon_kills_needed")),
}

_region_connections = {
    "Menu":       ["Crossroads"],
    "Crossroads": ["Erebus", "Ephyra"],
    "Erebus":     ["Oceanus"],
    "Oceanus":    ["Fields"],
    "Fields":     ["Tartarus"],
    "Tartarus":   [],
    "Ephyra":     ["Thessaly"],
    "Thessaly":   ["Olympus"],
    "Olympus":    ["Summit"],
    "Summit":     [],
}


def _add_location(region: Region, name: str, address):
    region.locations.append(HadesIILocation(region.player, name, address, region))


def create_regions(player, multiworld, location_database, options):
    regions = {name: Region(name, player, multiworld) for name in _region_connections}

    # Score checks: combined mode lives in Menu; separate mode places each route's budget in Erebus/Ephyra so fill respects surface access.
    if options.location_system == "score_based":
        n = options.score_rewards_amount.value
        if options.score_split_mode == 1:  # separate
            underworld_budget, surface_budget = score_check_split(n, options.surface_score_ratio.value)
            for i in range(1, underworld_budget + 1):
                name = f"Underworld Score Check {i}"
                _add_location(regions["Erebus"], name, location_table_underworld_score_checks[name])
            for i in range(1, surface_budget + 1):
                name = f"Surface Score Check {i}"
                _add_location(regions["Ephyra"], name, location_table_surface_score_checks[name])
        else:  # combined
            for i in range(1, n + 1):
                name = f"Score Check {i}"
                _add_location(regions["Menu"], name, location_table_score_checks[name])

    # Room-based systems: each depth's check goes in the biome region owning its run depth.
    room_region_tables = None
    if options.location_system == "room_based":
        room_region_tables = location_room_clears_by_region
    elif options.location_system == "room_weapon_based":
        room_region_tables = location_room_weapon_clears_by_region
    if room_region_tables:
        for region_name, table in room_region_tables.items():
            for name, loc_id in table.items():
                _add_location(regions[region_name], name, loc_id)

    # Biome victory events + boss reward checks; Chronos True Victory only exists under true_ending.
    for region_name, (event_table, boss_reward) in _biome_data.items():
        region = regions[region_name]
        for event_name in event_table:
            if event_name == "Chronos True Victory" and not options.true_ending:
                continue
            _add_location(region, event_name, None)  # event — address is None
        if boss_reward and options.true_ending:
            base_name, count_option = boss_reward
            count = getattr(options, count_option).value
            for i in range(1, count + 1):
                name = f"{base_name} {i}"
                _add_location(region, name, location_table_boss_rewards[name])

    # Option-gated locations
    if options.keepsakesanity:
        for name, loc_id in location_keepsakes.items():
            _add_location(regions["Crossroads"], name, loc_id)

    if options.weaponsanity:
        for name, loc_id in location_weapons.items():
            if not should_ignore_weapon_location(name, options):
                _add_location(regions["Crossroads"], name, loc_id)
        # Per-weapon final-boss clears — access rules set in Rules.set_rules.
        for name, loc_id in location_weapon_clears.items():
            _add_location(regions["Crossroads"], name, loc_id)

    if options.hidden_aspectsanity:
        for name, loc_id in location_hidden_aspects.items():
            _add_location(regions["Crossroads"], name, loc_id)

    # Base + standard aspects — the starting weapon's Initial Aspect is granted, not a check.
    if options.aspectsanity:
        for name, loc_id in {**location_base_aspects, **location_standard_aspects}.items():
            if not should_ignore_aspect_location(name, options):
                _add_location(regions["Crossroads"], name, loc_id)

    # Cauldronsanity owns the non-surface incantation locations; Rivals T4 is excluded under true_ending (post-goal gate).
    if options.cauldronsanity:
        for name, loc_id in location_incantations.items():
            if name in SURFACE_LOCK_LOCATIONS:
                continue
            if name == "Rivals of Old and Rot" and options.true_ending:
                continue
            # Broker granted for free at game start — drop its check.
            if name == "Summoning of Mercantile Fortune" and options.unlock_broker:
                continue
            _add_location(regions["Crossroads"], name, loc_id)

    # lock_surface_incantations owns the two surface-unlock locations.
    if options.lock_surface_incantations:
        for name in SURFACE_LOCK_LOCATIONS:
            _add_location(regions["Crossroads"], name, location_incantations[name])

    if options.fatesanity:
        for name, loc_id in location_table_prophecies.items():
            _add_location(regions["Crossroads"], name, loc_id)

    # Tool unlocks at Schelmy's shop, gated by toolsanity
    if options.toolsanity:
        for name, loc_id in location_tools.items():
            _add_location(regions["Crossroads"], name, loc_id)

    # Familiar recruits go in the biome where each wild familiar appears.
    if options.familiarsanity:
        for region_name, table in location_familiars_by_region.items():
            for name, loc_id in table.items():
                _add_location(regions[region_name], name, loc_id)

    # Wire up connections
    for source, targets in _region_connections.items():
        for target in targets:
            entrance = Entrance(player, f"{source} -> {target}", regions[source])
            entrance.connect(regions[target])
            regions[source].exits.append(entrance)

    multiworld.regions += list(regions.values())
    return regions
