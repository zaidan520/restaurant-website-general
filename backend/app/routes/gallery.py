from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import GalleryImage
from ..schemas import GalleryImageCreate, GalleryImageResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/gallery", tags=["gallery"])

@router.get("/{slug}", response_model=list[GalleryImageResponse])
async def get_gallery(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    result = await db.execute(
        select(GalleryImage)
        .where(GalleryImage.client_id == client.id)
        .order_by(GalleryImage.sort_order)
    )
    return result.scalars().all()

@router.post("/{slug}", response_model=GalleryImageResponse)
async def add_gallery_image(slug: str, data: GalleryImageCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
        
    image = GalleryImage(client_id=client.id, **data.dict())
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image
