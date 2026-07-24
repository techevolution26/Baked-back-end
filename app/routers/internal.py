from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..services.tenant import find_bakery_by_host

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/domain-check")
async def domain_check(domain: str, session: AsyncSession = Depends(get_session)):
    """
    Used by the reverse proxy's on-demand TLS "ask" mechanism to decide
    whether a certificate should be issued for an incoming domain.

    SECURITY NOTE: this route must never be reachable from the public
    internet -- only from the reverse proxy over the private docker
    network. See deploy/Caddyfile.
    """
    bakery = await find_bakery_by_host(session, domain)
    if not bakery:
        raise HTTPException(status_code=404, detail="Unknown domain")
    return {"ok": True}
