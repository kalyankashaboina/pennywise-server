from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    username: str
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
