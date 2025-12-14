# Banking API

Production-ready Banking API built with FastAPI, Async SQLAlchemy, and PostgreSQL.

## Features

- **Authentication**: JWT based OAuth2 password flow.
- **Users**: User registration and management.
- **Accounts**: Create and list bank accounts.
- **Transactions**: Deposit, Withdraw, and Transfer money between accounts (atomically).
- **Async**: Fully async database operations using `asyncpg`.
- **Validation**: Pydantic models for request/response validation.
- **Security**: Password hashing with Bcrypt.

## Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Database Setup**

Ensure you have a PostgreSQL database running. Update the `DATABASE_URL` in `.env` (or set env var).
Default is: `postgresql+asyncpg://postgres:postgres@localhost:5432/banking_db`

3. **Run Migrations**

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

4. **Run Application**

```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Auth
- `POST /api/v1/login/access-token`: Login to get JWT token.

### Users
- `POST /api/v1/users/`: Register a new user.
- `GET /api/v1/users/me`: Get current user details.

### Accounts
- `POST /api/v1/accounts/`: Create a new account.
- `GET /api/v1/accounts/`: List your accounts.

### Transactions
- `POST /api/v1/transactions/deposit`: Deposit money.
- `POST /api/v1/transactions/withdraw`: Withdraw money.
- `POST /api/v1/transactions/transfer`: Transfer money to another account.
- `GET /api/v1/transactions/`: List transactions.
