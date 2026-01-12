from fastapi import APIRouter

from app.api import auth, budgets, recurring, reports, transactions, users

api_router = APIRouter()

# --------------------
# Auth & Users
# --------------------
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])


# --------------------
# Finance Core
# --------------------
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["Transactions"]
)
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["Recurring"])

# --------------------
# Reports
# --------------------
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
