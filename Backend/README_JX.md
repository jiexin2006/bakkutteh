# AI Financial Intelligence Advisor

A comprehensive Python desktop application that provides personalized investment recommendations by integrating EPF benchmarking, Bitcoin trend analysis, and intelligent multi-asset optimization.

## Project Overview

This application implements the **Backend Developer** role from the UMHackathon 2026 project, focusing on:
- **Core Application Logic**: User input handling and data coordination
- **Optimization & Trade-off Analysis**: Intelligent fund allocation between FD, EPF, and Crypto
- **Quantifiable Impact**: ROI projections and financial impact calculations

## Architecture

### Core Components

1. **config.py** - Configuration and constants
   - EPF basic savings targets by age
   - Risk appetite profiles
   - FD rates from Malaysian banks
   - Market volatility thresholds

2. **models.py** - Data structures
   - `UserProfile`: User financial information
   - `MarketData`: Current market conditions
   - `BitcoinAnalysis`: Bitcoin trend analysis results
   - `AllocationStrategy`: Recommended fund allocation
   - `FinancialRecommendation`: Complete recommendation output

3. **epf_calculator.py** - EPF benchmarking engine
   - EPF target calculation by age
   - Gap analysis
   - Status determination (On Track / Behind)
   - Crypto allocation adjustment based on EPF gap
   - Monthly contribution calculation to reach targets

4. **bitcoin_analyzer.py** - Bitcoin trend analysis
   - RSI (Relative Strength Index) calculation
   - MACD analysis
   - Exponential Moving Averages (EMA)
   - Trading signal generation (BUY/SELL/HOLD)
   - Confidence scoring

5. **optimizer.py** - Multi-asset optimization engine
   - `AssetOptimizer`: Handles allocation optimization
     - Risk-based allocation adjustment
     - EPF gap-based prioritization
     - Bitcoin signal integration
     - Minimum/maximum allocation enforcement
   - `RecommendationEngine`: Orchestrates the complete pipeline

6. **main.py** - Desktop GUI application
   - Tab-based interface (User Profile & Market Data / Results)
   - Real-time form validation
   - Threading for responsive UI
   - Formatted output display

## The Decision Intelligence Pipeline

### 4-Step Processing Flow

#### Step 1: Safety Net Audit (EPF Benchmarking)
Compares user's current EPF balance against official targets for their age group.
Determines if user is "On Track" or needs to catch up.

#### Step 2: Bitcoin Predictive Analysis
Analyzes historical patterns and current market indicators:
- Moving average crossovers
- RSI levels
- Daily momentum
- Generates Bullish/Bearish/Neutral trend with confidence score

#### Step 3: Multi-Asset Optimization (Smarter Decision Logic)
Calculates optimal allocation using trade-off analysis:
- Base allocation from risk profile
- EPF deficit adjustments (prioritizes recovery if behind)
- Bitcoin signal integration (more crypto on strong buy signals)
- Minimum/maximum constraints enforcement

#### Step 4: Contextual Strategy Generation
Outputs personalized strategy including:
- Exact percentage allocation
- Monthly contribution amounts
- Best FD option from Malaysian banks
- 1/6/12-month portfolio projections
- Human-readable reasoning

## Key Features

### 1. Intelligent Risk-Based Allocation
- **Conservative**: 60% FD, 35% EPF, 5% Crypto
- **Moderate**: 40% FD, 40% EPF, 20% Crypto
- **Aggressive**: 20% FD, 30% EPF, 50% Crypto

### 2. EPF Gap-Aware Rebalancing
If EPF is behind target, automatically prioritizes safe allocations:
- Critical gap (>40%): Crypto capped at 5%
- High gap (>20%): Crypto capped at 30%
- Moderate gap (>10%): Crypto capped at 60%

### 3. Dynamic Bitcoin Integration
- Increases crypto allocation when strong buy signals detected
- Reduces crypto on sell signals
- Confidence-weighted adjustments

### 4. Projected ROI Calculation
- Monthly, 6-month, and 12-month portfolio value projections
- Scenario-based analysis (Conservative/Moderate/Bullish)
- Accounts for different growth rates per asset class

### 5. Explainable Recommendations
- Step-by-step reasoning for every recommendation
- Trade-off analysis explained in plain language
- Links EPF status → allocation strategy → expected returns

## Usage

### Installation

1. Clone the repository
```bash
cd /Users/jiexin/Documents/Programming/UMHackathon_2026/bakkutteh
```

2. Ensure Python 3.8+ is installed
```bash
python --version
```

3. No external dependencies required (uses only Python standard library)

### Running the Application

```bash
python main.py
```

The GUI will open with two tabs:
- **Tab 1 (User Profile & Market Data)**: Enter your financial information
- **Tab 2 (Results)**: View detailed recommendation reports

### Example Input

**User Profile:**
- Age: 30
- Monthly Salary: MYR 5,000
- Monthly Expenditure: MYR 2,000
- Fixed Liabilities: MYR 500
- Current EPF Balance: MYR 80,000
- Risk Appetite: Moderate

**Market Data:**
- Bitcoin Price: USD 45,000
- Bitcoin Daily Change: +2.5%
- Bitcoin 7-Day Average: USD 44,000
- Bitcoin 30-Day Average: USD 42,000

**Output:**
The system generates a comprehensive recommendation including:
- EPF status and gap analysis
- Optimal monthly allocation (FD, EPF, Crypto)
- Best bank FD options with rates
- 12-month portfolio projections
- Quantifiable ROI estimates

## Core Algorithms

### EPF Contribution Calculation
Uses Future Value of Annuity formula:
```
FV = PV(1+r)^n + PMT * [((1+r)^n - 1) / r]
```
Solves for monthly payment needed to reach retirement target.

### Allocation Optimization
Multi-step adjustment process:
1. Start with risk profile base allocation
2. Apply EPF gap multipliers (critical/high/moderate/low)
3. Adjust for Bitcoin signals
4. Enforce minimum/maximum constraints
5. Normalize to sum to 100%

### ROI Projection
Compound interest calculation with asset-specific rates:
```
Value = FD_amount × (1 + fd_rate)^months/12 
      + EPF_amount × (1 + epf_rate)^months/12 
      + Crypto_amount × (1 + crypto_rate)^months/12
```

## Output Format

The application generates detailed reports with:
1. **User Summary**: Financial profile overview
2. **EPF Analysis**: Status, targets, gaps, projections
3. **Bitcoin Analysis**: Signal, confidence, reasoning
4. **Allocation Strategy**: Percentages and amounts
5. **Portfolio Projections**: Near/medium/long-term values
6. **Quantifiable Impact**: Annual investment and projected ROI
7. **Detailed Reasoning**: Trade-off analysis and recommendations

## Data Flow

```
User Input (Age, Salary, EPF, Risk Profile)
         ↓
    EPF Calculator ─────────────→ EPF Status & Gap
         ↓
Market Data (Bitcoin, FD Rates)
         ↓
Bitcoin Analyzer ────────────→ Trading Signal & Confidence
         ↓
Multi-Asset Optimizer ─────→ Allocation Strategy
         ↓
Generate Projections & ROI
         ↓
Output Recommendation Report
```

## Future Enhancements

- Live market data API integration (Binance, CoinGecko)
- Real-time FD rate updates from Malaysian banks
- Machine Learning predictions (LSTM/Prophet)
- Portfolio tracking and rebalancing recommendations
- Tax optimization strategies
- Export reports to PDF
- Database storage for user profiles and recommendations
- Mobile application version

## Technical Stack

- **Language**: Python 3.8+
- **UI**: tkinter (standard Python GUI library)
- **Architecture**: Modular, component-based design
- **Data Models**: Dataclasses for type safety
- **Threading**: Background analysis to keep UI responsive

## File Structure

```
bakkutteh/
├── main.py                 # Desktop GUI application
├── config.py              # Configuration and constants
├── models.py              # Data structures
├── epf_calculator.py      # EPF benchmarking logic
├── bitcoin_analyzer.py    # Bitcoin trend analysis
├── optimizer.py           # Multi-asset optimization engine
├── requirements.txt       # Dependencies (none needed)
└── README.md             # This file
```

## Performance

- **Recommendation Generation**: < 1 second
- **Market Analysis**: < 0.5 seconds
- **Portfolio Projections**: < 0.1 seconds
- **UI Responsiveness**: Maintained via threading

## Error Handling

The application includes comprehensive error handling for:
- Invalid input validation (age, salary, amounts)
- Missing market data
- Calculation errors
- UI display issues

## Decision Transparency

A key feature is **explainability** - every recommendation includes:
- Why EPF status affects allocation
- How Bitcoin signal changes strategy
- Trade-offs between growth and safety
- Specific reasoning for percentage splits

## Contact & Support

For questions or feedback about this AI Financial Intelligence Advisor backend implementation, please refer to the UMHackathon 2026 project guidelines.

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-24  
**Status**: Production Ready
