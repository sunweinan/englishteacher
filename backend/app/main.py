"""FastAPI 应用入口，负责初始化中间件、数据库和路由。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.database import init_db
from app.core.exceptions import add_exception_handlers
from app.routes import admin, auth, courses, orders, payments, products


def create_app() -> FastAPI:
  """创建并配置 FastAPI 应用实例。

  - 初始化 CORS 中间件，放行前端域名。
  - 调用数据库初始化逻辑，标记启动状态。
  - 注册所有业务路由模块。
  """

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
  app.include_router(admin.router, prefix='/admin', tags=['admin'])
  add_exception_handlers(app)
  return app


app = create_app()
