from BaseClasses import Item, ItemClassification, LocationProgressType
from .bases import HadesIITestBase
from ..Options import hades_ii_option_presets


def _assert_score_checks_block_progression(test_case) -> None:
    """Score checks must reject progression items via their per-location item rule.

    Verifies the rule directly (no fill required) so the test is independent
    of fill order or RNG. EXCLUDED marking is intentionally NOT used.
    """
    fake_progression = Item("test", ItemClassification.progression, None, test_case.player)
    fake_filler = Item("test", ItemClassification.filler, None, test_case.player)
    score_locs = [
        loc for loc in test_case.multiworld.get_locations(test_case.player)
        if loc.name.startswith(("Score Check ", "Underworld Score Check ", "Surface Score Check "))
    ]
    test_case.assertGreater(len(score_locs), 0, "no score checks found")
    for loc in score_locs:
        test_case.assertNotEqual(loc.progress_type, LocationProgressType.EXCLUDED,
            f"{loc.name} must not be EXCLUDED — rely on item rule instead")
        test_case.assertFalse(loc.item_rule(fake_progression),
            f"{loc.name} should reject progression items")
        test_case.assertTrue(loc.item_rule(fake_filler),
            f"{loc.name} should accept filler items")


_WEAPON_CLEAR_NAMES = (
    "Staff Weapon Clear", "Daggers Weapon Clear", "Torches Weapon Clear",
    "Axe Weapon Clear", "Skull Weapon Clear", "Coat Weapon Clear",
)


class TestDefaultGeneration(HadesIITestBase):
    """Default options: True Ending goal at Normal difficulty (the bare defaults
    mirror the recommended 'True Ending Normal' preset), score_based system,
    default sanities, normal fear."""
    options = {}

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)

    def test_weapon_clears_present_and_filler_only(self) -> None:
        # Weaponsanity is on by default: the 6 per-weapon "<W> Clear" checks
        # exist, are gated (have an access rule), and reject progression items.
        fake_progression = Item("test", ItemClassification.progression, None, self.player)
        fake_filler = Item("test", ItemClassification.filler, None, self.player)
        for name in _WEAPON_CLEAR_NAMES:
            loc = self.multiworld.get_location(name, self.player)
            self.assertIsNotNone(loc.access_rule, f"{name} must have an access rule")
            self.assertFalse(loc.item_rule(fake_progression),
                f"{name} should reject progression items")
            self.assertTrue(loc.item_rule(fake_filler),
                f"{name} should accept filler items")

    def test_boss_rewards_present_by_default(self) -> None:
        # True Ending is the default goal: per-kill reward locations exist up to
        # chronos_kills_needed (7) and typhon_kills_needed (5).
        for name in ("Chronos Kill Reward 1", "Chronos Kill Reward 7",
                     "Typhon Kill Reward 1", "Typhon Kill Reward 5"):
            self.assertIsNotNone(self.multiworld.get_location(name, self.player))


class TestBossDefeatsHasNoBossRewards(HadesIITestBase):
    """BossDefeats goal counts run completions — no per-kill reward locations."""
    options = {"true_ending": 0}

    def test_no_boss_rewards(self) -> None:
        for name in ("Chronos Kill Reward 1", "Typhon Kill Reward 1"):
            self.assertRaises(KeyError, self.multiworld.get_location, name, self.player)


def _count_items(test_case, name: str) -> int:
    return sum(1 for i in test_case.multiworld.itempool
               if i.player == test_case.player and i.name == name)


class TestTrueEnding(HadesIITestBase):
    options = {"true_ending": 1}

    def test_true_ending_event_exists(self) -> None:
        loc = self.multiworld.get_location("Chronos True Victory", self.player)
        self.assertIsNotNone(loc)

    def test_boss_rewards_not_excluded(self) -> None:
        for name in ("Chronos Kill Reward 1", "Typhon Kill Reward 1"):
            loc = self.multiworld.get_location(name, self.player)
            self.assertNotEqual(loc.progress_type, LocationProgressType.EXCLUDED)

    def test_per_boss_reward_counts_default(self) -> None:
        # Defaults: 7 Chronos rewards, 5 Typhon rewards.
        chronos = [loc for loc in self.multiworld.get_locations(self.player)
                   if loc.name.startswith("Chronos Kill Reward ")]
        typhon = [loc for loc in self.multiworld.get_locations(self.player)
                  if loc.name.startswith("Typhon Kill Reward ")]
        self.assertEqual(len(chronos), 7)
        self.assertEqual(len(typhon), 5)

    def test_pool_size_matches_kills_needed_default(self) -> None:
        # Defaults: chronos_kills_needed=7 → 7 Zodiac Sand; typhon_kills_needed=5 → 5 Void Lens.
        # Pool count is decoupled from zodiac_sand_needed (4) / void_lens_needed (2);
        # extras are the slack the player can spend on Arcana upgrades.
        self.assertEqual(_count_items(self, "Zodiac Sand"), 7)
        self.assertEqual(_count_items(self, "Void Lens"), 5)


class TestTrueEndingCustomKillCounts(HadesIITestBase):
    options = {
        "true_ending": 1,
        "chronos_kills_needed": 3,
        "typhon_kills_needed": 2,
        "zodiac_sand_needed": 3,
        "void_lens_needed": 2,
    }

    def test_kill_counts_honored(self) -> None:
        chronos = [loc for loc in self.multiworld.get_locations(self.player)
                   if loc.name.startswith("Chronos Kill Reward ")]
        typhon = [loc for loc in self.multiworld.get_locations(self.player)
                  if loc.name.startswith("Typhon Kill Reward ")]
        self.assertEqual(len(chronos), 3)
        self.assertEqual(len(typhon), 2)

    def test_pool_size_matches_custom_kill_counts(self) -> None:
        # Pool tracks kills_needed, not the threshold.
        self.assertEqual(_count_items(self, "Zodiac Sand"), 3)
        self.assertEqual(_count_items(self, "Void Lens"), 2)


class TestTrueEndingThresholdEqualsKills(HadesIITestBase):
    """Threshold == kills_needed is the boundary case: validation must allow it
    and the player must collect every Z-Sand / V-Lens in the pool to win."""
    options = {
        "true_ending": 1,
        "chronos_kills_needed": 4,
        "typhon_kills_needed": 4,
        "zodiac_sand_needed": 4,
        "void_lens_needed": 4,
    }

    def test_pool_sizes_at_boundary(self) -> None:
        self.assertEqual(_count_items(self, "Zodiac Sand"), 4)
        self.assertEqual(_count_items(self, "Void Lens"), 4)


class TestTrueEndingThresholdTooHighChronos(HadesIITestBase):
    """zodiac_sand_needed > chronos_kills_needed must raise OptionError so the
    seed never generates an unwinnable goal."""
    auto_construct = False
    options = {
        "true_ending": 1,
        "chronos_kills_needed": 3,
        "zodiac_sand_needed": 5,
    }

    def test_raises_option_error(self) -> None:
        from Options import OptionError
        with self.assertRaises(OptionError):
            self.world_setup()


class TestTrueEndingThresholdTooHighTyphon(HadesIITestBase):
    """void_lens_needed > typhon_kills_needed must also raise."""
    auto_construct = False
    options = {
        "true_ending": 1,
        "typhon_kills_needed": 2,
        "void_lens_needed": 4,
    }

    def test_raises_option_error(self) -> None:
        from Options import OptionError
        with self.assertRaises(OptionError):
            self.world_setup()


class TestBossDefeatsModeHasNoSandOrLens(HadesIITestBase):
    """Regression: when true_ending is off, the pool must contain no Zodiac Sand
    or Void Lens regardless of chronos_kills_needed / typhon_kills_needed."""
    options = {"true_ending": 0, "chronos_kills_needed": 10, "typhon_kills_needed": 10}

    def test_no_sand_or_lens_in_pool(self) -> None:
        self.assertEqual(_count_items(self, "Zodiac Sand"), 0)
        self.assertEqual(_count_items(self, "Void Lens"), 0)


class TestTrueEndingAllSanities(HadesIITestBase):
    options = {
        "true_ending": 1,
        "keepsakesanity": 1,
        "weaponsanity": 1,
        "hidden_aspectsanity": 1,
        "familiarsanity": 1,
        "cauldronsanity": 1,
        "fatesanity": 1,
    }

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)


class TestAllSanitiesOff(HadesIITestBase):
    # true_ending off: with every sanity off there are no item locations beyond
    # the (progression-rejecting) score checks, so the True Ending default would
    # have nowhere to place its progression items. This class tests sanity-off
    # location absence under the simple BossDefeats goal.
    options = {
        "true_ending": 0,
        "keepsakesanity": 0,
        "weaponsanity": 0,
        "hidden_aspectsanity": 0,
        "familiarsanity": 0,
        "cauldronsanity": 0,
        "lock_surface_incantations": 0,
        "fatesanity": 0,
    }

    def test_no_weapon_clears_without_weaponsanity(self) -> None:
        for name in _WEAPON_CLEAR_NAMES:
            self.assertRaises(KeyError, self.multiworld.get_location, name, self.player)

    def test_no_familiar_locations_without_familiarsanity(self) -> None:
        for name in _FAMILIAR_LOCATION_NAMES:
            self.assertRaises(KeyError, self.multiworld.get_location, name, self.player)


_FAMILIAR_LOCATION_NAMES = (
    "Frinos Familiar Unlock Location",
    "Raki Familiar Unlock Location",
    "Toula Familiar Unlock Location",
    "Hecuba Familiar Unlock Location",
    "Gale Familiar Unlock Location",
)
_FAMILIAR_ITEM_NAMES = (
    "Frinos Familiar",
    "Raki Familiar",
    "Toula Familiar",
    "Hecuba Familiar",
    "Gale Familiar",
)


class TestFamiliarSanity(HadesIITestBase):
    """familiarsanity on: the five recruit locations and familiar items exist, and
    every recruit is gated behind the familiar-system unlock (post-Hecate)."""
    options = {"familiarsanity": 1, "toolsanity": 0, "cauldronsanity": 0}

    def test_familiar_locations_exist(self) -> None:
        for name in _FAMILIAR_LOCATION_NAMES:
            self.assertIsNotNone(self.multiworld.get_location(name, self.player))

    def test_familiar_items_in_pool(self) -> None:
        pool = {item.name for item in self.multiworld.itempool}
        for name in _FAMILIAR_ITEM_NAMES:
            self.assertIn(name, pool)

    def test_familiars_unreachable_before_hecate(self) -> None:
        # No items collected: the familiar-system unlock (post-Hecate) is missing,
        # so none of the recruit locations are reachable.
        for name in _FAMILIAR_LOCATION_NAMES:
            self.assertFalse(self.can_reach_location(name))


_SURFACE_LOCK_NAMES = ("Permeation of Witching-Wards", "Unraveling a Fateful Bond")


class TestLockSurfaceIncantationsDefault(HadesIITestBase):
    """lock_surface_incantations on, cauldronsanity off — the two surface
    incantations are AP items + locations and nothing else."""
    options = {"lock_surface_incantations": 1, "cauldronsanity": 0}

    def test_surface_items_are_progression(self) -> None:
        for name in _SURFACE_LOCK_NAMES:
            matching = [i for i in self.multiworld.itempool
                        if i.name == name and i.player == self.player]
            self.assertEqual(len(matching), 1,
                f"Expected exactly one {name!r} in the pool, got {len(matching)}")
            self.assertTrue(matching[0].advancement,
                f"{name!r} must be progression so _has_surface_* predicates see it")

    def test_surface_locations_exist(self) -> None:
        for name in _SURFACE_LOCK_NAMES:
            loc = self.multiworld.get_location(name, self.player)
            self.assertIsNotNone(loc)

    def test_other_incantations_absent(self) -> None:
        from worlds.hades_ii.Items import item_table_incantations
        cauldron_names = {n for n in item_table_incantations
                          if n not in _SURFACE_LOCK_NAMES}
        present = {i.name for i in self.multiworld.itempool
                   if i.player == self.player and i.name in cauldron_names}
        self.assertEqual(present, set(),
            "Cauldronsanity is off — non-surface incantations must not be in the pool")


class TestLockSurfaceOffCauldronsanityOn(HadesIITestBase):
    """lock_surface_incantations off, cauldronsanity on — the surface 2 are NOT
    AP items/locations. The cauldronsanity pool covers every non-surface incantation."""
    # unlock_broker off so the Broker incantation stays in the cauldronsanity pool
    # (this test asserts full non-surface coverage). true_ending off so the
    # true-ending-excluded "Rivals of Old and Rot" stays in the pool.
    options = {"lock_surface_incantations": 0, "cauldronsanity": 1, "unlock_broker": 0,
               "true_ending": 0}

    def test_surface_items_absent(self) -> None:
        for name in _SURFACE_LOCK_NAMES:
            matching = [i for i in self.multiworld.itempool
                        if i.name == name and i.player == self.player]
            self.assertEqual(matching, [],
                f"{name!r} must not be in the pool when lock_surface_incantations is off")

    def test_surface_locations_absent(self) -> None:
        for name in _SURFACE_LOCK_NAMES:
            self.assertRaises(KeyError,
                self.multiworld.get_location, name, self.player)

    def test_cauldronsanity_covers_all_non_surface_incantations(self) -> None:
        from worlds.hades_ii.Items import item_table_incantations
        cauldron_names = {n for n in item_table_incantations
                          if n not in _SURFACE_LOCK_NAMES}
        present = {i.name for i in self.multiworld.itempool
                   if i.player == self.player and i.name in cauldron_names}
        self.assertEqual(present, cauldron_names,
            "Cauldronsanity should add every non-surface incantation to the pool")


class TestLockSurfaceAndCauldronsanity(HadesIITestBase):
    """Both options on — surface 2 owned by the lock toggle, the remaining
    non-surface incantations by cauldronsanity, surface keepsakes + surface
    biome + the 11 surface-gated cauldron incantations are gated on the
    surface unlock items."""
    options = {
        "lock_surface_incantations": 1,
        "cauldronsanity": 1,
        "keepsakesanity": 1,
        # unlock_broker off so every incantation location is present.
        "unlock_broker": 0,
        # true_ending off so "Rivals of Old and Rot" stays in the pool.
        "true_ending": 0,
    }

    def test_no_duplicate_surface_items(self) -> None:
        for name in _SURFACE_LOCK_NAMES:
            matching = [i for i in self.multiworld.itempool
                        if i.name == name and i.player == self.player]
            self.assertEqual(len(matching), 1,
                f"Expected exactly one {name!r}, got {len(matching)}")
            self.assertTrue(matching[0].advancement)

    def test_all_incantation_locations_present(self) -> None:
        from worlds.hades_ii.Locations import location_incantations
        for name in location_incantations:
            loc = self.multiworld.get_location(name, self.player)
            self.assertIsNotNone(loc)


_BROKER_INCANTATION = "Summoning of Mercantile Fortune"
# Incantations whose brewing requires the Broker (Summoning of Mercantile
# Fortune) as a chain prereq in Rules._INCANTATION_CHAIN_RULES.
_BROKER_DEPENDENTS = (
    "Deathly Fortune",
    "Kinship Fortune",
    "Earthly Fortune",
    "Long Arm of the Unseen",
    "Night's Craftwork",
)


class TestUnlockBroker(HadesIITestBase):
    """unlock_broker on (default) with cauldronsanity on: the Broker incantation
    is removed from the item + location pools, but the incantations that depend
    on it stay reachable because _has_incantation treats it as satisfied."""
    options = {"cauldronsanity": 1, "unlock_broker": 1}

    def test_market_item_absent(self) -> None:
        matching = [i for i in self.multiworld.itempool
                    if i.name == _BROKER_INCANTATION and i.player == self.player]
        self.assertEqual(matching, [],
            f"{_BROKER_INCANTATION!r} must not be in the pool when unlock_broker is on")

    def test_market_location_absent(self) -> None:
        self.assertRaises(KeyError,
            self.multiworld.get_location, _BROKER_INCANTATION, self.player)

    def test_dependent_locations_present(self) -> None:
        for name in _BROKER_DEPENDENTS:
            loc = self.multiworld.get_location(name, self.player)
            self.assertIsNotNone(loc)

    def test_dependent_locations_reachable(self) -> None:
        # all_state collects every pool item — but NOT the removed Broker
        # incantation. The dependents must still be reachable, which only holds
        # if _has_incantation treats Market as satisfied under unlock_broker.
        all_state = self.multiworld.get_all_state()
        for name in _BROKER_DEPENDENTS:
            loc = self.multiworld.get_location(name, self.player)
            self.assertTrue(loc.can_reach(all_state),
                f"{name} must be reachable with the Broker granted for free")


class TestUnlockBrokerOff(HadesIITestBase):
    """unlock_broker off with cauldronsanity on: the Broker incantation stays a
    normal AP item + location."""
    options = {"cauldronsanity": 1, "unlock_broker": 0}

    def test_market_item_present(self) -> None:
        matching = [i for i in self.multiworld.itempool
                    if i.name == _BROKER_INCANTATION and i.player == self.player]
        self.assertEqual(len(matching), 1,
            f"{_BROKER_INCANTATION!r} must be in the pool when unlock_broker is off")

    def test_market_location_present(self) -> None:
        loc = self.multiworld.get_location(_BROKER_INCANTATION, self.player)
        self.assertIsNotNone(loc)


class TestVanillaFear(HadesIITestBase):
    """fear_system=3 puts no vow items into the pool."""
    options = {"fear_system": 3}

    def test_no_vow_items_in_pool(self) -> None:
        vow_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player and "Vow of" in item.name
        ]
        self.assertEqual(len(vow_items), 0, "Vanilla fear should add no vow items")


class TestFatesanityWithGoal(HadesIITestBase):
    options = {"fatesanity": 1, "fates_needed": 10}

    def test_prophecy_items_are_progression(self) -> None:
        prophecy_items = [
            item for item in self.multiworld.itempool
            if item.player == self.player and item.game == "Hades II"
            and "Prophecy" in item.name or "Fate" in item.name
        ]
        # When fates_needed > 0, prophecy items should be promoted to progression
        from worlds.hades_ii.Items import item_table_prophecies
        for name in item_table_prophecies:
            matching = [i for i in self.multiworld.itempool if i.name == name and i.player == self.player]
            for item in matching:
                self.assertTrue(item.advancement,
                    f"Prophecy item {name!r} should be progression when fates_needed > 0")


class TestKeepsakeGoal(HadesIITestBase):
    options = {"keepsakesanity": 1, "keepsakes_needed": 10}

    def test_keepsake_items_are_progression(self) -> None:
        from worlds.hades_ii.Items import item_table_keepsakes
        for name in item_table_keepsakes:
            matching = [i for i in self.multiworld.itempool if i.name == name and i.player == self.player]
            for item in matching:
                self.assertTrue(item.advancement,
                    f"Keepsake {name!r} should be progression when keepsakes_needed > 0")


def _assert_count_goal_gated(test, item_names, needed: int) -> None:
    """Shared gate check for a count-based goal (keepsakes / fates).

    Starts from all-state (endgame reachable, every relevant item collected),
    zeroes the counted items, then re-adds them one at a time. The goal must
    stay unmet at `needed - 1` and flip to met at `needed`. Mutates prog_items
    directly (add_item / remove_item) — the count goals read prog_items via
    `state.count`, and that is also what the AP client mirrors at runtime, so
    a fresh `create_item` (which keeps the CSV `useful` class) is deliberately
    avoided here.
    """
    player = test.player
    completion = test.multiworld.completion_condition[player]
    state = test.multiworld.get_all_state(False)
    test.assertTrue(completion(state),
        "all-state (every relevant item collected) should meet the goal")

    names = list(item_names)
    for name in names:
        have = state.count(name, player)
        if have:
            state.remove_item(name, player, have)
    for name in names[: needed - 1]:
        state.add_item(name, player)
    test.assertFalse(completion(state),
        f"goal must NOT be met with {needed - 1} of the counted items")

    state.add_item(names[needed - 1], player)
    test.assertTrue(completion(state),
        f"goal must be met once {needed} counted items are collected")


class TestKeepsakesGateCompletion(HadesIITestBase):
    """The keepsakes_needed threshold must actually gate the goal."""
    options = {"keepsakesanity": 1, "keepsakes_needed": 5}

    def test_completion_requires_enough_keepsakes(self) -> None:
        from worlds.hades_ii.Items import item_table_keepsakes
        _assert_count_goal_gated(self, item_table_keepsakes, self.options["keepsakes_needed"])


class TestFatesGateCompletion(HadesIITestBase):
    """Same gating check as keepsakes, for fates_needed / prophecy items."""
    options = {"fatesanity": 1, "fates_needed": 5}

    def test_completion_requires_enough_fates(self) -> None:
        from worlds.hades_ii.Items import item_table_prophecies
        _assert_count_goal_gated(self, item_table_prophecies, self.options["fates_needed"])


class TestScoreRewards72(HadesIITestBase):
    """Minimum valid score_rewards_amount."""
    options = {"location_system": 0, "score_rewards_amount": 72}

    def test_score_check_count(self) -> None:
        # Default split mode is separate, so the pool is split across the two
        # route-named pools, but their counts still sum to score_rewards_amount.
        score_locs = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.name.startswith(("Score Check ", "Underworld Score Check ", "Surface Score Check "))
        ]
        self.assertEqual(len(score_locs), 72)

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)


class TestScoreRewardsMax(HadesIITestBase):
    options = {"location_system": 0, "score_rewards_amount": 150}

    def test_score_check_count(self) -> None:
        score_locs = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.name.startswith(("Score Check ", "Underworld Score Check ", "Surface Score Check "))
        ]
        self.assertEqual(len(score_locs), 150)

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)


_WEAPON_UNLOCK_LOCATIONS = [
    "Staff Weapon Unlock Location",
    "Daggers Weapon Unlock Location",
    "Torches Weapon Unlock Location",
    "Axe Weapon Unlock Location",
    "Skull Weapon Unlock Location",
    "Coat Weapon Unlock Location",
]


class TestRandomInitialWeapon(HadesIITestBase):
    options = {"initial_weapon": "random", "weaponsanity": 1}

    def test_random_resolves_to_concrete_weapon(self) -> None:
        self.assertIn(self.world.options.initial_weapon.value, range(0, 6))

    def test_starting_weapon_location_excluded(self) -> None:
        idx = self.world.options.initial_weapon.value
        location_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertNotIn(_WEAPON_UNLOCK_LOCATIONS[idx], location_names)
        for i, name in enumerate(_WEAPON_UNLOCK_LOCATIONS):
            if i != idx:
                self.assertIn(name, location_names)


# ── handle_X refactor coverage ──────────────────────────────────────────────
# The plan replaced handle_surface_{incantations,fates,keepsakes} with three
# unified handlers (handle_keepsakes, handle_incantations, handle_prophecies)
# and folded surface gating into each per-entry table.

class TestExpandedSurfaceKeepsakes(HadesIITestBase):
    """Every keepsake in `_KEEPSAKE_RULES_SURFACE_ACCESS` must be blocked
    when the player has no surface-unlock items. Data-driven so the test
    follows the tuple — adjust the tuple, not the test."""
    options = {"keepsakesanity": 1, "lock_surface_incantations": 1}

    def test_surface_keepsakes_require_surface_access(self) -> None:
        from worlds.hades_ii.Rules import _KEEPSAKE_RULES_SURFACE_ACCESS
        from BaseClasses import CollectionState
        for loc_name in _KEEPSAKE_RULES_SURFACE_ACCESS:
            loc = self.multiworld.get_location(loc_name, self.player)
            state = CollectionState(self.multiworld)
            # Empty state — access_rule must refuse entry.
            self.assertFalse(loc.access_rule(state),
                f"{loc_name} should require surface access in an empty state")


class TestUnfinishedBusinessRemoved(HadesIITestBase):
    """`Unfinished Business` (QuestHelpOdysseus) was removed because it
    requires ReachedTrueEnding (post-goal). Confirm it appears as neither
    a location nor an item under any sanity combo."""
    options = {"fatesanity": 1}

    def test_unfinished_business_location_absent(self) -> None:
        self.assertRaises(KeyError,
            self.multiworld.get_location, "Unfinished Business", self.player)

    def test_unfinished_business_item_absent(self) -> None:
        from worlds.hades_ii.Items import item_table
        self.assertNotIn("Unfinished Business Reward", item_table)
        present = [i for i in self.multiworld.itempool
                   if i.player == self.player
                   and i.name == "Unfinished Business Reward"]
        self.assertEqual(present, [])


class TestRivalsOldAndRotExcludedUnderTrueEnding(HadesIITestBase):
    """Rivals of Old and Rot (T4) is excluded from cauldronsanity when
    true_ending is on — vanilla requires ReachedTrueEnding."""
    options = {"true_ending": 1, "cauldronsanity": 1}

    def test_t4_location_absent(self) -> None:
        self.assertRaises(KeyError,
            self.multiworld.get_location, "Rivals of Old and Rot", self.player)

    def test_t4_item_absent(self) -> None:
        present = [i for i in self.multiworld.itempool
                   if i.player == self.player
                   and i.name == "Rivals of Old and Rot"]
        self.assertEqual(present, [])


class TestRivalsOldAndRotPresentInBossDefeatsMode(HadesIITestBase):
    """Outside true_ending, T4 is still in the cauldronsanity pool."""
    options = {"true_ending": 0, "cauldronsanity": 1}

    def test_t4_location_present(self) -> None:
        loc = self.multiworld.get_location("Rivals of Old and Rot", self.player)
        self.assertIsNotNone(loc)

    def test_t4_item_present(self) -> None:
        present = [i for i in self.multiworld.itempool
                   if i.player == self.player
                   and i.name == "Rivals of Old and Rot"]
        self.assertEqual(len(present), 1)


class TestProphecyChainsAreProgression(HadesIITestBase):
    """Prophecy items that appear as chain prereqs in Rules.py must be
    progression-classified even when fates_needed is 0, otherwise
    state.has(...) can't see them."""
    options = {"fatesanity": 1, "fates_needed": 0}

    def test_chain_prereqs_are_progression(self) -> None:
        from worlds.hades_ii.Items import PROGRESSION_PROPHECY_ITEMS
        for name in PROGRESSION_PROPHECY_ITEMS:
            matching = [i for i in self.multiworld.itempool
                        if i.player == self.player and i.name == name]
            self.assertEqual(len(matching), 1, f"missing {name}")
            self.assertTrue(matching[0].advancement,
                f"{name} must be progression (used as a chain prereq)")


class TestNaturalTalentRequiresWitchReward(HadesIITestBase):
    """Natural Talent's access rule should require Hecate Victory AND
    `Witch of the Crossroads Reward`."""
    options = {"fatesanity": 1, "fates_needed": 0}

    def test_rule_blocks_without_prereqs(self) -> None:
        from BaseClasses import CollectionState
        loc = self.multiworld.get_location("Natural Talent", self.player)
        state = CollectionState(self.multiworld)
        self.assertFalse(loc.access_rule(state),
            "empty state must fail")

        # Hecate alone — still blocked by missing chain prereq.
        state.collect(
            next(i for i in self.multiworld.get_locations(self.player)
                 if i.name == "Hecate Victory").item, prevent_sweep=True)
        self.assertFalse(loc.access_rule(state),
            "Hecate alone must not satisfy Natural Talent")

        # Add Witch of the Crossroads Reward — should now pass.
        from worlds.hades_ii.Items import Hades_II_Item
        state.prog_items[self.player]["Witch of the Crossroads Reward"] = 1
        self.assertTrue(loc.access_rule(state),
            "Hecate + Witch of the Crossroads Reward must satisfy Natural Talent")


class TestIncantationChainsAreProgression(HadesIITestBase):
    """Every incantation referenced via `_has_incantation(...)` in Rules.py
    must be progression-classified so AP's all-state reachability check
    sees it via state.has(...). Promoting happens in Items.create_items
    via the PROGRESSION_INCANTATION_ITEMS set."""
    # unlock_broker off so "Summoning of Mercantile Fortune" stays in the pool.
    options = {"cauldronsanity": 1, "lock_surface_incantations": 1, "unlock_broker": 0}

    def test_chain_heads_are_progression(self) -> None:
        from worlds.hades_ii.Items import PROGRESSION_INCANTATION_ITEMS
        # Spot-check a representative subset of chain heads.
        critical = (
            "Summoning of Mercantile Fortune",
            "Night's Craftwork",
            "Flourishing Soil",
            "Rich Soil",
            "Faith of Familiar Spirits",
            "Abyssal Insight",
            "Rise of Stygian Wells",
        )
        for name in critical:
            self.assertIn(name, PROGRESSION_INCANTATION_ITEMS)
            matching = [i for i in self.multiworld.itempool
                        if i.player == self.player and i.name == name]
            self.assertEqual(len(matching), 1, f"missing {name}")
            self.assertTrue(matching[0].advancement,
                f"{name} must be progression (used in _has_incantation gates)")


class TestScoreSplitSeparate(HadesIITestBase):
    """Separate score split (default): underworld score checks live in Erebus
    (reachable from start) and surface ones in Ephyra (gated by surface access).
    lock_surface_incantations on so the surface gate has teeth."""
    options = {
        "score_split_mode": "separate",
        "score_rewards_amount": 100,
        "surface_score_ratio": 40,
        "lock_surface_incantations": 1,
    }

    def test_split_boundary(self) -> None:
        from worlds.hades_ii.Locations import score_check_split
        under, surf = score_check_split(100, 40)
        self.assertEqual((under, surf), (60, 40))

    def test_underworld_checks_in_erebus(self) -> None:
        # The underworld budget (60) of route-named checks is placed in Erebus.
        loc = self.multiworld.get_location("Underworld Score Check 1", self.player)
        self.assertEqual(loc.parent_region.name, "Erebus")
        loc = self.multiworld.get_location("Underworld Score Check 60", self.player)
        self.assertEqual(loc.parent_region.name, "Erebus")

    def test_surface_checks_in_ephyra(self) -> None:
        # The surface budget (40) of route-named checks is placed in Ephyra.
        loc = self.multiworld.get_location("Surface Score Check 1", self.player)
        self.assertEqual(loc.parent_region.name, "Ephyra")
        loc = self.multiworld.get_location("Surface Score Check 40", self.player)
        self.assertEqual(loc.parent_region.name, "Ephyra")

    def test_surface_checks_need_surface_access(self) -> None:
        # With no items collected the surface unlock incantations are missing,
        # so surface score checks are unreachable while underworld ones are not.
        self.assertTrue(self.can_reach_location("Underworld Score Check 1"))
        self.assertFalse(self.can_reach_location("Surface Score Check 40"))


class TestScoreSplitCombined(HadesIITestBase):
    """Combined score split: all checks live in Menu and are reachable from the
    start regardless of surface access."""
    options = {
        "score_split_mode": "combined",
        "score_rewards_amount": 100,
        "lock_surface_incantations": 1,
    }

    def test_all_checks_in_menu(self) -> None:
        for name in ("Score Check 1", "Score Check 100"):
            loc = self.multiworld.get_location(name, self.player)
            self.assertEqual(loc.parent_region.name, "Menu")

    def test_all_checks_reachable_from_start(self) -> None:
        self.assertTrue(self.can_reach_location("Score Check 1"))
        self.assertTrue(self.can_reach_location("Score Check 100"))


# ── Room-based location systems ───────────────────────────────────────────────

def _assert_room_checks_block_progression(test_case) -> None:
    fake_progression = Item("test", ItemClassification.progression, None, test_case.player)
    fake_filler = Item("test", ItemClassification.filler, None, test_case.player)
    room_locs = [
        loc for loc in test_case.multiworld.get_locations(test_case.player)
        if loc.name.startswith("Clear ")
    ]
    test_case.assertGreater(len(room_locs), 0, "no room checks found")
    for loc in room_locs:
        test_case.assertFalse(loc.item_rule(fake_progression),
            f"{loc.name} should reject progression items")
        test_case.assertTrue(loc.item_rule(fake_filler),
            f"{loc.name} should accept filler items")


class TestRoomBased(HadesIITestBase):
    """room_based: per-route depth checks, no score checks. lock_surface on so the
    surface gate has teeth."""
    options = {"location_system": "room_based", "lock_surface_incantations": 1}

    def test_no_score_checks(self) -> None:
        score = [loc for loc in self.multiworld.get_locations(self.player)
                 if loc.name.startswith("Score Check ")]
        self.assertEqual(score, [])

    def test_room_counts_match_constants(self) -> None:
        from worlds.hades_ii.Locations import UNDERWORLD_ROOM_MAX, SURFACE_ROOM_MAX
        under = [loc for loc in self.multiworld.get_locations(self.player)
                 if loc.name.startswith("Clear Underworld Room ")]
        surf = [loc for loc in self.multiworld.get_locations(self.player)
                if loc.name.startswith("Clear Surface Room ")]
        self.assertEqual(len(under), UNDERWORLD_ROOM_MAX)
        self.assertEqual(len(surf), SURFACE_ROOM_MAX)

    def test_room_region_placement(self) -> None:
        # Each depth lands in the biome region that owns its run depth, so the
        # boss-victory gates apply. (Boundaries from {UNDERWORLD,SURFACE}_BIOME_BOUNDS.)
        from worlds.hades_ii.Locations import (
            UNDERWORLD_BIOME_BOUNDS, SURFACE_BIOME_BOUNDS, room_region_for)
        for depth in (1, 12, 21, 26, 40):
            self.assertEqual(
                self.multiworld.get_location(f"Clear Underworld Room {depth:02d}", self.player)
                    .parent_region.name, room_region_for(UNDERWORLD_BIOME_BOUNDS, depth))
        for depth in (1, 30):
            self.assertEqual(
                self.multiworld.get_location(f"Clear Surface Room {depth:02d}", self.player)
                    .parent_region.name, room_region_for(SURFACE_BIOME_BOUNDS, depth))

    def test_shallow_underworld_room_reachable_from_start(self) -> None:
        # Erebus is reachable from the Crossroads with no items.
        self.assertTrue(self.can_reach_location("Clear Underworld Room 01"))

    def test_deep_underworld_room_needs_biome_bosses(self) -> None:
        # A Tartarus-depth room requires Hecate+Scylla+Cerberus victories, so it
        # is NOT reachable from an empty state.
        self.assertFalse(self.can_reach_location("Clear Underworld Room 40"))

    def test_surface_rooms_need_surface_access(self) -> None:
        self.assertFalse(self.can_reach_location("Clear Surface Room 01"))

    def test_room_checks_block_progression(self) -> None:
        _assert_room_checks_block_progression(self)


class TestRoomWeaponBased(HadesIITestBase):
    """room_weapon_based: room_based set x 6 weapons."""
    options = {"location_system": "room_weapon_based"}

    def test_room_weapon_count(self) -> None:
        from worlds.hades_ii.Locations import (
            UNDERWORLD_ROOM_MAX, SURFACE_ROOM_MAX, ROOM_WEAPON_TOKENS)
        room_locs = [loc for loc in self.multiworld.get_locations(self.player)
                     if loc.name.startswith("Clear ")]
        expected = (UNDERWORLD_ROOM_MAX + SURFACE_ROOM_MAX) * len(ROOM_WEAPON_TOKENS)
        self.assertEqual(len(room_locs), expected)

    def test_weapon_suffixed_names_exist(self) -> None:
        for name in ("Clear Underworld Room 01 Staff", "Clear Surface Room 01 Coat"):
            self.assertIsNotNone(self.multiworld.get_location(name, self.player))

    def test_room_checks_block_progression(self) -> None:
        _assert_room_checks_block_progression(self)


# ── Ingredient logic ──────────────────────────────────────────────────────────
# Cost-bearing locations (shops, cauldron recipes, gather-dependent prophecies)
# must require the matching gathering tool or familiar plus its farming reach.

class TestIngredientLogicAllSanities(HadesIITestBase):
    """Tool/familiar ingredient gates under the full sanity suite."""
    options = {
        "toolsanity": 1, "familiarsanity": 1, "weaponsanity": 1,
        "hidden_aspectsanity": 1, "cauldronsanity": 1, "fatesanity": 1,
        "keepsakesanity": 1, "lock_surface_incantations": 1, "unlock_broker": 0,
        "initial_weapon": 0,
    }

    def _empty_state(self):
        from BaseClasses import CollectionState
        return CollectionState(self.multiworld)

    def _grant(self, state, *names):
        for name in names:
            state.prog_items[self.player][name] += 1

    def test_tool_shop_needs_nights_craftwork(self) -> None:
        loc = self.multiworld.get_location("Crescent Pickaxe Tool Unlock Location", self.player)
        state = self._empty_state()
        self.assertFalse(loc.access_rule(state), "tool shop tab needs Night's Craftwork")
        self._grant(state, "Night's Craftwork")
        self.assertTrue(loc.access_rule(state))

    def test_spade_purchase_needs_mining(self) -> None:
        loc = self.multiworld.get_location("Silver Spade Tool Unlock Location", self.player)
        state = self._empty_state()
        self._grant(state, "Night's Craftwork")
        self.assertFalse(loc.access_rule(state), "8 Silver — needs a miner")
        # Raki substitutes the pickaxe.
        self._grant(state, "Raki Familiar")
        self.assertTrue(loc.access_rule(state))

    def test_rod_purchase_needs_mining_and_surface(self) -> None:
        loc = self.multiworld.get_location("Rod of Fishing Tool Unlock Location", self.player)
        state = self._empty_state()
        self._grant(state, "Night's Craftwork", "Crescent Pickaxe Tool Unlock")
        self.assertFalse(loc.access_rule(state), "1 Bronze — needs Ephyra reach")
        self._grant(state, "Permeation of Witching-Wards", "Unraveling a Fateful Bond")
        self.assertTrue(loc.access_rule(state))

    def test_skull_weapon_needs_priors_mining_and_reach(self) -> None:
        loc = self.multiworld.get_location("Skull Weapon Unlock Location", self.player)
        state = self._empty_state()
        self._grant(state, "Daggers Weapon Unlock", "Torches Weapon Unlock",
                    "Axe Weapon Unlock", "Crescent Pickaxe Tool Unlock")
        self.assertFalse(loc.access_rule(state),
            "Bronze needs surface, Glassrock needs Scylla")
        self._grant(state, "Scylla Victory",
                    "Permeation of Witching-Wards", "Unraveling a Fateful Bond")
        self.assertTrue(loc.access_rule(state))

    def test_incantation_needs_mining(self) -> None:
        loc = self.multiworld.get_location("Woodsy Lifespring", self.player)
        state = self._empty_state()
        self.assertFalse(loc.access_rule(state), "3 Silver — needs a miner")
        self._grant(state, "Crescent Pickaxe Tool Unlock")
        self.assertTrue(loc.access_rule(state))

    def test_grown_plant_needs_dig_and_garden(self) -> None:
        loc = self.multiworld.get_location("Rise of Stygian Wells", self.player)
        state = self._empty_state()
        self._grant(state, "Night's Craftwork", "Silver Spade Tool Unlock")
        self.assertFalse(loc.access_rule(state), "Nightshade needs the garden")
        self._grant(state, "Flourishing Soil")
        self.assertTrue(loc.access_rule(state))

    def test_tools_of_the_unseen_needs_all_four_tools(self) -> None:
        loc = self.multiworld.get_location("Tools of the Unseen", self.player)
        state = self._empty_state()
        self._grant(state, "Crescent Pickaxe Tool Unlock", "Silver Spade Tool Unlock",
                    "Tablet of Peace Tool Unlock")
        self.assertFalse(loc.access_rule(state), "missing the Rod")
        self._grant(state, "Rod of Fishing Tool Unlock")
        self.assertTrue(loc.access_rule(state))

    def test_denizen_of_the_depths_needs_fishing(self) -> None:
        loc = self.multiworld.get_location("Denizen of the Depths", self.player)
        state = self._empty_state()
        self._grant(state, "Night's Craftwork", "Rite of River-Fording")
        self.assertFalse(loc.access_rule(state), "needs the Rod or Toula")
        self._grant(state, "Toula Familiar")
        self.assertTrue(loc.access_rule(state))

    def test_hidden_aspect_needs_system_and_ore(self) -> None:
        loc = self.multiworld.get_location("Coat Weapon Shiva Aspect Unlock Location", self.player)
        state = self._empty_state()
        self._grant(state, "Coat Weapon Unlock", "Crescent Pickaxe Tool Unlock",
                    "Scylla Victory")
        self.assertFalse(loc.access_rule(state), "needs Aspects of Night and Darkness")
        self._grant(state, "Aspects of Night and Darkness")
        self.assertTrue(loc.access_rule(state))


class TestIngredientLogicVanillaWeapons(HadesIITestBase):
    """Weapon prophecies with weaponsanity OFF fall back to the vanilla
    purchase chain (mining + shop sequencing reach)."""
    options = {
        "weaponsanity": 0, "toolsanity": 0, "familiarsanity": 0,
        "cauldronsanity": 0, "fatesanity": 1, "lock_surface_incantations": 1,
    }

    def test_black_coat_vanilla_chain(self) -> None:
        from BaseClasses import CollectionState
        loc = self.multiworld.get_location("The Black Coat", self.player)
        state = CollectionState(self.multiworld)
        self.assertFalse(loc.access_rule(state))
        for name in ("Hecate Victory", "Scylla Victory", "Eris Victory",
                      "Permeation of Witching-Wards"):
            state.prog_items[self.player][name] += 1
        self.assertFalse(loc.access_rule(state), "Bronze needs full surface access")
        state.prog_items[self.player]["Unraveling a Fateful Bond"] += 1
        self.assertTrue(loc.access_rule(state))


# ── Preset smoke tests ────────────────────────────────────────────────────────
# Generate every shipped preset and run the inherited base checks (fill +
# all-state reachability), so a preset can never ship an ungeneratable combo.

def _make_preset_test(preset_name, preset_opts):
    class _PresetTest(HadesIITestBase):
        options = dict(preset_opts)
    _PresetTest.__doc__ = f"Smoke test: preset {preset_name!r} generates a completable world."
    return _PresetTest


for _preset_name, _preset_opts in hades_ii_option_presets.items():
    _cls_name = "TestPreset" + _preset_name.title().replace(" ", "")
    globals()[_cls_name] = _make_preset_test(_preset_name, _preset_opts)
    globals()[_cls_name].__name__ = _cls_name
    globals()[_cls_name].__qualname__ = _cls_name
del _preset_name, _preset_opts, _cls_name
