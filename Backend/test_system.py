#!/usr/bin/env python3
"""
Test script to verify the AI Financial Intelligence Advisor system
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from bitcoin_analyzer import BitcoinAnalyzer
from Prompt import get_financial_reasoning_prompt
from ZAI import IlmuApiError, ZAI
from config import FD_RATES, EPF_INTEREST_RATE, EPF_TIER_TARGETS, get_fd_prompt_context
from epf_calculator import EPFCalculator
from models import MarketData, UserProfile


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MOCK_USERS_PATH = DATA_DIR / "Mock_User_Profiles.json"


def load_mock_user_profile(user_id: str = "U001") -> UserProfile:
    with MOCK_USERS_PATH.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    users = payload.get("users", [])
    if not isinstance(users, list) or not users:
        raise ValueError("Mock_User_Profiles.json does not contain any users")

    selected_user = next((item for item in users if item.get("user_id") == user_id), users[0])

    user_profile = UserProfile(
        age=int(selected_user["age"]),
        monthly_salary=float(selected_user["monthly_salary_rm"]),
        monthly_expenditure=0.0,
        current_epf_balance=float(selected_user["epf_balance_rm"]),
        fixed_liabilities=float(selected_user["fixed_liabilities_rm"]),
        risk_appetite=str(selected_user["risk_appetite"]),
        epf_deduction_rm=float(selected_user.get("epf_deduction_rm", 0.0)),
        target_retirement_tier=str(selected_user.get("target_retirement_tier", "basic")).lower(),
        user_id=str(selected_user.get("user_id")),
    )

    return user_profile


def build_decision_context(epf_analysis: dict, user_profile: UserProfile) -> dict:
    surplus = max(user_profile.monthly_surplus, 0.0)
    return {
        "current_surplus_rm": round(surplus, 2),
        "fd_minimum_rm": 500,
        "bitcoin_minimum_rm": 100,
        "epf_status": epf_analysis["status"],
        "priority_level": epf_analysis["priority_level"],
        "selected_target_rm": epf_analysis["selected_target_rm"],
        "deficit_rm": epf_analysis["deficit_rm"],
        "deficit_percentage": epf_analysis["deficit_percentage"],
    }


def print_section(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)
    print()


def safe_load_zai() -> ZAI | None:
    try:
        return ZAI()
    except IlmuApiError as exc:
        print(f"  - ZAI client unavailable: {exc}")
        return None

def test_system():
    """Run the prompt integration test path used by the GLM reasoning flow."""

    print_section("AI Financial Intelligence Advisor - Prompt Integration Test")

    print("✓ Test 1: Module imports and data loading")
    print("  - config.py loaded successfully")
    print(f"  - EPF tiers loaded for {len(EPF_TIER_TARGETS)} ages")
    print(f"  - FD rates loaded for {len(FD_RATES)} banks")
    print("  - epf_calculator.py loaded successfully")
    print("  - bitcoin_analyzer.py loaded successfully")
    print("  - prompt.py loaded successfully")
    print("  - ZAI.py loaded successfully")
    print()

    print("✓ Test 2: Creating user profile from mock data")
    user = load_mock_user_profile("U001")
    print(f"  - Age: {user.age}")
    print(f"  - Monthly Surplus: MYR {user.monthly_surplus:,.2f}")
    print(f"  - Annual Surplus: MYR {user.annual_surplus:,.2f}")
    print()

    print("✓ Test 3: Creating market data")
    market = MarketData(
        bitcoin_price=45000,
        bitcoin_daily_change=2.5,
        bitcoin_7day_avg=44000,
        bitcoin_30day_avg=42000,
        fd_rates=FD_RATES,
        epf_interest_rate=3.5,
        timestamp=datetime.now()
    )
    print(f"  - Bitcoin Price: USD {market.bitcoin_price:,.0f}")
    print(f"  - Bitcoin Daily Change: {market.bitcoin_daily_change:+.2f}%")
    print(f"  - FD Rates Loaded: {len(market.fd_rates)} banks")
    print()

    print("✓ Test 4: Running EPF analysis")
    try:
        epf_report = EPFCalculator.get_epf_analysis(user, "Basic")
        print(f"  - EPF Status: {epf_report['status']}")
        print(f"  - EPF Gap: MYR {epf_report['deficit_rm']:,.2f}")
        print(f"  - Priority Level: {epf_report['priority_level']}")
        print(f"  - Target Tier: {epf_report['target_epf_level']}")
        print()
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

    print("✓ Test 5: Running Bitcoin analysis")
    try:
        bitcoin_analysis = BitcoinAnalyzer.analyze_trend(market)
        bitcoin_summary = BitcoinAnalyzer.get_prompt_summary(market)
        print(f"  - Signal: {bitcoin_summary['bitcoin_signal']}")
        print(f"  - Confidence: {bitcoin_summary['bitcoin_confidence']:.0%}")
        print(f"  - Trend: {bitcoin_summary['bitcoin_trend']}")
    except Exception as e:
        print(f"  - Bitcoin analysis failed: {e}")
        return False
    print()

    print("✓ Test 6: Building prompt context")
    user_data = user.getUserProfile()
    epf_analysis = EPFCalculator.get_epf_analysis(user, "Basic")
    allocation = build_decision_context(epf_analysis, user)
    market_signals = bitcoin_summary
    print(f"  - Decision context: {allocation}")
    print(f"  - EPF priority: {epf_analysis['priority_level']}")
    print(f"  - Bitcoin signal: {market_signals['bitcoin_signal']}")
    print()

    print("✓ Test 7: Generating prompt for ZAI")
    fd_market_data = get_fd_prompt_context(limit=3)
    prompt = get_financial_reasoning_prompt(
        user_data=user_data,
        allocation=allocation,
        epf_analysis=epf_analysis,
        fd_market_data={
            **fd_market_data,
            "bitcoin_signal": market_signals["bitcoin_signal"],
            "bitcoin_confidence": market_signals["bitcoin_confidence"],
            "bitcoin_trend": market_signals["bitcoin_trend"],
        },
    )
    print(f"  - Prompt length: {len(prompt)} characters")
    print(f"  - Prompt preview: {prompt}")
    print()

    print("✓ Test 8: Calling ZAI with prompt")
    zai = safe_load_zai()
    if zai is None:
        print("  - Skipping live ZAI call because the client could not be initialized.")
        print()
        print_section("PROMPT TEST COMPLETED")
        return True

    try:
        response_text = zai.chat(prompt)
        print("  - ZAI response received: ----------------------------------------------------------------------")
        print(response_text)
        try:
            parsed = json.loads(response_text)
            print(f"  - Parsed JSON keys: {list(parsed.keys())}")
        except json.JSONDecodeError:
            print("  - Response was not valid JSON")
        print()
    except Exception as e:
        print(f"  ✗ ZAI CALL FAILED: {e}")
        return False

    print_section("ALL PROMPT TESTS PASSED")
    print("System is ready to exercise prompt.py with live ZAI if the API key is available.")
    print()
    return True


if __name__ == "__main__":
    try:
        success = test_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
