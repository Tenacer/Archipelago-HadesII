#!/usr/bin/env python3
"""Regenerate the room_clear / room_weapon_clear rows in data/locations.csv.

Re-runnable: drops the existing room rows and re-appends fresh ones (non-room
ids stay stable). Each room depth is assigned to the biome region that owns it,
so the apworld's boss-victory entrance rules gate it exactly as in-game.

The bounds below MUST stay in sync with {UNDERWORLD,SURFACE}_BIOME_BOUNDS and
ROOM_WEAPON_TOKENS in Locations.py (kept here as plain data so the script runs
standalone, without the Archipelago import environment).
"""
import csv
import os

CSV = os.path.join(os.path.dirname(__file__), "..", "data", "locations.csv")
CSV = os.path.abspath(CSV)

# (region, last_run_depth) per route — keep in sync with Locations.py.
UNDERWORLD_BIOME_BOUNDS = [("Erebus", 11), ("Oceanus", 20), ("Fields", 25), ("Tartarus", 40)]
SURFACE_BIOME_BOUNDS    = [("Ephyra", 11), ("Thessaly", 19), ("Olympus", 29), ("Summit", 36)]
WEAPON_TOKENS = ["Staff", "Daggers", "Torches", "Axe", "Skull", "Coat"]

ROUTES = [("Underworld", UNDERWORLD_BIOME_BOUNDS), ("Surface", SURFACE_BIOME_BOUNDS)]
ROOM_CATEGORIES = {"room_clear", "room_weapon_clear"}


def region_for(bounds, depth):
    for region, last in bounds:
        if depth <= last:
            return region
    return bounds[-1][0]


def main():
    with open(CSV, newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]

    kept = [r for r in data if len(r) < 4 or r[3] not in ROOM_CATEGORIES]
    next_id = max(int(r[0]) for r in kept if r[0].isdigit()) + 1

    new = []
    # room_clear: one set per route, region by depth.
    for route, bounds in ROUTES:
        for depth in range(1, bounds[-1][1] + 1):
            new.append([str(next_id), f"Clear {route} Room {depth:02d}",
                        region_for(bounds, depth), "room_clear"])
            next_id += 1
    # room_weapon_clear: room_clear set x 6 weapons.
    for weapon in WEAPON_TOKENS:
        for route, bounds in ROUTES:
            for depth in range(1, bounds[-1][1] + 1):
                new.append([str(next_id), f"Clear {route} Room {depth:02d} {weapon}",
                            region_for(bounds, depth), "room_weapon_clear"])
                next_id += 1

    with open(CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(kept)
        w.writerows(new)

    print(f"Wrote {len(kept)} kept + {len(new)} room rows to {CSV}")


if __name__ == "__main__":
    main()
