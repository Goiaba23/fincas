from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api.v1.endpoints import (
    auth,
    accounts,
    transactions,
    workspaces,
    categories,
    budgets,
    goals,
    rules,
    payees,
    tags,
    recurring,
    credit_cards,
    bank_sync,
    reports,
    notifications,
    ai,
    ai_insights,
    ai_simulations,
    dashboard,
    fincas,
    subscriptions,
    imports,
)
from app.providers.bank import pluggy

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://frontend-goiaba23s-projects.vercel.app",
        "https://frontend-39m18xm8s-goiaba23s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(workspaces.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(payees.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(recurring.router, prefix="/api/v1")
app.include_router(credit_cards.router, prefix="/api/v1")
app.include_router(bank_sync.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(ai_insights.router, prefix="/api/v1")
app.include_router(ai_simulations.router, prefix="/api/v1")
app.include_router(fincas.router, prefix="/api/v1")
app.include_router(dashboard.router)
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")

pluggy.init_providers()


@app.on_event("startup")
async def startup():
    logger.info("Starting Fincas API")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down Fincas API")
    await engine.dispose()


@app.exception_handler(Exception)
async def global_exception(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
