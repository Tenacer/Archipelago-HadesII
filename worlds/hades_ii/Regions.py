from BaseClasses import Region, Entrance
from .Locations import (
    HadesIILocation,
    SURFACE_LOCK_LOCATIONS,
    location_table_score_checks,
    score_check_split,
    location_table_boss_rewards,
    location_keepsakes,
    location_weapons,
    location_weapon_clears,
    location_hidden_aspects,
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
)

# Biome → (event location table, boss reward base name or None).
# When base name is set, per-kill rewards "<base> N" are emitted up to the
# matching option count (chronos_kills_needed / typhon_kills_needed) in True
# Ending mode only.
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

    # Score checks — only populated under the score_based location system and
    # limited to the first N per ScoreRewardsAmount.
    # Combined split mode: all live in Menu (always accessible — any route can
    #   earn every check).
    # Separate split mode: the underworld route can only earn its budget share
    #   and the surface route only earns the rest, so the checks are placed in
    #   the region whose access they actually require — the first
    #   `underworld_budget` in Erebus (reachable from start), the remaining
    #   surface ones in Ephyra (gated by the Crossroads -> Ephyra surface rule).
    #   This keeps multiworld fill from treating surface checks as reachable
    #   before surface access is unlocked.
    # Progress types are set later in set_rules once the item pool is known.
    if options.location_system == "score_based":
        n = options.score_rewards_amount.value
        if options.score_split_mode == 1:  # separate
            underworld_budget, _ = score_check_split(n, options.surface_score_ratio.value)
            for i in range(1, n + 1):
                name = f"Score Check {i}"
                region = regions["Erebus"] if i <= underworld_budget else regions["Ephyra"]
                _add_location(region, name, location_table_score_checks[name])
        else:  # combined
            for i in range(1, n + 1):
                name = f"Score Check {i}"
                _add_location(regions["Menu"], name, location_table_score_checks[name])

    # Biome victory events + boss reward checks.
    # `Chronos True Victory` is the True-Ending-only sentinel — the second Chronos
    # kill performed after Dissolution of Time. Skip it unless the goal needs it.
    # Boss rewards are only emitted in True Ending mode, up to the per-boss kill
    # count option (chronos_kills_needed / typhon_kills_needed).
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

    # Cauldronsanity owns the 86 non-surface incantation locations.
    # `Rivals of Old and Rot` is excluded under true_ending — vanilla T4
    # requires `ReachedTrueEnding` (post-goal). Mirror in Items.create_items
    # and Locations.setup_location_table_with_settings.
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

    # Lock-surface toggle owns the two surface-unlock incantation locations,
    # independent of cauldronsanity.
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

    # Familiar recruits, gated by familiarsanity — placed in the biome where each
    # wild familiar appears (Frinos in the Crossroads hub). Access rules are set in
    # Rules.handle_familiars; biome reachability is enforced by region connectivity.
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
