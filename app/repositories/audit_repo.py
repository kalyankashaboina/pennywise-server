from datetime import datetime

from bson import ObjectId

from app.database import get_database
from app.models.audit import AuditLogInDB


class AuditRepository:
    def __init__(self):
        self.col = get_database().audit_logs

    async def create(
        self,
        *,
        action: str,
        user_id: str | None,
        entity: str | None = None,
        entity_id: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLogInDB:
        doc = {
            "action": action,
            "user_id": ObjectId(user_id) if user_id else None,
            "entity": entity,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow(),
        }

        res = await self.col.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        if doc["user_id"]:
            doc["user_id"] = str(doc["user_id"])

        return AuditLogInDB(**doc)
