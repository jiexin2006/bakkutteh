# Configuration and Constants for AI Financial Intelligence Advisor

from pathlib import Path
import json


class EPFDataError(Exception):
    """Raised when EPF data file cannot be loaded or is invalid."""
    pass


class FDDataError(Exception):
    """Raised when FD data file cannot be loaded or is invalid."""
    pass


def _load_epf_standards_by_age() -> dict[int, dict[str, float]]:
    """Load EPF tier targets by age from data JSON.

    Raises:
        EPFDataError: If the data file is missing or cannot be parsed.
    """
    data_dir = Path(__file__).resolve().parent.parent / "data"
    json_path = data_dir / "epf-standards.json"

    if not json_path.exists():
        raise EPFDataError(
            f"EPF data file not found: {json_path}\n"
            f"Please ensure epf-standards.json exists in the data folder."
        )

    try:
        with json_path.open("r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)
    except json.JSONDecodeError as e:
        raise EPFDataError(f"Invalid JSON in epf-standards.json: {e}") from e

    rows = payload.get("epf_standards_by_age", [])
    targets: dict[int, dict[str, float]] = {}

    for row in rows:
        age = row.get("age")
        basic_rm = row.get("basic_rm")
        adequate_rm = row.get("adequate_rm")
        enhanced_rm = row.get("enhanced_rm")

        if not isinstance(age, int):
            continue
        if not isinstance(basic_rm, (int, float)):
            continue
        if not isinstance(adequate_rm, (int, float)):
            continue
        if not isinstance(enhanced_rm, (int, float)):
            continue

        targets[age] = {
            "basic": float(basic_rm),
            "adequate": float(adequate_rm),
            "enhanced": float(enhanced_rm),
        }

    if not targets:
        raise EPFDataError(
            "No valid EPF targets found in epf-standards.json. "
            "Expected 'epf_standards_by_age' entries with age/basic_rm/adequate_rm/enhanced_rm."
        )

    return targets


def _load_fd_rates() -> dict[str, dict[str, float]]:
    """Load FD rates from data/FD_rates&EPF_dividend.json.

    Output shape:
    {
        "Bank_Name": {"3_month": 3.2, "6_month": 3.1, "12_month": 3.4}
    }
    """
    data_dir = Path(__file__).resolve().parent.parent / "data"
    json_path = data_dir / "FD_rates&EPF_dividend.json"

    if not json_path.exists():
        raise FDDataError(
            f"FD data file not found: {json_path}\n"
            "Please ensure FD_rates&EPF_dividend.json exists in the data folder."
        )

    try:
        with json_path.open("r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)
    except json.JSONDecodeError as e:
        raise FDDataError(f"Invalid JSON in FD_rates&EPF_dividend.json: {e}") from e

    rows = payload.get("fixed_deposits", [])
    if not isinstance(rows, list) or not rows:
        raise FDDataError(
            "No valid fixed_deposits entries found in FD_rates&EPF_dividend.json."
        )

    rates: dict[str, dict[str, float]] = {}
    for row in rows:
        bank_name = row.get("bank_name")
        tenure_months = row.get("tenure_months")
        interest_rate_pct = row.get("interest_rate_pct")

        if not isinstance(bank_name, str):
            continue
        if not isinstance(tenure_months, int):
            continue
        if not isinstance(interest_rate_pct, (int, float)):
            continue

        period = f"{tenure_months}_month"
        if period not in {"3_month", "6_month", "12_month"}:
            continue

        normalized_bank = bank_name.strip().replace(" ", "_")
        if normalized_bank not in rates:
            rates[normalized_bank] = {}

        # Keep the highest offered rate per bank/tenure if multiple products exist.
        current_rate = rates[normalized_bank].get(period)
        if current_rate is None or float(interest_rate_pct) > current_rate:
            rates[normalized_bank][period] = float(interest_rate_pct)

    if not rates:
        raise FDDataError(
            "Could not parse any supported FD rate entries (3/6/12 months) from the data file."
        )

    return rates


# EPF tiered savings targets (in MYR) loaded from data/epf-standards.json
EPF_TIER_TARGETS = _load_epf_standards_by_age()

# Backward-compatible basic targets map
EPF_TARGETS = {age: tiers["basic"] for age, tiers in EPF_TIER_TARGETS.items()}


def get_nearest_epf_age(age: int) -> int:
    """Return the closest age key available in EPF target data."""
    if not EPF_TIER_TARGETS:
        raise EPFDataError("EPF target data is empty.")

    ages = sorted(EPF_TIER_TARGETS)
    if age <= ages[0]:
        return ages[0]
    if age >= ages[-1]:
        return ages[-1]
    return min(ages, key=lambda candidate: abs(candidate - age))


def get_epf_targets_for_age(age: int) -> dict[str, float]:
    """Get basic/adequate/enhanced targets for the nearest supported age."""
    nearest_age = get_nearest_epf_age(age)
    return EPF_TIER_TARGETS[nearest_age]

# Interpolate targets for ages not in the table
def get_epf_target(age: int, tier: str = "basic") -> float:
    """Get the EPF savings target for a given age and tier."""
    if not EPF_TARGETS:
        return 0

    normalized_tier = tier.lower().strip()
    if normalized_tier not in {"basic", "adequate", "enhanced"}:
        raise EPFDataError(
            f"Unsupported EPF tier '{tier}'. Supported tiers: basic, adequate, enhanced."
        )

    # Exact age -> exact tier lookup
    if age in EPF_TIER_TARGETS:
        return EPF_TIER_TARGETS[age][normalized_tier]

    # Schema requires nearest age fallback if exact match does not exist.
    nearest_age = get_nearest_epf_age(age)
    return EPF_TIER_TARGETS[nearest_age][normalized_tier]


# Risk Appetite Profiles
RISK_PROFILES = {
    "Conservative": {
        "fd_weight": 0.60,       # 60% Fixed Deposit
        "epf_weight": 0.35,      # 35% EPF
        "crypto_weight": 0.05    # 5% Crypto
    },
    "Moderate": {
        "fd_weight": 0.40,
        "epf_weight": 0.40,
        "crypto_weight": 0.20
    },
    "Aggressive": {
        "fd_weight": 0.20,
        "epf_weight": 0.30,
        "crypto_weight": 0.50
    }
}

# Fixed Deposit Rates (annual %) loaded from data/FD_rates&EPF_dividend.json
FD_RATES = _load_fd_rates()

# EPF Interest Rates (average annual %)
EPF_INTEREST_RATE = 3.5

# Bitcoin Volatility Thresholds
BITCOIN_THRESHOLDS = {
    "high_volatility": 5.0,     # % daily change threshold
    "low_volatility": 1.0       # % daily change threshold
}

# Confidence Score Thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.75,
    "medium": 0.50,
    "low": 0.0
}

# Allocation Adjustment based on EPF Status
EPF_DEFICIT_ADJUSTMENTS = {
    "critical": 0.1,   # If deficit > 40%, reduce crypto to 10% of max
    "high": 0.3,       # If deficit > 20%, reduce crypto to 30% of max
    "moderate": 0.6,   # If deficit > 10%, reduce crypto to 60% of max
    "low": 1.0         # On track, use normal allocation
}

# Minimum thresholds for allocation
MIN_FD_ALLOCATION = 0.10  # At least 10% in FD for liquidity
MIN_EPF_ALLOCATION = 0.15 # At least 15% in EPF for retirement
MAX_CRYPTO_ALLOCATION = 0.50 # Max 50% in crypto regardless

# Minimum placement rules
FD_MIN_PLACEMENT_RM = 500.0
BITCOIN_MIN_PLACEMENT_RM = 100.0

# Simulation settings
PROJECTION_MONTHS = 12
SCENARIOS = {
    "conservative": 0.04,  # 4% annual growth
    "moderate": 0.08,      # 8% annual growth
    "bullish": 0.15        # 15% annual growth (Bitcoin)
}
