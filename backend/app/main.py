from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import clients, menu, gallery, testimonials, hours, reservations, orders, categories

app = FastAPI(title="Restaurant Platform API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(menu.router)
app.include_router(categories.router)
app.include_router(gallery.router)
app.include_router(testimonials.router)
app.include_router(hours.router)
app.include_router(reservations.router)
app.include_router(orders.router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}
