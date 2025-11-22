# EnglishTeacher Commerce Skeleton

This repository contains a Vue 3 + TypeScript frontend (Vite) and a FastAPI backend with MySQL persistence and JWT-based authentication.

## Frontend
- Located in `frontend/`
- Vue Router with login and admin role guards
- Pinia stores for user/session and cart
- Axios interceptors attach JWT and redirect to login on 401
- Basic pages: Home, Login, Product List/Detail, Checkout with WeChat JS-SDK hooks, admin placeholders

### Run
```bash
cd frontend
npm install
npm run dev
```

## Backend
- Located in `backend/`
- FastAPI with SQLAlchemy, JWT auth, product/order/payment services, and admin routes
- MySQL connection configured via `DATABASE_URL`

### Run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker Compose
A `docker-compose.yml` is provided to start MySQL, backend, and frontend together.
