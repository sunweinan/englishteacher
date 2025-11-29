from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import admin, auth, courses, install, orders, payments, products
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
  try:
    init_db()
    app.state.db_ready = True
  except Exception as exc:  # noqa: BLE001
    app.state.db_ready = False
    app.state.db_error = str(exc)

  app.include_router(auth.router, prefix='/auth', tags=['auth'])
  app.include_router(products.router, prefix='/products', tags=['products'])
  app.include_router(orders.router, prefix='/orders', tags=['orders'])
  app.include_router(payments.router, prefix='/payments', tags=['payments'])
  app.include_router(courses.router, prefix='/courses', tags=['courses'])
  app.include_router(install.router)
  app.include_router(admin.router, prefix='/admin', tags=['admin'])
  add_exception_handlers(app)
  return app


app = create_app()
