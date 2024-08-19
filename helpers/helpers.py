from datetime import datetime
from typing import Dict


def generate_initials(name: str) -> str:
    """Generate initials from a name."""
    name_parts = name.split()
    if len(name_parts) == 1:
        # Single name: use the first 3 letters
        initials = name_parts[0][:3].upper()
    else:
        # Multiple names: use the first letter of each part
        initials = "".join(part[0].upper() for part in name_parts)
    # Ensure initials do not exceed 4 characters
    return initials[:4]


def get_today_date() -> str:
    """Retrieve today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def count_money(bill_counts: Dict[int, int], cent_counts: Dict[int, int]) -> float:
    """Retrive the sum of money of the bills and cents given."""
    bill_count = 0
    for denom, count in bill_counts.items():
        bill_count += denom * count

    cent_count = 0
    for denom, count in cent_counts.items():
        cent_count += (denom / 100) * count
    return bill_count + cent_count
