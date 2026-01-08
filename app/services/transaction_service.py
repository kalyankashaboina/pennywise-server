from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.repositories.transaction_repo import TransactionRepository
from app.schemas.transaction import TransactionFilter
from app.services.audit_service import AuditService
from app.utils.logger import get_logger
from app.errors.base import AppError
from app.errors.codes import ErrorCode

logger = get_logger("pennywise.transactions")


class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.audit = AuditService()

    # -------------------------------------------------
    # Create single transaction
    # -------------------------------------------------
    async def create(
        self,
        *,
        user_id: str,
        payload: dict,
        request=None,
    ):
        logger.info(
            "Transaction create requested",
            extra={
                "user_id": user_id,
                "amount": payload.get("amount"),
                "type": payload.get("type"),
                "category": payload.get("category"),
                "source": payload.get("source"),
            },
        )

        tx = await self.repo.create(user_id, payload)

        await self.audit.log(
            action="TRANSACTION_CREATED",
            user_id=user_id,
            entity="transaction",
            entity_id=tx.id,
            metadata={
                "amount": tx.amount,
                "type": tx.type,
                "category": tx.category,
                "date": tx.date.isoformat(),
                "source": tx.source,
            },
            request=request,
        )

        return tx

    # -------------------------------------------------
    # Update
    # -------------------------------------------------
    async def update(
        self,
        *,
        user_id: str,
        transaction_id: str,
        payload: dict,
        request=None,
    ):
        tx = await self.repo.update(user_id, transaction_id, payload)
        if not tx:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="TRANSACTION_UPDATED",
            user_id=user_id,
            entity="transaction",
            entity_id=transaction_id,
            metadata=payload,
            request=request,
        )

        return tx

    # -------------------------------------------------
    # Delete
    # -------------------------------------------------
    async def delete(
        self,
        *,
        user_id: str,
        transaction_id: str,
        request=None,
    ):
        deleted = await self.repo.delete(user_id, transaction_id)
        if not deleted:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="TRANSACTION_DELETED",
            user_id=user_id,
            entity="transaction",
            entity_id=transaction_id,
            request=request,
        )

        return True

    # -------------------------------------------------
    # List with pagination
    # -------------------------------------------------
    async def list(
        self,
        *,
        user_id: str,
        filters: TransactionFilter,
        page: int,
        limit: int,
        request=None,
    ):
        query: dict = {}

        if filters.from_date or filters.to_date:
            query["date"] = {}
            if filters.from_date:
                query["date"]["$gte"] = filters.from_date
            if filters.to_date:
                query["date"]["$lte"] = filters.to_date

        if filters.category:
            query["category"] = filters.category

        if filters.type:
            query["type"] = filters.type

        if filters.min_amount or filters.max_amount:
            query["amount"] = {}
            if filters.min_amount:
                query["amount"]["$gte"] = filters.min_amount
            if filters.max_amount:
                query["amount"]["$lte"] = filters.max_amount

        results, total = await self.repo.list(
    user_id=user_id,
    query=query,
    page=page,
    limit=limit,
)


        await self.audit.log(
            action="TRANSACTION_LIST_VIEWED",
            user_id=user_id,
            entity="transaction",
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
# Get transaction by ID
# -------------------------------------------------
    async def get_by_id(
        self,
        *,
        user_id: str,
        transaction_id: str,
        request=None,
    ):
        tx = await self.repo.get_by_id(
            user_id=user_id,
            transaction_id=transaction_id,
        )

        if not tx:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                message="Transaction not found",
                status_code=404,
            )

        await self.audit.log(
            action="TRANSACTION_VIEWED",
            user_id=user_id,
            entity="transaction",
            entity_id=transaction_id,
            request=request,
        )

        return tx


    # -------------------------------------------------
    # CONFIRM bulk import (after FE confirmation)
    # -------------------------------------------------
    async def confirm_bulk_import(
        self,
        *,
        user_id: str,
        transactions: List[dict],
        import_id: Optional[str],
        source: str,
        request=None,
    ):
        if not import_id:
            import_id = str(uuid4())

        for tx in transactions:
            tx["source"] = source

        created = await self.repo.bulk_create(
            user_id=user_id,
            transactions=transactions,
            import_id=import_id,
        )

        await self.audit.log(
            action="TRANSACTION_BULK_CONFIRMED",
            user_id=user_id,
            entity="transaction",
            metadata={
                "count": len(created),
                "source": source,
                "import_id": import_id,
            },
            request=request,
        )

        return created

    # -------------------------------------------------
    # List transactions for a given month (YYYY-MM)
    # -------------------------------------------------
    async def list_for_month(
        self,
        *,
        user_id: str,
        month: str,
        request=None,
    ):
        """
        Get all transactions for a specific month.
        
        Args:
            user_id: The user's ID
            month: Month in YYYY-MM format
            request: Optional request object for audit logging
            
        Returns:
            List of TransactionInDB objects for the given month
        """
        transactions = await self.repo.list_for_month(
            user_id=user_id,
            month=month,
        )

        await self.audit.log(
            action="TRANSACTION_MONTH_LISTED",
            user_id=user_id,
            entity="transaction",
            metadata={
                "month": month,
                "count": len(transactions),
            },
            request=request,
        )

        return transactions

    # -------------------------------------------------
    # Aggregation summary
    # -------------------------------------------------
    async def summary(
        self,
        *,
        user_id: str,
        from_date: datetime,
        to_date: datetime,
        request=None,
    ):
        summary = await self.repo.aggregate_summary(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
        )

        await self.audit.log(
            action="TRANSACTION_SUMMARY_VIEWED",
            user_id=user_id,
            entity="transaction",
            metadata={
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
            },
            request=request,
        )

        return summary
