from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import Client, MenuCategory, MenuItem
from ..schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/menu", tags=["menu"])

@router.get("/{slug}")
async def get_menu(slug: str, featured: bool = None, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    if featured:
        result = await db.execute(
            select(MenuItem)
            .where(MenuItem.client_id == client.id, MenuItem.is_featured == True)
            .order_by(MenuItem.sort_order)
        )
        items = result.scalars().all()
        return items

    cat_result = await db.execute(
        select(MenuCategory)
        .where(MenuCategory.client_id == client.id)
        .order_by(MenuCategory.sort_order)
    )
    categories = cat_result.scalars().all()

    response_data = []
    for cat in categories:
        item_result = await db.execute(
            select(MenuItem)
            .where(MenuItem.client_id == client.id, MenuItem.category_id == cat.id)
            .order_by(MenuItem.sort_order)
        )
        items = item_result.scalars().all()
        response_data.append({
            "category": cat.name,
            "id": cat.id,
            "items": items
        })
    return response_data

@router.post("/{slug}", response_model=MenuItemResponse)
async def add_menu_item(slug: str, data: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    item = MenuItem(client_id=client.id, **data.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/{slug}/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(slug: str, item_id: int, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.client_id == client.id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(404, "Menu item not found")
    return item

@router.put("/{slug}/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(slug: str, item_id: int, data: MenuItemUpdate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.client_id == client.id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(404, "Menu item not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{slug}/{item_id}")
async def delete_menu_item(slug: str, item_id: int, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.client_id == client.id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(404, "Menu item not found")

    await db.delete(item)
    await db.commit()
    return {"success": True}
