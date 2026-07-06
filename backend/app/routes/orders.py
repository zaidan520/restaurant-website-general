from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, date
import random
from ..database import get_db
from ..models import Client, Order, MenuItem, Reservation
from ..schemas import OrderCreate, OrderResponse
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/{slug}", response_model=OrderResponse)
async def create_order(slug: str, data: OrderCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    order_code = f"ORD-{random.randint(10000, 99999)}"
    order = Order(client_id=client.id, order_code=order_code, **data.dict())
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@router.get("/{slug}")
async def get_orders(slug: str, status: str = Query(None), db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    query = select(Order).where(Order.client_id == client.id)
    if status:
        query = query.where(Order.status == status)
    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    return [
        {
            "id": o.id,
            "order_code": o.order_code,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "customer_email": o.customer_email,
            "total": o.total,
            "status": o.status,
            "items": o.items,
            "order_type": o.order_type,
            "notes": o.notes,
            "created_at": o.created_at.isoformat() if o.created_at else None
        }
        for o in orders
    ]

@router.get("/{slug}/summary")
async def get_dashboard_summary(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    today_orders_result = await db.execute(
        select(Order).where(Order.client_id == client.id, Order.created_at >= today_start)
    )
    today_orders = today_orders_result.scalars().all()

    today_reservations_result = await db.execute(
        select(Reservation).where(Reservation.client_id == client.id, Reservation.date == today.isoformat())
    )
    today_reservations = today_reservations_result.scalars().all()

    status_counts = {}
    for o in today_orders:
        status_counts[o.status] = status_counts.get(o.status, 0) + 1

    total_revenue = sum(float(o.total or 0) for o in today_orders if o.status != "cancelled")

    menu_count_result = await db.execute(
        select(func.count(MenuItem.id)).where(MenuItem.client_id == client.id)
    )
    menu_count = menu_count_result.scalar()

    out_of_stock_result = await db.execute(
        select(func.count(MenuItem.id)).where(MenuItem.client_id == client.id, MenuItem.is_available == False)
    )
    out_of_stock = out_of_stock_result.scalar()

    return {
        "today_orders_count": len(today_orders),
        "today_revenue": total_revenue,
        "status_breakdown": status_counts,
        "today_reservations_count": len(today_reservations),
        "pending_reservations_count": len([r for r in today_reservations if r.status == "pending"]),
        "menu_items_count": menu_count,
        "out_of_stock_count": out_of_stock,
        "recent_orders": [
            {
                "id": o.id,
                "order_code": o.order_code,
                "customer_name": o.customer_name,
                "customer_phone": o.customer_phone,
                "total": o.total,
                "status": o.status,
                "order_type": o.order_type,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in today_orders[:20]
        ],
        "recent_reservations": [
            {
                "id": r.id,
                "reservation_code": r.reservation_code,
                "name": r.name,
                "party_size": r.party_size,
                "date": r.date,
                "time": r.time,
                "status": r.status
            }
            for r in today_reservations[:20]
        ]
    }

@router.put("/{slug}/{order_id}", response_model=OrderResponse)
async def update_order(slug: str, order_id: int, data: OrderCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(select(Order).where(Order.id == order_id, Order.client_id == client.id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(404, "Order not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(order, key, value)

    await db.commit()
    await db.refresh(order)
    return order

@router.delete("/{slug}/{order_id}")
async def delete_order(slug: str, order_id: int, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Client not found")

    result = await db.execute(select(Order).where(Order.id == order_id, Order.client_id == client.id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(404, "Order not found")

    await db.delete(order)
    await db.commit()
    return {"success": True}
