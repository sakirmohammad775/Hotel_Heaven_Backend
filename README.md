

# 📄 README.md — HotelHeaven Backend

```md
# 🏨 HotelHeaven - Backend API

HotelHeaven is a full-featured hotel booking backend built with Django and Django REST Framework.  
It allows users to explore hotels, book rooms, leave reviews, and manage their accounts with secure authentication and payment integration.
Live Link : https://hotel-heaven-backend.vercel.app/api/v1/auth/

---

## 🚀 Features

### 🔐 Authentication & User Management
- User Registration with Email Verification (Djoser + JWT)
- Login & Logout using JWT Authentication
- Custom User Model (Email-based login)
- User Profile (address, phone number)

---

### 🏨 Hotel Management
- List all hotels
- View detailed hotel information
- Hotel images support (Cloudinary)
- Category-based hotel filtering
- Search & ordering support

---

### ⭐ Reviews System
- Authenticated users can add reviews
- Rating system (1–5)
- Only review author can update/delete
- Check if user has booked before reviewing

---

### 🛒 Booking System
- Add hotel rooms to cart
- Manage cart items (add/update/delete)
- Create booking from cart
- Booking status management

---

### 💳 Payment Integration
- SSLCommerz Payment Gateway (Sandbox)
- Payment initiation API
- Success / Fail / Cancel handling
- Booking status auto-update after payment

---

### 🛠️ Admin Dashboard Features
- Manage hotels (CRUD)
- Manage categories
- View bookings
- Track users and activity

---

## 🏗️ Project Structure

```

HotelHeaven/
│
├── api/                # Main API routing
├── hotels/             # Hotel models, serializers, views
├── bookings/           # Cart, Booking, Payment logic
├── users/              # Custom user model & auth
├── core/               # Common/shared logic (if used)
│
├── fixtures/           # Sample JSON data
├── manage.py
└── requirements.txt

````

---

## ⚙️ Tech Stack

- Python 3.13
- Django
- Django REST Framework
- Djoser (Authentication)
- Simple JWT
- SQLite / PostgreSQL
- Cloudinary (Media Storage)
- SSLCommerz (Payment Gateway)
- DRF-YASG (Swagger API Docs)

---

## 🔧 Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/hotelheaven-backend.git
cd hotelheaven-backend
````

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv .hotels_env
source .hotels_env/Scripts/activate  # Windows (Git Bash)
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create `.env` file:

```env
SECRET_KEY=your_secret_key
DEBUG=True

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_password

FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://127.0.0.1:8000

cloud_name=your_cloud_name
cloudinary_api_key=your_api_key
api_secret=your_api_secret
```

---

### 5️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6️⃣ Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/hotel_data.json
```

---

### 7️⃣ Run Server

```bash
python manage.py runserver
```

---

## 📡 API Endpoints

### 🔐 Authentication

```
POST   /api/v1/auth/users/              → Register
POST   /api/v1/auth/jwt/create/         → Login
POST   /api/v1/auth/jwt/refresh/        → Refresh Token
```

---

### 🏨 Hotels

```
GET    /api/v1/hotels/                  → List hotels
GET    /api/v1/hotels/{id}/             → Hotel details
POST   /api/v1/hotels/                  → Create (Admin)
PATCH  /api/v1/hotels/{id}/             → Update (Admin)
DELETE /api/v1/hotels/{id}/             → Delete (Admin)
```

---

### 🖼️ Hotel Images

```
GET    /api/v1/hotels/{id}/images/
POST   /api/v1/hotels/{id}/images/
```

---

### ⭐ Reviews

```
GET    /api/v1/hotels/{id}/reviews/
POST   /api/v1/hotels/{id}/reviews/
PATCH  /api/v1/hotels/{id}/reviews/{id}/
DELETE /api/v1/hotels/{id}/reviews/{id}/
```

---

### 🛒 Cart

```
POST   /api/v1/carts/
GET    /api/v1/carts/{id}/
DELETE /api/v1/carts/{id}/
```

---

### 🧾 Cart Items

```
POST   /api/v1/carts/{cart_id}/items/
PATCH  /api/v1/carts/{cart_id}/items/{id}/
DELETE /api/v1/carts/{cart_id}/items/{id}/
```

---

### 📦 Booking

```
POST   /api/v1/bookings/                → Create booking
GET    /api/v1/bookings/                → List bookings
GET    /api/v1/bookings/{id}/           → Booking details
```

---

### 💳 Payment

```
POST   /api/v1/payment/initiate/
POST   /api/v1/payment/success/
POST   /api/v1/payment/fail/
POST   /api/v1/payment/cancel/
```

---

## 📄 API Documentation

Swagger UI:

```
http://127.0.0.1:8000/swagger/
```

ReDoc:

```
http://127.0.0.1:8000/redoc/
```

---

## 🔐 Permissions

* Admin → Full access
* Authenticated users → Booking, Reviews
* Guests → Read-only access

---

## 🚀 Deployment

* Can be deployed on:

  * Render
  * Railway
  * Vercel (backend proxy)
  * AWS / DigitalOcean

---

## 🔮 Future Improvements

* Payment history system
* Wallet system
* Real-time booking availability
* Recommendation system
* AI-based hotel suggestions

---

## 👨‍💻 Author

**Sakir Mohammad Safayet**
Backend Developer | Django | DRF

---

