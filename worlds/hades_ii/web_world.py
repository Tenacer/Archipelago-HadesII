from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .Options import hades_ii_option_groups, hades_ii_option_presets


class HadesIIWebWorld(WebWorld):
    game = "Hades II"

    setup_en = Tutorial(
        tutorial_name="Multiworld Setup Guide",
        description="A guide to setting up Hades II for Archipelago multiworld play.",
        language="English",
        file_name="setup_en.md",
        link="setup/en",
        authors=["Tenacer"],
    )
    tutorials = [setup_en]

    bug_report_page = "https://github.com/Tenacer/Archipelago-HadesII/issues"

    option_groups = hades_ii_option_groups
    options_presets = hades_ii_option_presets
