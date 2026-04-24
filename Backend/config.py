# Configuration and Constants for AI Financial Intelligence Advisor

from pathlib import Path
import json


class EPFDataError(Exception):
    """Raised when EPF data file cannot be loaded or is invalid."""
    pass


def _load_epf_targets() -> dict[int, float]:
    """Load EPF basic targets from data JSON.
    
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
    targets: dict[int, float] = {}
    
    for row in rows:
        age = row.get("age")
        basic_rm = row.get("basic_rm")
        if isinstance(age, int) and isinstance(basic_rm, (int, float)):
            targets[age] = float(basic_rm)
    
    if not targets:
        raise EPFDataError(
            "No valid EPF targets found in epf-standards.json. "
            "Expected 'epf_standards_by_age' array with 'age' and 'basic_rm' fields."
        )
    
    return targets


# EPF Basic Savings Targets (in MYR) loaded from data/epf-standards_Version2.json
EPF_TARGETS = _load_epf_targets()

# Interpolate targets for ages not in the table
def get_epf_target(age: int) -> float:
    """Get the EPF basic savings target for a given age."""
    if not EPF_TARGETS:
        return 0

    min_age = min(EPF_TARGETS)
    max_age = max(EPF_TARGETS)

    if age < min_age:
        return 0
    if age in EPF_TARGETS:
        return EPF_TARGETS[age]
    if age >= max_age:
        return EPF_TARGETS[max_age]
    
    # Linear interpolation for ages between targets
    lower_age = max([a for a in EPF_TARGETS if a <= age])
    upper_age = min([a for a in EPF_TARGETS if a > age])
    
    lower_target = EPF_TARGETS[lower_age]
    upper_target = EPF_TARGETS[upper_age]
    
    # Interpolate
    ratio = (age - lower_age) / (upper_age - lower_age)
    return lower_target + ratio * (upper_target - lower_target)


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

# Average Malaysia Fixed Deposit Rates (annual %)
FD_RATES = {
    "Maybank": {"3_month": 3.15, "6_month": 3.25, "12_month": 3.35},
    "Hong_Leong": {"3_month": 3.10, "6_month": 3.20, "12_month": 3.30},
    "CIMB": {"3_month": 3.05, "6_month": 3.15, "12_month": 3.25},
    "Public_Bank": {"3_month": 3.00, "6_month": 3.10, "12_month": 3.20},
}

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

# Simulation settings
PROJECTION_MONTHS = 12
SCENARIOS = {
    "conservative": 0.04,  # 4% annual growth
    "moderate": 0.08,      # 8% annual growth
    "bullish": 0.15        # 15% annual growth (Bitcoin)
}
