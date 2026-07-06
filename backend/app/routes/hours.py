from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import BusinessHours
from ..schemas import BusinessHoursSet, BusinessHoursResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/hours", tags=["hours"])

@router.get("/{slug}", response_model=list[BusinessHoursResponse])
async def get_hours(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    result = await db.execute(
        select(BusinessHours)
        .where(BusinessHours.client_id == client.id)
        .order_by(BusinessHours.day_of_week)
    )
    return result.scalars().all()

@router.post("/{slug}")
async def set_hours(slug: str, data: list[BusinessHoursSet], db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    # Delete existing hours first
    from sqlalchemy import delete
    await db.execute(
        delete(BusinessHours).where(BusinessHours.client_id == client.id)
    )
    
    # Bulk insert new hours
    new_hours = [
        BusinessHours(client_id=client.id, **day.dict())
        for day in data
    ]
    db.add_all(new_hours)
    await db.commit()
    return {"success": True}
