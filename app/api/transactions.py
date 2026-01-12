from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.dependencies.auth import get_current_user
from app.schemas.transaction import (
    BulkTransactionConfirm,
    TransactionCreate,
    TransactionFilter,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService

router = APIRouter(tags=["Transactions"])
service = TransactionService()


# -------------------------------------------------
# Create single transaction
# -------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    tx = await service.create(
        user_id=current_user.id,
        payload=payload.dict(),
        request=request,
    )

    return {
        "success": True,
        "data": tx,
    }


# -------------------------------------------------
# Bulk confirm transactions
# -------------------------------------------------
@router.post("/bulk/confirm", status_code=status.HTTP_201_CREATED)
async def confirm_bulk_import(
    payload: BulkTransactionConfirm,
    request: Request,
    current_user=Depends(get_current_user),
):
    created = await service.confirm_bulk_import(
        user_id=current_user.id,
        transactions=[t.dict() for t in payload.transactions],
        import_id=payload.import_id,
        source="bulk_confirmed",
        request=request,
    )

    return {
        "success": True,
        "count": len(created),
        "import_id": payload.import_id,
    }


# -------------------------------------------------
# Transaction summary (must be before {transaction_id})
# -------------------------------------------------
@router.get("/summary")
async def transaction_summary(
    from_date: datetime,
    to_date: datetime,
    request: Request,
    current_user=Depends(get_current_user),
):
    summary = await service.summary(
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
        request=request,
    )

    return {
        "success": True,
        "data": summary,
    }


# -------------------------------------------------
# List transactions with pagination
# -------------------------------------------------
@router.get("/")
async def list_transactions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    current_user=Depends(get_current_user),
):
    filters = TransactionFilter(
        from_date=from_date,
        to_date=to_date,
        category=category,
        type=type,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    result = await service.list(
        user_id=current_user.id,
        filters=filters,
        page=page,
        limit=limit,
        request=request,
    )

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": result["total"],
        "count": len(result["items"]),
        "pages": (result["total"] + limit - 1) // limit,
        "data": result["items"],
    }


# -------------------------------------------------
# Get transaction by ID
# -------------------------------------------------
@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str = Path(..., description="Transaction ID (24-char hex)"),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    tx = await service.get_by_id(
        user_id=current_user.id,
        transaction_id=transaction_id,
        request=request,
    )

    return {
        "success": True,
        "data": tx,
    }


# -------------------------------------------------
# Update transaction
# -------------------------------------------------
@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str = Path(..., description="Transaction ID (24-char hex)"),
    payload: TransactionUpdate = None,
    request: Request = None,
    current_user=Depends(get_current_user),
):
    await service.update(
        user_id=current_user.id,
        transaction_id=transaction_id,
        payload=payload.dict(exclude_unset=True),
        request=request,
    )

    return {"success": True}


# -------------------------------------------------
# Delete transaction
# -------------------------------------------------
@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
async def delete_transaction(
    transaction_id: str = Path(..., description="Transaction ID (24-char hex)"),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    await service.delete(
        user_id=current_user.id,
        transaction_id=transaction_id,
        request=request,
    )

    return {"success": True}
