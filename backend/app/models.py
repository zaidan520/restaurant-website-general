from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    business_name = Column(String, nullable=False)
    niche = Column(String, nullable=False, default="restaurant")
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    google_maps_url = Column(String, nullable=True)
    facebook_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)
    lead_score = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    demo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    categories = relationship("MenuCategory", back_populates="client", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="client", cascade="all, delete-orphan")
    gallery_images = relationship("GalleryImage", back_populates="client", cascade="all, delete-orphan")
    testimonials = relationship("Testimonial", back_populates="client", cascade="all, delete-orphan")
    hours = relationship("BusinessHours", back_populates="client", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="client", cascade="all, delete-orphan")

    # ADD THIS LINE:
    orders = relationship("Order", back_populates="client", cascade="all, delete-orphan")

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)          # "Starters", "Mains"...
    sort_order = Column(Integer, default=0)

    client = relationship("Client", back_populates="categories")
    menu_items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(String, nullable=True)           # e.g. "12" (USD)
    image_url = Column(String, nullable=True)
    is_featured = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    client = relationship("Client", back_populates="menu_items")
    category = relationship("MenuCategory", back_populates="menu_items")

class GalleryImage(Base):
    __tablename__ = "gallery_images"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    image_url = Column(String, nullable=False)
    alt_text = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)

    client = relationship("Client", back_populates="gallery_images")

class Testimonial(Base):
    __tablename__ = "testimonials"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    author_name = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)          # 1-5
    text = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=True)

    client = relationship("Client", back_populates="testimonials")

class BusinessHours(Base):
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)      # 0=Mon ... 6=Sun
    open_time = Column(String, nullable=True)          # "11:00", null = closed
    close_time = Column(String, nullable=True)
    is_closed = Column(Boolean, default=False)

    client = relationship("Client", back_populates="hours")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    reservation_code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    party_size = Column(Integer, nullable=False)
    date = Column(String, nullable=False)              # "YYYY-MM-DD"
    time = Column(String, nullable=False)               # "HH:MM"
    notes = Column(Text, nullable=True)
    status = Column(String, default="pending")           # pending/confirmed/cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="reservations")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    order_code = Column(String, unique=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    total = Column(String, nullable=True)
    status = Column(String, default="pending")
    items = Column(Text, nullable=True)
    order_type = Column(String, default="dine_in")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    client = relationship("Client", back_populates="orders")
