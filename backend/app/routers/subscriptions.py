"""Router de assinaturas para Subscription Tracker."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models import (
    get_all_subscriptions, get_subscription_by_id,
    create_subscription, update_subscription, delete_subscription, toggle_subscription,
    get_dashboard_stats,
)
from app.schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionOut, DashboardStats

router = APIRouter(prefix="/subscriptions", tags=["assinaturas"])


@router.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard():
    """Retorna estatísticas do dashboard."""
    return await get_dashboard_stats()


@router.get("/", response_model=list[SubscriptionOut])
async def list_subscriptions(
    active_only: bool = Query(True),
    category_id: int | None = Query(None),
):
    """Lista todas as assinaturas."""
    subs = await get_all_subscriptions(active_only=active_only)
    if category_id is not None:
        subs = [s for s in subs if s["category_id"] == category_id]
    return subs


@router.get("/{sub_id}", response_model=SubscriptionOut)
async def get_subscription(sub_id: int):
    """Busca uma assinatura por ID."""
    sub = await get_subscription_by_id(sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    return sub


@router.post("/", response_model=SubscriptionOut, status_code=201)
async def create_new(body: SubscriptionCreate):
    """Adiciona uma nova assinatura."""
    sub_id = await create_subscription(body.model_dump())
    result = await get_subscription_by_id(sub_id)
    return result


@router.put("/{sub_id}", response_model=SubscriptionOut)
async def edit_subscription(sub_id: int, body: SubscriptionUpdate):
    """Atualiza uma assinatura."""
    existing = await get_subscription_by_id(sub_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    await update_subscription(sub_id, updates)
    result = await get_subscription_by_id(sub_id)
    return result


@router.delete("/{sub_id}", status_code=204)
async def remove_subscription(sub_id: int):
    """Remove permanentemente uma assinatura."""
    existing = await get_subscription_by_id(sub_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    await delete_subscription(sub_id)


@router.patch("/{sub_id}/toggle", response_model=SubscriptionOut)
async def toggle_active(sub_id: int):
    """Ativa/desativa uma assinatura sem deletar."""
    await toggle_subscription(sub_id)
    result = await get_subscription_by_id(sub_id)
    return result
