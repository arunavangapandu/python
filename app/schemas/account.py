from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class AccountBase(BaseModel):
    account_number: Optional[str] = None
    balance: Optional[float] = 0.0
    currency: Optional[str] = "USD"

class AccountCreate(AccountBase):
    account_number: str
    currency: str

class AccountUpdate(AccountBase):
    pass

class AccountInDBBase(AccountBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Account(AccountInDBBase):
    pass
