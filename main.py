from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List
import uuid
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory DB
orders_db = {}

# Allowed values
PRICE_LIST = {
    "Shirt": 10,
    "Pants": 15,
    "Saree": 20
}

VALID_STATUSES = ["RECEIVED", "PROCESSING", "READY", "DELIVERED"]

# Models
class Garment(BaseModel):
    type: str
    quantity: int

    @validator("quantity")
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    garments: List[Garment]

    @validator("phone")
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v


# Helper
def calculate_total(garments):
    total = 0
    for g in garments:
        if g.type not in PRICE_LIST:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid garment type: {g.type}. Allowed: {list(PRICE_LIST.keys())}"
            )
        total += PRICE_LIST[g.type] * g.quantity
    return total


# 1. Create Order
@app.post("/orders")
def create_order(order: OrderCreate):
    order_id = str(uuid.uuid4())

    total = calculate_total(order.garments)

    new_order = {
        "id": order_id,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "garments": order.garments,
        "total": total,
        "status": "RECEIVED"
    }

    orders_db[order_id] = new_order
    return new_order


# 2. Update Status
@app.put("/orders/{order_id}/status")
def update_status(order_id: str, status: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")

    normalized_status = status.upper()

    if normalized_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {VALID_STATUSES}"
        )

    orders_db[order_id]["status"] = normalized_status
    return orders_db[order_id]


# 3. View Orders
@app.get("/orders")
def get_orders(status: str = None, search: str = None, garment: str = None):
    results = list(orders_db.values())

    # Status filter
    if status:
        normalized_status = status.strip().upper()
        results = [o for o in results if o["status"] == normalized_status]

    # Name/phone search
    if search:
        search = search.strip().lower()
        results = [
            o for o in results
            if search in o["customer_name"].lower()
            or search in o["phone"]
        ]

    if garment:
        garment = garment.strip().lower()
        results = [
            o for o in results
            if any(garment in g.type.lower() for g in o["garments"])
        ]

    return results


# 4. Dashboard
@app.get("/dashboard")
def dashboard():
    total_orders = len(orders_db)
    total_revenue = sum(o["total"] for o in orders_db.values())

    status_count = {}
    for o in orders_db.values():
        status_count[o["status"]] = status_count.get(o["status"], 0) + 1

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "orders_per_status": status_count
    }