from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal,List


class TransactionCreate(BaseModel):
    date: datetime
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: Optional[str] = None
    description: Optional[str] = None
    source: str = "manual"
    is_recurring: bool = False


class TransactionUpdate(BaseModel):
    date: Optional[datetime] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_recurring: Optional[bool] = None


class TransactionFilter(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    category: Optional[str] = None
    type: Optional[Literal["income", "expense"]] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class BulkTransactionConfirm(BaseModel):
    import_id: Optional[str] = None
    transactions: List[TransactionCreate]
