# Hades II

## Where is the options page?

Hades II is a non-core game, so it is not yet hosted on the Archipelago
website. Build your YAML from the preset templates bundled with the
[hades_ii.apworld release](https://github.com/Tenacer/Archipelago-HadesII/releases)
(see the setup guide for details).

## What does randomization do to this game?

Many of the persistent things Melinoë normally unlocks across runs can be
shuffled into the Archipelago item pool, each behind its own option:

- **Keepsakes** (`keepsakesanity`) — every keepsake becomes an AP item; the
  check fires when the gifting conversation completes with the matching NPC.
- **Weapons** (`weaponsanity`) — the witch's tools have to arrive from AP
  before they can be equipped. Buying their unlock at the weapon shop fires
  the check.
- **Hidden aspects** (`hidden_aspectsanity`) — the third aspect on each
  weapon is split off as its own item and check.
- **Incantations** (`cauldronsanity`) — the cauldron page hides each
  incantation until AP delivers it; brewing then fires the check normally.
- **Surface incantations** (`lock_surface_incantations`, default on) — the
  two surface-unlock incantations (*Permeation of Witching-Wards* and
  *Unraveling a Fateful Bond*) are gated behind their own AP items even
  when full cauldronsanity is off, so the surface biome is a real
  progression step.
- **Prophecies** (`fatesanity`) — completing and cashing out a prophecy
  fires an AP check; the resource reward is delivered by AP instead.

Rooms also count toward a **score system**: every cleared room earns
points, and reaching a score milestone fires an AP check (configurable
with `score_rewards_amount`). Score checks hold ordinary randomised
items, progression included — each route's checks are spread across that
route's four biomes in logic, so later checks sit behind deeper
progress. The deepest eighth of each route is the exception: those are
the longest grind, so they only ever hold non-progression items. By
default the score is
**split per route** (`score_split_mode`): the underworld route (Erebus →
Tartarus, the Chronos path) and the surface route (Ephyra → Summit, the
Typhon path) each accumulate their own score and can only earn their own
share of the checks (`surface_score_ratio`, default 40% to the surface),
so earning every score check means playing both routes. In separate mode
the checks are named per route — *Underworld Score Check N* and *Surface
Score Check N* — so the route is visible in the client and on trackers, and
the in-game toast names which route's score you're building. Set
`score_split_mode` to *combined* for a single *Score Check N* pool where
either route can earn all of them.

In **True Ending** mode, the rewards normally dropped after each Chronos
and Typhon kill are replaced with AP location checks (one per kill, up to
`chronos_kills_needed` and `typhon_kills_needed`).

## What is the goal of the game?

Two goal modes are available (selected with `true_ending`, which is **on by
default** — the default goal is True Ending):

- **Boss Defeats** — clear Chronos and/or Typhon a configurable number of
  times. `boss_defeats_mode` switches between *combined* (either boss
  counts) and *separate* (both must be cleared the requested number of
  times).
- **True Ending** — collect the keys required to brew the two final
  incantations (*Dissolution of Time* and *Disintegration of Monstrosity*)
  and let the game's True Ending sequence play out. The progression items
  for this path are Zodiac Sand, Void Lens, Gigaros, Entropy, and the two
  goal incantations themselves.

## Do I need to start from a fresh file or a completed one?

A **fresh save** is needed.

## Which items can be in another player's world?

Depending on the options selected, the following items can be shuffled into
other players' worlds:

- Keepsakes, weapons, hidden aspects
- Incantations (including the two surface-unlock incantations)
- Prophecy rewards
- True Ending progression items 
- Vow items (only in `reverse_fear` mode)
- Filler resource packs (Ash, Bones, Psyche, Nectar, Ambrosia, Moon Dust,
  Nightmare, Fate Fabric) and helper packs

## What does another world's item look like?

Incantation entries in the cauldron, prophecy entries in the Fated List,
keepsake gifting presentations, and the special True-Ending boss-reward
drops all carry the Archipelago logo when the location holds another
world's item. The display name is rewritten to read "Item Name [Player]"
so you know who you are about to send to.

## When the player receives an item, what happens?

Every AP packet surfaces in-game on a console-style notification overlay,
colour-coded by event type (sent / received / score tick / milestone).
Resources and filler packs are credited to their counters directly;
keepsakes become equippable in the Training Grounds the moment they
arrive; weapons and hidden aspects light up in their respective shops;
incantations appear in the cauldron once their gate flag flips.

## What settings can I change in the YAML?

The world ships with **six presets** — **Easy**, **Normal**, and **Hard**
for each of the two goal modes:

- **True Ending Easy / Normal / Hard**
- **Boss Defeats Easy / Normal / Hard**

The difficulty tier sets resource generosity, starting Fear, trap share,
score-check count (Hard offers the most, 250), and scope (e.g. Easy turns
off hidden aspects and traps; Hard turns on fatesanity and is the
stingiest). The goal tier sets the win condition and its thresholds: Boss
Defeats scales the required kill count (Easy counts both bosses together;
Normal and Hard count Chronos and Typhon separately), and True Ending
scales the ingredient costs and per-boss kill counts.

The **default** (a bare YAML with no preset chosen) is **True Ending
Normal** — the recommended starting point. From there, every "sanity"
toggle, score amount, score-split mode, fear-system mode, per-resource pack
value, and goal threshold can be adjusted individually. See the preset
YAMLs in the release for a starting point.
