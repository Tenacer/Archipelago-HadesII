from typing import TYPE_CHECKING
from .Items import item_table_fears, item_table_keepsakes, item_table_prophecies
from .Locations import initial_aspect_item
from worlds.AutoWorld import LogicMixin
from worlds.generic.Rules import add_rule, add_item_rule

# NOTE: All the `# type: ignore` blocks are to clear the unknown property error sometimes caused by state stuff

if TYPE_CHECKING:
    from . import HadesIIWorld

weapons = [
    "Staff Weapon",
    "Daggers Weapon",
    "Torches Weapon",
    "Axe Weapon",
    "Skull Weapon",
    "Coat Weapon",
]

class HadesIILogic(LogicMixin):
    # Checks if the player has enough of a given item 
    def _has_enough_of_item(self, player: int, amount: int, item: str) -> bool:
        return self.count(item, player) >= amount  # type: ignore
    
    # Generation-time approximation: owning N weapons + endgame reach proves N distinct clears are possible; the real count is enforced client-side.
    def _has_enough_weapons(self, player: int, options, amount: int) -> bool:
        if not options.weaponsanity:
            return True
        return sum(self._has_weapon(w, player, options) for w in weapons) >= amount
    
    # Checks if the player has a given weapon
    def _has_weapon(self, weaponName: str, player: int, options) -> bool:
        if not options.weaponsanity:
            return True
        idx = weapons.index(weaponName)
        return (options.initial_weapon == idx or self.has(f"{weaponName} Unlock", player)) # type: ignore
    
    # Checks if the player has enough keepsakes for goal
    def _has_enough_keepsakes(self, player: int, amount: int) -> bool:
        amount_keepsakes = 0
        for keepsake_name in item_table_keepsakes:
            amount_keepsakes += self.count(keepsake_name, player) # type: ignore
        return amount_keepsakes >= amount
    
    # Checks if the player has enough prophecies completed for goal
    def _has_enough_prophecies_done(self, player: int, amount: int) -> bool:
        amount_props = 0 
        for prop in item_table_prophecies:
            amount_props += self.count(prop, player) # type: ignore
        return amount_props >= amount
    
    # Checks if the player has defeated the boss with enough (depending on options):
    def _can_get_victory(self, player: int, options) -> bool:
        if options.true_ending:
            can_win = self._has_true_ending_requirements(player, options)
        else:
            can_win = self._can_reach_endgame(player, options)

        # Weapons cleared
        if options.weaponsanity:
            weapons_temp = options.weapons_clears_needed.value
            can_win = (can_win) and (self._enough_weapons_victories(player, options, weapons_temp))

        # Keepsakes owned
        if options.keepsakesanity:
            keepsakes = options.keepsakes_needed.value
            can_win = (can_win) and (self._has_enough_keepsakes(player, keepsakes))

        # Prophecies cleared
        if options.fatesanity:
            fates = options.fates_needed.value
            can_win = (can_win) and (self._has_enough_prophecies_done(player, fates))

        return can_win

    # True Ending needs both final bosses, the incantation ingredients, and the final Chronos kill event.
    def _has_true_ending_requirements(self, player: int, options) -> bool:
        return (
            self.has("Chronos True Victory", player)  # type: ignore
            and self.has("Typhon Victory", player)  # type: ignore
            and self.has("Gigaros", player)  # type: ignore
            and self.has("Entropy", player)  # type: ignore
            and self.count("Zodiac Sand", player) >= options.zodiac_sand_needed.value  # type: ignore
            and self.count("Void Lens", player) >= options.void_lens_needed.value  # type: ignore
        )
    
    # Sugar: boss base name + " Victory".
    def _has_boss(self, boss: str, player: int) -> bool:
        return self.has(f"{boss} Victory", player)  # type: ignore

    # True when cauldronsanity is off or the incantation's AP item has been received (surface-unlock 2 excluded).
    def _has_incantation(self, name: str, player: int, options) -> bool:
        # The Broker is free under unlock_broker, so treat its incantation as satisfied.
        if name == "Summoning of Mercantile Fortune" and options.unlock_broker:
            return True
        if not options.cauldronsanity:
            # Brewed vanilla — still needs its gathered ingredients.
            return self._can_afford(name, player, options)
        return self.has(name, player)  # type: ignore

    # Familiar recruits sit behind the familiar-system unlock: Hecate + its incantation + the three tools.
    def _has_familiar_system(self, player: int, options) -> bool:
        if not self._has_boss("Hecate", player):
            return False
        if not self._has_incantation("Faith of Familiar Spirits", player, options):
            return False
        return self._has_familiar_tools(player, options)

    # The three tools must be available before Hecate's conversation unlocks the familiar-system incantation.
    def _has_familiar_tools(self, player: int, options) -> bool:
        if not options.toolsanity:
            return True
        return (
            self.has("Tablet of Peace Tool Unlock", player)  # type: ignore
            and self.has("Crescent Pickaxe Tool Unlock", player)  # type: ignore
            and self.has("Silver Spade Tool Unlock", player)  # type: ignore
        )

    # Endgame: combined mode needs either final boss, separate mode needs both (kill counts enforced client-side).
    def _can_reach_endgame(self, player: int, options) -> bool:
        if options.boss_defeats_mode == 1:  # separate
            return self.has("Chronos Victory", player) and self.has("Typhon Victory", player)  # type: ignore
        return self.has("Chronos Victory", player) or self.has("Typhon Victory", player)  # type: ignore

    # Checks if the player has enough weapon wins for goal
    def _enough_weapons_victories(self, player: int, options, amount: int) -> bool:
        return self._can_reach_endgame(player, options) and self._has_enough_weapons(player, options, amount)
    
    # Surface access: Permeation opens the door, Unraveling cures the penalty; AP items only under lock_surface_incantations.
    def _has_surface_door(self, player: int, options) -> bool:
        if not options.lock_surface_incantations:
            # Brewed vanilla — Permeation's recipe needs a Hecate boss material.
            return self._can_afford("Permeation of Witching-Wards", player, options)
        return self.has("Permeation of Witching-Wards", player)  # type: ignore

    def _has_surface_access(self, player: int, options) -> bool:
        if not options.lock_surface_incantations:
            # Brewed vanilla — Moss is deliberately absent from the atoms so this can't recurse into surface access.
            return (self._has_surface_door(player, options)
                    and self._can_afford("Unraveling a Fateful Bond", player, options))
        return (
            self.has("Permeation of Witching-Wards", player)  # type: ignore
            and self.has("Unraveling a Fateful Bond", player)  # type: ignore
        )

    # Moros appears only after the first surface run, which needs just the door.
    def _has_moros_access(self, player: int, options) -> bool:
        return self._has_surface_door(player, options)

    # ── Gathering capabilities ────────────────────────────────────────────────
    # Recipes still charge their vanilla costs under AP, so cost-bearing locations need the matching tool/familiar and biome reach.

    # Pickaxe: 1 Psyche at the (Night's Craftwork) tool shop when toolsanity is off.
    def _has_pickaxe(self, player: int, options) -> bool:
        if options.toolsanity:
            return self.has("Crescent Pickaxe Tool Unlock", player)  # type: ignore
        return self._has_incantation("Night's Craftwork", player, options)

    # Tablet of Peace: 4 Silver — vanilla purchase needs mining first.
    def _has_tablet(self, player: int, options) -> bool:
        if options.toolsanity:
            return self.has("Tablet of Peace Tool Unlock", player)  # type: ignore
        return (self._has_incantation("Night's Craftwork", player, options)
                and self._can_mine(player, options))

    # Silver Spade: 8 Silver — vanilla purchase needs mining first.
    def _has_spade(self, player: int, options) -> bool:
        if options.toolsanity:
            return self.has("Silver Spade Tool Unlock", player)  # type: ignore
        return (self._has_incantation("Night's Craftwork", player, options)
                and self._can_mine(player, options))

    # Rod of Fishing: 1 Bronze (Ephyra ore) — vanilla purchase needs mining + surface.
    def _has_rod(self, player: int, options) -> bool:
        if options.toolsanity:
            return self.has("Rod of Fishing Tool Unlock", player)  # type: ignore
        return (self._has_incantation("Night's Craftwork", player, options)
                and self._can_mine(player, options)
                and self._has_surface_access(player, options))

    # All four tools owned/obtainable (QuestToolsUnlocks completion).
    def _has_all_tools(self, player: int, options) -> bool:
        return (self._has_pickaxe(player, options)
                and self._has_tablet(player, options)
                and self._has_spade(player, options)
                and self._has_rod(player, options))

    # A gathering familiar: the AP item alone, or the vanilla recruit (system + home biome).
    def _has_gather_familiar(self, item: str, boss, player: int, options) -> bool:
        if options.familiarsanity:
            return self.has(item, player)  # type: ignore
        if not self._has_familiar_system(player, options):
            return False
        return boss is None or self._has_boss(boss, player)

    # Mining: Crescent Pickaxe or Raki.
    def _can_mine(self, player: int, options) -> bool:
        return (self._has_pickaxe(player, options)
                or self._has_gather_familiar("Raki Familiar", None, player, options))

    # Digging: Silver Spade or Hecuba; shovel points only spawn once Night's Craftwork is active.
    def _can_dig(self, player: int, options) -> bool:
        if not self._has_incantation("Night's Craftwork", player, options):
            return False
        return (self._has_spade(player, options)
                or self._has_gather_familiar("Hecuba Familiar", "Scylla", player, options))

    # Grown plants: dig the biome seed, then grow it in the (Flourishing Soil) garden.
    def _can_grow(self, player: int, options) -> bool:
        return (self._can_dig(player, options)
                and self._has_incantation("Flourishing Soil", player, options))

    # Fishing: Rod or Toula — fishing points also need Night's Craftwork active.
    def _can_fish(self, player: int, options) -> bool:
        if not self._has_incantation("Night's Craftwork", player, options):
            return False
        return (self._has_rod(player, options)
                or self._has_gather_familiar("Toula Familiar", "Hecate", player, options))

    # Reach of a farming biome's gather points; Chaos gates open from Erebus.
    def _can_farm_biome(self, biome: str, player: int, options) -> bool:
        if biome in ("F", "Chaos"):
            return True
        if biome == "G":
            return self._has_boss("Hecate", player)
        if biome == "H":
            return self._has_boss("Scylla", player)
        if biome == "I":
            return self._has_boss("Cerberus", player)
        if not self._has_surface_access(player, options):
            return False
        if biome == "N":
            return True
        if biome == "O":
            return self._has_boss("Polyphemus", player)
        if biome == "P":
            return self._has_boss("Eris", player)
        return self._has_boss("Prometheus", player)  # Q

    # One ingredient atom: mine/dig/grow/pick = capability + reach, boss = victory, well = Rise of Stygian Wells.
    def _has_ingredient(self, atom, player: int, options) -> bool:
        kind, arg = atom
        if kind == "mine":
            return self._can_mine(player, options) and self._can_farm_biome(arg, player, options)
        if kind == "dig":
            return self._can_dig(player, options) and self._can_farm_biome(arg, player, options)
        if kind == "grow":
            return self._can_grow(player, options) and self._can_farm_biome(arg, player, options)
        if kind == "pick":
            return self._can_farm_biome(arg, player, options)
        if kind == "boss":
            return self._has_boss(arg, player)
        if kind == "well":
            return self._has_incantation("Rise of Stygian Wells", player, options)
        return True

    # All gathered-ingredient atoms of an incantation's vanilla recipe.
    def _can_afford(self, name: str, player: int, options) -> bool:
        return all(
            self._has_ingredient(atom, player, options)
            for atom in _INCANTATION_INGREDIENTS.get(name, ())
        )

    # The aspect purchase system: granted from the start by the QoL toggle, else the incantation.
    def _has_aspect_system(self, player: int, options) -> bool:
        if options.aspect_system_unlocked:
            return True
        return self._has_incantation("Aspects of Night and Darkness", player, options)

    # A standard aspect owned/obtainable: the AP item (or granted initial aspect) under
    # aspectsanity; otherwise the vanilla purchase = weapon + system + cost (+ familiar).
    def _has_standard_aspect(self, item: str, player: int, options) -> bool:
        if options.aspectsanity:
            return item == initial_aspect_item(options) or self.has(item, player)  # type: ignore
        weapon, atoms, needs_familiar = _STANDARD_ASPECT_BY_ITEM[item]
        if not self._has_weapon(weapon, player, options):
            return False
        if not self._has_aspect_system(player, options):
            return False
        if needs_familiar and not self._has_familiar_system(player, options):
            return False
        return all(self._has_ingredient(a, player, options) for a in atoms)

    # Aspect leveling to rank 5 needs Nightmare. Outside vanilla fear it is supplied via the
    # filler pool; in vanilla fear it wants the run progress that yields Nightmare (both bosses).
    def _nightmare_available(self, player: int, options) -> bool:
        if options.fear_system.value != 3:
            return True
        return self.has("Chronos Victory", player) and self.has("Typhon Victory", player)  # type: ignore

    # Faithful vanilla hidden-aspect reveal: system + both standard aspects + all six weapons
    # + reach the revealing god + rank-5 Nightmare + the purchase's gathered ingredients.
    def _can_unlock_hidden_aspect(self, weapon, atoms, reveal, player: int, options) -> bool:
        if not self._has_aspect_system(player, options):
            return False
        if not _reveal_gate_ok(self, reveal, player, options):
            return False
        s1, s2 = _WEAPON_STANDARD_ITEMS[weapon]
        if not (self._has_standard_aspect(s1, player, options)
                and self._has_standard_aspect(s2, player, options)):
            return False
        if not self._has_enough_weapons(player, options, 6):
            return False
        if not self._nightmare_available(player, options):
            return False
        return all(self._has_ingredient(a, player, options) for a in atoms)

    # A hidden aspect owned/obtainable: the AP item under hidden_aspectsanity;
    # otherwise the vanilla reveal chain + purchase.
    def _has_hidden_aspect(self, item: str, player: int, options) -> bool:
        if options.hidden_aspectsanity:
            return self.has(item, player)  # type: ignore
        weapon, atoms, reveal = _HIDDEN_ASPECT_VANILLA[item]
        return self._can_unlock_hidden_aspect(weapon, atoms, reveal, player, options)

    # A weapon obtainable at the Silver Pool: the AP item (or initial weapon)
    # under weaponsanity; otherwise the cumulative vanilla purchase costs
    # (the shop only offers Skull/Coat after the earlier weapons are bought).
    def _weapon_obtainable(self, weapon: str, player: int, options) -> bool:
        if options.weaponsanity:
            return self._has_weapon(weapon, player, options)
        return all(
            self._has_ingredient(a, player, options)
            for a in _WEAPON_VANILLA_ATOMS[weapon]
        )

# ── Ingredient data ───────────────────────────────────────────────────────────
# Gathered-ingredient atoms per incantation recipe (from WorldUpgradeData.lua Cost tables); free resources carry no atom. Biome letters: F=Erebus G=Oceanus H=Fields I=Tartarus N=Ephyra O=Thessaly P=Olympus Q=Summit.
_INCANTATION_INGREDIENTS = {
    "Abyssal Insight":                 (("boss", "Scylla"), ("grow", "F")),
    "Acceptance of Another Fate":      (("boss", "Chronos"), ("boss", "Typhon")),
    "Alteration of Familiar Forms":    (("boss", "Polyphemus"), ("mine", "Chaos")),
    "Arisen Troves":                   (("mine", "G"), ("mine", "O")),
    "Ashen Memories of Life":          (("grow", "G"),),
    "Aspects of Night and Darkness":   (("mine", "N"), ("grow", "F")),
    "Augmentation of Bone Density":    (("mine", "G"), ("mine", "P")),
    "Bones of Arcane Wisdom":          (("grow", "H"),),
    "Bounties of the Infinite Abyss":  (("mine", "H"), ("mine", "Q")),
    "Bravery of Familiar Spirits":     (("grow", "H"), ("boss", "Polyphemus")),
    "Briny Lifespring":                (("pick", "G"), ("mine", "G")),
    "Circles of Protection":           (("mine", "F"), ("pick", "P")),
    "Circles of the Moon":             (("grow", "F"), ("grow", "O")),
    "Cleansing of Fountain-Waters":    (("grow", "G"),),
    "Consecration of Ashes":           (("boss", "Hecate"),),
    "Deathly Fortune":                 (("grow", "N"),),
    "Doomed Beckoning":                (("grow", "F"),),
    "Empath's Intuition":              (("pick", "H"),),
    "End to Dearest Slumber":          (("grow", "O"), ("grow", "I")),
    "End to Deepest Slumber":          (("grow", "O"), ("grow", "I")),
    "End to Dumbest Slumber":          (("pick", "I"), ("grow", "I")),
    "Essence of Sorrow":               (("boss", "Cerberus"),),
    "Exhumed Troves":                  (("grow", "F"), ("mine", "G")),
    "Eyes of Night and Darkness":      (("mine", "H"), ("mine", "P")),
    "Faith of Familiar Spirits":       (("pick", "G"),),
    "Fated Intervention":              (("mine", "F"),),
    "Favored of All Keepsakes":        (("pick", "I"), ("pick", "P")),
    "Frozen Lifespring":               (("pick", "P"), ("mine", "P")),
    "Gathering of Ancient Bones":      (("mine", "G"),),
    "Gathering of Subterranean Riches": (("mine", "I"),),
    "Golden Lifespring":               (("pick", "I"), ("mine", "I")),
    "Greater Favor of Gaia":           (("mine", "H"), ("mine", "I"), ("mine", "O")),
    "Greater Removal of Rubbish":      (("pick", "N"), ("grow", "N")),
    "Greater Sowing of Gardens":       (("grow", "P"), ("grow", "I")),
    "Greatest Gift of Gaia":           (("grow", "Q"), ("grow", "P")),
    "Green Hand of Gaia":              (("grow", "H"), ("grow", "Q")),
    "Kindred Keepsakes":               (("mine", "G"), ("pick", "G")),
    "Necromantic Influence":           (("grow", "F"),),
    "Nectar of Godly Savor":           (("grow", "N"),),
    "Observance of Gaia's Secrets":    (("pick", "N"), ("grow", "H")),
    "Path to Desired Blessings":       (("grow", "Q"),),
    "Permeation of Witching-Wards":    (("boss", "Hecate"),),
    "Power to Pause and Reflect":      (("boss", "Chronos"),),
    "Propensity Toward Gold":          (("mine", "G"),),
    "Purification of Crystal Clarity": (("grow", "G"), ("grow", "O")),
    "Purification of Fountain-Waters": (("grow", "F"), ("grow", "G")),
    "Quickening of Sentimental Value": (("pick", "N"),),
    "Rage of the Elements":            (("mine", "Q"), ("boss", "Hecate")),
    "Return of Latent Memories":       (("grow", "G"),),
    "Revival of a Desecrating Pool":   (("pick", "I"), ("mine", "O")),
    "Reviving a Mournful Husk":        (("pick", "H"),),
    "Rich Soil":                       (("grow", "G"),),
    "Rise of Stygian Wells":           (("grow", "F"),),
    "Rite of River-Fording":           (("grow", "G"), ("pick", "O")),
    "Rite of Social Solidarity":       (("grow", "N"),),
    "Rite of Vapor-Cleansing":         (("pick", "G"), ("grow", "F")),
    "Rush of Fresh Air":               (("pick", "O"), ("boss", "Polyphemus")),
    "Sandy Lifespring":                (("pick", "O"), ("mine", "O")),
    "Shuffling of Noted Ballads":      (("pick", "I"), ("pick", "Q"), ("well", None)),
    "Spreading of Ashes":              (("grow", "P"),),
    "Summoning a Colony of Bats":      (("pick", "N"),),
    "Summoning of Historic Travails":  (("mine", "I"), ("boss", "Cerberus")),
    "Summoning of Musical Rhapsody":   (("boss", "Cerberus"), ("pick", "G")),
    "Summoning of Personal Insights":  (("pick", "I"),),
    "Surge of Fresh Air":              (("grow", "N"), ("grow", "O")),
    "Surge of Stygian Wells":          (("mine", "H"),),
    "Temporal Fluctuation":            (("pick", "I"),),
    # Moss (Ephyra) intentionally omitted to keep surface access non-circular.
    "Unraveling a Fateful Bond":       (("pick", "G"), ("grow", "F")),
    "Verdant Soil":                    (("grow", "H"), ("grow", "N")),
    "Woodsy Lifespring":               (("mine", "F"),),
}

# Weapon shop entries under weaponsanity: (location, ingredient atoms, prereq weapons).
_WEAPON_SHOP_RULES = (
    # The mod reprices the Staff to 1 Silver when it isn't the starting weapon.
    ("Staff Weapon Unlock Location",   (("mine", "F"),), ()),
    ("Daggers Weapon Unlock Location", (("mine", "F"),), ()),
    ("Torches Weapon Unlock Location", (("mine", "F"), ("boss", "Hecate")), ()),
    ("Axe Weapon Unlock Location",     (("mine", "F"),), ()),
    ("Skull Weapon Unlock Location",   (("mine", "H"), ("mine", "N")),
        ("Daggers Weapon", "Torches Weapon", "Axe Weapon")),
    ("Coat Weapon Unlock Location",    (("mine", "P"), ("boss", "Hecate")),
        ("Daggers Weapon", "Torches Weapon", "Axe Weapon", "Skull Weapon")),
)

# Cumulative vanilla purchase atoms per weapon (weaponsanity off).
_WEAPON_VANILLA_ATOMS = {
    "Staff Weapon":   (),
    "Daggers Weapon": (("mine", "F"),),
    "Torches Weapon": (("mine", "F"), ("boss", "Hecate")),
    "Axe Weapon":     (("mine", "F"),),
    "Skull Weapon":   (("mine", "F"), ("boss", "Hecate"), ("mine", "H"), ("mine", "N")),
    "Coat Weapon":    (("mine", "F"), ("boss", "Hecate"), ("mine", "H"), ("mine", "N"), ("mine", "P")),
}

# Tool shop entries under toolsanity: (location, ingredient atoms); the whole tab needs Night's Craftwork.
_TOOL_SHOP_RULES = (
    ("Crescent Pickaxe Tool Unlock Location", ()),                    # 1 Psyche
    ("Tablet of Peace Tool Unlock Location",  (("mine", "F"),)),      # 4 Silver
    ("Silver Spade Tool Unlock Location",     (("mine", "F"),)),      # 8 Silver
    ("Rod of Fishing Tool Unlock Location",   (("mine", "N"),)),      # 1 Bronze
)

# Hidden aspects: (location, item, weapon, ingredient atoms, reveal gate).
_HIDDEN_ASPECT_DATA = (
    ("Staff Weapon Anubis Aspect Unlock Location", "Anubis Aspect Unlock",
        "Staff Weapon", (("pick", "Q"), ("boss", "Cerberus")), "surface"),   # Circe reveals
    ("Daggers Weapon Morrigan Aspect Unlock Location", "Morrigan Aspect Unlock",
        "Daggers Weapon", (("mine", "O"), ("boss", "Prometheus")), None),    # Artemis reveals
    ("Torches Weapon Supay Aspect Unlock Location", "Supay Aspect Unlock",
        "Torches Weapon", (("mine", "I"),), "door"),                         # Moros reveals
    ("Axe Weapon Nergal Aspect Unlock Location", "Nergal Aspect Unlock",
        "Axe Weapon", (("mine", "Q"), ("mine", "O")), None),                 # Charon reveals
    ("Skull Weapon Hel Aspect Unlock Location", "Hel Aspect Unlock",
        "Skull Weapon", (("mine", "P"), ("grow", "Q")), "surface"),          # Medea reveals
    ("Coat Weapon Shiva Aspect Unlock Location", "Shiva Aspect Unlock",
        "Coat Weapon", (("mine", "H"),), None),                              # Selene reveals
)

# item → (weapon, atoms, reveal) for the vanilla path of _has_hidden_aspect.
_HIDDEN_ASPECT_VANILLA = {
    item: (weapon, atoms, reveal)
    for _loc, item, weapon, atoms, reveal in _HIDDEN_ASPECT_DATA
}

# Base aspects: (location, item, weapon). The Bones cost carries no gathering atom.
_BASE_ASPECT_DATA = (
    ("Staff Weapon Melinoe Aspect Unlock Location",   "Staff Melinoe Aspect Unlock",   "Staff Weapon"),
    ("Daggers Weapon Melinoe Aspect Unlock Location", "Daggers Melinoe Aspect Unlock", "Daggers Weapon"),
    ("Torches Weapon Melinoe Aspect Unlock Location", "Torches Melinoe Aspect Unlock", "Torches Weapon"),
    ("Axe Weapon Melinoe Aspect Unlock Location",     "Axe Melinoe Aspect Unlock",     "Axe Weapon"),
    ("Skull Weapon Melinoe Aspect Unlock Location",   "Skull Melinoe Aspect Unlock",   "Skull Weapon"),
    ("Coat Weapon Melinoe Aspect Unlock Location",    "Coat Melinoe Aspect Unlock",    "Coat Weapon"),
)

# Standard aspects: (location, item, weapon, ingredient atoms, needs_familiar). Costs from WeaponShopData.
_STANDARD_ASPECT_DATA = (
    ("Staff Weapon Circe Aspect Unlock Location",     "Circe Aspect Unlock",     "Staff Weapon",   (("grow", "G"), ("mine", "I")), True),
    ("Staff Weapon Momus Aspect Unlock Location",     "Momus Aspect Unlock",     "Staff Weapon",   (("boss", "Scylla"), ("mine", "G")), False),
    ("Daggers Weapon Artemis Aspect Unlock Location", "Artemis Aspect Unlock",   "Daggers Weapon", (("mine", "H"),), False),
    ("Daggers Weapon Pan Aspect Unlock Location",     "Pan Aspect Unlock",       "Daggers Weapon", (("grow", "I"), ("boss", "Polyphemus")), False),
    ("Torches Weapon Moros Aspect Unlock Location",   "Moros Aspect Unlock",     "Torches Weapon", (("boss", "Cerberus"), ("mine", "N")), False),
    ("Torches Weapon Eos Aspect Unlock Location",     "Eos Aspect Unlock",       "Torches Weapon", (("boss", "Eris"), ("grow", "O")), False),
    ("Axe Weapon Charon Aspect Unlock Location",      "Charon Aspect Unlock",    "Axe Weapon",     (("boss", "Scylla"),), False),
    ("Axe Weapon Thanatos Aspect Unlock Location",    "Thanatos Aspect Unlock",  "Axe Weapon",     (("mine", "H"), ("grow", "F")), False),
    ("Skull Weapon Medea Aspect Unlock Location",     "Medea Aspect Unlock",     "Skull Weapon",   (("mine", "O"), ("grow", "O")), False),
    ("Skull Weapon Persephone Aspect Unlock Location","Persephone Aspect Unlock","Skull Weapon",   (("grow", "I"), ("grow", "N")), False),
    ("Coat Weapon Nyx Aspect Unlock Location",        "Nyx Aspect Unlock",       "Coat Weapon",    (("mine", "Chaos"),), False),
    ("Coat Weapon Selene Aspect Unlock Location",     "Selene Aspect Unlock",    "Coat Weapon",    (), False),
)

# item → (weapon, atoms, needs_familiar) for the vanilla path of _has_standard_aspect.
_STANDARD_ASPECT_BY_ITEM = {
    item: (weapon, atoms, needs_familiar)
    for _loc, item, weapon, atoms, needs_familiar in _STANDARD_ASPECT_DATA
}

# weapon → its two standard aspect items (the pair the hidden reveal chain requires).
_WEAPON_STANDARD_ITEMS = {
    weapon: tuple(item for _l, item, w, _a, _f in _STANDARD_ASPECT_DATA if w == weapon)
    for _loc, _item, weapon, _atoms, _needs in _STANDARD_ASPECT_DATA
}


def _reveal_gate_ok(state, reveal, player, options) -> bool:
    if reveal == "surface":
        return state._has_surface_access(player, options)
    if reveal == "door":
        return state._has_surface_door(player, options)
    return True


def handle_ingredients(world, player: int, options) -> None:
    """Gate cost-bearing locations on the capability and reach their vanilla costs imply."""

    def atoms_rule(atoms):
        return lambda state, ats=atoms: all(
            state._has_ingredient(a, player, options) for a in ats
        )

    # Cauldron incantations (the surface-lock two are owned by the toggle below).
    if options.cauldronsanity:
        for loc_name, atoms in _INCANTATION_INGREDIENTS.items():
            if loc_name in ("Permeation of Witching-Wards", "Unraveling a Fateful Bond"):
                continue
            try:
                location = world.get_location(loc_name, player)
            except KeyError:
                continue  # e.g. Summoning of Mercantile Fortune under unlock_broker
            add_rule(location, atoms_rule(atoms))

    if options.lock_surface_incantations:
        for loc_name in ("Permeation of Witching-Wards", "Unraveling a Fateful Bond"):
            add_rule(
                world.get_location(loc_name, player),
                atoms_rule(_INCANTATION_INGREDIENTS[loc_name]),
            )

    # Weapon shop: costs + purchase sequencing.
    if options.weaponsanity:
        for loc_name, atoms, prereq_weapons in _WEAPON_SHOP_RULES:
            try:
                location = world.get_location(loc_name, player)
            except KeyError:
                continue  # the initial weapon has no shop location
            add_rule(location, lambda state, ats=atoms, ws=prereq_weapons: (
                all(state._has_ingredient(a, player, options) for a in ats)
                and all(state._has_weapon(w, player, options) for w in ws)
            ))

    # Tool shop: the tab itself needs Night's Craftwork, then each tool's cost.
    if options.toolsanity:
        for loc_name, atoms in _TOOL_SHOP_RULES:
            add_rule(world.get_location(loc_name, player), lambda state, ats=atoms: (
                state._has_incantation("Night's Craftwork", player, options)
                and all(state._has_ingredient(a, player, options) for a in ats)
            ))

    # Hidden aspects: the faithful vanilla reveal chain (system + both standards + all six
    # weapons + reach god + rank-5 Nightmare + cost).
    if options.hidden_aspectsanity:
        for loc_name, _item, weapon, atoms, reveal in _HIDDEN_ASPECT_DATA:
            add_rule(world.get_location(loc_name, player),
                     lambda state, w=weapon, ats=atoms, rev=reveal:
                     state._can_unlock_hidden_aspect(w, ats, rev, player, options))

    # Base + standard aspects: both live in the system-gated weapon-shop category. Base
    # costs only Bones (no gathering atom); standard adds its vanilla ingredient cost.
    if options.aspectsanity:
        for loc_name, _item, weapon in _BASE_ASPECT_DATA:
            try:
                location = world.get_location(loc_name, player)
            except KeyError:
                continue  # the initial aspect has no shop location
            add_rule(location, lambda state, w=weapon: (
                state._has_weapon(w, player, options)
                and state._has_aspect_system(player, options)
            ))
        for loc_name, _item, weapon, atoms, needs_familiar in _STANDARD_ASPECT_DATA:
            try:
                location = world.get_location(loc_name, player)
            except KeyError:
                continue
            add_rule(location, lambda state, w=weapon, ats=atoms, f=needs_familiar: (
                state._has_weapon(w, player, options)
                and state._has_aspect_system(player, options)
                and (not f or state._has_familiar_system(player, options))
                and all(state._has_ingredient(a, player, options) for a in ats)
            ))


def _restrict_score_check_progression(world, player: int, options) -> None:
    """Block progression items from score/room checks while letting useful + filler fill them uniformly."""
    score_prefixes = ("Score Check ", "Underworld Score Check ", "Surface Score Check ", "Clear ")
    for loc in world.get_locations(player):
        if loc.name.startswith(score_prefixes):
            add_item_rule(loc, lambda item: not item.advancement)


def _set_weapon_clear_rules(world, player: int, options) -> None:
    """Weapon Clear checks are trackable filler; the weapon-clears goal itself is enforced client-side."""
    if not options.weaponsanity:
        return
    for weapon in weapons:
        name = f"{weapon} Clear"
        try:
            loc = world.get_location(name, player)
        except KeyError:
            continue
        add_rule(loc, lambda state, w=weapon: (
            state._has_weapon(w, player, options)
            and state._can_reach_endgame(player, options)
        ))
        add_item_rule(loc, lambda item: not item.advancement)


def set_rules(world, player: int, options) -> None:
    handle_area_logic(world, player, options)
    _restrict_score_check_progression(world, player, options)
    _set_weapon_clear_rules(world, player, options)
    world.completion_condition[player] = lambda state: state._can_get_victory(player, options)

    # One unified handler per sanity.
    handle_keepsakes(world, player, options)
    handle_hidden_aspects(world, player, options)
    handle_familiars(world, player, options)
    handle_incantations(world, player, options)
    handle_prophecies(world, player, options)
    handle_ingredients(world, player, options)

    # True Ending: the final Chronos kill needs the first kill plus the goal-incantation ingredients.
    if options.true_ending:
        add_rule(
            world.get_location("Chronos True Victory", player),
            lambda state: (
                state.has("Chronos Victory", player)
                and state.has("Gigaros", player)
                and state.has("Entropy", player)
                and state.count("Zodiac Sand", player) >= options.zodiac_sand_needed.value
            ),
        )

# Defines logic for each area / region
def handle_area_logic(world, player, options):
    area_rules = [ # ("Region name", "Boss Victory")
    ("Erebus -> Oceanus", "Hecate Victory"),
    ("Oceanus -> Fields", "Scylla Victory"),
    ("Fields -> Tartarus", "Cerberus Victory"),

    ("Ephyra -> Thessaly", "Polyphemus Victory"),
    ("Thessaly -> Olympus", "Eris Victory"),
    ("Olympus -> Summit", "Prometheus Victory"),
    ]

    for entrance_name, victory_item in area_rules:
        add_rule(world.get_entrance(entrance_name, player), lambda state, v=victory_item: state.has(v, player))

    # Requiring full surface access here keeps both surface-unlock items off the whole surface chain.
    add_rule(
        world.get_entrance("Crossroads -> Ephyra", player),
        lambda state: state._has_surface_access(player, options),  # type: ignore
    )

# Each hidden aspect can only be unlocked once the player has the corresponding weapon.
def handle_hidden_aspects(world, player, options):
    if not options.hidden_aspectsanity:
        return
    hidden_aspect_rules = [
        ("Staff Weapon Anubis Aspect Unlock Location",    "Staff Weapon"),
        ("Daggers Weapon Morrigan Aspect Unlock Location","Daggers Weapon"),
        ("Torches Weapon Supay Aspect Unlock Location",   "Torches Weapon"),
        ("Axe Weapon Nergal Aspect Unlock Location",      "Axe Weapon"),
        ("Skull Weapon Hel Aspect Unlock Location",       "Skull Weapon"),
        ("Coat Weapon Shiva Aspect Unlock Location",      "Coat Weapon"),
    ]
    for location_name, weapon_name in hidden_aspect_rules:
        add_rule(
            world.get_location(location_name, player),
            lambda state, w=weapon_name: state._has_weapon(w, player, options),
        )


# Familiar recruits only need _has_familiar_system; biome reach is enforced by region connectivity.
def handle_familiars(world, player, options):
    if not options.familiarsanity:
        return
    familiar_locations = (
        "Frinos Familiar Unlock Location",
        "Raki Familiar Unlock Location",
        "Toula Familiar Unlock Location",
        "Hecuba Familiar Unlock Location",
        "Gale Familiar Unlock Location",
    )
    for loc_name in familiar_locations:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_familiar_system(player, options),  # type: ignore
        )


# ── Keepsake gates ───────────────────────────────────────────────────────────
# Each keepsake is gated on its NPC's reachability; [VERIFY] rows still need cross-checking against the game data.

_KEEPSAKE_RULES_BOSS = (
    # (AP location, boss base name)
    ("Hermes Keepsake", "Hecate"),
)

_KEEPSAKE_RULES_SURFACE_ACCESS = (
    # Ephyra NPCs
    "Medea Keepsake",
    "Heracles Keepsake",
    # Thessaly NPCs
    "Circe Keepsake",
    "Eris Keepsake",          # [VERIFY] ErisGift01 may pre-date the Eris boss room
    # Olympus / surface NPCs
    "Icarus Keepsake",
    "Dionysus Keepsake",
    "Athena Keepsake",
    # Olympians whose first-pickup requires a surface trip
    "Hera Keepsake",          # RequirementsData.lua:108 — HeraUnlocked needs WorldUpgradeSurfacePenaltyCure
    "Ares Keepsake",          # AresUnlocked needs RoomsEntered.Q_Boss01 >= 1
)

_KEEPSAKE_RULES_SURFACE_DOOR = (
    "Moros Keepsake",         
)


def handle_keepsakes(world, player, options):
    """Gate every keepsake location on its NPC's reachability (Crossroads and underworld-biome NPCs need no rule)."""
    if not options.keepsakesanity:
        return

    for loc_name, boss in _KEEPSAKE_RULES_BOSS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    for loc_name in _KEEPSAKE_RULES_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    for loc_name in _KEEPSAKE_RULES_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )


# ── Incantation gates ────────────────────────────────────────────────────────
# Sourced from WorldUpgradeData.lua GameStateRequirements chains.

# Entries needing prereq incantations: (location, [incantation prereqs]) resolved via _has_incantation.
_INCANTATION_CHAIN_RULES = (
    # Group 2 — underworld biome reprieves / Erebus shops
    ("Surge of Stygian Wells",       ("Rise of Stygian Wells",)),
    ("Surge of Desecrating Pools",   ("Revival of a Desecrating Pool",)),
    ("Purification of Fountain-Waters", ("Cleansing of Fountain-Waters",)),
    ("Gathering of Subterranean Riches", ("Gathering of Ancient Bones",)),
    # Group 4 — Olympian market hub
    ("Deathly Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Kinship Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Earthly Fortune",  ("Summoning of Mercantile Fortune",)),
    ("Long Arm of the Unseen",
        ("Summoning of Mercantile Fortune", "Night's Craftwork")),
    # Group 5 — Tools / Garden chain
    ("Night's Craftwork",        ("Summoning of Mercantile Fortune",)),
    ("Greater Favor of Gaia",    ("Night's Craftwork",)),
    ("Flourishing Soil",         ("Night's Craftwork",)),
    ("Observance of Gaia's Secrets", ("Flourishing Soil",)),
    ("Rich Soil",                ("Observance of Gaia's Secrets",)),
    ("Verdant Soil",             ("Rich Soil",)),
    ("Green Hand of Gaia",       ("Observance of Gaia's Secrets",)),
    ("Greater Sowing of Gardens", ("Rich Soil",)),
    ("Greatest Gift of Gaia",
        ("Verdant Soil", "Observance of Gaia's Secrets")),
    # Group 6 — Bounty / familiar systems
    ("Abyssal Reflection",       ("Abyssal Insight",)),
    ("Bravery of Familiar Spirits", ("Faith of Familiar Spirits",)),
    # Group 8 — Hypnos chain (T3 is not an AP location — always vanilla-brewed)
    ("End to Dearest Slumber",   ("End to Deepest Slumber",)),
    # Group 9 — Misc
    ("Path to Desired Blessings",
        ("Forget-Me-Not", "Insight into Offerings")),
    ("Kindred Keepsakes",        ("Favored of All Keepsakes",)),  # [VERIFY]
)

# Entries needing a boss victory: (location, boss base name).
_INCANTATION_BOSS_RULES = (
    ("Necromantic Influence",   "Hecate"),
    ("Abyssal Insight",         "Hecate"),
    # "Faith of Familiar Spirits" is handled separately: it needs Hecate AND the three tools.
)

# Entries gated purely on surface access.
_INCANTATION_SURFACE_ACCESS = (
    # Group 1 tail
    "Greater Removal of Rubbish",
    # Group 3 — surface-gated proper
    "Summoning a Colony of Bats",
    "Rush of Fresh Air",
    "Sandy Lifespring",
    "Frozen Lifespring",
    "Rage of the Elements",
    "Arisen Troves",
    "Bounties of the Infinite Abyss",
    "Circles of Protection",
    # Group 8 — surface NPC-quest incantations
    "Purification of Crystal Clarity",
    "Return of Latent Memories",
    "Essence of Sorrow",
    # Hypnos T2's recipe is revealed by Medea (MedeaGrantsHypnosSpell01)
    "End to Dearest Slumber",
)

# Entries gated on surface access AND a prereq incantation: (location, [incantation prereqs]).
_INCANTATION_SURFACE_ACCESS_AND_CHAIN = (
    ("Surge of Fresh Air",           ("Rush of Fresh Air",)),
    ("Eyes of Night and Darkness",   ("Arisen Troves", "Exhumed Troves",)), 
    ("Circles of the Moon",          ("Circles of Protection",)),
    ("Alteration of Familiar Forms", ("Faith of Familiar Spirits",)),  # [VERIFY]
)

# Entries gated on the surface door only (Moros doesn't need the cure).
_INCANTATION_SURFACE_DOOR = (
    "Doomed Beckoning",         # MorosUnlock
)

# Rivals chain: (location, [bosses], requires_surface); T4 is excluded from the pool under true_ending. [VERIFY] boss triples for T2/T3.
_INCANTATION_RIVALS_RULES = (
    ("Rivals of Depth and Sea",   ("Scylla", "Eris"),             True),
    ("Rivals of Plain and Peak",  ("Prometheus", "Cerberus"),     True),
    ("Rivals of Old and Rot",     ("Chronos", "Typhon"),          True),
)


def handle_incantations(world, player, options):
    """Gate cauldron-incantation locations on their in-game prerequisites."""
    # Surface-unlock 2 — owned by lock_surface_incantations.
    if options.lock_surface_incantations:
        add_rule(
            world.get_location("Unraveling a Fateful Bond", player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    if not options.cauldronsanity:
        return

    # Intra-cauldron prereq chains.
    for loc_name, prereqs in _INCANTATION_CHAIN_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: all(
                state._has_incantation(p, player, options) for p in ps  # type: ignore
            ),
        )

    # Boss-victory gates.
    for loc_name, boss in _INCANTATION_BOSS_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    # Familiar-system incantation: Hecate AND the three tools.
    add_rule(
        world.get_location("Faith of Familiar Spirits", player),
        lambda state: (
            state._has_boss("Hecate", player)  # type: ignore
            and state._has_familiar_tools(player, options)  # type: ignore
        ),
    )

    # Surface-access-only gates.
    for loc_name in _INCANTATION_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    # Surface-access AND prereq incantation.
    for loc_name, prereqs in _INCANTATION_SURFACE_ACCESS_AND_CHAIN:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: (
                state._has_surface_access(player, options)  # type: ignore
                and all(state._has_incantation(p, player, options) for p in ps)  # type: ignore
            ),
        )

    # Surface-door only.
    for loc_name in _INCANTATION_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    # Rivals tiers — boss list + optional surface gate.
    for loc_name, bosses, requires_surface in _INCANTATION_RIVALS_RULES:
        # T4 is removed from the pool under true_ending; skip if not present.
        try:
            location = world.get_location(loc_name, player)
        except KeyError:
            continue
        add_rule(
            location,
            lambda state, bs=bosses, surf=requires_surface: (
                all(state._has_boss(b, player) for b in bs)  # type: ignore
                and (state._has_surface_access(player, options) if surf else True)  # type: ignore
            ),
        )


# ── Prophecy gates ───────────────────────────────────────────────────────────
# Mirrors handle_incantations, sourced from QuestData.lua requirement chains.

_PROPHECY_BOSS_RULES = (
    # Group A — boss-defeat
    ("Witch of the Crossroads",  "Hecate"),
    ("Temporary Setback",        "Chronos"),
    ("Storm in the Heavens",     "Typhon"),
    ("Den Mother",               "Hecate"),   # [VERIFY] coarse — also requires 2 cleared runs
    # Group F — system unlocks gated post-Hecate
    ("Visions of Victory",       "Hecate"),   # [VERIFY] ChaosGrantsBountyBoard01
    ("Whims of Chaos",           "Hecate"),   # [VERIFY] coarse — BountyBoard already viewed
    ("Familiar Confidant",       "Hecate"),   # [VERIFY] HecateHideAndSeek03
    ("Close Companions",         "Hecate"),   # [VERIFY] HecateBossGrantsFamiliarSystem01
    ("Keeper of Shadows",        "Hecate"),
    ("Improbable Outcomes",      "Hecate"),   # [VERIFY] coarse — ChaosGift06 + bounty board
)

# (location, boss, (prereq "X Reward" item names)); each prereq must be in Items.PROGRESSION_PROPHECY_ITEMS so state.has() can see it.
_PROPHECY_BOSS_AND_CHAIN_RULES = (
    ("Natural Talent",      "Hecate",  ("Witch of the Crossroads Reward",)),  # QuestBeatHecateWithoutArcana → QuestBeatHecate
    ("Arcana of the Ages",  "Chronos", ("Temporary Setback Reward",)),         # QuestBeatChronosWithArcana → QuestFirstUnderworldClear
    ("Beyond Familiar",     "Hecate",  ("Close Companions Reward",)),          # QuestUpgradeFamiliars → QuestRecruitFamiliars
)

# Boss A OR boss B (Chronos or Typhon — either route can complete).
_PROPHECY_BOSS_OR_RULES = (
    ("Born to Win",        ("Chronos", "Typhon")),
)

# Surface-access only.
_PROPHECY_SURFACE_ACCESS = (
    # Group A
    "Unrivaled Prowess",      # [VERIFY] also wants BossEris02 etc. EM2 grind
    "Shadow of Doom",
    # Group B — surface-only Olympians
    "Mistress of Battle",     # [VERIFY] Athena
    "Master of Revelry",      # [VERIFY] Dionysus
    # Group C — NPC-bond on surface
    "Haunted by the Past",
    "Voice and Vanity",
    "Bitter Tears",           # [VERIFY] MedeaAboutConcoctionQuest01
    "Weaver of Fineries",
    "Denier of Suitors",
    "Voice of Truth",
    "Witch of Shadows",
    "Witch of Changing",
    "Wings of Freedom",
    # Group D — hidden-aspect deliveries through surface NPCs
    "The Jackal's Aspect",    # [VERIFY] Anubis path
    "The Shadow's Aspect",    # [VERIFY] Supay path
    "The Grave's Aspect",     # [VERIFY] Hel path
)

# Surface-access AND a specific boss.
_PROPHECY_SURFACE_ACCESS_AND_BOSS = (
    ("Silk and Spitefulness", "Hecate"),
    ("Drowned Ambitions",     "Scylla"),    # [VERIFY] CirceAboutScyllaQuest01
    ("Nobody but Nobody",     "Polyphemus"),
)

# Surface-door only (Moros).
_PROPHECY_SURFACE_DOOR = (
    "Harbinger of Doom",      # QuestUnlockMoros
)

# Incantation-system gates (Group F-ish).
_PROPHECY_INCANTATION_RULES = (
    ("Note to Self",          ("Forget-Me-Not",)),
    ("Valued Customer",       ("Rise of Stygian Wells",)),
    ("Spectral Forms",        ("Necromantic Influence",)),
)

# Weapon-unlock and hammer prophecies: completing them needs the weapon obtainable.
_PROPHECY_WEAPON_RULES = (
    ("The Witch's Staff",     "Staff Weapon"),
    ("The Sister Blades",     "Daggers Weapon"),
    ("The Umbral Flames",     "Torches Weapon"),
    ("The Moonstone Axe",     "Axe Weapon"),
    ("The Argent Skull",      "Skull Weapon"),
    ("The Black Coat",        "Coat Weapon"),
    ("Blades of Pure Silver", "Daggers Weapon"),   # QuestUnlockDagger
)

# Hidden-aspect delivery prophecies: unlocked by owning the aspect.
_PROPHECY_ASPECT_DELIVERY_RULES = (
    ("The Jackal's Aspect",    "Anubis Aspect Unlock"),
    ("The Crow's Aspect",      "Morrigan Aspect Unlock"),
    ("The Shadow's Aspect",    "Supay Aspect Unlock"),
    ("The Warrior's Aspect",   "Nergal Aspect Unlock"),
    ("The Grave's Aspect",     "Hel Aspect Unlock"),
    ("The Destroyer's Aspect", "Shiva Aspect Unlock"),
)

# Base-aspect rank-5 chain costs per initial weapon.
_INITIAL_WEAPON_RANK5_ATOMS = {
    0: (("mine", "F"),),                     # Staff: Silver only
    1: (("mine", "F"),),                     # Daggers: Silver + Fabric
    2: (("mine", "F"), ("boss", "Hecate")),  # Torches: Silver + Nightmare
    3: (("mine", "F"), ("mine", "N")),       # Axe: Silver + Bronze
    4: (("mine", "G"),),                     # Skull: Limestone + Ash
    5: (("mine", "P"), ("boss", "Hecate")),  # Coat: Adamant + Nightmare
}

# Sword of the Night: Typhon Victory AND every weapon AND the Temporary Setback prereq.
def _sword_of_the_night_rule(state, player, options):
    if not state._has_boss("Typhon", player):  # type: ignore
        return False
    if not state._has_enough_weapons(player, options, 6):  # type: ignore
        return False
    return state.has("Temporary Setback Reward", player)  # type: ignore


# Bearing Dark Gifts: (Chronos OR Typhon) AND The Unseen Sentinel Reward.
def _bearing_dark_gifts_rule(state, player, options):
    if not (state._has_boss("Chronos", player) or state._has_boss("Typhon", player)):  # type: ignore
        return False
    return state.has("The Unseen Sentinel Reward", player)  # type: ignore


# Tools of the Unseen (QuestToolsUnlocks): completes on owning all four tools.
def _tools_of_the_unseen_rule(state, player, options):
    return state._has_all_tools(player, options)  # type: ignore


# Precision Instrument: all four tool level-2 upgrade costs plus the Gaia incantations and the Tools of the Unseen reward.
_PRECISION_INSTRUMENT_ATOMS = (
    ("mine", "H"), ("mine", "I"), ("mine", "N"), ("mine", "O"), ("mine", "Q"),
    ("grow", "P"), ("pick", "O"),
)


def _precision_instrument_rule(state, player, options):
    if not state._has_incantation("Greater Favor of Gaia", player, options):  # type: ignore
        return False
    if not state._has_incantation("Observance of Gaia's Secrets", player, options):  # type: ignore
        return False
    if not state._has_all_tools(player, options):  # type: ignore
        return False
    if not all(state._has_ingredient(a, player, options) for a in _PRECISION_INSTRUMENT_ATOMS):  # type: ignore
        return False
    return state.has("Tools of the Unseen Reward", player)  # type: ignore


# Denizen of the Depths: fishing capability plus River-Fording.
def _denizen_of_the_depths_rule(state, player, options):
    return (state._can_fish(player, options)  # type: ignore
            and state._has_incantation("Rite of River-Fording", player, options))  # type: ignore


# The Arms of Night (QuestUnlockAllWeapons): all six weapons obtainable.
def _arms_of_night_rule(state, player, options):
    if options.weaponsanity:
        return state._has_enough_weapons(player, options, 6)  # type: ignore
    return state._weapon_obtainable("Coat Weapon", player, options)  # type: ignore


# The Unseen Sentinel: every aspect of every weapon (atom superset of the purchasable aspect costs).
_UNSEEN_SENTINEL_ATOMS = (
    ("mine", "Q"), ("mine", "I"), ("grow", "Q"), ("grow", "I"),
)


def _unseen_sentinel_rule(state, player, options):
    if not _arms_of_night_rule(state, player, options):
        return False
    if not state._has_incantation("Aspects of Night and Darkness", player, options):  # type: ignore
        return False
    if not all(state._has_ingredient(a, player, options) for a in _UNSEEN_SENTINEL_ATOMS):  # type: ignore
        return False
    return all(
        state._has_hidden_aspect(item, player, options)  # type: ignore
        for _loc, item, _w, _a, _r in _HIDDEN_ASPECT_DATA
    )


# Awakened Aspect: rank 5 on any aspect via the initial weapon's base aspect chain.
def _awakened_aspect_rule(state, player, options):
    if not state._has_incantation("Aspects of Night and Darkness", player, options):  # type: ignore
        return False
    atoms = _INITIAL_WEAPON_RANK5_ATOMS[options.initial_weapon.value]
    return all(state._has_ingredient(a, player, options) for a in atoms)  # type: ignore


# All five familiar items (promoted to progression under familiarsanity).
_FAMILIAR_ITEMS = (
    "Frinos Familiar", "Raki Familiar", "Toula Familiar",
    "Hecuba Familiar", "Gale Familiar",
)


# Soundest of Slumbers: the full Hypnos wake chain, including the always-vanilla T3 brew.
def _soundest_of_slumbers_rule(state, player, options):
    if not state._has_incantation("End to Deepest Slumber", player, options):  # type: ignore
        return False
    if not state._has_incantation("End to Dearest Slumber", player, options):  # type: ignore
        return False
    if not state._has_surface_access(player, options):  # type: ignore
        return False
    return all(
        state._has_ingredient(a, player, options)  # type: ignore
        for a in _INCANTATION_INGREDIENTS["End to Dumbest Slumber"]
    )


# Beyond Familiar: the upgrade system plus an owned familiar.
def _beyond_familiar_extra_rule(state, player, options):
    if not state._has_incantation("Bravery of Familiar Spirits", player, options):  # type: ignore
        return False
    if options.familiarsanity:
        return state.has_any(_FAMILIAR_ITEMS, player)  # type: ignore
    return True


# Close Companions: 3 of 5 familiars owned.
def _close_companions_extra_rule(state, player, options):
    if options.familiarsanity:
        return state.has_from_list(_FAMILIAR_ITEMS, player, 3)  # type: ignore
    return state._has_familiar_system(player, options)  # type: ignore


# Den Mother: clear runs with all five familiars.
def _den_mother_extra_rule(state, player, options):
    if options.familiarsanity:
        return state.has_all(_FAMILIAR_ITEMS, player)  # type: ignore
    return (state._has_familiar_system(player, options)  # type: ignore
            and state._can_farm_biome("G", player, options)  # type: ignore
            and state._can_farm_biome("H", player, options)  # type: ignore
            and state._can_farm_biome("P", player, options))  # type: ignore


def handle_prophecies(world, player, options):
    """Gate every prophecy location on its in-game completion prerequisites."""
    if not options.fatesanity:
        return

    for loc_name, boss in _PROPHECY_BOSS_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: state._has_boss(b, player),  # type: ignore
        )

    # Boss-victory AND prereq prophecy cashed out (chain on another quest).
    for loc_name, boss, prereqs in _PROPHECY_BOSS_AND_CHAIN_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss, ps=prereqs: (
                state._has_boss(b, player)  # type: ignore
                and all(state.has(p, player) for p in ps)  # type: ignore
            ),
        )

    for loc_name, bosses in _PROPHECY_BOSS_OR_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, bs=bosses: any(
                state._has_boss(b, player) for b in bs  # type: ignore
            ),
        )

    for loc_name in _PROPHECY_SURFACE_ACCESS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_access(player, options),  # type: ignore
        )

    for loc_name, boss in _PROPHECY_SURFACE_ACCESS_AND_BOSS:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, b=boss: (
                state._has_surface_access(player, options)  # type: ignore
                and state._has_boss(b, player)  # type: ignore
            ),
        )

    for loc_name in _PROPHECY_SURFACE_DOOR:
        add_rule(
            world.get_location(loc_name, player),
            lambda state: state._has_surface_door(player, options),  # type: ignore
        )

    for loc_name, prereqs in _PROPHECY_INCANTATION_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, ps=prereqs: all(
                state._has_incantation(p, player, options) for p in ps  # type: ignore
            ),
        )

    # Weapon-unlock / hammer prophecies.
    for loc_name, weapon in _PROPHECY_WEAPON_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, w=weapon: state._weapon_obtainable(w, player, options),  # type: ignore
        )

    # Hidden-aspect deliveries.
    for loc_name, aspect_item in _PROPHECY_ASPECT_DELIVERY_RULES:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, a=aspect_item: state._has_hidden_aspect(a, player, options),  # type: ignore
        )

    named_rules = (
        ("Sword of the Night",      _sword_of_the_night_rule),
        ("Bearing Dark Gifts",      _bearing_dark_gifts_rule),
        ("Tools of the Unseen",     _tools_of_the_unseen_rule),
        ("Precision Instrument",    _precision_instrument_rule),
        ("Denizen of the Depths",   _denizen_of_the_depths_rule),
        ("The Arms of Night",       _arms_of_night_rule),
        ("The Unseen Sentinel",     _unseen_sentinel_rule),
        ("Awakened Aspect",         _awakened_aspect_rule),
        ("Soundest of Slumbers",    _soundest_of_slumbers_rule),
        ("Beyond Familiar",         _beyond_familiar_extra_rule),
        ("Close Companions",        _close_companions_extra_rule),
        ("Den Mother",              _den_mother_extra_rule),
    )
    for loc_name, rule_fn in named_rules:
        add_rule(
            world.get_location(loc_name, player),
            lambda state, fn=rule_fn: fn(state, player, options),
        )