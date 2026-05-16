# Hades II Setup Guide

## Required Software

- **Hades II** on Steam.
- **[r2modmanPlus](https://thunderstore.io/c/hades-ii/)** — the mod
  manager used to install the game mod and its dependencies. Create a
  Hades II profile in r2modman before continuing.
- **`Tenacer_AP / HadesII_AP`** mod (search for `HadesII_AP` in
  r2modman's Online tab). Installing it auto-pulls its dependencies:
  Hell2Modding, LuaENVY, SGG_Modding-ModUtil, ReLoad, SJSON, and Chalk.
- **Archipelago** client, minimum version `0.6.4`.
- **`hades_ii.apworld`** — download the latest release from
  [Tenacer/Archipelago-HadesII](https://github.com/Tenacer/Archipelago-HadesII/releases).
  The release also bundles preset YAML files (see "Configuring your YAML
  file" below).

## Installation

1. Install r2modmanPlus and create a Hades II profile.
2. In r2modman's **Online** tab, search for `HadesII_AP` and click
   **Install**. The dependency mods install automatically.
3. Drop `hades_ii.apworld` into Archipelago's `custom_worlds/` folder
   (next to your Archipelago install — same place you keep other
   community apworlds).
4. Launch Hades II from r2modman using **Start modded**. This boots the
   game with the Lua mod loaded; running it from Steam directly will
   start it unmodded.

## Configuring your YAML file

### What is a YAML file and why do I need one?

Your YAML file contains the configuration options that tell the
Archipelago generator how to build your slot of the multiworld. Each
player provides their own YAML, so different players in the same seed
can play with different options.

### Where do I get a YAML file?

Hades II is a **non-core** Archipelago game, so the Archipelago website
does not yet have a player-options page that generates a YAML for you.
Instead, the `hades_ii.apworld` GitHub release bundles four preset YAML
templates — pick the one that matches the experience you want and edit
it from there:

- **Easy** — friendlier filler values, no hidden aspects or fates,
  lighter fear floor. A good first run.
- **Normal** — balanced filler amounts, hidden aspects on, light traps.
- **Hard** — full sanity coverage (hidden aspects + fates), tight filler
  amounts, high fear floor, more traps.
- **True Ending** — Boss Defeats off, True Ending goal on. Includes
  Zodiac Sand / Void Lens / Gigaros / Entropy as progression items.

Drop your chosen YAML into Archipelago's `Players/` folder (the same
folder you use for any other game's YAML).

## Joining a MultiWorld game

1. Generate the seed with `Generate.py` (or have your host do it) and
   start the room. The room serves on a host:port the way every other
   Archipelago room does.
2. Open the **Archipelago Launcher** and click the **Hades II Client**
   entry. (The component is registered by the apworld, so it only
   appears once `hades_ii.apworld` is in `custom_worlds/`.)
3. In the client window, connect with `/connect host:port slotname` (or
   the GUI fields).
4. **Connect AP first, then launch the modded game from r2modman.** On
   connect, the client writes `ap_settings.json` and scouts incantation,
   prophecy, and boss-reward locations so the in-game UI can show the
   correct item names. If you start the game before the client is
   connected, names fall back to a generic placeholder until you restart.

## Troubleshooting

- **Game-side logs.** The mod writes to
  `ReturnOfModding/plugins_data/Tenacer_AP-HadesII_AP/LogOutput.log` in
  your r2modman profile. Lines prefixed with `[HadesII_AP]` cover check
  sends, item receives, and goal status — start there if something seems
  out of sync.
- **`/resync` in the client.** If a disconnect leaves the client behind
  on location checks, run `/resync` in the AP client to re-read the
  game's outbox file and re-send anything pending.
- **Display names show a generic placeholder.** Restart Hades II from
  r2modman *after* the AP client is connected — the cauldron, Fated
  List, and boss-reward presentations read names from a scout file
  written when the client connects.
