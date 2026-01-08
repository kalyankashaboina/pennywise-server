from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from app.database import get_database
from app.models.transaction import TransactionInDB
from app.errors.base import AppError
from app.errors.codes import ErrorCode


class TransactionRepository:
    def __init__(self):
        self.collection = get_database()["transactions"]

    # -------------------------------------------------
    # Create single transaction
    # -------------------------------------------------
    async def create(
        self,
        user_id: str,
        payload: dict,
    ) -> TransactionInDB:
        doc = {
    **payload,
    "user_id": user_id,
    "is_deleted": False,
    "deleted_at": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}


        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)

        return TransactionInDB(**doc)

    # -------------------------------------------------
    # Bulk create (used after FE confirmation)
    # -------------------------------------------------
    async def bulk_create(
        self,
        *,
        user_id: str,
        transactions: List[dict],
        import_id: Optional[str] = None,
    ) -> List[TransactionInDB]:
        if not transactions:
            return []

        now = datetime.utcnow()

        docs = []
        for payload in transactions:
            docs.append(
                {
    **payload,
    "user_id": user_id,
    "import_id": import_id,
    "is_deleted": False,
    "deleted_at": None,
    "created_at": now,
    "updated_at": now,
}

            )

        result = await self.collection.insert_many(docs)

        for doc, oid in zip(docs, result.inserted_ids):
            doc["_id"] = str(oid)

        return [TransactionInDB(**doc) for doc in docs]

    # -------------------------------------------------
    # Update
    # -------------------------------------------------
    async def update(
        self,
        user_id: str,
        transaction_id: str,
        payload: dict,
    ) -> TransactionInDB | None:
        payload["updated_at"] = datetime.utcnow()

        doc = await self.collection.find_one_and_update(
            {
    "_id": ObjectId(transaction_id),
    "user_id": user_id,
    "is_deleted": False,
}
,
            {"$set": payload},
            return_document=True,
        )

        if not doc:
            return None

        doc["_id"] = str(doc["_id"])
        return TransactionInDB(**doc)

    # -------------------------------------------------
    # Delete
    # -------------------------------------------------
    async def delete(
        self,
        user_id: str,
        transaction_id: str,
    ) -> bool:
        result = await self.collection.update_one(
            {
                "_id": ObjectId(transaction_id),
                "user_id": user_id,
                "is_deleted": False,
            },
            {
                "$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return result.modified_count == 1


# -------------------------------------------------
# Get by ID
# -------------------------------------------------
    async def get_by_id(
        self,
        *,
        user_id: str,
        transaction_id: str,
    ) -> TransactionInDB | None:
        doc = await self.collection.find_one(
            {
                "_id": ObjectId(transaction_id),
                "user_id": user_id,
            }
        )

        if not doc:
            return None

        doc["_id"] = str(doc["_id"])
        return TransactionInDB(**doc)

    # -------------------------------------------------
    # List with pagination
    # -------------------------------------------------
    async def list(
        self,
        *,
        user_id: str,
        query: dict,
        page: int,
        limit: int,
    ) -> tuple[list[TransactionInDB], int]:
        skip = (page - 1) * limit

        base_filter = {
    "user_id": user_id,
    "is_deleted": False,
    **query,
}


        total = await self.collection.count_documents(base_filter)

        cursor = (
            self.collection
            .find(base_filter)
            .sort("date", -1)
            .skip(skip)
            .limit(limit)
        )

        results: list[TransactionInDB] = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(TransactionInDB(**doc))

        return results, total

    # -------------------------------------------------
    # List transactions for a given month (YYYY-MM)
    # -------------------------------------------------
    async def list_for_month(
        self,
        *,
        user_id: str,
        month: str,
    ) -> List[TransactionInDB]:
        try:
            start = datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid month format. Expected YYYY-MM",
                status_code=400,
            )

        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)

        cursor = (
            self.collection
            .find(
                {
                    "user_id": user_id,
                    "is_deleted": False,
                    "date": {"$gte": start, "$lt": end},
                }
            )
            .sort("date", 1)
        )

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(TransactionInDB(**doc))

        return results

    # -------------------------------------------------
    # Aggregation summary
    # -------------------------------------------------
    async def aggregate_summary(
        self,
        *,
        user_id: str,
        from_date: datetime,
        to_date: datetime,
    ) -> dict:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {
                        "$gte": from_date,
                        "$lte": to_date,
                    },
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                }
            },
        ]

        result = {
            "income": 0.0,
            "expense": 0.0,
            "net": 0.0,
        }

        async for row in self.collection.aggregate(pipeline):
            result[row["_id"]] = row["total"]

        result["net"] = result["income"] - result["expense"]
        return result
