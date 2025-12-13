#!/usr/bin/env python3
"""
Seed script: generate an agent token, store its SHA-256 hash in `agent_keys`, and print the plaintext token.
Usage:
    python src/scripts/seed_agent_key.py [server_id]

Defaults to server_id=1.
"""

import asyncio
import sys
import secrets
import hashlib

from src.database import async_session
from src.models.db_models import AgentKey, Server, Region


async def main(server_id: int = 1):
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    key_hash = f"sha256:{digest}"

    async with async_session() as session:
        async with session.begin():
            # ensure a test region exists (some app code expects servers->region)
            region = await session.get(Region, 1)
            if region is None:
                region = Region(name="test")
                session.add(region)
                await session.flush()

            # ensure server exists (create minimal server row if missing)
            existing = await session.get(Server, server_id)
            if existing is None:
                srv = Server(id=server_id, ip="127.0.0.1", region_id=region.id)
                session.add(srv)
            ak = AgentKey(server_id=server_id, key_hash=key_hash)
            session.add(ak)
        # attempt to refresh to get DB-side generated fields (id)
        try:
            await session.refresh(ak)
        except Exception:
            pass

    print("Generated agent token (keep this secret):")
    print(token)
    print()
    print("Stored key_hash:", key_hash)
    print("AgentKey id:", getattr(ak, "id", None))


if __name__ == "__main__":
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    asyncio.run(main(sid))
