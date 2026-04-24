"""Placeholder optimizer module for future GLM-powered implementation.

This file intentionally contains no business logic. The real allocation,
trade-off analysis, and recommendation generation will be implemented in a
separate prompt-engineered script that calls the GLM model.

The public class and method names are preserved so the rest of the project can
keep importing this module without large structural changes.
"""

from __future__ import annotations

from datetime import datetime

from Backend.models import (
    AllocationStrategy,
    BankRecommendation,
    BitcoinAnalysis,
    FinancialRecommendation,
    MarketData,
    UserProfile,
)


class PlaceholderOptimizerError(NotImplementedError):
    """Raised when placeholder optimization methods are called."""


class AssetOptimizer:
    """Stub container for future optimization logic."""

    @staticmethod
    def optimize_allocation(
        user_profile: UserProfile,
        market_data: MarketData,
        bitcoin_analysis: BitcoinAnalysis,
        epf_report: dict,
    ) -> AllocationStrategy:
        raise PlaceholderOptimizerError(
            "Asset optimization is currently a placeholder. "
            "Implement the GLM-backed allocation logic in a separate script."
        )

    @staticmethod
    def calculate_allocation_amounts(
        allocation_strategy: AllocationStrategy,
        monthly_surplus: float,
    ) -> tuple[dict, dict]:
        raise PlaceholderOptimizerError(
            "Allocation amount calculation is currently a placeholder."
        )

    @staticmethod
    def select_best_fd_option(
        market_data: MarketData,
        preferred_period: str = "12_month",
    ) -> BankRecommendation:
        raise PlaceholderOptimizerError(
            "FD selection is currently a placeholder."
        )

    @staticmethod
    def project_portfolio(
        user_profile: UserProfile,
        allocation_strategy: AllocationStrategy,
        bitcoin_analysis: BitcoinAnalysis,
        market_data: MarketData,
        epf_report: dict,
    ) -> tuple[float, float, float]:
        raise PlaceholderOptimizerError(
            "Portfolio projection is currently a placeholder."
        )

    @staticmethod
    def generate_reasoning(
        user_profile: UserProfile,
        epf_report: dict,
        allocation_strategy: AllocationStrategy,
        bitcoin_analysis: BitcoinAnalysis,
        market_data: MarketData,
        allocation_monthly: dict,
    ) -> str:
        raise PlaceholderOptimizerError(
            "Explanation generation is currently a placeholder."
        )


class RecommendationEngine:
    """Stub entry point for future recommendation generation."""

    @staticmethod
    def generate_recommendation(
        user_profile: UserProfile,
        market_data: MarketData,
    ) -> FinancialRecommendation:
        raise PlaceholderOptimizerError(
            "Recommendation generation is currently a placeholder. "
            "A separate GLM prompt-engineering script will provide the final logic."
        )


PLACEHOLDER_IMPLEMENTATION = True
IMPLEMENTATION_STATUS = "placeholder"
IMPLEMENTATION_NOTE = (
    "This module only preserves the API surface for future GLM integration."
)
