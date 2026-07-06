from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class ClientCreate(BaseModel):
    business_name: str = Field(..., min_length=1)
    niche: str = "restaurant"
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    state: Optional[str] = None
    rating: Optional[str] = None
    google_maps_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    lead_score: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class ClientResponse(ClientCreate):
    id: int
    slug: str
    demo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: bool = False
    is_available: bool = True

class MenuItemResponse(MenuItemCreate):
    id: int
    class Config:
        from_attributes = True

class GalleryImageCreate(BaseModel):
    image_url: str
    alt_text: Optional[str] = None

class GalleryImageResponse(GalleryImageCreate):
    id: int
    class Config:
        from_attributes = True

class TestimonialCreate(BaseModel):
    author_name: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: str

class TestimonialResponse(TestimonialCreate):
    id: int
    is_approved: bool
    class Config:
        from_attributes = True

class BusinessHoursSet(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_closed: bool = False

class BusinessHoursResponse(BusinessHoursSet):
    id: int
    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=8)
    email: EmailStr
    party_size: int = Field(..., ge=1, le=50)
    date: str
    time: str
    notes: Optional[str] = ""

class ReservationResponse(BaseModel):
    success: bool
    reservationCode: str
    message: Optional[str] = None

class MenuCategoryCreate(BaseModel):
    name: str
    sort_order: int = 0

class MenuCategoryResponse(MenuCategoryCreate):
    id: int
    class Config:
        from_attributes = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_available: Optional[bool] = None
    sort_order: Optional[int] = None
    category_id: Optional[int] = None

class OrderCreate(BaseModel):
    reservation_id: Optional[int] = None
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    total: Optional[str] = None
    status: str = "pending"
    items: Optional[str] = None
    order_type: str = "dine_in"
    notes: Optional[str] = None

class OrderResponse(OrderCreate):
    id: int
    order_code: str
    created_at: datetime
    class Config:
        from_attributes = True
