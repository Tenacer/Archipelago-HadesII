from worlds.AutoWorld import WebWorld

from .Options import hades_ii_option_groups, hades_ii_option_presets


class HadesIIWebWorld(WebWorld):
    game = "Hades II"
    option_groups = hades_ii_option_groups
    options_presets = hades_ii_option_presets
