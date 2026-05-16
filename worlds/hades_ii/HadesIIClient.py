"""
Hades II Archipelago Client
Bridges the Hades II game mod (via JSON files in the OS user-data dir, e.g.
~/.local/share/HadesII_AP/ on Linux or %LOCALAPPDATA%\\HadesII_AP\\ on Windows)
with the AP server. The location can be overridden via the `hades_ii_options.ipc_directory`
setting in host.yaml.
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import Utils
from CommonClient import (
    CommonContext,
    ClientCommandProcessor,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from NetUtils import ClientStatus

from .Locations import (
    SCORE_LOCATION_COUNT,
    hades_ii_base_location_id,
    location_table,
)

POLL_INTERVAL = 0.5

# name→id for every non-event location; used to resolve names from the outbox
_LOCATION_NAME_TO_ID = {name: d.code for name, d in location_table.items() if d.code is not None}

# id→name for locations whose item placements we display in-game (cauldron / Fated List)
_INCANTATION_LOCATION_IDS: dict = {
    d.code: name for name, d in location_table.items()
    if d.category == "incantation" and d.code is not None
}
_PROPHECY_LOCATION_IDS: dict = {
    d.code: name for name, d in location_table.items()
    if d.category == "prophecy" and d.code is not None
}
# Boss kill reward locations are scouted so the Lua mod can decide whether to
# spawn the AP icon obstacle (other player's item, or our own non-resource item)
# or the matching vanilla resource-drop obstacle (when the placed item is one
# of our own resources like Zodiac Sand / Void Lens / etc).
_BOSS_REWARD_LOCATION_IDS: dict = {
    d.code: name for name, d in location_table.items()
    if d.category == "boss_reward" and d.code is not None
}
_SCOUTABLE_LOCATION_IDS: dict = {
    **_INCANTATION_LOCATION_IDS,
    **_PROPHECY_LOCATION_IDS,
    **_BOSS_REWARD_LOCATION_IDS,
}


def _platform_default_ipc_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "HadesII_AP"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "HadesII_AP"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "HadesII_AP"


def get_ipc_dir() -> Path:
    try:
        from . import HadesIIWorld
        override = str(HadesIIWorld.settings.ipc_directory or "").strip()
        if override:
            return Path(override).expanduser()
    except Exception:
        pass
    return _platform_default_ipc_dir()


class HadesIIClientCommandProcessor(ClientCommandProcessor):
    def _cmd_score(self):
        """Show current score and checks sent from the game."""
        outbox = self.ctx._ipc_file("ap_out.json") if isinstance(self.ctx, HadesIIContext) else get_ipc_dir() / "ap_out.json"
        if not outbox.exists():
            logger.info("No outbox found — is the game running with the mod?")
            return
        try:
            with open(outbox) as f:
                data = json.load(f)
            logger.info(
                f"Score: {data.get('score', 0)} | "
                f"Checks sent: {data.get('checks_sent', 0)} | "
                f"Items received: {data.get('items_index', 0)}"
            )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Could not read outbox: {e}")

    def _cmd_resync(self):
        """Re-read the outbox and re-send all pending checks to the server."""
        if isinstance(self.ctx, HadesIIContext):
            Utils.async_start(self.ctx.resync())

    def _cmd_deathlink(self) -> bool:
        """Toggle DeathLink for this session."""
        if isinstance(self.ctx, HadesIIContext):
            self.ctx.deathlink_enabled = not self.ctx.deathlink_enabled
            self.ctx.deathlink_client_override = True
            Utils.async_start(self.ctx.update_death_link(self.ctx.deathlink_enabled))
        return True


class HadesIIContext(CommonContext):
    game = "Hades II"
    command_processor = HadesIIClientCommandProcessor
    items_handling = 0b111  # full — receive all items including starting inventory

    def __init__(self, server_address: str, password: Optional[str]):
        super().__init__(server_address, password)
        self.ipc_dir = get_ipc_dir()
        self.ipc_dir.mkdir(exist_ok=True)
        self.deathlink_client_override = False
        self._world_id: Optional[str] = None
        self._last_checks_sent = 0
        self._sent_named_location_ids: set = set()
        self._sent_hint_location_ids: set = set()
        self._last_death_count = 0
        self._sent_goal = False

    def _ipc_file(self, name: str) -> Path:
        """Return the world-specific path for an IPC file (e.g. ap_in_seed_1.json)."""
        if self._world_id:
            base, ext = name.rsplit(".", 1)
            return self.ipc_dir / f"{base}_{self._world_id}.{ext}"
        return self.ipc_dir / name

    # ── AP server callbacks ───────────────────────────────────────────────────

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "RoomInfo":
            self.seed_name = args.get("seed_name")
        elif cmd == "Connected":
            slot_data = args.get("slot_data", {})
            world_id = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{self.seed_name}_{self.slot}")
            self._world_id = world_id
            logger.info(f"World ID: {world_id}")
            self._write_settings(slot_data)
            self._write_inbox()
            # Enable DeathLink if the slot data says so (and the player hasn't overridden it)
            if not self.deathlink_client_override and slot_data.get("death_link"):
                Utils.async_start(self.update_death_link(True))
            # Scout incantation/prophecy locations so the game mod can display
            # AP item names. Boss reward locations are scouted in TrueEnding mode
            # so the mod can pick the matching obstacle on each boss kill.
            to_scout: list = []
            if slot_data.get("cauldronsanity") == 1:
                to_scout.extend(_INCANTATION_LOCATION_IDS.keys())
            if slot_data.get("fatesanity") == 1:
                to_scout.extend(_PROPHECY_LOCATION_IDS.keys())
            if slot_data.get("true_ending"):
                chronos_n = slot_data.get("chronos_kills_needed", 7)
                typhon_n = slot_data.get("typhon_kills_needed", 5)
                for name, loc_id in [(n, i) for i, n in _BOSS_REWARD_LOCATION_IDS.items()]:
                    # name pattern is "Chronos Kill Reward N" / "Typhon Kill Reward N"
                    parts = name.rsplit(" ", 1)
                    if len(parts) != 2 or not parts[1].isdigit():
                        continue
                    idx = int(parts[1])
                    if name.startswith("Chronos") and idx <= chronos_n:
                        to_scout.append(loc_id)
                    elif name.startswith("Typhon") and idx <= typhon_n:
                        to_scout.append(loc_id)
            if to_scout:
                Utils.async_start(self._scout_locations(to_scout))
        elif cmd == "LocationInfo":
            self._write_location_items(args)
        elif cmd == "ReceivedItems":
            self._write_inbox()
        elif cmd == "Bounced":
            # DeathLink bounce from another player
            if "DeathLink" in args.get("tags", []) and "DeathLink" in self.tags:
                self._handle_incoming_deathlink(args)

    # ── Settings (slot data → game mod) ──────────────────────────────────────

    def _write_settings(self, slot_data: dict):
        """Write the AP slot data so the Lua mod can read its configuration."""
        data = dict(slot_data)
        data["world_id"] = self._world_id
        path = self.ipc_dir / "ap_settings.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Wrote slot data to ap_settings.json (world_id={self._world_id})")

    # ── Inbox (AP server → game mod) ─────────────────────────────────────────

    def _write_inbox(self):
        """
        Write all received items to ap_in.json.
        Each entry has: index (int), item_code (int), item_name (str).
        The Lua mod maps item_name to its internal resource IDs.
        """
        items = []
        for i, net_item in enumerate(self.items_received):
            item_name = self.item_names.lookup_in_slot(net_item.item, self.slot)
            items.append({
                "index":     i,
                "item_code": net_item.item,
                "item_name": item_name,
            })

        inbox = {
            "connected":   True,
            "items_count": len(items),
            "items":       items,
        }
        with open(self._ipc_file("ap_in.json"), "w") as f:
            json.dump(inbox, f)
        logger.debug(f"Inbox updated — {len(items)} item(s)")

    # ── DeathLink ────────────────────────────────────────────────────────────

    def _handle_incoming_deathlink(self, args: dict):
        """Append a deathlink flag to the world inbox so the Lua mod can kill Melinoë."""
        inbox_path = self._ipc_file("ap_in.json")
        try:
            with open(inbox_path) as f:
                inbox = json.load(f)
        except (OSError, json.JSONDecodeError):
            inbox = {"connected": True, "items": []}
        inbox["deathlink_seq"] = inbox.get("deathlink_seq", 0) + 1
        inbox["deathlink"] = True
        inbox["deathlink_source"] = args.get("data", {}).get("source", "unknown")
        with open(inbox_path, "w") as f:
            json.dump(inbox, f)
        logger.info(f"DeathLink received from {inbox['deathlink_source']}")

    async def _send_deathlink(self):
        source = self.username or "Hades II"
        await self.send_msgs([{
            "cmd": "Bounce",
            "tags": ["DeathLink"],
            "data": {
                "time":   time.time(),
                "cause":  "Melinoë was defeated",
                "source": source,
            },
        }])
        logger.info("DeathLink sent")

    # ── Location scouting (item names for in-game display) ───────────────────────

    async def _scout_locations(self, location_ids: list) -> None:
        """Scout the given location IDs so the game mod can display AP item names."""
        await self.send_msgs([{
            "cmd": "LocationScouts",
            "locations": location_ids,
            "create_as_hint": 0,
        }])
        logger.debug(f"Scouted {len(location_ids)} locations")

    def _write_location_items(self, args: dict) -> None:
        """Merge LocationInfo into ap_location_items.json (location_name → entry).

        Each entry is structured as:
            {"item_name": str, "player_slot": int, "player_name": str,
             "is_local": bool, "display": str}

        - `item_name` is the raw item (no [Player] suffix).
        - `is_local` lets the Lua mod tell apart our own items vs other players'.
        - `display` is the cauldron/Fated List label ("Item Name" or
          "Item Name [Player]" for remote items).
        """
        if not self._world_id:
            return
        path = self._ipc_file("ap_location_items.json")
        try:
            with open(path) as f:
                location_items: dict = json.load(f)
        except (OSError, json.JSONDecodeError):
            location_items = {}
        added = 0
        for net_item in args.get("locations", []):
            loc_id = net_item.location
            if loc_id not in _SCOUTABLE_LOCATION_IDS:
                continue
            location_name = _SCOUTABLE_LOCATION_IDS[loc_id]
            try:
                item_name = self.item_names.lookup_in_slot(net_item.item, net_item.player)
            except Exception:
                item_name = f"Item {net_item.item}"
            is_local = (net_item.player == self.slot)
            player_name = self.player_names.get(net_item.player, f"Player {net_item.player}")
            display = item_name if is_local else f"{item_name} [{player_name}]"
            location_items[location_name] = {
                "item_name":   item_name,
                "player_slot": net_item.player,
                "player_name": player_name,
                "is_local":    is_local,
                "display":     display,
            }
            added += 1
        if not added:
            return
        with open(path, "w") as f:
            json.dump(location_items, f, indent=2)
        logger.debug(f"Wrote {added} item names to {path.name} (total {len(location_items)})")

    # ── Outbox polling (game mod → AP server) ────────────────────────────────

    async def resync(self):
        """Reset client-side counters and reprocess the outbox from scratch."""
        self._last_checks_sent = 0
        self._sent_named_location_ids.clear()
        self._sent_hint_location_ids.clear()
        self._last_death_count = 0
        self._sent_goal = False
        outbox_path = self._ipc_file("ap_out.json")
        try:
            with open(outbox_path) as f:
                data = json.load(f)
            await self._process_outbox(data)
        except (OSError, json.JSONDecodeError):
            logger.warning("Resync: could not read outbox")

    async def poll_outbox(self):
        while not self.exit_event.is_set():
            try:
                if self._world_id and self.server:
                    outbox_path = self._ipc_file("ap_out.json")
                    if outbox_path.exists():
                        with open(outbox_path) as f:
                            data = json.load(f)
                        await self._process_outbox(data)
            except (json.JSONDecodeError, OSError) as e:
                logger.debug(f"Outbox read error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    async def _process_outbox(self, data: dict):
        await self._process_score_checks(data)
        await self._process_named_checks(data)
        await self._process_hints(data)
        await self._process_victory(data)
        await self._process_deathlink(data)

    async def _process_score_checks(self, data: dict):
        """Convert the Lua mod's checks_sent counter into AP LocationChecks."""
        checks_sent = data.get("checks_sent", 0)
        if checks_sent <= self._last_checks_sent:
            return

        new_locations = set()
        for i in range(self._last_checks_sent, checks_sent):
            if i < SCORE_LOCATION_COUNT:
                loc_id = hades_ii_base_location_id + i
                if loc_id not in self.checked_locations:
                    new_locations.add(loc_id)

        if new_locations:
            await self.send_msgs([{"cmd": "LocationChecks", "locations": list(new_locations)}])
            logger.info(f"Sent {len(new_locations)} score check(s) (total: {checks_sent})")

        self._last_checks_sent = checks_sent

    async def _process_named_checks(self, data: dict):
        """
        Handle all non-score location checks reported by name from the game.
        The outbox 'checked_locations' field is a list of AP location name strings.
        Covers: boss rewards, keepsakes, weapons, tools, hidden aspects,
                incantations, and prophecy checks.
        """
        checked = data.get("checked_locations", [])
        if not checked:
            return

        new_locations = set()
        for name in checked:
            loc_id = _LOCATION_NAME_TO_ID.get(name)
            if loc_id is not None and loc_id not in self.checked_locations and loc_id not in self._sent_named_location_ids:
                new_locations.add(loc_id)

        if new_locations:
            self._sent_named_location_ids.update(new_locations)
            await self.send_msgs([{"cmd": "LocationChecks", "locations": list(new_locations)}])
            logger.info(f"Sent {len(new_locations)} named check(s)")

    async def _process_hints(self, data: dict):
        """
        Hint locations the game has displayed (cauldron tab / Fated List).
        Lua sends a cumulative 'hinted_locations' array; we dedupe via a session
        set and call LocationScouts with create_as_hint=2 (free hint, no point cost).
        Already-checked locations are skipped — hinting a collected location is a no-op.
        """
        hinted = data.get("hinted_locations", [])
        if not hinted:
            return
        new_ids = set()
        for name in hinted:
            loc_id = _LOCATION_NAME_TO_ID.get(name)
            if loc_id is None:
                continue
            if loc_id in self._sent_hint_location_ids:
                continue
            if loc_id in self.checked_locations:
                self._sent_hint_location_ids.add(loc_id)
                continue
            new_ids.add(loc_id)
        if not new_ids:
            return
        self._sent_hint_location_ids.update(new_ids)
        await self.send_msgs([{
            "cmd": "LocationScouts",
            "locations": list(new_ids),
            "create_as_hint": 2,
        }])
        logger.debug(f"Hinted {len(new_ids)} location(s)")

    async def _process_victory(self, data: dict):
        """Send goal status when the game signals the run is complete."""
        if self._sent_goal:
            return
        if data.get("victory"):
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            self._sent_goal = True
            logger.debug("Goal complete — victory sent to server!")

    async def _process_deathlink(self, data: dict):
        """Forward deaths from the game to other AP players via DeathLink bounce."""
        if "DeathLink" not in self.tags:
            return
        death_count = data.get("deaths", 0)
        if death_count > self._last_death_count:
            self._last_death_count = death_count
            await self._send_deathlink()


# ── Entry point ───────────────────────────────────────────────────────────────

async def main(args):
    ctx = HadesIIContext(args.connect, args.password)
    ctx.auth = args.name

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    poller = asyncio.create_task(ctx.poll_outbox(), name="HadesII outbox poller")

    await server_loop(ctx)
    await ctx.exit_event.wait()
    poller.cancel()
    await ctx.shutdown()


def launch():
    parser = get_base_parser(description="Hades II Archipelago Client")
    parser.add_argument("--name", help="Slot name")
    args = parser.parse_args()
    Utils.init_logging("HadesIIClient")
    asyncio.run(main(args))


if __name__ == "__main__":
    launch()
