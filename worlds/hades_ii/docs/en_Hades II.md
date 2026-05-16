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
points, and reaching a score milestone fires a filler-item check
(configurable with `score_rewards_amount`).

In **True Ending** mode, the rewards normally dropped after each Chronos
and Typhon kill are replaced with AP location checks (one per kill, up to
`chronos_kills_needed` and `typhon_kills_needed`).

## What is the goal of the game?

Two goal modes are available:

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

A **fresh save** is strongly recommended. The mod injects story flags into
`GameState.TextLinesRecord` as it delivers progression items (e.g.
ZagreusPastMeeting flags when Zodiac Sand arrives) so that the vanilla
story gating lines up with AP item flow. On a completed save those flags
are already set, which can confuse some intermediate cutscenes.

## Which items can be in another player's world?

Depending on the options selected, the following items can be shuffled into
other players' worlds:

- Keepsakes, weapons, hidden aspects
- Incantations (including the two surface-unlock incantations and, in
  True Ending mode, the two goal incantations)
- Prophecy rewards
- True Ending progression items (Zodiac Sand, Void Lens, Gigaros, Entropy)
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

The world ships with four presets — **Easy**, **Normal**, **Hard**, and
**True Ending** — covering common difficulty/scope combinations. From
there, every "sanity" toggle, score amount, fear-system mode, per-resource
pack values, and goal threshold can be adjusted individually. See the
preset YAMLs in the release for a starting point.
