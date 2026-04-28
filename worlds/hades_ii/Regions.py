from BaseClasses import Region, Entrance
from .Locations import (
    HadesIILocation,
    location_table_score_checks,
    location_table_boss_rewards,
    location_keepsakes,
    location_weapons,
    location_hidden_aspects,
    location_tools,
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
)

# Biome → (event location table, boss reward location name or None)
_biome_data = {
    "Erebus":    (location_table_erebus,   None),
    "Oceanus":   (location_table_oceanus,  None),
    "Fields":    (location_table_fields,   None),
    "Tartarus":  (location_table_tartarus, "Chronos Kill Reward"),
    "Ephyra":    (location_table_ephyra,   None),
    "Thessaly":  (location_table_thessaly, None),
    "Olympus":   (location_table_olympus,  None),
    "Summit":    (location_table_summit,   "Typhon Kill Reward"),
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

    # Score checks — live in Menu, only populated under score_based location
    # system and limited to the first N per ScoreRewardsAmount.
    # Progress types are set later in set_rules once the item pool is known.
    if options.location_system == "score_based":
        for i in range(1, options.score_rewards_amount.value + 1):
            name = f"Score Check {i}"
            _add_location(regions["Menu"], name, location_table_score_checks[name])

    # Biome victory events + boss reward checks
    # `Chronos True Victory` is the True-Ending-only sentinel — the second Chronos
    # kill performed after Dissolution of Time. Skip it unless the goal needs it.
    for region_name, (event_table, boss_reward_name) in _biome_data.items():
        region = regions[region_name]
        for event_name in event_table:
            if event_name == "Chronos True Victory" and not options.true_ending:
                continue
            _add_location(region, event_name, None)  # event — address is None
        if boss_reward_name:
            _add_location(region, boss_reward_name, location_table_boss_rewards[boss_reward_name])

    # Option-gated locations
    if options.keepsakesanity:
        for name, loc_id in location_keepsakes.items():
            _add_location(regions["Crossroads"], name, loc_id)

    if options.weaponsanity:
        for name, loc_id in location_weapons.items():
            if not should_ignore_weapon_location(name, options):
                _add_location(regions["Crossroads"], name, loc_id)

    if options.hidden_aspectsanity:
        for name, loc_id in location_hidden_aspects.items():
            _add_location(regions["Crossroads"], name, loc_id)

    if options.cauldronsanity:
        for name, loc_id in location_incantations.items():
            _add_location(regions["Crossroads"], name, loc_id)

    if options.fatesanity:
        for name, loc_id in location_table_prophecies.items():
            _add_location(regions["Crossroads"], name, loc_id)

    # Tools are always available at the shop
    for name, loc_id in location_tools.items():
        _add_location(regions["Crossroads"], name, loc_id)

    # Wire up connections
    for source, targets in _region_connections.items():
        for target in targets:
            entrance = Entrance(player, f"{source} -> {target}", regions[source])
            entrance.connect(regions[target])
            regions[source].exits.append(entrance)

    multiworld.regions += list(regions.values())
    return regions
