from app.repositories.audit_repo import AuditRepository
from app.utils.logger import get_logger

logger = get_logger("pennywise.audit")


class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    async def log(
        self,
        *,
        action: str,
        user_id: str | None,
        entity: str | None = None,
        entity_id: str | None = None,
        metadata: dict | None = None,
        request=None,
    ):
        try:
            await self.repo.create(
                action=action,
                user_id=user_id,
                entity=entity,
                entity_id=entity_id,
                metadata=metadata,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )
        except Exception:
            # NEVER break main flow because of audit
            logger.exception("Audit log failed")
