"""统一的异常处理模块。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def add_exception_handlers(app: FastAPI):
  """为应用注册通用异常处理器。

  当前默认捕获所有异常并返回 500 状态码，
  便于在开发或部署早期阶段快速定位错误信息。
  """

  @app.exception_handler(Exception)
  async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'detail': str(exc)})
