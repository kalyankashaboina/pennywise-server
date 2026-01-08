from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RecurringTransactionInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    amount: float
    type: Literal["income", "expense"]
    category: str
    description: str
    frequency: Literal[
        "daily", "weekly", "monthly", "yearly"
    ]
    next_run_at: datetime
    active: bool = True
    parent_recurring_id: Optional[str] = None  # For recursive recurring transactions
    last_executed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
