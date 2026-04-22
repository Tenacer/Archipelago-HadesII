from worlds.AutoWorld import World
from .Options import HadesIIOptions
from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings
from .Regions import create_regions
from .Items import item_table, item_name_groups, create_items, Hades_II_Item
from .Rules import set_rules


class HadesIIWorld(World):
    """Hades II Archipelago implementation."""

    game: str = "Hades II"
    options_dataclass = HadesIIOptions
    topology_present: bool = False
    required_client_version: tuple = (0, 6, 4)

    item_name_to_id = {name: data.code for name, data in item_table.items() if data.code is not None}
    location_name_to_id = give_all_locations_table()

    item_name_groups = {name: set(group) for name, group in item_name_groups.items()}
    location_name_groups = {name: set(group) for name, group in location_name_groups.items()}

    def create_regions(self):
        create_regions(self.player, self.multiworld, self.location_name_to_id, self.options)

    def create_item(self, name: str):
        return Hades_II_Item(name, self.player)

    def create_items(self):
        create_items(self)

    def set_rules(self):
        local_location_table = setup_location_table_with_settings(self.options).copy()
        set_rules(self.multiworld, self.player, local_location_table, self.options)

    def fill_slot_data(self) -> dict:
        # Everything the Lua mod needs to know about the seed.
        # Excludes start_inventory_from_pool (AP core handles it) and the
        # *_percentage / filler_trap_percentage options (generation-time only —
        # they shape the pool, they don't influence runtime behaviour).
        return self.options.as_dict(
            # Gameplay
            "initial_weapon",
            "location_system",
            "score_rewards_amount",
            # Sanities
            "keepsakesanity",
            "weaponsanity",
            "hidden_aspectsanity",
            "cauldronsanity",
            "fatesanity",
            # Goal configuration
            "true_ending",
            "zodiac_sand_needed",
            "void_lens_needed",
            "boss_defeats_needed",
            "weapons_clears_needed",
            "keepsakes_needed",
            "fates_needed",
            # Fear system
            "fear_system",
            "pain_vow_amount",
            "grit_vow_amount",
            "wards_vow_amount",
            "frenzy_vow_amount",
            "hordes_vow_amount",
            "menace_vow_amount",
            "return_vow_amount",
            "fangs_vow_amount",
            "scars_vow_amount",
            "debt_vow_amount",
            "shadow_vow_amount",
            "forfeit_vow_amount",
            "time_vow_amount",
            "void_vow_amount",
            "hubris_vow_amount",
            "denial_vow_amount",
            "rivals_vow_amount",
            # Filler pack sizes (how much resource each pack grants when received)
            "ash_pack_value",
            "bones_pack_value",
            "psyche_pack_value",
            "nectar_pack_value",
            "ambrosia_pack_value",
            "nightmare_pack_value",
            "moon_dust_pack_value",
            "fate_fabric_pack_value",
            # Quality of life
            "reverse_order_rivals",
            "ignore_win_deaths",
            "cauldron_give_hints",
            "death_link",
            "death_link_amnesty",
        )
