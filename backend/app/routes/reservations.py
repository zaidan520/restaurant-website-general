from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import random
import logging
from ..database import get_db
from ..models import Reservation, Order
from ..schemas import ReservationCreate, ReservationResponse, OrderCreate
from ..services.pdf import generate_booking_pdf
from ..services.email import send_confirmation_email
from ..services.whatsapp import send_whatsapp_message
from .clients import get_client_by_slug

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

def validate_reservation(data: dict):
    from datetime import datetime
    import re
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', data["email"]):
        raise HTTPException(400, "Invalid email format")
    if not re.match(r'^[\d\s()+-]{8,20}$', data["phone"]):
        raise HTTPException(400, "Invalid phone number")
    try:
        d = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if d < datetime.now().date():
            raise HTTPException(400, "Date must be today or later")
    except ValueError:
        raise HTTPException(400, "Invalid date format (use YYYY-MM-DD)")
    if not data["time"]:
        raise HTTPException(400, "Time is required")
    return data

@router.post("/{slug}", response_model=ReservationResponse)
async def create_reservation(slug: str, data: ReservationCreate, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Restaurant not found")

    validated = validate_reservation(data.dict())
    code = f"R-{random.randint(10000, 99999)}"

    reservation = Reservation(client_id=client.id, reservation_code=code, **validated)
    db.add(reservation)

    order_code = f"ORD-{random.randint(10000, 99999)}"
    order = Order(
        client_id=client.id,
        reservation_id=reservation.id,
        order_code=order_code,
        customer_name=data.name,
        customer_phone=data.phone,
        customer_email=data.email,
        status="pending",
        order_type="reservation",
        notes=data.notes
    )
    db.add(order)

    await db.commit()

    try:
        pdf_bytes = generate_booking_pdf(validated, code)
        send_confirmation_email(validated, code, pdf_bytes)
    except Exception as e:
        logging.error(f"Email/PDF failed: {e}")

    try:
        send_whatsapp_message(validated, code, to_number=client.phone or "+15550000000")
    except Exception as e:
        logging.error(f"WhatsApp failed: {e}")

    return {"success": True, "reservationCode": code, "message": "Reservation request sent."}

@router.get("/{slug}")
async def get_reservations(slug: str, db: AsyncSession = Depends(get_db)):
    client = await get_client_by_slug(slug, db)
    if not client:
        raise HTTPException(404, "Restaurant not found")
        
    result = await db.execute(
        select(Reservation)
        .where(Reservation.client_id == client.id)
        .order_by(Reservation.created_at.desc())
    )
    return result.scalars().all()
