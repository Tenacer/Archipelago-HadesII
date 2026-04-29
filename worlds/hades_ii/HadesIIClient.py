"""
Hades II Archipelago Client
Bridges the Hades II game mod (via JSON files in ~/hadesii_ap/) with the AP server.
"""

import asyncio
import json
import re
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


def get_ipc_dir() -> Path:
    return Path.home() / "hadesii_ap"


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
        if cmd == "Connected":
            slot_data = args.get("slot_data", {})
            world_id = re.sub(r'[^a-zA-Z0-9_-]', '_', f"{self.seed_name}_{self.slot}")
            self._world_id = world_id
            logger.info(f"World ID: {world_id}")
            self._write_settings(slot_data)
            self._write_inbox()
            # Enable DeathLink if the slot data says so (and the player hasn't overridden it)
            if not self.deathlink_client_override and slot_data.get("death_link"):
                Utils.async_start(self.update_death_link(True))
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
        logger.info(f"Wrote slot data to ap_settings.json (world_id={self._world_id})")

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
        logger.info(f"Inbox updated — {len(items)} item(s)")

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

    # ── Outbox polling (game mod → AP server) ────────────────────────────────

    async def resync(self):
        """Reset client-side counters and reprocess the outbox from scratch."""
        self._last_checks_sent = 0
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
            if loc_id is not None and loc_id not in self.checked_locations:
                new_locations.add(loc_id)

        if new_locations:
            await self.send_msgs([{"cmd": "LocationChecks", "locations": list(new_locations)}])
            logger.info(f"Sent {len(new_locations)} named check(s)")

    async def _process_victory(self, data: dict):
        """Send goal status when the game signals the run is complete."""
        if self._sent_goal:
            return
        if data.get("victory"):
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            self._sent_goal = True
            logger.info("Goal complete — victory sent to server!")

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
