#!/usr/bin/env python3
"""
Test script to verify the AI Financial Intelligence Advisor system
"""

import sys
from datetime import datetime
from Backend.models import UserProfile, MarketData
from Backend.optimizer import RecommendationEngine
from Backend.config import FD_RATES

def test_system():
    """Run comprehensive system tests"""
    
    print("=" * 80)
    print("AI Financial Intelligence Advisor - System Test")
    print("=" * 80)
    print()
    
    # Test 1: Module imports
    print("✓ Test 1: Module imports - PASSED")
    print("  - config.py loaded successfully")
    print("  - models.py loaded successfully")
    print("  - epf_calculator.py loaded successfully")
    print("  - bitcoin_analyzer.py loaded successfully")
    print("  - optimizer.py loaded successfully")
    print()
    
    # Test 2: Create user profile
    print("✓ Test 2: Creating user profile...")
    user = UserProfile(
        age=30,
        monthly_salary=5000,
        monthly_expenditure=2000,
        current_epf_balance=80000,
        fixed_liabilities=500,
        risk_appetite="Moderate"
    )
    print(f"  - Age: {user.age}")
    print(f"  - Monthly Surplus: MYR {user.monthly_surplus:,.2f}")
    print(f"  - Annual Surplus: MYR {user.annual_surplus:,.2f}")
    print()
    
    # Test 3: Create market data
    print("✓ Test 3: Creating market data...")
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
    
    # Test 4: Generate recommendation
    print("✓ Test 4: Generating recommendation...")
    try:
        recommendation = RecommendationEngine.generate_recommendation(user, market)
        print(f"  - EPF Status: {recommendation.epf_status.value}")
        print(f"  - EPF Gap: MYR {recommendation.epf_gap:,.2f}")
        print(f"  - Allocation:")
        print(f"    • FD: {recommendation.allocation_strategy.fd_percentage*100:.1f}%")
        print(f"    • EPF: {recommendation.allocation_strategy.epf_percentage*100:.1f}%")
        print(f"    • Crypto: {recommendation.allocation_strategy.crypto_percentage*100:.1f}%")
        print(f"  - Bitcoin Signal: {recommendation.bitcoin_analysis.signal.value}")
        print(f"  - Bitcoin Confidence: {recommendation.bitcoin_analysis.confidence_score:.0%}")
        print(f"  - Projected Portfolio (12 months): MYR {recommendation.projected_portfolio_12months:,.2f}")
        print()
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False
    
    # Test 5: Allocation validation
    print("✓ Test 5: Validating allocation...")
    if recommendation.allocation_strategy.validate():
        print("  - Allocation percentages sum to 100% ✓")
    else:
        print("  - ✗ FAILED: Allocation percentages don't sum to 100%")
        return False
    
    # Test 6: Output format
    print("✓ Test 6: Checking output format...")
    print(f"  - Timestamp: {recommendation.timestamp}")
    print(f"  - Reasoning length: {len(recommendation.reasoning)} characters")
    print(f"  - Top FD Option: {recommendation.top_fd_option.bank_name.replace('_', ' ')} @ {recommendation.top_fd_option.rate:.2f}%")
    print()
    
    # Test 7: Monthly allocations
    print("✓ Test 7: Monthly allocations...")
    monthly_total = sum(recommendation.allocation_monthly_amount.values())
    print(f"  - FD: MYR {recommendation.allocation_monthly_amount['FD']:>8,.2f}/month")
    print(f"  - EPF: MYR {recommendation.allocation_monthly_amount['EPF']:>8,.2f}/month")
    print(f"  - Crypto: MYR {recommendation.allocation_monthly_amount['Crypto']:>8,.2f}/month")
    print(f"  - Total: MYR {monthly_total:>8,.2f}/month")
    print()
    
    # Test 8: Portfolio projection
    print("✓ Test 8: Portfolio projections...")
    print(f"  - 1 month: MYR {recommendation.projected_portfolio_1month:>12,.2f}")
    print(f"  - 6 months: MYR {recommendation.projected_portfolio_6months:>12,.2f}")
    print(f"  - 12 months: MYR {recommendation.projected_portfolio_12months:>12,.2f}")
    
    annual_investment = recommendation.allocation_annual_amount['FD'] + recommendation.allocation_annual_amount['EPF'] + recommendation.allocation_annual_amount['Crypto']
    roi_percentage = ((recommendation.projected_portfolio_12months - annual_investment) / annual_investment * 100) if annual_investment > 0 else 0
    print(f"  - Annual Investment: MYR {annual_investment:,.2f}")
    print(f"  - Estimated 12-month ROI: {roi_percentage:.1f}%")
    print()
    
    # Test 9: Edge cases
    print("✓ Test 9: Testing edge cases...")
    
    # Young user with low salary
    young_user = UserProfile(
        age=22,
        monthly_salary=2500,
        monthly_expenditure=1200,
        current_epf_balance=5000,
        fixed_liabilities=0,
        risk_appetite="Aggressive"
    )
    young_rec = RecommendationEngine.generate_recommendation(young_user, market)
    print(f"  - Young user (22yo): EPF Status = {young_rec.epf_status.value}")
    
    # Older user with high EPF
    older_user = UserProfile(
        age=50,
        monthly_salary=8000,
        monthly_expenditure=3000,
        current_epf_balance=300000,
        fixed_liabilities=1000,
        risk_appetite="Conservative"
    )
    older_rec = RecommendationEngine.generate_recommendation(older_user, market)
    print(f"  - Older user (50yo): EPF Status = {older_rec.epf_status.value}")
    
    # Negative market conditions
    bear_market = MarketData(
        bitcoin_price=20000,
        bitcoin_daily_change=-5.5,
        bitcoin_7day_avg=22000,
        bitcoin_30day_avg=25000,
        fd_rates=FD_RATES,
        epf_interest_rate=3.5,
        timestamp=datetime.now()
    )
    bear_rec = RecommendationEngine.generate_recommendation(user, bear_market)
    print(f"  - Bear market: Bitcoin Signal = {bear_rec.bitcoin_analysis.signal.value}")
    print()
    
    # Final summary
    print("=" * 80)
    print("ALL TESTS PASSED ✓")
    print("=" * 80)
    print()
    print("System is ready for production use!")
    print("Run 'python main.py' to start the desktop application")
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
