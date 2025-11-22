from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, products, orders, payments, admin
from app.core.database import init_db
from app.core.exceptions import add_exception_handlers


def create_app() -> FastAPI:
  app = FastAPI(title='EnglishTeacher Shop')
  app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
  )
  init_db()
  app.include_router(auth.router, prefix='/auth', tags=['auth'])
  app.include_router(products.router, prefix='/products', tags=['products'])
  app.include_router(orders.router, prefix='/orders', tags=['orders'])
  app.include_router(payments.router, prefix='/payments', tags=['payments'])
  app.include_router(admin.router, prefix='/admin', tags=['admin'])
  add_exception_handlers(app)
  return app


app = create_app()
