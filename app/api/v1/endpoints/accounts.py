from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.account import Account
from app.models.user import User
from app.schemas.account import Account as AccountSchema, AccountCreate

router = APIRouter()

@router.get("/", response_model=List[AccountSchema])
async def read_accounts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve accounts.
    """
    # If superuser, can see all accounts. If not, only their own.
    if current_user.is_superuser:
        query = select(Account).offset(skip).limit(limit)
    else:
        query = select(Account).where(Account.owner_id == current_user.id).offset(skip).limit(limit)
        
    result = await db.execute(query)
    accounts = result.scalars().all()
    return accounts

@router.post("/", response_model=AccountSchema)
async def create_account(
    *,
    db: AsyncSession = Depends(deps.get_db),
    account_in: AccountCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new account.
    """
    # Check if account number exists
    result = await db.execute(select(Account).where(Account.account_number == account_in.account_number))
    existing_account = result.scalars().first()
    if existing_account:
         raise HTTPException(
            status_code=400,
            detail="Account number already exists",
        )

    account = Account(
        account_number=account_in.account_number,
        currency=account_in.currency,
        owner_id=current_user.id,
        balance=0.0
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account
