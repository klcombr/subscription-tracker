"""Subscription Tracker - Backend FastAPI completo."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import init_db
from app.routers import categories, subscriptions

app = FastAPI(
    title="Subscription Tracker API",
    description="API para rastrear e gerenciar suas assinaturas mensais/anuais",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    return {
        "message": "Subscription Tracker API",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
