import os
from pydantic import BaseModel


class Settings(BaseModel):
  database_url: str = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost:3306/englishteacher')
  jwt_secret: str = os.getenv('JWT_SECRET', 'supersecret')
  jwt_algorithm: str = 'HS256'
  access_token_expire_minutes: int = 60 * 24
  cors_origins: list[str] = os.getenv('CORS_ORIGINS', '*').split(',')


settings = Settings()
