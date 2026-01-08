from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, field_validator


# -------------------------------------------------
# Internal DB model (never returned directly)
# -------------------------------------------------
class UserInDB(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    avatar: Optional[str] = None

    # password reset
    reset_token_hash: Optional[str] = None
    reset_token_expires_at: Optional[datetime] = None

    is_active: bool = True
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_object_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True


# -------------------------------------------------
# Request model (Register)
# -------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    avatar: Optional[str] = None


# -------------------------------------------------
# Public response model (safe for FE)
# -------------------------------------------------
class UserPublic(BaseModel):
    id: str
    email: EmailStr
    username: str
    avatar: Optional[str] = None
    created_at: datetime
