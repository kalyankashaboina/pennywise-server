from datetime import datetime, timedelta

from app.database import get_database
from app.services.transaction_service import TransactionService
from app.utils.logger import get_logger

logger = get_logger("pennywise.recurring")


async def run_recurring_transactions():
    db = get_database()
    service = TransactionService()

    cursor = db.recurring.find(
        {
            "active": True,
            "next_run_at": {"$lte": datetime.utcnow()},
        }
    )

    async for r in cursor:
        logger.info("Running recurring transaction", extra={"id": str(r["_id"])})

        await service.create(
            user_id=str(r["user_id"]),
            payload={
                "date": datetime.utcnow(),
                "amount": r["amount"],
                "type": r["type"],
                "category": r["category"],
                "description": r["description"],
                "source": "recurring",
                "is_recurring": True,
            },
        )

        next_run = _next_run(r["frequency"])
        await db.recurring.update_one(
            {"_id": r["_id"]},
            {"$set": {"next_run_at": next_run}},
        )


def _next_run(freq: str) -> datetime:
    now = datetime.utcnow()
    return {
        "daily": now + timedelta(days=1),
        "weekly": now + timedelta(days=7),
        "monthly": now + timedelta(days=30),
    }[freq]
