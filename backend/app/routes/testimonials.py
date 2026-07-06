from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import Testimonial
from ..schemas import TestimonialCreate, TestimonialResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/testimonials", tags=["testimonials"])

@router.get("/{slug}", response_model=list[TestimonialResponse])
async def get_testimonials(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    result = await db.execute(
        select(Testimonial)
        .where(Testimonial.client_id == client.id, Testimonial.is_approved == True)
    )
    return result.scalars().all()

@router.post("/{slug}", response_model=TestimonialResponse)
async def add_testimonial(slug: str, data: TestimonialCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    testimonial = Testimonial(client_id=client.id, **data.dict())
    db.add(testimonial)
    await db.commit()
    await db.refresh(testimonial)
    return testimonial
