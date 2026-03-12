from BaseClasses import Location

#TODO: Figure out why it's done this way, why specifically 1700 in H1?
hades_ii_base_location_id = 1
max_number_room_checks = 1700 + hades_ii_base_location_id

location_table_crossroads = {}

location_table_erebus = {
    "Hecate Victory": None
}

location_table_oceanus = {
    "Scylla Victory": None
}

location_table_fields = {
    "Cerberus Victory": None
}

location_table_tartarus = {
    "Chronos Victory": None
}

location_table_ephyra = {
    "Polyphemus Victory": None
}

location_table_thessaly = {
    "Eris Victory": None
}

location_table_olympus = {
    "Prometheus Victory": None
}

location_table_summit = {
    "Typhon Victory": None
}

location_keepsakes = {    
    "Hecate Keepsake": max_number_room_checks + 1,
    "Odysseus Keepsake": max_number_room_checks + 2,
    "Schelemeus Keepsake": max_number_room_checks + 3,
    "Dora Keepsake": max_number_room_checks + 4,
    "Nemisis Keepsake": max_number_room_checks + 5,
    "Moros Keepsake": max_number_room_checks + 6,
    "Eris Keepsake": max_number_room_checks + 7,
    "Charon Keepsake": max_number_room_checks + 8,
    "Hermes Keepsake": max_number_room_checks + 9,
    "Artemis Keepsake": max_number_room_checks + 10,
    "Selene Keepsake": max_number_room_checks + 11,
    
    "Zeus Keepsake": max_number_room_checks + 12,
    "Hera Keepsake": max_number_room_checks + 13,
    "Poseidon Keepsake": max_number_room_checks + 14,
    "Demeter Keepsake": max_number_room_checks + 15,
    "Apollo Keepsake": max_number_room_checks +16,
    "Aphrodite Keepsake": max_number_room_checks + 17,
    "Hephaestus Keepsake": max_number_room_checks + 18,
    "Hestia Keepsake": max_number_room_checks + 19,
    "Ares Keepsake": max_number_room_checks + 20,
    "Athena Keepsake": max_number_room_checks + 21,
    "Dionysus Keepsake": max_number_room_checks + 22,
    
    "Arachne Keepsake": max_number_room_checks + 23,
    "Narcissus Keepsake": max_number_room_checks + 24,
    "Echo Keepsake": max_number_room_checks + 25,
    "Heracles Keepsake": max_number_room_checks + 26,
    "Medea Keepsake": max_number_room_checks + 27,
    "Circe Keepsake": max_number_room_checks + 28,
    "Icarus Keepsake": max_number_room_checks + 29,
    
    "Hades/Persephone Keepsake": max_number_room_checks + 30,
    "Zagreus Keepsake": max_number_room_checks + 31,
    "Chronos Keepsake": max_number_room_checks + 32,
    
    "Chaos Keepsake": max_number_room_checks + 33,
}

location_weapons = {
    "Staff Weapon Unlock Location": max_number_room_checks + 34,
    "Coat weapon Unlock Location": max_number_room_checks + 39
}

location_tools = {
    "Shovel Tool Unlock Location": max_number_room_checks + 40,
    "Last Tool Unlock Location": max_number_room_checks + 44
}

location_table_prophecies = {
    "Witch of the Crossroads Prophecy":  max_number_room_checks + 45,
    "Last prophecy": max_number_room_checks + 133
}

location_table_prophecies_events = {
    "Witch of the Crossroads Event": None,
    "Last prophecy": None
}

group_keepsakes = {"keepsakes": location_keepsakes.keys()}
group_weapons = {"weapons": location_weapons.keys()}
group_tools = {"tools": location_tools.keys()}
group_prophecies = {"prophecies": location_table_prophecies.keys()}

location_name_groups = {
    **group_keepsakes,
    **group_weapons,
    **group_tools,
    **group_prophecies,
}

def give_all_locations_table() -> dict:
    return {
        **location_keepsakes,
        **location_weapons,
        **location_tools,
        **location_table_prophecies,
        **location_table_prophecies_events,
    }

def setup_location_table_with_settings(options):
    total_table = {}
 
    total_table.update(location_table_prophecies_events)
    
    if options.keepsakesanity.value == 1:
        total_table.update(location_keepsakes)
     
    if options.weaponsanity.value == 1:
        for weaponLocation, weaponData in location_weapons.items():
            if not should_ignore_weapon_location(weaponLocation, options):
                total_table.update({weaponLocation: weaponData})
    
    if options.fatesanity == 1:
        total_table.update(location_table_prophecies)
    
    return total_table

def should_ignore_weapon_location(weaponLocation : str, options):
    if options.initial_weapon.value == 0 and weaponLocation == "Staff Weapon Unlock Location":
        return True
    if options.initial_weapon.value == 1 and weaponLocation == "Daggers Weapon Unlock Location":
        return True
    if options.initial_weapon.value == 2 and weaponLocation == "Torch Weapon Unlock Location":
        return True
    if options.initial_weapon.value == 3 and weaponLocation == "Axe Weapon Unlock Location":
        return True
    if options.initial_weapon.value == 4 and weaponLocation == "Skull Weapon Unlock Location":
        return True
    if options.initial_weapon.value == 5 and weaponLocation == "Coat Weapon Unlock Location":
        return True
    return False


class HadesIILocation(Location):
    game: str = "Hades II"

    def __init__(self, player: int, name: str, address=None, parent=None):
        super(HadesIILocation, self).__init__(player, name, address, parent)
        if address is None:
            self.event = True
            self.locked = True