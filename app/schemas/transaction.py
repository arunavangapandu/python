from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.transaction import TransactionType

class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    account_id: int

class TransactionInDBBase(TransactionBase):
    id: int
    account_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class Transaction(TransactionInDBBase):
    pass
