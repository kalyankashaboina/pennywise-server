# PennyBank - Personal Finance Management Backend

A production-grade personal finance backend API built with FastAPI and MongoDB. Manage transactions, budgets, recurring payments, and financial reports with secure authentication.

---

## Features

- **User Management** – Registration, login, authentication with secure cookies
- **Transaction Tracking** – Record, categorize, and search financial transactions
- **Budget Management** – Set and monitor spending budgets across categories
- **Recurring Transactions** – Automate recurring payments and income
- **Financial Reports** – Generate PDF reports with charts and summaries
- **PDF Import** – Import transactions from bank statements (PhonePe support)
- **Audit Logging** – Track all user actions for compliance and security

---

## Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** MongoDB with async driver (Motor)
- **Authentication:** JWT with secure cookies
- **PDF Processing:** PyPDF, WeasyPrint
- **Task Scheduling:** APScheduler
- **Logging:** Structured JSON logging with request tracking

---

## Project Structure

```
app/
├── api/              # HTTP routes and endpoints
├── services/         # Business logic layer
├── repositories/     # Database access layer
├── models/           # Internal data models
├── schemas/          # API request/response contracts
├── domain/           # Finance domain rules
├── middleware/       # Request logging, timing, request IDs
├── errors/           # Error handling and mapping
├── dependencies/     # Auth and database dependencies
├── tasks/            # Background jobs and schedulers
├── utils/            # Helper utilities
├── database.py       # MongoDB connection lifecycle
├── security.py       # Authentication and password hashing
├── settings.py       # Environment configuration
└── main.py           # Application bootstrap
```

---

## Architecture

```
Client → FastAPI Router → Services → Repositories → MongoDB
                ↓
        Middleware (Logging, Timing, Auth)
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB
- pip/venv

### Installation

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with MongoDB URI, JWT secret, etc.

# Run the application
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

---

## API Endpoints

### Authentication
- `POST /api/auth/register` – Create new account
- `POST /api/auth/login` – User login
- `POST /api/auth/logout` – User logout
- `POST /api/auth/refresh` – Refresh token
- `GET /api/auth/me` – Get current user

### Users
- `GET /api/users/{user_id}` – Get user profile
- `PUT /api/users/{user_id}` – Update profile

### Transactions
- `POST /api/transactions` – Create transaction
- `GET /api/transactions` – List transactions
- `PUT /api/transactions/{id}` – Update transaction
- `DELETE /api/transactions/{id}` – Delete transaction

### Budgets
- `POST /api/budgets` – Create budget
- `GET /api/budgets` – List budgets
- `PUT /api/budgets/{id}` – Update budget

### Recurring Transactions
- `POST /api/recurring` – Create recurring transaction
- `GET /api/recurring` – List recurring transactions

### Reports
- `GET /api/reports/summary` – Financial summary
- `GET /api/reports/pdf` – Generate PDF report

---

## Development

```bash
# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload

# View logs
# Check app/utils/logger.py for structured JSON logging
```

---

## License

Proprietary - Personal Project

Uses HTTP-only cookies with JWT.

---

## Transactions

- Income & expenses
- Categories
- Date-based filters

---

## Budgets

- Monthly category limits
- Budget vs actual

---

## Recurring Transactions

- Subscriptions
- Auto-generated entries

---

## Reports

- Monthly summaries
- Category analytics
- Export ready

---

## Audit Logs

Tracks:
- Auth actions
- Financial changes

---

## Running the App

python -m venv .venv
activate environment
pip install -r requirements.txt
uvicorn app.main:app --reload

Docs: /docs

---

## Status

Auth complete
Core architecture stable
Transactions next
