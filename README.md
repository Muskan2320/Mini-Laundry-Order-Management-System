# 🧺 Mini Laundry Order Management System (AI-First)

## 🚀 Overview

This project is a lightweight backend system for managing laundry orders
for a dry cleaning store.

It supports: - Order creation with billing - Status tracking - Order
filtering - Dashboard analytics

Built using an AI-first development approach.

------------------------------------------------------------------------

## ⚙️ Tech Stack

-   Python
-   FastAPI
-   Pydantic
-   In-memory storage

------------------------------------------------------------------------

## ▶️ Setup Instructions

``` bash
git clone https://github.com/Muskan2320/Mini-Laundry-Order-Management-System.git
cd Mini-Laundry-Order-Management-System

pip install -r requirements.txt
uvicorn main:app --reload
```

Open: http://127.0.0.1:8000/docs

------------------------------------------------------------------------

## 📌 Features

### Create Order

-   Customer name & phone
-   Garments with quantity
-   Auto bill calculation
-   Unique order ID

### Order Status

-   RECEIVED
-   PROCESSING
-   READY
-   DELIVERED
-   Case-insensitive input supported

### View Orders

-   Filter by status
-   Search by name or phone

### Dashboard

-   Total orders
-   Total revenue
-   Orders per status

------------------------------------------------------------------------

## 🤖 AI Usage

### Tools

-   ChatGPT

### Where AI Helped

-   API scaffolding
-   Data modeling
-   Endpoint design

### Improvements Made

-   Added validation for phone numbers
-   Rejected invalid garment types
-   Made status handling case-insensitive
-   Improved filtering logic

------------------------------------------------------------------------

## ⚖️ Tradeoffs

-   No database (in-memory)
-   No authentication

------------------------------------------------------------------------

