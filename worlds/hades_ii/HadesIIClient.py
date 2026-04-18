"""
Hades II Archipelago Client
Bridges the Hades II game mod (via JSON files in ~/hadesii_ap/) with the AP server.
"""

import asyncio
import json
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

from .Locations import BOSS_ROOM_TO_LOCATION_ID, SCORE_LOCATION_COUNT, hades_ii_base_location_id
from .Items import ITEM_CODE_TO_RESOURCE

POLL_INTERVAL = 1.0


def get_ipc_dir() -> Path:
    return Path.home() / "hadesii_ap"


class HadesIICommandProcessor(ClientCommandProcessor):
    def _cmd_score(self):
        """Show current score and checks sent from the game."""
        outbox = get_ipc_dir() / "ap_out.json"
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


class HadesIIContext(CommonContext):
    game = "Hades II"
    command_processor = HadesIICommandProcessor
    items_handling = 0b111  # receive all items

    def __init__(self, server_address: str, password: Optional[str]):
        super().__init__(server_address, password)
        self.ipc_dir = get_ipc_dir()
        self.ipc_dir.mkdir(exist_ok=True)
        self._last_checks_sent = 0
        self._last_boss_status: Optional[str] = None

    # ── AP server callbacks ───────────────────────────────────────────────────

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "ReceivedItems":
            self._write_inbox()

    # ── Inbox (client → game mod) ─────────────────────────────────────────────

    def _write_inbox(self):
        items = []
        for i, net_item in enumerate(self.items_received):
            result = ITEM_CODE_TO_RESOURCE.get(net_item.item)
            if result:
                resource_id, amount = result
                items.append({"index": i, "resource_id": resource_id, "amount": amount})
            else:
                logger.debug(f"Item code {net_item.item} has no resource mapping (keepsake/weapon/etc.) — skipped")

        inbox = {
            "connected":           True,
            "items_count":         len(items),
            "items":               items,
            "points_per_room":     1,
            "points_per_location": 10,
        }

        with open(self.ipc_dir / "ap_in.json", "w") as f:
            json.dump(inbox, f)

        logger.info(f"Inbox updated — {len(items)} grantable item(s)")

    # ── Outbox polling (game mod → client) ────────────────────────────────────

    async def poll_outbox(self):
        outbox_path = self.ipc_dir / "ap_out.json"
        while not self.exit_event.is_set():
            try:
                if outbox_path.exists() and self.server:
                    with open(outbox_path) as f:
                        data = json.load(f)
                    await self._process_score_checks(data)
                    await self._process_boss_cleared(data)
            except (json.JSONDecodeError, OSError) as e:
                logger.debug(f"Outbox read error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

    async def _process_score_checks(self, data: dict):
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
            logger.info(f"Sent {len(new_locations)} score check(s)")

        self._last_checks_sent = checks_sent

    async def _process_boss_cleared(self, data: dict):
        if data.get("status") != "boss_cleared":
            return
        boss_room = data.get("boss_room")
        if boss_room == self._last_boss_status:
            return

        loc_id = BOSS_ROOM_TO_LOCATION_ID.get(boss_room)
        if loc_id and loc_id not in self.checked_locations:
            await self.send_msgs([{"cmd": "LocationChecks", "locations": [loc_id]}])
            logger.info(f"Sent boss check: {boss_room} → location {loc_id}")

        self._last_boss_status = boss_room


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
