from __future__ import annotations

from Backend.config import (
    BITCOIN_MIN_PLACEMENT_RM,
    FD_MIN_PLACEMENT_RM,
    get_epf_target,
    get_epf_targets_for_age,
)
from Backend.models import EPFStatus, UserProfile


class PlaceholderEPFError(NotImplementedError):
    """Raised when placeholder EPF methods are called."""


class EPFCalculator:
    """Deterministic EPF benchmarking logic based on data/epf-standards.json."""

    VALID_TIERS = {"basic", "adequate", "enhanced"}

    @staticmethod
    def normalize_target_tier(target_retirement_tier: str) -> str:
        """Normalize external tier labels (Basic/Adequate/Enhanced) to internal lowercase."""
        normalized = target_retirement_tier.strip().lower()
        if normalized not in EPFCalculator.VALID_TIERS:
            raise ValueError(
                "target_retirement_tier must be one of: Basic, Adequate, Enhanced"
            )
        return normalized

    @staticmethod
    def get_target_balance(age: int, target_tier: str = "basic") -> float:
        """Get EPF target for a specific age and target tier using nearest-age fallback."""
        normalized_tier = EPFCalculator.normalize_target_tier(target_tier)
        return get_epf_target(age=age, tier=normalized_tier)

    @staticmethod
    def calculate_gap(current_balance: float, target_balance: float) -> float:
        """Schema deficit formula: selected_target_rm - current_epf_balance_rm."""
        return float(target_balance) - float(current_balance)

    @staticmethod
    def calculate_gap_percentage(current_balance: float, target_balance: float) -> float:
        """Schema deficit percentage: (deficit_rm / selected_target_rm) * 100."""
        if target_balance <= 0:
            return 0.0
        gap = EPFCalculator.calculate_gap(current_balance, target_balance)
        return (gap / float(target_balance)) * 100.0

    @staticmethod
    def determine_status(gap_percentage: float) -> EPFStatus:
        """Determine EPF status from deficit percentage."""
        if gap_percentage <= 0:
            return EPFStatus.ON_TRACK
        if gap_percentage >= 75:
            return EPFStatus.WAY_BEHIND
        return EPFStatus.BEHIND

    @staticmethod
    def calculate_monthly_contribution_to_reach_target(
        current_balance: float,
        target_balance: float,
        months_until_retirement: int,
        annual_return_rate: float = 3.5,
    ) -> float:
        """Compute required monthly contribution for future-value target."""
        if months_until_retirement <= 0:
            return max(target_balance - current_balance, 0.0)

        monthly_rate = (annual_return_rate / 100.0) / 12.0
        future_value_current = current_balance * ((1 + monthly_rate) ** months_until_retirement)
        remaining_value = max(target_balance - future_value_current, 0.0)
        if remaining_value == 0:
            return 0.0

        if monthly_rate == 0:
            return remaining_value / months_until_retirement

        annuity_factor = (((1 + monthly_rate) ** months_until_retirement) - 1) / monthly_rate
        if annuity_factor <= 0:
            return 0.0
        return remaining_value / annuity_factor

    @staticmethod
    def get_crypto_allocation_cap(gap_percentage: float) -> float:
        """Return max crypto weight based on EPF deficit severity."""
        if gap_percentage <= 0:
            return 0.50
        if gap_percentage >= 75:
            return 0.10
        if gap_percentage >= 50:
            return 0.20
        if gap_percentage >= 25:
            return 0.35
        return 0.45

    @staticmethod
    def project_epf_balance(
        current_balance: float,
        monthly_contribution: float,
        annual_return_rate: float,
        months: int,
    ) -> float:
        """Project EPF balance with monthly compounding and monthly contributions."""
        if months <= 0:
            return float(current_balance)

        monthly_rate = (annual_return_rate / 100.0) / 12.0
        balance = float(current_balance)
        for _ in range(months):
            balance = balance * (1 + monthly_rate) + float(monthly_contribution)
        return balance

    @staticmethod
    def generate_epf_report(
        user_profile: UserProfile,
        target_retirement_tier: str = "Basic",
    ) -> dict:
        """Generate schema-aligned EPF report for a user profile."""
        normalized_tier = EPFCalculator.normalize_target_tier(target_retirement_tier)
        tier_targets = get_epf_targets_for_age(user_profile.age)

        selected_target = tier_targets[normalized_tier]
        deficit_rm = EPFCalculator.calculate_gap(user_profile.current_epf_balance, selected_target)
        deficit_percentage = EPFCalculator.calculate_gap_percentage(
            user_profile.current_epf_balance,
            selected_target,
        )
        status_label = "On Track" if deficit_rm <= 0 else "Behind"
        priority_level = (
            "No Priority"
            if deficit_percentage <= 0
            else "Critical"
            if deficit_percentage >= 75
            else "High"
            if deficit_percentage >= 50
            else "Medium"
            if deficit_percentage >= 25
            else "Low"
        )
        return {
            "age": user_profile.age,
            "target_epf_level": normalized_tier,
            "basic_target_rm": tier_targets["basic"],
            "adequate_target_rm": tier_targets["adequate"],
            "enhanced_target_rm": tier_targets["enhanced"],
            "selected_target_rm": selected_target,
            "deficit_rm": deficit_rm,
            "deficit_percentage": deficit_percentage,
            "status": status_label,
            "priority_level": priority_level,
            "status_enum": EPFCalculator.determine_status(deficit_percentage).value,
        }

    @staticmethod
    def recommend_surplus_parking(
        monthly_surplus_rm: float,
        deficit_percentage: float,
    ) -> dict:
        """Recommend EPF/Savings mix when user is not eligible for FD/Bitcoin minimum placement."""
        surplus = float(monthly_surplus_rm)
        fd_eligible = surplus >= FD_MIN_PLACEMENT_RM
        bitcoin_eligible = surplus >= BITCOIN_MIN_PLACEMENT_RM

        if surplus <= 0:
            return {
                "strategy": "No Allocation",
                "fd_eligible": False,
                "bitcoin_eligible": False,
                "savings_amount_rm": 0.0,
                "epf_amount_rm": 0.0,
                "reason": (
                    "No surplus is available for allocation. Prioritize reducing fixed liabilities "
                    "or increasing monthly income first."
                ),
                "risk_note": "No investment action until monthly surplus becomes positive.",
            }

        if fd_eligible or bitcoin_eligible:
            return {
                "strategy": "Investable",
                "fd_eligible": fd_eligible,
                "bitcoin_eligible": bitcoin_eligible,
                "savings_amount_rm": 0.0,
                "epf_amount_rm": 0.0,
                "reason": (
                    "Surplus already meets at least one minimum placement rule, so normal allocation "
                    "logic can proceed beyond liquidity parking."
                ),
                "risk_note": "User can diversify into eligible instruments with controlled risk sizing.",
            }

        # Low-surplus path: user is not eligible for FD and Bitcoin minimum placements.
        if deficit_percentage >= 50:
            epf_ratio = 1.0
            strategy = "EPF"
            reason = (
                "EPF deficit is significant relative to the selected retirement tier target, so "
                "prioritizing EPF contribution is recommended despite lower liquidity."
            )
            risk_note = (
                "Higher lock-in risk due to reduced liquidity, but better retirement catch-up potential."
            )
        elif deficit_percentage <= 0:
            epf_ratio = 0.0
            strategy = "Savings"
            reason = (
                "EPF balance is currently on track for the selected retirement tier, so parking surplus "
                "in Savings preserves full liquidity until amount is large enough for FD placement."
            )
            risk_note = "Very low liquidity risk, but no dividend/return while parked in Savings."
        else:
            if deficit_percentage >= 25:
                epf_ratio = 0.7
            else:
                epf_ratio = 0.4
            strategy = "EPF+Savings"
            reason = (
                "EPF is behind target but not critically, so split surplus between EPF catch-up and "
                "Savings liquidity buffer until minimum placement thresholds are met."
            )
            risk_note = (
                "Balanced trade-off: moderate retirement catch-up with partial liquidity retained."
            )

        epf_amount = round(surplus * epf_ratio, 2)
        savings_amount = round(surplus - epf_amount, 2)

        return {
            "strategy": strategy,
            "fd_eligible": False,
            "bitcoin_eligible": False,
            "savings_amount_rm": savings_amount,
            "epf_amount_rm": epf_amount,
            "reason": reason,
            "risk_note": risk_note,
        }

