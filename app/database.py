from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.settings import settings
from app.utils.logger import get_logger

logger = get_logger("pennywise.db")

# ---------------------------
# Global client / DB objects
# ---------------------------
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


# ---------------------------
# Accessors
# ---------------------------
def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[settings.MONGO_DB_NAME]
    return _db


# ---------------------------
# Lifecycle
# ---------------------------
async def connect_to_database() -> None:
    global _db

    logger.info("Connecting to MongoDB")
    client = get_client()
    _db = client[settings.MONGO_DB_NAME]

    # Force connection check
    await client.admin.command("ping")

    logger.info(
        "MongoDB connected",
        extra={"database": settings.MONGO_DB_NAME},
    )

    await create_indexes()


async def close_database_connection() -> None:
    global _client, _db

    if _client:
        logger.info("Closing MongoDB connection")
        _client.close()

    _client = None
    _db = None


# -------------------------------------------------
# Index definitions (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
async def create_indexes() -> None:
    db = get_database()
    logger.info("Ensuring MongoDB indexes")

    # Helper to safely create an index
    async def safe_create_index(
        collection: "AsyncIOMotorDatabase",
        keys: list[tuple[str, int]],
        name: str,
        unique: bool = False,
    ) -> None:
        existing_indexes = await collection.index_information()
        if name in existing_indexes:
            # Check if the existing index matches the keys
            existing_keys = existing_indexes[name]["key"]
            if existing_keys != keys:
                logger.warning(
                    f"Index '{name}' exists but keys differ. Dropping "
                    "and recreating."
                )
                await collection.drop_index(name)
            else:
                logger.info(f"Index '{name}' already exists. Skipping creation.")
                return
        await collection.create_index(keys, unique=unique, name=name)
        logger.info(f"Index '{name}' created successfully.")

    # ---------------- USERS ----------------
    await safe_create_index(
        db.users, [("email", 1)], "uniq_users_email", unique=True
    )
    await safe_create_index(
        db.users, [("username", 1)], "uniq_users_username", unique=True
    )

    # ---------------- TRANSACTIONS ----------------
    await safe_create_index(
        db.transactions, [("user_id", 1), ("date", -1)], "idx_tx_user_date"
    )
    await safe_create_index(
        db.transactions, [("user_id", 1), ("type", 1)], "idx_tx_user_type"
    )
    await safe_create_index(
        db.transactions, [("user_id", 1), ("category", 1)], "idx_tx_user_category"
    )
    await safe_create_index(db.transactions, [("date", -1)], "idx_tx_date")

    # ---------------- AUDIT LOGS ----------------
    await safe_create_index(db.audit_logs, [("user_id", 1)], "idx_audit_user")
    await safe_create_index(db.audit_logs, [("action", 1)], "idx_audit_action")
    await safe_create_index(
        db.audit_logs, [("created_at", -1)], "idx_audit_created_at"
    )

    logger.info("MongoDB indexes ready")
