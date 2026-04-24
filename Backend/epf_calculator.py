from __future__ import annotations

from config import get_epf_target, get_epf_targets_for_age
from models import EPFStatus, RETIREMENT_TIER, UserProfile


class PlaceholderEPFError(NotImplementedError):
    """Raised when placeholder EPF methods are called."""


class EPFCalculator:
    """Deterministic EPF benchmarking logic based on data/epf-standards.json."""

    @staticmethod
    def normalize_target_tier(target_retirement_tier: str | RETIREMENT_TIER) -> RETIREMENT_TIER:
        """Normalize a tier label into the canonical retirement tier enum."""
        if isinstance(target_retirement_tier, RETIREMENT_TIER):
            return target_retirement_tier

        normalized = str(target_retirement_tier).strip().upper()
        try:
            return RETIREMENT_TIER[normalized]
        except KeyError as exc:
            raise ValueError(
                "target_retirement_tier must be one of: Basic, Adequate, Enhanced"
            ) from exc

    @staticmethod
    def get_target_balance(age: int, target_tier: str | RETIREMENT_TIER = RETIREMENT_TIER.BASIC) -> float:
        """Get EPF target for a specific age and target tier using nearest-age fallback."""
        normalized_tier = EPFCalculator.normalize_target_tier(target_tier)
        return get_epf_target(age=age, target_tier=normalized_tier)

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
        target_retirement_tier: str | RETIREMENT_TIER = RETIREMENT_TIER.BASIC,
    ) -> dict:
        """Generate a compact EPF payload for prompting and downstream reasoning."""
        normalized_tier = EPFCalculator.normalize_target_tier(target_retirement_tier)
        tier_targets = get_epf_targets_for_age(user_profile.age)

        tier_key = normalized_tier.value.lower()
        selected_target = tier_targets[tier_key]
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
            "target_epf_level": tier_key,
            "selected_target_rm": selected_target,
            "deficit_rm": deficit_rm,
            "deficit_percentage": round(deficit_percentage, 2),
            "status": status_label,
            "priority_level": priority_level,
        }

    @staticmethod
    def get_epf_analysis(
        user_profile: UserProfile,
        target_retirement_tier: str | RETIREMENT_TIER = RETIREMENT_TIER.BASIC,
    ) -> dict:
        """Clean exit point for prompt payload generation."""
        return EPFCalculator.generate_epf_report(user_profile, target_retirement_tier)

