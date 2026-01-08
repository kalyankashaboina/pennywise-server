from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from app.database import get_database
from app.models.recurring import RecurringTransactionInDB


class RecurringRepository:
    def __init__(self):
        self.collection = get_database()["recurring"]

    # -------------------------------------------------
    # Create recurring transaction
    # -------------------------------------------------
    async def create(
        self,
        user_id: str,
        payload: dict,
    ) -> RecurringTransactionInDB:
        doc = {
            **payload,
            "user_id": user_id,
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)

        return RecurringTransactionInDB(**doc)

    # -------------------------------------------------
    # Get by ID
    # -------------------------------------------------
    async def get_by_id(
        self,
        *,
        user_id: str,
        recurring_id: str,
    ) -> RecurringTransactionInDB | None:
        doc = await self.collection.find_one(
            {
                "_id": ObjectId(recurring_id),
                "user_id": user_id,
            }
        )

        if not doc:
            return None

        doc["_id"] = str(doc["_id"])
        return RecurringTransactionInDB(**doc)

    # -------------------------------------------------
    # Update recurring transaction
    # -------------------------------------------------
    async def update(
        self,
        user_id: str,
        recurring_id: str,
        payload: dict,
    ) -> RecurringTransactionInDB | None:
        payload["updated_at"] = datetime.utcnow()

        doc = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(recurring_id),
                "user_id": user_id,
            },
            {"$set": payload},
            return_document=True,
        )

        if not doc:
            return None

        doc["_id"] = str(doc["_id"])
        return RecurringTransactionInDB(**doc)

    # -------------------------------------------------
    # Delete (deactivate) recurring transaction
    # -------------------------------------------------
    async def delete(
        self,
        user_id: str,
        recurring_id: str,
    ) -> bool:
        result = await self.collection.update_one(
            {
                "_id": ObjectId(recurring_id),
                "user_id": user_id,
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return result.modified_count == 1

    # -------------------------------------------------
    # List with pagination and filters
    # -------------------------------------------------
    async def list(
        self,
        *,
        user_id: str,
        active_only: bool = True,
        frequency: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        page: int,
        limit: int,
    ) -> tuple[list[RecurringTransactionInDB], int]:
        skip = (page - 1) * limit

        base_filter = {
            "user_id": user_id,
        }

        if active_only:
            base_filter["active"] = True

        if frequency:
            base_filter["frequency"] = frequency

        if category:
            base_filter["category"] = category

        if transaction_type:
            base_filter["type"] = transaction_type

        total = await self.collection.count_documents(base_filter)

        cursor = (
            self.collection
            .find(base_filter)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        results: list[RecurringTransactionInDB] = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(RecurringTransactionInDB(**doc))

        return results, total

    # -------------------------------------------------
    # Get due recurring transactions for execution
    # -------------------------------------------------
    async def get_due_rules(
        self,
    ) -> List[RecurringTransactionInDB]:
        cursor = self.collection.find(
            {
                "active": True,
                "next_run_at": {"$lte": datetime.utcnow()},
            }
        )

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(RecurringTransactionInDB(**doc))

        return results

    # -------------------------------------------------
    # Mark recurring transaction as executed
    # -------------------------------------------------
    async def mark_executed(
        self,
        recurring_id: str,
    ) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(recurring_id)},
            {
                "$set": {
                    "last_executed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return result.modified_count == 1

    # -------------------------------------------------
    # Get all recurring transactions for a user
    # -------------------------------------------------
    async def get_all_by_user(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> List[RecurringTransactionInDB]:
        query = {"user_id": user_id}
        if active_only:
            query["active"] = True

        cursor = self.collection.find(query).sort("created_at", -1)

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(RecurringTransactionInDB(**doc))

        return results
