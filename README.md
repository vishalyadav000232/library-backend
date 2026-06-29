# 📚 Yadav Ji Library — Backend

A production-ready Library Management System backend built with **FastAPI**, featuring real-time seat booking, JWT authentication, Redis-based race condition prevention, and Razorpay payment integration.

---

## 🚀 Live Demo

> Coming soon — deploy in progress

---

## ✨ Features

- **JWT Authentication** — Access + Refresh token rotation with httponly cookies
- **Role-Based Access Control** — Student and Admin roles with route guards
- **Seat Booking System** — Real-time seat locking using Redis to prevent race conditions
- **WebSocket Support** — Live seat availability updates for admin dashboard
- **Payment Integration** — Razorpay order creation and webhook verification
- **PDF Report Generation** — Downloadable booking reports
- **Shift Management** — Morning/Evening shift support for seat bookings
- **Admin Dashboard** — Full user, seat, booking, and revenue management

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Migrations | Alembic |
| Cache / Lock | Redis |
| Auth | JWT (python-jose) |
| Payments | Razorpay |
| Real-time | WebSockets |
| Password | bcrypt (passlib) |
| PDF | ReportLab |

---

## 📁 Project Structure

```
app/
├── api/
│   ├── admin/          # Admin-only routes (users, seats, bookings, shifts)
│   └── v1/             # Public routes (auth, bookings, payments, reports)
├── auth/               # JWT token provider with interface pattern
├── database/           # DB session and engine setup
├── middleware/         # Token rotation middleware
├── models/             # SQLAlchemy models
├── payments/           # Razorpay client
├── redis/              # Seat locking with Redis
├── repository/         # Data access layer (Repository pattern)
├── schemas/            # Pydantic request/response schemas
├── services/           # Business logic layer
├── utils/              # PDF generator, booking utils
└── websockets/         # WebSocket connection manager
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### 1. Clone the repo
```bash
git clone https://github.com/vishalyadav000232/library-backend.git
cd library-backend
```

### 2. Create virtual environment
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in the root:
```env
SQLALCHEMY_DATABASE_URL=postgresql://user:password@localhost/library_db
SECRET_KEY=your_secret_key_here
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=http://localhost:5173
```

### 5. Run migrations
```bash
alembic upgrade head
```

### 6. Start the server
```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

## 🔑 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT + sets cookie) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout and clear cookie |
| GET | `/api/v1/auth/me` | Get current user profile |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/bookings/` | Create a booking |
| GET | `/api/v1/bookings/me` | Get my bookings |
| GET | `/api/v1/bookings/{id}` | Get booking by ID |
| PATCH | `/api/v1/bookings/{id}/cancel` | Cancel booking |
| POST | `/api/v1/bookings/create-with-payment` | Book + create Razorpay order |
| POST | `/api/v1/bookings/verify-payment` | Verify Razorpay payment |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard` | Dashboard stats |
| GET | `/api/v1/admin/user` | List all users |
| GET/POST | `/api/v1/admin/seats` | Manage seats |
| GET/POST | `/api/v1/admin/bookings` | Manage bookings |
| GET/POST | `/api/v1/admin/shifts` | Manage shifts |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/admin` | Real-time seat updates |

---

## 🔐 Architecture Highlights

### Redis Seat Locking
Prevents double-booking race conditions — seat is locked in Redis for 5 minutes during payment flow, then released on confirmation.

### Token Rotation
Refresh tokens are rotated on every use and stored hashed in the database. Middleware auto-rotates tokens on each request.

### Repository Pattern
All DB queries are abstracted behind repository interfaces, making services fully testable and database-agnostic.

---

## 👨‍💻 Author

**Vishal Yadav**
- GitHub: [@vishalyadav000232](https://github.com/vishalyadav000232)
- LinkedIn: [vishalyadav000232-dev](https://linkedin.com/in/vishalyadav000232-dev)
- Email: vishalyadav000232@gmail.com

---

## 📄 License

MIT License