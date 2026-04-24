"""Placeholder EPF calculator module.

This file intentionally contains no final business logic. EPF-related analysis
and trade-off behavior should be implemented later by the model/prompt owner in
separate scripts.

The class and method signatures are preserved to avoid breaking imports.
"""

from __future__ import annotations

from Backend.models import EPFStatus, UserProfile


class PlaceholderEPFError(NotImplementedError):
    """Raised when placeholder EPF methods are called."""


class EPFCalculator:
    """Stub container for future EPF benchmarking logic."""

    @staticmethod
    def get_target_balance(age: int) -> float:
        raise PlaceholderEPFError(
            "EPF target lookup is currently a placeholder. "
            "Implement it in the future model/prompt pipeline."
        )

    @staticmethod
    def calculate_gap(current_balance: float, target_balance: float) -> float:
        raise PlaceholderEPFError("EPF gap calculation is currently a placeholder.")

    @staticmethod
    def calculate_gap_percentage(current_balance: float, target_balance: float) -> float:
        raise PlaceholderEPFError(
            "EPF gap percentage calculation is currently a placeholder."
        )

    @staticmethod
    def determine_status(gap_percentage: float) -> EPFStatus:
        raise PlaceholderEPFError(
            "EPF status determination is currently a placeholder."
        )

    @staticmethod
    def calculate_monthly_contribution_to_reach_target(
        current_balance: float,
        target_balance: float,
        months_until_retirement: int,
        annual_return_rate: float = 3.5,
    ) -> float:
        raise PlaceholderEPFError(
            "EPF monthly contribution calculation is currently a placeholder."
        )

    @staticmethod
    def get_crypto_allocation_cap(gap_percentage: float) -> float:
        raise PlaceholderEPFError(
            "EPF-to-crypto cap mapping is currently a placeholder."
        )

    @staticmethod
    def project_epf_balance(
        current_balance: float,
        monthly_contribution: float,
        annual_return_rate: float,
        months: int,
    ) -> float:
        raise PlaceholderEPFError(
            "EPF projection is currently a placeholder."
        )

    @staticmethod
    def generate_epf_report(user_profile: UserProfile) -> dict:
        raise PlaceholderEPFError(
            "EPF report generation is currently a placeholder."
        )


PLACEHOLDER_IMPLEMENTATION = True
IMPLEMENTATION_STATUS = "placeholder"
IMPLEMENTATION_NOTE = (
    "This module only preserves the API surface for future model integration."
)
