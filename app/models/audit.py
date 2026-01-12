from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuditLogInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: Optional[str] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        populate_by_name = True
