from typing import Dict, List
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components
from .Options import HadesIIOptions
from .Locations import give_all_locations_table, location_name_groups, setup_location_table_with_settings
from .Regions import create_regions
from .Items import item_table, item_name_groups, create_items, Hades_II_Item
from .Rules import set_rules

# Shrine point costs per rank for each vow (index 0 = cost of rank 1, etc.)
_VOW_POINT_COSTS: Dict[str, List[int]] = {
    "EnemyDamageShrineUpgrade":     [1, 2, 2],
    "EnemyHealthShrineUpgrade":     [1, 1, 1],
    "EnemyShieldShrineUpgrade":     [1, 1],
    "EnemySpeedShrineUpgrade":      [3, 3],
    "EnemyCountShrineUpgrade":      [1, 1, 1],
    "NextBiomeEnemyShrineUpgrade":  [1, 2],
    "EnemyRespawnShrineUpgrade":    [1, 1],
    "EnemyEliteShrineUpgrade":      [2, 3],
    "HealingReductionShrineUpgrade":[1, 1, 2],
    "ShopPricesShrineUpgrade":      [1, 1],
    "MinibossCountShrineUpgrade":   [2],
    "BoonSkipShrineUpgrade":        [3],
    "BiomeSpeedShrineUpgrade":      [1, 2, 3],
    "LimitGraspShrineUpgrade":      [1, 1, 1, 2],
    "BoonManaReserveShrineUpgrade": [1, 1],
    "BanUnpickedBoonsShrineUpgrade":[2],
    "BossDifficultyShrineUpgrade":  [2, 3, 3, 4],
}


def _launch_client(*args):
    from .HadesIIClient import launch
    launch()


components.append(Component(
    "Hades II Client",
    func=_launch_client,
    component_type=Type.CLIENT,
))


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

    def _compute_vow_ranks(self, total_points: int) -> Dict[str, int]:
        """Randomly distribute total_points shrine points across vows using self.random."""
        ranks: Dict[str, int] = {name: 0 for name in _VOW_POINT_COSTS}
        remaining = total_points
        while remaining > 0:
            affordable = [
                name for name, costs in _VOW_POINT_COSTS.items()
                if ranks[name] < len(costs) and costs[ranks[name]] <= remaining
            ]
            if not affordable:
                break
            chosen = self.random.choice(affordable)
            remaining -= _VOW_POINT_COSTS[chosen][ranks[chosen]]
            ranks[chosen] += 1
        return {name: rank for name, rank in ranks.items() if rank > 0}

    def generate_early(self) -> None:
        self.vow_ranks: Dict[str, int] = {}
        fear = self.options.fear_system.value
        if fear == 1:
            self.vow_ranks = self._compute_vow_ranks(self.options.initial_fear_level.value)
        elif fear == 2:
            self.vow_ranks = self._compute_vow_ranks(self.options.minimal_fear_level.value)

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
        slot_data = self.options.as_dict(
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
            # Fear system mode
            "fear_system",
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
        # vow_ranks: shrine_upgrade_name -> rank (only non-zero entries).
        # Lua mod applies these as starting/locked levels (reverse_Fear) or floor (minimal_Fear).
        slot_data["vow_ranks"] = self.vow_ranks
        return slot_data
