"""
=========================================================
Formatting Utility Layer
ABLBL Sourcing Intelligence Platform
=========================================================
"""

def fmt_price(val, decimals=2):
    """
    Format currency/price values.
    Example:
    454.9445400593472 -> 454.94
    """
    try:
        return f"{float(val):,.{decimals}f}"
    except (ValueError, TypeError):
        return "—"


def fmt_pct(val):
    """
    Format percentage values.
    Example:
    98.333333 -> 98.3%
    """
    try:
        return f"{float(val):.1f}%"
    except (ValueError, TypeError):
        return "—"


def fmt_int(val):
    """
    Format whole numbers.
    Example:
    12345.0 -> 12,345
    """
    try:
        return f"{int(float(val)):,}"
    except (ValueError, TypeError):
        return "—"


def fmt_id(val):
    """
    Format IDs and codes.
    Example:
    1208915.0 -> 1208915
    """
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val)


def fmt_price_with_unit(val, unit=None):
    """
    Format standardized price for ERP display.

    Examples
    --------
    55508.15 + ₹/Candy -> ₹55,508 / Candy
    487.24 + ₹/Kg      -> ₹487 / Kg
    """

    try:
        price = f"₹{float(val):,.0f}"

        if unit:
            # Remove ₹/ or Rs/ from the unit to avoid duplication
            clean_unit = (
                str(unit)
                .replace("₹/", "")
                .replace("Rs/", "")
                .replace("Rs", "")
                .replace("₹", "")
                .strip()
            )

            return f"{price} / {clean_unit}"

        return price

    except (ValueError, TypeError):
        return "—"