from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class RecurringTransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str
    description: str
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    next_run_at: datetime
    parent_recurring_id: Optional[str] = None  # For linking recursive recurring transactions


class RecurringTransactionUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    next_run_at: Optional[datetime] = None
    active: Optional[bool] = None


class RecurringTransactionFilter(BaseModel):
    frequency: Optional[str] = None
    category: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    active_only: bool = True
