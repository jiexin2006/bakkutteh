# Data Models for AI Financial Intelligence Advisor

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
from datetime import datetime


class BitcoinSignal(Enum):
    """Bitcoin trading signals"""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class EPFStatus(Enum):
    """EPF status relative to targets"""
    ON_TRACK = "ON_TRACK"
    BEHIND = "BEHIND"
    WAY_BEHIND = "WAY_BEHIND"


@dataclass
class UserProfile:
    """User's financial profile"""
    age: int
    monthly_salary: float
    monthly_expenditure: float
    current_epf_balance: float
    fixed_liabilities: float  # e.g., loans, rent commitments
    risk_appetite: str  # "Conservative", "Moderate", "Aggressive"
    
    @property
    def monthly_surplus(self) -> float:
        """Calculate monthly surplus after expenses and liabilities"""
        return self.monthly_salary - self.monthly_expenditure - self.fixed_liabilities
    
    @property
    def annual_surplus(self) -> float:
        """Annual surplus"""
        return self.monthly_surplus * 12


@dataclass
class MarketData:
    """Current market conditions"""
    bitcoin_price: float
    bitcoin_daily_change: float  # Percentage
    bitcoin_7day_avg: float      # 7-day moving average
    bitcoin_30day_avg: float     # 30-day moving average
    fd_rates: Dict[str, Dict[str, float]]  # Bank -> {period -> rate}
    epf_interest_rate: float
    timestamp: datetime


@dataclass
class BitcoinAnalysis:
    """Result of Bitcoin trend analysis"""
    signal: BitcoinSignal
    confidence_score: float  # 0.0 to 1.0
    trend: str  # "Bullish", "Bearish", "Neutral"
    reasoning: str  # Explanation of the analysis


@dataclass
class AllocationStrategy:
    """Recommended fund allocation strategy"""
    fd_percentage: float
    epf_percentage: float
    crypto_percentage: float
    
    def validate(self) -> bool:
        """Validate that percentages sum to 100%"""
        total = self.fd_percentage + self.epf_percentage + self.crypto_percentage
        return abs(total - 1.0) < 0.01


@dataclass
class BankRecommendation:
    """Specific bank FD recommendation"""
    bank_name: str
    period: str  # "3_month", "6_month", "12_month"
    rate: float
    projected_return: float  # Over the period


@dataclass
class FinancialRecommendation:
    """Complete recommendation output"""
    user_profile: UserProfile
    epf_status: EPFStatus
    epf_target: float
    epf_gap: float  # Current balance vs. target
    epf_gap_percentage: float  # Gap as % of target
    
    allocation_strategy: AllocationStrategy
    allocation_monthly_amount: Dict[str, float]  # {"FD": X, "EPF": Y, "Crypto": Z}
    allocation_annual_amount: Dict[str, float]
    
    bitcoin_analysis: BitcoinAnalysis
    top_fd_option: Optional[BankRecommendation]
    
    # Projections
    projected_portfolio_1month: float
    projected_portfolio_6months: float
    projected_portfolio_12months: float
    
    # Explanation
    reasoning: str
    
    timestamp: datetime


@dataclass
class ProjectionScenario:
    """Scenario for financial projection"""
    scenario_name: str  # "Conservative", "Moderate", "Bullish"
    fd_annual_return: float  # %
    epf_annual_return: float  # %
    crypto_annual_return: float  # %
    likelihood: float  # 0.0 to 1.0
    
    def calculate_portfolio_growth(
        self, 
        fd_amount: float, 
        epf_amount: float, 
        crypto_amount: float, 
        months: int
    ) -> float:
        """Calculate portfolio value after given months under this scenario"""
        fd_value = fd_amount * (1 + self.fd_annual_return / 100) ** (months / 12)
        epf_value = epf_amount * (1 + self.epf_annual_return / 100) ** (months / 12)
        crypto_value = crypto_amount * (1 + self.crypto_annual_return / 100) ** (months / 12)
        return fd_value + epf_value + crypto_value
