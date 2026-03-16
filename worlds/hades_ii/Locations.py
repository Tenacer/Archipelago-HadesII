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

# Finished
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

# Finished
weapon_checks = keepsake_checks + 33
location_weapons = {
    "Staff Weapon Unlock Location": weapon_checks + 1,
    "Daggers Weapon Unlock Location": weapon_checks + 2,
    "Torches Weapon Unlock Location": weapon_checks + 3,
    "Axe Weapon Unlock Location": weapon_checks + 4,
    "Skull Weapon Unlock Location": weapon_checks + 5,
    "Coat weapon Unlock Location": weapon_checks +6
}

# Finished
tool_checks = weapon_checks + 6
location_tools = {
    "Crescent Pickaxe Tool Unlock Location": tool_checks + 1,
    "Silver Spade Tool Unlock Location": tool_checks + 2,
    "Tablet of Peace Tool Unlock Location": tool_checks + 3,
    "Rod of Fishing Tool Unlock Location": tool_checks + 4,
}

# Finished (ouch my wrists)
prophecies_checks = tool_checks + 4
location_table_prophecies = {
    "Melinoë, Help Us Check":  prophecies_checks + 1,
    "Melinoë, Remember Us Check": prophecies_checks + 2,
    "Melinoë, Seek Us Check": prophecies_checks + 3,
    "Melinoë, Find Us Check":  prophecies_checks + 4,
    "Storm in the Heavens Check": prophecies_checks + 5,
    "Temporary Setback Check": prophecies_checks + 6,
    "Harbinger of Doom Check": prophecies_checks + 7,
    "Witch of the Crossroads Check": prophecies_checks + 8,
    "Natural Talent Check": prophecies_checks + 9, 
    "Sword of the Night Check": prophecies_checks + 10,
    "Arcana of the Ages Check": prophecies_checks + 11,
    "Unrivaled Prowess Check": prophecies_checks + 12,
    "Bearing Dark Gifts Check": prophecies_checks + 13,
    "Den Mother Check": prophecies_checks + 14, 
    "Family in Need Check": prophecies_checks + 15, 
    "Visions of Victory Check": prophecies_checks + 16, 
    "Unfinished Business Check": prophecies_checks + 17, 
    "Haunted by the Past Check": prophecies_checks + 18, 
    "Silk and Spitefulness Check": prophecies_checks + 19,
    "Voice and Vanity Check": prophecies_checks + 20,
    "Bitter Tears Check": prophecies_checks + 21,
    "Drowned Ambitions Check": prophecies_checks + 22,
    "The Jackal's Aspect Check": prophecies_checks + 23, 
    "The Crow's Aspect Check": prophecies_checks + 24,
    "The Shadow's Aspect Check": prophecies_checks + 25,
    "The Warrior's Aspect Check": prophecies_checks + 26,
    "The Grave's Aspect Check": prophecies_checks + 27,
    "The Destroyer's Aspect Check": prophecies_checks + 28,
    "Nobody but Nobody Check": prophecies_checks + 29,
    "Born to Win Check": prophecies_checks + 30,
    "Improbable Outcomes Check": prophecies_checks + 31,
    "Soundest of Slumbers Check": prophecies_checks + 32,
    "Customary Gift Check": prophecies_checks + 33,
    "Mindful Craft Check": prophecies_checks + 34,
    "Blades of Pure Silver Check": prophecies_checks + 35,
    "The Arms of Night Check": prophecies_checks + 36,
    "The Unseen Sentinel Check": prophecies_checks + 37,
    "Awakened Aspect Check": prophecies_checks + 38,
    "Major Arcana Check": prophecies_checks + 39,
    "Familiar Confidant Check": prophecies_checks + 40,
    "Note to Self Check": prophecies_checks + 41,
    "The Invoker Check": prophecies_checks + 42,
    "Whims of Chaos Check": prophecies_checks + 43,
    "Breadth of Knowledge Check": prophecies_checks + 44,
    "Weight in Gold Check": prophecies_checks + 45,
    "Valued Customer Check": prophecies_checks + 46,
    "Close Companions Check": prophecies_checks + 47,
    "Beyond Familiar Check": prophecies_checks + 48,
    "Denizen of the Depths Check": prophecies_checks + 49,
    "Keeper of Shadows Check": prophecies_checks + 50,
    "Tools of the Unseen Check": prophecies_checks + 51,
    "Precision Instrument Check": prophecies_checks + 52,
    "Home in the Crossroads Check": prophecies_checks + 53,
    "Spectral Forms Check": prophecies_checks + 54,
    "Shadow of Death Check": prophecies_checks + 55,
    "Shadow of Doom Check": prophecies_checks + 56,
    "Gifts of the Moon Check": prophecies_checks + 57,
    "Godsent Favor Check": prophecies_checks + 58,
    "Master of the Dead Check": prophecies_checks + 59,
    "Master of the Heavens Check": prophecies_checks + 60,
    "Mistress of Wedlock Check": prophecies_checks + 61,
    "Master of the Sea Check": prophecies_checks + 62,
    "Mistress of Seasons Check": prophecies_checks + 63,
    "Master of Light Check": prophecies_checks + 64,
    "Mistress of Beauty Check": prophecies_checks + 65,
    "Master of the Forge Check": prophecies_checks + 66,
    "Mistress of the Hearth Check": prophecies_checks + 67,
    "Master of War Check": prophecies_checks + 68,
    "Mistress of the Hunt Check": prophecies_checks + 69, 
    "Master of Swiftness Check": prophecies_checks + 70,
    "Mistress of Battle Check": prophecies_checks + 71,
    "Master of Revelry Check": prophecies_checks + 72,
    "Original Sins Check": prophecies_checks + 73,
    "Original Virtues Check": prophecies_checks + 74,
    "Power Beyond Legend Check": prophecies_checks + 75,
    "Combined Might Check": prophecies_checks + 76,
    "Weaver of Fineries Check": prophecies_checks + 77,
    "Denier of Suitors Check": prophecies_checks + 78,
    "Voice of Truth Check": prophecies_checks + 79,
    "Witch of Shadows Check": prophecies_checks + 80,
    "Witch of Changing Check": prophecies_checks + 81,
    "Wings of Freedom Check": prophecies_checks + 82,
    "Bared Fangs Check": prophecies_checks + 83,
    "The Witch's Staff Check": prophecies_checks + 84,
    "The Sister Blades Check": prophecies_checks + 85,
    "The Umbral Flames Check": prophecies_checks + 86,
    "The Moonstone Axe Check": prophecies_checks + 87,
    "The Argent Skull Check": prophecies_checks + 88,
    "The Black Coat Check": prophecies_checks + 89
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
    }

def setup_location_table_with_settings(options):
    total_table = {}
    
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