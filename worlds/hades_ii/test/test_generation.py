from BaseClasses import Item, ItemClassification, LocationProgressType
from .bases import HadesIITestBase


def _assert_score_checks_block_progression(test_case) -> None:
    """Score checks must reject progression items via their per-location item rule.

    Verifies the rule directly (no fill required) so the test is independent
    of fill order or RNG. EXCLUDED marking is intentionally NOT used.
    """
    fake_progression = Item("test", ItemClassification.progression, None, test_case.player)
    fake_filler = Item("test", ItemClassification.filler, None, test_case.player)
    score_locs = [
        loc for loc in test_case.multiworld.get_locations(test_case.player)
        if loc.name.startswith("Score Check ")
    ]
    test_case.assertGreater(len(score_locs), 0, "no score checks found")
    for loc in score_locs:
        test_case.assertNotEqual(loc.progress_type, LocationProgressType.EXCLUDED,
            f"{loc.name} must not be EXCLUDED — rely on item rule instead")
        test_case.assertFalse(loc.item_rule(fake_progression),
            f"{loc.name} should reject progression items")
        test_case.assertTrue(loc.item_rule(fake_filler),
            f"{loc.name} should accept filler items")


class TestDefaultGeneration(HadesIITestBase):
    """Default options: score_based system, all sanities enabled, normal fear."""
    options = {}

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)

    def test_no_boss_rewards_when_not_true_ending(self) -> None:
        # BossDefeats mode counts run completions; no per-kill reward locations.
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
        "cauldronsanity": 1,
        "fatesanity": 1,
    }

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)


class TestAllSanitiesOff(HadesIITestBase):
    options = {
        "keepsakesanity": 0,
        "weaponsanity": 0,
        "hidden_aspectsanity": 0,
        "cauldronsanity": 0,
        "lock_surface_incantations": 0,
        "fatesanity": 0,
    }


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
    options = {"lock_surface_incantations": 0, "cauldronsanity": 1}

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


class TestScoreRewards72(HadesIITestBase):
    """Minimum valid score_rewards_amount."""
    options = {"location_system": 0, "score_rewards_amount": 72}

    def test_score_check_count(self) -> None:
        score_locs = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.name.startswith("Score Check ")
        ]
        self.assertEqual(len(score_locs), 72)

    def test_score_checks_block_progression(self) -> None:
        _assert_score_checks_block_progression(self)


class TestScoreRewardsMax(HadesIITestBase):
    options = {"location_system": 0, "score_rewards_amount": 150}

    def test_score_check_count(self) -> None:
        score_locs = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.name.startswith("Score Check ")
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
    options = {"initial_weapon": 6, "weaponsanity": 1}

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
    options = {"cauldronsanity": 1, "lock_surface_incantations": 1}

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
