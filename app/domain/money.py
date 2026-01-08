# app/domain/money.py

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format a number as a currency string.

    Args:
        amount: The numeric value to format
        currency_symbol: The symbol to prepend (default "$")

    Returns:
        Formatted currency string, e.g., "$1,234.56"
    """
    try:
        return f"{currency_symbol}{amount:,.2f}"
    except (TypeError, ValueError):
        # Fallback in case of invalid input
        return f"{currency_symbol}0.00"
