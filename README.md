# 🧺 Mini Laundry Order Management System (AI-First)

## 🚀 Overview

This project is a lightweight yet production-style system for managing laundry orders in a dry cleaning store.

It supports:

* Order creation with billing
* Status tracking
* Order filtering and search
* Dashboard analytics
* Delivery time estimation (queue-based)

Built using an **AI-first development approach** with iterative improvements.

---

## 🎥 Demo & Live Application

* 🌍 **Live App:**
  https://mini-laundry-order-management-system-bwtu.onrender.com/

* 🎬 **Demo Video (Loom):**
  https://www.loom.com/share/4bac1958599f4090a2b7174008f639b9

## ⚙️ Tech Stack

* Python
* FastAPI
* MongoDB Atlas (cloud database)
* Pydantic
* HTML + JavaScript (Frontend)
* JWT Authentication

---

## ▶️ Setup Instructions

```bash
git clone https://github.com/Muskan2320/Mini-Laundry-Order-Management-System.git
cd Mini-Laundry-Order-Management-System

pip install -r requirements.txt
uvicorn main:app --reload
```

Open API Docs:

```
http://127.0.0.1:8000/docs
```

---

## 🔐 Environment Variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
ADMIN_USERNAME=username
ADMIN_PASSWORD=password
MONGO_URL=your_mongodb_connection_string
```

---

## 📌 Features

### 🧾 Create Order

* Customer name & phone validation
* Multiple garments with quantity
* Automatic bill calculation
* Unique order ID
* Duplicate garment types merged (frontend optimization)

---

### 🔄 Order Status Management

* RECEIVED
* PROCESSING
* READY
* DELIVERED
* Case-insensitive updates supported

---

### 🔍 View Orders

* Filter by status
* Search by name or phone
* Filter by garment type

---

### 📊 Dashboard

* Total orders
* Total revenue
* Orders grouped by status

---

### 🚚 Delivery Estimation (Advanced Feature)

#### 1. System-Level Estimation

* Calculates total pending garments
* Uses daily processing capacity (30 garments/day)

#### 2. Per-Order Estimation

* Queue-based logic (FIFO using MongoDB `_id`)
* Considers:

  * Orders before current order
  * Current order workload
* Returns:

  * Estimated days
  * Expected delivery date

---

### 🔐 Authentication

* JWT-based login system
* Protected endpoints
* Token-based authorization

---

### 🌐 Frontend

* Simple HTML + JS interface
* Create orders dynamically
* Add/remove garments
* Search and filter orders
* Update order status
* View dashboard
* Estimate delivery by order ID

---

## 🤖 AI Usage Report

### Tools Used

* ChatGPT

### Where AI Helped

* Initial API scaffolding
* Database integration (MongoDB)
* Authentication setup (JWT)
* Frontend UI structure
* Delivery estimation logic design

### Where Improvements Were Made

* Fixed MongoDB ObjectId serialization issues for proper API responses
* Added strict input validation (e.g., 10-digit phone number format)
* Improved input handling with validation checks for quantity and garment types
* Added restrictions to prevent invalid or malformed data entries
* Handled duplicate garments via frontend normalization (merged same types)
* Made order status updates case-insensitive and validated against allowed values
* Implemented queue-based delivery estimation using real-world capacity logic
* Included current order workload in delivery estimation for accuracy
* Enhanced error handling with clear API responses and frontend feedback
* Improved overall UX by handling edge cases (invalid login, empty inputs, etc.)

---

## ⚖️ Tradeoffs

* Single-file backend (kept simple for speed)
* Basic authentication (no user roles)
* No pagination on large datasets
* UI is minimal (functionality-focused)

---

## 🚀 Future Improvements

* Role-based authentication
* Pagination & sorting
* Better UI (React)
* Order timestamps for more accurate scheduling
* Notifications for order readiness
* Docker + CI/CD pipeline

---

## 🎯 Key Highlights

* End-to-end system (frontend + backend + DB)
* Real-world business logic (queue-based delivery estimation)
* AI-assisted development with manual refinements
* Production-like architecture using cloud database

---
