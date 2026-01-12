from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    username: str
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
