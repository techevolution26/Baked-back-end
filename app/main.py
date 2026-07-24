from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import auth, bakeries, templates, blueprints, orders, users, internal

settings = get_settings()

app = FastAPI(title="Cake Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(bakeries.router)
app.include_router(templates.router)
app.include_router(blueprints.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(internal.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
