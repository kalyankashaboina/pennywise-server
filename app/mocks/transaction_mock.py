from datetime import datetime

TRANSACTION_MOCKS = [
    {
        "_id": "t1",
        "user_id": "user1",
        "date": datetime(2026, 1, 5, 12, 0),
        "amount": 500.0,
        "type": "income",
        "category": "Salary",
        "description": "January salary",
        "source": "bulk_confirmed",
        "import_id": "import1",
        "is_recurring": False,
        "created_at": datetime(2026, 1, 5, 12, 0),
    },
    {
        "_id": "t2",
        "user_id": "user1",
        "date": datetime(2026, 1, 5, 13, 0),
        "amount": 50.0,
        "type": "expense",
        "category": "Food",
        "description": "Lunch",
        "source": "bulk_confirmed",
        "import_id": "import1",
        "is_recurring": False,
        "created_at": datetime(2026, 1, 5, 13, 0),
    },
    # Add more mock transactions (total 10-15 for testing)
]
