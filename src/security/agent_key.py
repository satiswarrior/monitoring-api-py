from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

from src.config import settings
from src.database import get_session
from src.models.db_models import AgentKey


async def verify_agent_key(x_api_key: str = Header(...), session: AsyncSession = Depends(get_session)):
    # developer fallback (local/dev keys)
    if x_api_key in settings.VALID_AGENT_KEYS:
        return x_api_key

    # compute sha256 hex digest of provided key
    try:
        provided_sha = hashlib.sha256(x_api_key.encode()).hexdigest()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid agent API key")

    # load active (non-revoked) keys
    stmt = select(AgentKey).where(AgentKey.revoked_at.is_(None))
    res = await session.execute(stmt)
    keys = res.scalars().all()

    for ak in keys:
        kh = ak.key_hash
        if not kh:
            continue

        # direct match (legacy plain token stored)
        if kh == x_api_key:
            return x_api_key

        if isinstance(kh, str):
            # support stored formats like 'sha256:... or sha256$...'
            if kh.startswith("sha256:") or kh.startswith("sha256$"):
                val = kh.split(":", 1)[1] if ":" in kh else kh.split("$", 1)[1]
                if val == provided_sha:
                    return x_api_key

            # plain hex digest (64 hex chars)
            if len(kh) == 64 and all(c in "0123456789abcdefABCDEF" for c in kh):
                if kh.lower() == provided_sha.lower():
                    return x_api_key

    raise HTTPException(status_code=401, detail="Invalid agent API key")
