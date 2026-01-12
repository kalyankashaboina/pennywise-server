from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.dependencies.auth import get_current_user
from app.schemas.recurring import (
    RecurringTransactionCreate,
    RecurringTransactionFilter,
    RecurringTransactionUpdate,
)
from app.services.recurring_service import RecurringService

router = APIRouter(tags=["Recurring Transactions"])
service = RecurringService()


# -------------------------------------------------
# Create recurring transaction
# -------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recurring(
    payload: RecurringTransactionCreate,
    request: Request,
    current_user=Depends(get_current_user),
):
    recurring = await service.create(
        user_id=current_user.id,
        payload=payload.dict(),
        request=request,
    )

    return {
        "success": True,
        "data": recurring,
    }


# -------------------------------------------------
# Execute recurring transaction NOW (Real-time Testing)
# -------------------------------------------------
@router.post("/{recurring_id}/execute-now", status_code=status.HTTP_200_OK)
async def execute_recurring_now(
    recurring_id: str = Path(..., description="Recurring Transaction ID (24-char hex)"),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    """
    Manually trigger execution of a recurring transaction immediately.
    This is useful for real-time testing and verification.
    """
    result = await service.execute_now(
        user_id=current_user.id,
        recurring_id=recurring_id,
        request=request,
    )

    return result


# -------------------------------------------------
# Get generated transactions from a recurring rule
# -------------------------------------------------
@router.get("/{recurring_id}/transactions")
async def get_recurring_transactions(
    recurring_id: str = Path(..., description="Recurring Transaction ID (24-char hex)"),
    request: Request = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """
    Fetch all transactions generated from a specific recurring rule.
    Useful for tracking and verifying recurring transaction execution.
    """
    result = await service.get_generated_transactions(
        user_id=current_user.id,
        recurring_id=recurring_id,
        page=page,
        limit=limit,
        request=request,
    )

    return {
        "success": True,
        "recurring_id": recurring_id,
        "page": page,
        "limit": limit,
        "total": result["total"],
        "count": len(result["items"]),
        "pages": (result["total"] + limit - 1) // limit,
        "data": result["items"],
    }


# -------------------------------------------------
# Get recurring transaction by ID
# -------------------------------------------------
@router.get("/{recurring_id}")
async def get_recurring(
    recurring_id: str = Path(..., description="Recurring Transaction ID (24-char hex)"),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    recurring = await service.get_by_id(
        user_id=current_user.id,
        recurring_id=recurring_id,
        request=request,
    )

    return {
        "success": True,
        "data": recurring,
    }


# -------------------------------------------------
# Update recurring transaction
# -------------------------------------------------
@router.put("/{recurring_id}")
async def update_recurring(
    recurring_id: str = Path(..., description="Recurring Transaction ID (24-char hex)"),
    payload: RecurringTransactionUpdate = None,
    request: Request = None,
    current_user=Depends(get_current_user),
):
    recurring = await service.update(
        user_id=current_user.id,
        recurring_id=recurring_id,
        payload=payload.dict(exclude_unset=True),
        request=request,
    )

    return {
        "success": True,
        "data": recurring,
    }


# -------------------------------------------------
# Delete (deactivate) recurring transaction
# -------------------------------------------------
@router.delete("/{recurring_id}", status_code=status.HTTP_200_OK)
async def delete_recurring(
    recurring_id: str = Path(..., description="Recurring Transaction ID (24-char hex)"),
    request: Request = None,
    current_user=Depends(get_current_user),
):
    await service.delete(
        user_id=current_user.id,
        recurring_id=recurring_id,
        request=request,
    )

    return {"success": True}


# -------------------------------------------------
# List recurring transactions with pagination and filters
# -------------------------------------------------
@router.get("/")
async def list_recurring(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    frequency: Optional[str] = Query(None, pattern="^(daily|weekly|monthly|yearly)$"),
    category: Optional[str] = None,
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    active_only: bool = Query(True),
    current_user=Depends(get_current_user),
):
    filters = RecurringTransactionFilter(
        frequency=frequency,
        category=category,
        type=type,
        active_only=active_only,
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
