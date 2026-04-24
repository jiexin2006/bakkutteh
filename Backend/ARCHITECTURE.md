# AI Financial Intelligence Advisor - Architecture Summary

## What Was Built

A complete Python backend system for the **Backend Developer** role of UMHackathon 2026 AI Financial Intelligence Advisor project.

## Core Deliverables

### 1. **Functional API** (Implemented in optimizer.py)
- `RecommendationEngine.generate_recommendation()` - Main API function
- Takes user profile + market data as input
- Returns comprehensive recommendation with allocations, projections, reasoning

### 2. **Optimization & Trade-off Analysis** (optimizer.py)
- Multi-step asset optimization algorithm
- Balances three objectives:
  - **Safety**: EPF recovery if behind target
  - **Security**: Fixed deposit allocations for liquidity
  - **Growth**: Bitcoin allocation based on market signals
- Trade-off logic: If EPF gap > 40%, crypto capped at 5%; if gap < 10%, full allocation allowed

### 3. **Quantifiable Impact Calculation** (optimizer.py)
- ROI projections: 1-month, 6-month, 12-month scenarios
- Annual investment vs projected growth
- Confidence-weighted Bitcoin returns
- Compound interest calculations for all asset classes

## Technical Implementation

### Processing Pipeline (4 Steps)

```
Step 1: EPF Benchmarking (epf_calculator.py)
├─ Compare current balance vs age-based target
├─ Calculate gap percentage
└─ Determine status (On Track / Behind)

Step 2: Bitcoin Predictive Analysis (bitcoin_analyzer.py)
├─ Calculate RSI, MACD, Moving Averages
├─ Generate trading signal (BUY/SELL/HOLD)
└─ Confidence scoring based on technical indicators

Step 3: Multi-Asset Optimization (optimizer.py)
├─ Start with risk profile allocation
├─ Adjust for EPF gap using multipliers
├─ Integrate Bitcoin signals
└─ Enforce min/max constraints

Step 4: Contextual Strategy Generation (optimizer.py)
├─ Calculate monthly/annual amounts
├─ Select best FD option from Malaysian banks
├─ Project portfolio values
└─ Generate human-readable explanations
```

### Key Algorithms

1. **EPF Gap-Based Rebalancing**
   - Critical (>40%): Crypto = 5% of allocation
   - High (>20%): Crypto = 30% of allocation  
   - Moderate (>10%): Crypto = 60% of allocation
   - Low: Use full allocation

2. **Multi-Objective Optimization**
   - Weighted adjustment of three asset classes
   - Respects constraints: Min EPF 15%, Min FD 10%, Max Crypto 50%
   - Normalizes to 100%

3. **Portfolio Projection**
   - Uses asset-specific annual returns
   - Compounds monthly contributions
   - Bitcoin rate adjusted by signal + confidence

## Data Models

- `UserProfile`: Age, salary, EPF, surplus, risk appetite
- `MarketData`: Bitcoin price/trends, FD rates
- `BitcoinAnalysis`: Signal, confidence, reasoning
- `AllocationStrategy`: FD%, EPF%, Crypto%
- `FinancialRecommendation`: Complete output with reasoning

## Output Format

Each recommendation includes:
- EPF status indicator + gap analysis
- Allocation percentages & amounts
- Bitcoin signal with confidence level
- Best FD option (rate, bank, term)
- Portfolio projections (1/6/12 months)
- Estimated ROI percentage
- Plain-language reasoning for all decisions

## Testing & Validation

- ✓ All 9 system tests pass
- ✓ Edge cases handled (young/old users, bear/bull markets)
- ✓ Allocations always sum to 100%
- ✓ Constraints always enforced
- ✓ Realistic projections calculated

## Files Generated

| File | Purpose |
|------|---------|
| main.py | Desktop GUI (tkinter) |
| config.py | Constants & settings |
| models.py | Data structures |
| epf_calculator.py | EPF benchmarking |
| bitcoin_analyzer.py | Bitcoin analysis |
| optimizer.py | Optimization engine |
| test_system.py | System validation |
| run.sh / run.bat | Launch scripts |
| README.md | Full documentation |

## How to Use

1. **Run the GUI**:
   ```bash
   python main.py
   ```

2. **Or integrate the API**:
   ```python
   from models import UserProfile, MarketData
   from optimizer import RecommendationEngine
   
   user = UserProfile(...)
   market = MarketData(...)
   recommendation = RecommendationEngine.generate_recommendation(user, market)
   ```

## Key Features Implemented

✓ Context-aware reasoning (EPF deficit affects crypto allocation)  
✓ Explainable recommendations (plain-language justifications)  
✓ Trade-off analysis (balancing growth vs safety)  
✓ Quantifiable impact (ROI, projections, amounts)  
✓ Multi-asset optimization (FD, EPF, Crypto)  
✓ Risk-based personalization (3 profiles)  
✓ Malaysian-specific data (EPF targets, FD rates)  
✓ Desktop application (user-friendly GUI)  

## Performance

- Recommendation generation: <1 second
- All validations: Real-time
- UI remains responsive (threading)

## Ready for Next Steps

This backend is production-ready and can be:
- Integrated with frontend/UI team's application
- Connected to live market data APIs
- Enhanced with ML models (LSTM/Prophet)
- Extended with additional features (tax optimization, etc.)
