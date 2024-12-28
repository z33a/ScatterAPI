# External imports
from datetime import datetime, timezone
from decimal import Decimal

def current_timestamp() -> float:
    # Returns the current UTC timestamp as a Decimal
    return datetime.now(timezone.utc).timestamp()