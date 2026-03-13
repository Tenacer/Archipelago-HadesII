from BaseClasses import Location

# 2500 is arbitrary here, we'll find a more accurate amount later
hades_ii_base_location_id = 1
max_number_room_checks = 2500 + hades_ii_base_location_id

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

keepsake_checks = max_number_room_checks
location_keepsakes = {    
    "Hecate Keepsake": keepsake_checks + 1,
    "Odysseus Keepsake": keepsake_checks + 2,
    "Schelemeus Keepsake": keepsake_checks + 3,
    "Dora Keepsake": keepsake_checks + 4,
    "Nemisis Keepsake": keepsake_checks + 5,
    "Moros Keepsake": keepsake_checks + 6,
    "Eris Keepsake": keepsake_checks + 7,
    "Charon Keepsake": keepsake_checks + 8,
    "Hermes Keepsake": keepsake_checks + 9,
    "Artemis Keepsake": keepsake_checks + 10,
    "Selene Keepsake": keepsake_checks + 11,
    
    "Zeus Keepsake": keepsake_checks + 12,
    "Hera Keepsake": keepsake_checks + 13,
    "Poseidon Keepsake": keepsake_checks + 14,
    "Demeter Keepsake": keepsake_checks + 15,
    "Apollo Keepsake": keepsake_checks +16,
    "Aphrodite Keepsake": keepsake_checks + 17,
    "Hephaestus Keepsake": keepsake_checks + 18,
    "Hestia Keepsake": keepsake_checks + 19,
    "Ares Keepsake": keepsake_checks + 20,
    "Athena Keepsake": keepsake_checks + 21,
    "Dionysus Keepsake": keepsake_checks + 22,
    
    "Arachne Keepsake": keepsake_checks + 23,
    "Narcissus Keepsake": keepsake_checks + 24,
    "Echo Keepsake": keepsake_checks + 25,
    "Heracles Keepsake": keepsake_checks + 26,
    "Medea Keepsake": keepsake_checks + 27,
    "Circe Keepsake": keepsake_checks + 28,
    "Icarus Keepsake": keepsake_checks + 29,
    
    "Hades/Persephone Keepsake": keepsake_checks + 30,
    "Zagreus Keepsake": keepsake_checks + 31,
    "Chronos Keepsake": keepsake_checks + 32,
    
    "Chaos Keepsake": keepsake_checks + 33,
}

weapon_checks = keepsake_checks + 33
location_weapons = {
    "Staff Weapon Unlock Location": weapon_checks + 1,
    "Daggers Weapon Unlock Location": weapon_checks + 2,
    "Torches Weapon Unlock Location": weapon_checks + 3,
    "Axe Weapon Unlock Location": weapon_checks + 4,
    "Skull Weapon Unlock Location": weapon_checks + 5,
    "Coat weapon Unlock Location": weapon_checks +6
}

tool_checks = weapon_checks + 6
location_tools = {
    "Crescent Pickaxe Tool Unlock Location": tool_checks + 1,
    "Silver Spade Tool Unlock Location": tool_checks + 2,
    "Tablet of Peace Tool Unlock Location": tool_checks + 3,
    "Rod of Fishing Tool Unlock Location": tool_checks + 4,
}

prophecies_checks = tool_checks + 4
location_table_prophecies = {
    "Witch of the Crossroads Prophecy":  prophecies_checks + 1,
    "Last prophecy": prophecies_checks + 133
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