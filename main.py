from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, validator
from typing import List
import uuid
import re
import os
import math
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------- ENV ----------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
MONGO_URL = os.getenv("MONGO_URL")

# ---------------- DB ----------------
client = AsyncIOMotorClient(MONGO_URL)
db = client.laundry_db
orders_collection = db.orders

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- AUTH ----------------
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users_db = {
    ADMIN_USERNAME: {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
}

# ---------------- MODELS ----------------
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


class LoginRequest(BaseModel):
    username: str
    password: str

# ---------------- CONSTANTS ----------------
PRICE_LIST = {
    "Shirt": 10,
    "Pants": 15,
    "Saree": 20
}

VALID_STATUSES = ["RECEIVED", "PROCESSING", "READY", "DELIVERED"]

# ---------------- HELPERS ----------------
def calculate_total(garments):
    total = 0
    for g in garments:
        if g.type not in PRICE_LIST:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid garment type: {g.type}"
            )
        total += PRICE_LIST[g.type] * g.quantity
    return total


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise credentials_exception

    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# ---------------- AUTH API ----------------
@app.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})

    return {"access_token": token, "token_type": "bearer"}

# ---------------- CREATE ORDER ----------------
@app.post("/orders")
async def create_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    order_id = str(uuid.uuid4())

    total = calculate_total(order.garments)

    new_order = {
        "id": order_id,
        "customer_name": order.customer_name,
        "phone": order.phone,
        "garments": [g.dict() for g in order.garments],
        "total": total,
        "status": "RECEIVED"
    }

    result = await orders_collection.insert_one(new_order)
    new_order["_id"] = str(result.inserted_id)

    return new_order

# ---------------- GET ORDERS ----------------
@app.get("/orders")
async def get_orders(status: str = None, search: str = None, garment: str = None, user: dict = Depends(get_current_user)):
    query = {}

    if status:
        query["status"] = status.strip().upper()

    if search:
        query["$or"] = [
            {"customer_name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search}}
        ]

    if garment:
        query["garments.type"] = {"$regex": garment, "$options": "i"}

    results = []
    async for order in orders_collection.find(query):
        order["_id"] = str(order["_id"])
        results.append(order)

    return results

# ---------------- UPDATE STATUS ----------------
@app.put("/orders/{order_id}/status")
async def update_status(order_id: str, status: str, user: dict = Depends(get_current_user)):
    status = status.upper()

    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await orders_collection.update_one(
        {"id": order_id},
        {"$set": {"status": status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Updated", "status": status}

# ---------------- DASHBOARD ----------------
@app.get("/dashboard")
async def dashboard(user: dict = Depends(get_current_user)):
    total_orders = await orders_collection.count_documents({})

    total_revenue = 0
    status_count = {}

    async for order in orders_collection.find({}):
        total_revenue += order["total"]
        s = order["status"]
        status_count[s] = status_count.get(s, 0) + 1

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "orders_per_status": status_count
    }

@app.get("/estimate-delivery/{order_id}")
async def estimate_delivery_for_order(order_id: str, user: dict = Depends(get_current_user)):
    DAILY_CAPACITY = 30

    # Step 1: check if order exists
    order = await orders_collection.find_one({"id": order_id})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Step 2: check status
    if order["status"] == "READY":
        return {
            "message": "Order is already ready for pickup",
            "estimated_days": 0
        }

    if order["status"] == "DELIVERED":
        return {
            "message": "Order already delivered",
            "estimated_days": 0
        }

    # Step 3: calculate garments before this order
    total_garments_before = 0

    cursor = orders_collection.find({
        "status": {"$in": ["RECEIVED", "PROCESSING"]}
    }).sort("_id", 1)

    async for o in cursor:
        if o["id"] == order_id:
            break

        for g in o["garments"]:
            total_garments_before += g["quantity"]

    # Step 4: estimate days
    current_order_garments = sum(g["quantity"] for g in order["garments"])
    total_garments = total_garments_before + current_order_garments

    estimated_days = math.ceil(total_garments / DAILY_CAPACITY)

    # Step 5: expected delivery date
    delivery_date = datetime.utcnow() + timedelta(days=estimated_days)

    return {
        "order_id": order_id,
        "status": order["status"],
        "garments_before": total_garments_before,
        "current_order_garments": current_order_garments,
        "daily_capacity": DAILY_CAPACITY,
        "estimated_days": estimated_days,
        "expected_delivery_date": delivery_date.strftime("%Y-%m-%d")
    }