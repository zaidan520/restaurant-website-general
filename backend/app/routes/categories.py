from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import Client, MenuCategory
from ..schemas import MenuCategoryCreate, MenuCategoryResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/{slug}", response_model=list[MenuCategoryResponse])
async def get_categories(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuCategory)
        .where(MenuCategory.client_id == client.id)
        .order_by(MenuCategory.sort_order)
    )
    return result.scalars().all()

@router.post("/{slug}", response_model=MenuCategoryResponse)
async def create_category(slug: str, data: MenuCategoryCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    category = MenuCategory(client_id=client.id, **data.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.put("/{slug}/{category_id}", response_model=MenuCategoryResponse)
async def update_category(slug: str, category_id: int, data: MenuCategoryCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuCategory).where(MenuCategory.id == category_id, MenuCategory.client_id == client.id)
    )
    category = result.scalars().first()
    if not category:
        raise HTTPException(404, "Category not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/{slug}/{category_id}")
async def delete_category(slug: str, category_id: int, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuCategory).where(MenuCategory.id == category_id, MenuCategory.client_id == client.id)
    )
    category = result.scalars().first()
    if not category:
        raise HTTPException(404, "Category not found")

    await db.delete(category)
    await db.commit()
    return {"success": True}
