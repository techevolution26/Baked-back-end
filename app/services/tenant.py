"""
Tenant (bakery) resolution for the domain-per-bakery model.

Every bakery is reachable at either its platform-provided subdomain
(e.g. "sweetfig.<PLATFORM_DOMAIN>") or a verified custom domain
(e.g. "sweetfigbakery.com"). This module is the single place that turns
an incoming hostname into the Bakery row it belongs to.
"""
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.database import get_session
from ..models import Bakery


async def find_bakery_by_host(session: AsyncSession, host: str) -> Bakery | None:
    host = host.split(":")[0].lower()

    bakery = await session.scalar(select(Bakery).where(Bakery.custom_domain == host))
    if bakery:
        return bakery

    settings = get_settings()
    suffix = f".{settings.platform_domain}"
    if host.endswith(suffix):
        subdomain = host[: -len(suffix)]
        return await session.scalar(select(Bakery).where(Bakery.subdomain == subdomain))

    return None


async def require_tenant(
    x_tenant_host: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> Bakery:
    """
    Resolves the bakery for the current request from a trusted
    X-Tenant-Host header.

    SECURITY NOTE: this header must only ever be set by our own Next.js
    server, which reads the real browser-supplied Host header and
    forwards it here over the private docker network. The FastAPI
    backend must never be exposed directly to the public internet --
    if it were, a client could forge this header and register/log in
    as if they were on a bakery domain they don't actually control.
    """
    if not x_tenant_host:
        raise HTTPException(status_code=400, detail="Missing tenant context")

    bakery = await find_bakery_by_host(session, x_tenant_host)
    if not bakery:
        raise HTTPException(status_code=404, detail="No bakery found for this domain")
    return bakery
