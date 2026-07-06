from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models import Client
from ..schemas import ClientCreate, ClientResponse
from ..utils.slug import make_slug
from ..services.demo_seed import seed_demo_content
import os
import datetime

router = APIRouter(prefix="/api/clients", tags=["clients"])

async def get_client_by_slug(slug: str, db: AsyncSession) -> Client:
    result = await db.execute(select(Client).where(Client.slug == slug))
    return result.scalars().first()

@router.post("/register")
async def register_client(data: ClientCreate, db: AsyncSession = Depends(get_db)):
    if not data.business_name.strip():
        raise HTTPException(400, "business_name is required")

    slug = make_slug(data.business_name.strip())
    demo_url = f"{os.getenv('DEMO_BASE_URL', 'http://localhost:4321')}/{slug}"

    existing = await get_client_by_slug(slug, db)
    if existing:
        for k, v in data.dict(exclude_unset=True).items():
            setattr(existing, k, v)
        existing.demo_url = demo_url
        client = existing
        is_new = False
    else:
        client = Client(slug=slug, demo_url=demo_url, **data.dict())
        db.add(client)
        is_new = True

    await db.commit()
    await db.refresh(client)

    if is_new:
        await seed_demo_content(client, db)

    return {"success": True, "slug": slug, "demo_url": demo_url}

@router.get("/demo-links")
async def get_demo_links(since: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Client)
    if since:
        try:
            parsed_date = datetime.datetime.fromisoformat(since)
            query = query.where(Client.created_at >= parsed_date)
        except ValueError:
            raise HTTPException(400, "Invalid datetime format for 'since'. Use ISO format.")
    result = await db.execute(query)
    clients_list = result.scalars().all()
    return {c.slug: c.demo_url for c in clients_list}

@router.get("/{slug}", response_model=ClientResponse)
async def get_client(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")
    return client

@router.get("/", response_model=list[ClientResponse])
async def list_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    return result.scalars().all()
