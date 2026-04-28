from BaseClasses import LocationProgressType
from .bases import HadesIITestBase


class TestDefaultGeneration(HadesIITestBase):
    """Default options: score_based system, all sanities enabled, normal fear."""
    options = {}

    def test_score_checks_excluded_up_to_pure_filler(self) -> None:
        pure_filler = sum(
            1 for item in self.multiworld.itempool
            if item.player == self.player and not item.advancement and not item.useful
        )
        excluded_score = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.progress_type == LocationProgressType.EXCLUDED
            and loc.name.startswith("Score Check ")
        ]
        self.assertLessEqual(len(excluded_score), pure_filler,
            "More score checks excluded than pure filler items — fill will fail")

    def test_boss_rewards_not_excluded(self) -> None:
        for name in ("Chronos Kill Reward", "Typhon Kill Reward"):
            loc = self.multiworld.get_location(name, self.player)
            self.assertNotEqual(loc.progress_type, LocationProgressType.EXCLUDED,
                f"{name} must not be EXCLUDED")


class TestTrueEnding(HadesIITestBase):
    options = {"true_ending": 1}

    def test_true_ending_event_exists(self) -> None:
        loc = self.multiworld.get_location("Chronos True Victory", self.player)
        self.assertIsNotNone(loc)

    def test_boss_rewards_not_excluded(self) -> None:
        for name in ("Chronos Kill Reward", "Typhon Kill Reward"):
            loc = self.multiworld.get_location(name, self.player)
            self.assertNotEqual(loc.progress_type, LocationProgressType.EXCLUDED)


class TestTrueEndingAllSanities(HadesIITestBase):
    options = {
        "true_ending": 1,
        "keepsakesanity": 1,
        "weaponsanity": 1,
        "hidden_aspectsanity": 1,
        "cauldronsanity": 1,
        "fatesanity": 1,
    }

    def test_score_checks_excluded_up_to_pure_filler(self) -> None:
        pure_filler = sum(
            1 for item in self.multiworld.itempool
            if item.player == self.player and not item.advancement and not item.useful
        )
        excluded_score = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.progress_type == LocationProgressType.EXCLUDED
            and loc.name.startswith("Score Check ")
        ]
        self.assertLessEqual(len(excluded_score), pure_filler)


class TestAllSanitiesOff(HadesIITestBase):
    options = {
        "keepsakesanity": 0,
        "weaponsanity": 0,
        "hidden_aspectsanity": 0,
        "cauldronsanity": 0,
        "fatesanity": 0,
    }


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

    def test_excluded_count_safe(self) -> None:
        pure_filler = sum(
            1 for item in self.multiworld.itempool
            if item.player == self.player and not item.advancement and not item.useful
        )
        excluded_score = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.progress_type == LocationProgressType.EXCLUDED
            and loc.name.startswith("Score Check ")
        ]
        self.assertLessEqual(len(excluded_score), pure_filler)
        # All 72 checks that fit within pure filler should be excluded
        self.assertEqual(len(excluded_score), min(72, pure_filler))


class TestScoreRewardsMax(HadesIITestBase):
    options = {"location_system": 0, "score_rewards_amount": 150}

    def test_score_check_count(self) -> None:
        score_locs = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.name.startswith("Score Check ")
        ]
        self.assertEqual(len(score_locs), 150)

    def test_excluded_count_safe(self) -> None:
        pure_filler = sum(
            1 for item in self.multiworld.itempool
            if item.player == self.player and not item.advancement and not item.useful
        )
        excluded_score = [
            loc for loc in self.multiworld.get_locations(self.player)
            if loc.progress_type == LocationProgressType.EXCLUDED
            and loc.name.startswith("Score Check ")
        ]
        self.assertLessEqual(len(excluded_score), pure_filler)
