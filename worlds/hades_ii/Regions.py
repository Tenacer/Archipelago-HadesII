from BaseClasses import Region, Entrance, Location
from .Locations import location_table_crossroads, location_table_erebus, location_table_oceanus, \
    location_table_fields, location_table_tartarus, location_table_ephyra, location_table_thessaly, \
    location_table_olympus, location_table_summit
from .Options import HadesIIOptions

options: HadesIIOptions

from BaseClasses import Region, Entrance, Location

region_connections = {
    "Crossroads": ["Erebus", "Ephyra"],

    "Erebus": ["Oceanus"],
    "Oceanus": ["Fields"],
    "Fields": ["Tartarus"],

    "Ephyra": ["Thessaly"],
    "Thessaly": ["Olympus"],
    "Olympus": ["Summit"]
}

region_locations = {
    "Erebus": location_table_erebus,
    "Oceanus": location_table_oceanus,
    "Fields": location_table_fields,
    "Tartarus": location_table_tartarus,

    "Ephyra": location_table_ephyra,
    "Thessaly": location_table_thessaly,
    "Olympus": location_table_olympus,
    "Summit": location_table_summit,

    "Crossroads": location_table_crossroads,
}

def create_regions(player, multiworld, location_database):

    regions = {}

    # Create region objects
    for region_name in region_locations.keys():
        regions[region_name] = Region(region_name, player, multiworld)

    # Add locations
    for region_name, location_table in region_locations.items():
        region = regions[region_name]

        for loc_name in location_table:
            region.locations.append(
                Location(player, loc_name, location_database[loc_name], region)
            )

    # Create connections
    for source, targets in region_connections.items():
        for target in targets:
            entrance = Entrance(player, f"{source} -> {target}", regions[source])
            entrance.connect(regions[target])
            regions[source].exits.append(entrance)

    multiworld.regions += list(regions.values())

    return regions