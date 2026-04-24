from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserProfile:
    """User's financial profile.

    This is the canonical user profile object used throughout Backend.
    """

    age: int
    monthly_salary: float
    monthly_expenditure: float
    current_epf_balance: float
    fixed_liabilities: float
    risk_appetite: str
    epf_deduction_rm: float = 0.0
    target_retirement_tier: str = "basic"
    user_id: str | None = None

    @property
    def monthly_surplus(self) -> float:
        """Calculate monthly surplus after expenses, liabilities, and EPF deduction."""
        return (
            self.monthly_salary
            - self.monthly_expenditure
            - self.fixed_liabilities
            - self.epf_deduction_rm
        )

    @property
    def annual_surplus(self) -> float:
        """Annual surplus."""
        return self.monthly_surplus * 12

    def getUserProfile(self) -> dict:
        """Return a compact prompt payload for downstream reasoning."""
        return {
            "user_id": self.user_id,
            "age": self.age,
            "current_epf_balance_rm": self.current_epf_balance,
            "current_surplus_rm": self.monthly_surplus,
            "risk_appetite": self.risk_appetite,
            "target_retirement_tier": self.target_retirement_tier,
        }

    def to_prompt_payload(self) -> dict:
        """Alias for the compact prompt payload."""
        return self.getUserProfile()