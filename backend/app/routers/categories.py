"""Router de categorias para Subscription Tracker."""

from fastapi import APIRouter, Depends, HTTPException

from app.models import (
    get_all_categories, create_category, update_category, delete_category,
)
from app.schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categorias"])


@router.get("/", response_model=list[CategoryOut])
async def list_categories():
    """Lista todas as categorias."""
    return await get_all_categories()


@router.post("/", response_model=CategoryOut, status_code=201)
async def create_new_category(body: CategoryCreate):
    """Cria uma nova categoria."""
    existing = await get_all_categories()
    if any(c["name"].lower() == body.name.lower() for c in existing):
        raise HTTPException(status_code=400, detail="Categoria já existe")
    cat_id = await create_category(body.name, body.color)
    all_cats = await get_all_categories()
    return next((c for c in all_cats if c["id"] == cat_id), None)


@router.put("/{category_id}", response_model=CategoryOut)
async def edit_category(category_id: int, body: CategoryCreate):
    """Atualiza nome e cor de uma categoria."""
    await update_category(category_id, body.name, body.color)
    all_cats = await get_all_categories()
    return next((c for c in all_cats if c["id"] == category_id), None)


@router.delete("/{category_id}", status_code=204)
async def remove_category(category_id: int):
    """Remove uma categoria (não remove assinaturas vinculadas)."""
    await delete_category(category_id)
