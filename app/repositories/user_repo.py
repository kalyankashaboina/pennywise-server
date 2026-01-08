from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.database import get_database
from app.models.user import UserInDB


class UserRepository:
    def __init__(self):
        self.collection = get_database()["users"]

    # -------------------------
    # Queries
    # -------------------------
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
        return UserInDB(**doc)

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"username": username})
        if not doc:
            return None
        return UserInDB(**doc)

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        return UserInDB(**doc)

    async def get_by_reset_token(self, token_hash: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one(
            {
                "reset_token_hash": token_hash,
                "reset_token_expires_at": {"$gt": datetime.utcnow()},
            }
        )
        if not doc:
            return None
        return UserInDB(**doc)

    # -------------------------
    # Mutations
    # -------------------------
    async def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        avatar: Optional[str] = None,
    ) -> UserInDB:
        doc = {
            "email": email,
            "username": username,
            "hashed_password": hashed_password,
            "avatar": avatar,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "reset_token_hash": None,
            "reset_token_expires_at": None,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return UserInDB(**doc)

    async def set_reset_token(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "reset_token_hash": token_hash,
                    "reset_token_expires_at": expires_at,
                }
            },
        )

    async def update_password(
        self,
        user_id: str,
        hashed_password: str,
    ) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "reset_token_hash": None,
                    "reset_token_expires_at": None,
                }
            },
        )
