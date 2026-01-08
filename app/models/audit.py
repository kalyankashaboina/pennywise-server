from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class AuditLogInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: Optional[str]
    action: str
    entity: Optional[str]
    entity_id: Optional[str]
    metadata: dict = {}
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        populate_by_name = True
