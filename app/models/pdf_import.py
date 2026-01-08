from datetime import datetime
from pydantic import BaseModel, Field


class PdfImportInDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    filename: str
    source: str
    status: str
    created_at: datetime
