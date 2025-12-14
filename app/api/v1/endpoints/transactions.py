from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.transaction import Transaction, TransactionType
from app.models.account import Account
from app.models.user import User
from app.schemas.transaction import Transaction as TransactionSchema, TransactionCreate

router = APIRouter()

@router.get("/", response_model=List[TransactionSchema])
async def read_transactions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve transactions for current user.
    """
    # Find all accounts for user
    result = await db.execute(select(Account.id).where(Account.owner_id == current_user.id))
    account_ids = result.scalars().all()
    
    if not account_ids:
        return []

    # Find transactions for these accounts
    query = select(Transaction).where(Transaction.account_id.in_(account_ids)).offset(skip).limit(limit)
    result = await db.execute(query)
    transactions = result.scalars().all()
    return transactions

@router.post("/deposit", response_model=TransactionSchema)
async def deposit(
    *,
    db: AsyncSession = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Deposit money into an account.
    """
    if transaction_in.type != TransactionType.DEPOSIT:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    
    result = await db.execute(select(Account).where(Account.id == transaction_in.account_id))
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Verify ownership (or allow deposits from others? restricting to owner for now)
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    account.balance += transaction_in.amount
    
    transaction = Transaction(
        account_id=account.id,
        amount=transaction_in.amount,
        type=TransactionType.DEPOSIT,
        description=transaction_in.description
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

@router.post("/withdraw", response_model=TransactionSchema)
async def withdraw(
    *,
    db: AsyncSession = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Withdraw money from an account.
    """
    if transaction_in.type != TransactionType.WITHDRAWAL:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
        
    result = await db.execute(select(Account).where(Account.id == transaction_in.account_id))
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    if account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if account.balance < transaction_in.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    account.balance -= transaction_in.amount
    
    transaction = Transaction(
        account_id=account.id,
        amount=transaction_in.amount,
        type=TransactionType.WITHDRAWAL,
        description=transaction_in.description
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

class TransferSchema(TransactionCreate):
    to_account_id: int

@router.post("/transfer", response_model=TransactionSchema)
async def transfer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    transfer_in: TransferSchema,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Transfer money between accounts.
    """
    if transfer_in.type != TransactionType.TRANSFER:
         raise HTTPException(status_code=400, detail="Invalid transaction type")

    # Fetch source account
    result = await db.execute(select(Account).where(Account.id == transfer_in.account_id))
    source_account = result.scalars().first()
    
    if not source_account:
        raise HTTPException(status_code=404, detail="Source account not found")
        
    if source_account.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if source_account.balance < transfer_in.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Fetch destination account
    result = await db.execute(select(Account).where(Account.id == transfer_in.to_account_id))
    dest_account = result.scalars().first()
    
    if not dest_account:
        raise HTTPException(status_code=404, detail="Destination account not found")

    # Perform transfer
    source_account.balance -= transfer_in.amount
    dest_account.balance += transfer_in.amount
    
    # Record transaction (for source)
    transaction = Transaction(
        account_id=source_account.id,
        amount=transfer_in.amount,
        type=TransactionType.TRANSFER,
        description=f"Transfer to account {dest_account.account_number}. {transfer_in.description or ''}"
    )
    
    # Optionally record transaction for destination as well, or have a smarter transaction model linking two accounts.
    # For simplicity, we record the debit on source.
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction
