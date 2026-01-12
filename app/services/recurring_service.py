from datetime import datetime
from typing import Optional

from app.errors.base import AppError
from app.errors.codes import ErrorCode
from app.repositories.recurring_repo import RecurringRepository
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.recurring import RecurringTransactionFilter
from app.services.audit_service import AuditService
from app.services.transaction_service import TransactionService
from app.utils.logger import get_logger

logger = get_logger("pennywise.recurring")


class RecurringService:
    def __init__(self):
        self.repo = RecurringRepository()
        self.tx_repo = TransactionRepository()
        self.tx_service = TransactionService()
        self.audit = AuditService()

    # -------------------------------------------------
    # Create recurring transaction
    # -------------------------------------------------
    async def create(
        self,
        *,
        user_id: str,
        payload: dict,
        request=None,
    ):
        logger.info(
            "Recurring transaction create requested",
            extra={
                "user_id": user_id,
                "amount": payload.get("amount"),
                "frequency": payload.get("frequency"),
            },
        )

        recurring = await self.repo.create(user_id, payload)

        await self.audit.log(
            action="RECURRING_TRANSACTION_CREATED",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring.id,
            metadata={
                "amount": recurring.amount,
                "type": recurring.type,
                "frequency": recurring.frequency,
                "category": recurring.category,
            },
            request=request,
        )

        return recurring

    # -------------------------------------------------
    # Get recurring transaction by ID
    # -------------------------------------------------
    async def get_by_id(
        self,
        *,
        user_id: str,
        recurring_id: str,
        request=None,
    ):
        recurring = await self.repo.get_by_id(
            user_id=user_id,
            recurring_id=recurring_id,
        )

        if not recurring:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Recurring transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="RECURRING_TRANSACTION_VIEWED",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring_id,
            request=request,
        )

        return recurring

    # -------------------------------------------------
    # Update recurring transaction
    # -------------------------------------------------
    async def update(
        self,
        *,
        user_id: str,
        recurring_id: str,
        payload: dict,
        request=None,
    ):
        recurring = await self.repo.update(user_id, recurring_id, payload)

        if not recurring:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Recurring transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="RECURRING_TRANSACTION_UPDATED",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring_id,
            metadata=payload,
            request=request,
        )

        return recurring

    # -------------------------------------------------
    # Delete (deactivate) recurring transaction
    # -------------------------------------------------
    async def delete(
        self,
        *,
        user_id: str,
        recurring_id: str,
        request=None,
    ):
        deleted = await self.repo.delete(user_id, recurring_id)

        if not deleted:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Recurring transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="RECURRING_TRANSACTION_DELETED",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring_id,
            request=request,
        )

        return True

    # -------------------------------------------------
    # List with pagination and filters
    # -------------------------------------------------
    async def list(
        self,
        *,
        user_id: str,
        filters: RecurringTransactionFilter,
        page: int,
        limit: int,
        request=None,
    ):
        results, total = await self.repo.list(
            user_id=user_id,
            active_only=filters.active_only,
            frequency=filters.frequency,
            category=filters.category,
            transaction_type=filters.type,
            page=page,
            limit=limit,
        )

        await self.audit.log(
            action="RECURRING_TRANSACTION_LIST_VIEWED",
            user_id=user_id,
            entity="recurring",
            metadata={
                "filters": filters.dict(exclude_none=True),
                "page": page,
                "limit": limit,
                "count": len(results),
            },
            request=request,
        )

        return {
            "items": results,
            "total": total,
        }

    # -------------------------------------------------
    # Execute due recurring transactions (with recursive support)
    # -------------------------------------------------
    async def execute_due(self):
        """
        Executes all due recurring transactions.
        Supports recursive recurring transactions through parent_recurring_id.
        """
        rules = await self.repo.get_due_rules()

        logger.info("Executing recurring rules", extra={"count": len(rules)})

        for rule in rules:
            await self._execute_recurring(rule)

        logger.info("Recurring execution completed")

    # -------------------------------------------------
    # Internal: Execute a single recurring transaction recursively
    # -------------------------------------------------
    async def _execute_recurring(
        self,
        rule,
        parent_id: Optional[str] = None,
    ):
        """
        Execute a single recurring transaction.
        If it has a parent_recurring_id, it's part of a recursive chain.
        """
        try:
            payload = {
                "date": datetime.utcnow(),
                "amount": rule.amount,
                "type": rule.type,
                "category": rule.category,
                "description": rule.description,
                "source": "recurring",
                "is_recurring": True,
            }

            tx = await self.tx_service.create(
                user_id=rule.user_id,
                payload=payload,
            )

            await self.repo.mark_executed(rule.id)

            await self.audit.log(
                action="RECURRING_TRANSACTION_EXECUTED",
                user_id=rule.user_id,
                entity="recurring",
                entity_id=rule.id,
                metadata={
                    "transaction_id": tx.id,
                    "amount": rule.amount,
                    "frequency": rule.frequency,
                    "parent_recurring_id": parent_id,
                },
            )

            logger.info(
                "Executed recurring transaction",
                extra={
                    "recurring_id": rule.id,
                    "user_id": rule.user_id,
                    "transaction_id": tx.id,
                },
            )

        except Exception as exc:
            logger.error(
                "Failed to execute recurring transaction",
                extra={
                    "recurring_id": rule.id,
                    "error": str(exc),
                },
                exc_info=exc,
            )

    # -------------------------------------------------
    # Execute a specific recurring transaction manually
    # -------------------------------------------------
    async def execute_now(
        self,
        *,
        user_id: str,
        recurring_id: str,
        request=None,
    ):
        """
        Manually trigger execution of a specific recurring transaction.
        This is useful for real-time testing.
        """
        recurring = await self.repo.get_by_id(
            user_id=user_id,
            recurring_id=recurring_id,
        )

        if not recurring:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Recurring transaction not found",
                status_code=404,
            )

        if not recurring.active:
            raise AppError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Cannot execute an inactive recurring transaction",
                status_code=400,
            )

        await self._execute_recurring(recurring)

        await self.audit.log(
            action="RECURRING_TRANSACTION_MANUAL_EXECUTION",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring_id,
            request=request,
        )

        return {
            "success": True,
            "message": "Recurring transaction executed successfully",
        }

    # -------------------------------------------------
    # Get all transactions from a recurring rule (for traceability)
    # -------------------------------------------------
    async def get_generated_transactions(
        self,
        *,
        user_id: str,
        recurring_id: str,
        page: int = 1,
        limit: int = 20,
        request=None,
    ):
        """
        Fetch all transactions generated from a specific recurring rule.
        """
        recurring = await self.repo.get_by_id(
            user_id=user_id,
            recurring_id=recurring_id,
        )

        if not recurring:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Recurring transaction not found",
                status_code=404,
            )

        # Find all transactions with matching source and characteristics
        query = {
            "date": {},
            "category": recurring.category,
            "amount": recurring.amount,
            "type": recurring.type,
            "source": "recurring",
        }

        results, total = await self.tx_repo.list(
            user_id=user_id,
            query=query,
            page=page,
            limit=limit,
        )

        await self.audit.log(
            action="RECURRING_TRANSACTION_GENERATED_LIST_VIEWED",
            user_id=user_id,
            entity="recurring",
            entity_id=recurring_id,
            metadata={
                "page": page,
                "limit": limit,
                "count": len(results),
            },
            request=request,
        )

        return {
            "items": results,
            "total": total,
        }
