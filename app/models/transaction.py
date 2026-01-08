from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal


class TransactionInDB(BaseModel):
    # Mongo ID
    id: str = Field(alias="_id")

    # Ownership
    user_id: str

    # Core financial data
    date: datetime
    amount: float
    type: Literal["income", "expense"]
    category: Optional[str] = None
    description: Optional[str] = None

    # Source metadata
    source: str                      # manual | phonepe | pdf | recurring | bulk_confirmed
    import_id: Optional[str] = None
    is_recurring: bool = False

    # ✅ SOFT DELETE
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    # System metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
