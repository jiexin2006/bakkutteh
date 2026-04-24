from __future__ import annotations

from datetime import datetime
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic import field_validator

from ZAI import IlmuApiError
from bitcoin_analyzer import BitcoinAnalyzer
from config import EPF_INTEREST_RATE, FD_MIN_PLACEMENT_RM, FD_RATES, get_fd_prompt_context
from epf_calculator import EPFCalculator
from models import MarketData
from response import ResponseParseError, get_zai_response_json
from userProfile import UserProfile


logger = logging.getLogger("bakkutteh.api")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class AdvisoryRequest(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=18, le=100)
    salary: float = Field(ge=0)
    monthlyExpenses: float = Field(ge=0)
    currentFD: float = Field(default=0, ge=0)
    currentEPF: float = Field(default=0, ge=0)
    cryptoHoldings: float = Field(default=0, ge=0)
    fixedLiabilities: float = Field(default=0, ge=0)
    riskAppetite: str = Field(default="Moderate")
    epfDeductionRm: float = Field(default=0, ge=0)
    targetRetirementTier: str = Field(default="basic")
    bitcoinPrice: float = Field(default=47500, gt=0)
    bitcoinDailyChange: float = Field(default=2.5)
    bitcoin7DayAvg: float = Field(default=46800, gt=0)
    bitcoin30DayAvg: float = Field(default=45200, gt=0)

    @field_validator(
        "age",
        "salary",
        "monthlyExpenses",
        "currentFD",
        "currentEPF",
        "cryptoHoldings",
        "fixedLiabilities",
        "epfDeductionRm",
        "bitcoinPrice",
        "bitcoinDailyChange",
        "bitcoin7DayAvg",
        "bitcoin30DayAvg",
        mode="before",
    )
    @classmethod
    def _coerce_numeric_input(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.replace(",", "").strip()
            if normalized == "":
                return 0
            return normalized
        return value


app = FastAPI(title="Bakkutteh Financial Advisor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_decision_context(epf_analysis: dict, user_profile: UserProfile) -> dict:
    surplus = max(user_profile.monthly_surplus, 0.0)
    return {
        "current_surplus_rm": round(surplus, 2),
        "fd_minimum_rm": FD_MIN_PLACEMENT_RM,
        "epf_status": epf_analysis["status"],
        "priority_level": epf_analysis["priority_level"],
        "selected_target_rm": epf_analysis["selected_target_rm"],
        "deficit_rm": epf_analysis["deficit_rm"],
        "deficit_percentage": epf_analysis["deficit_percentage"],
    }


def _build_temporary_fallback_advisory(
    epf_analysis: dict,
    decision_context: dict,
    market_signals: dict,
    fd_context: dict,
) -> dict:
    """Temporary fallback response while live ZAI endpoint is unavailable."""
    surplus = float(decision_context.get("current_surplus_rm", 0.0))
    priority = str(epf_analysis.get("priority_level", "Medium"))
    fd_rates = fd_context.get("verified_market_rates", [])
    top_fd = fd_rates[0] if isinstance(fd_rates, list) and fd_rates else None

    fd_action = "Use top verified FD option"
    if isinstance(top_fd, dict):
        fd_action = (
            f"Use {top_fd.get('bank_name', 'verified bank')} "
            f"{top_fd.get('tenure_months', 12)}-month FD"
        )

    if surplus < FD_MIN_PLACEMENT_RM:
        action_plan = [
            {
                "percentage": "60%",
                "category": "EPF",
                "action": "Top-up EPF via i-Akaun",
                "reasoning": "Fallback mode prioritizes retirement safety with limited monthly surplus.",
            },
            {
                "percentage": "40%",
                "category": "Cash on Hand",
                "action": "Hold liquidity buffer",
                "reasoning": "FD minimum is not met, so liquidity is preserved.",
            },
        ]
    else:
        action_plan = [
            {
                "percentage": "40%",
                "category": "EPF",
                "action": "Top-up EPF via i-Akaun",
                "reasoning": "Fallback mode keeps retirement contributions active.",
            },
            {
                "percentage": "45%",
                "category": "FD",
                "action": fd_action,
                "reasoning": "Fallback mode uses verified FD market context for stable allocation.",
            },
            {
                "percentage": "15%",
                "category": "Crypto",
                "action": "Keep small BTC allocation",
                "reasoning": "Crypto remains capped during fallback mode.",
            },
        ]

    return {
        "overall_strategy": "Temporary fallback strategy while AI model is unavailable",
        "safety_gauge": priority,
        "action_plan": action_plan,
        "next_step": (
            "Apply this temporary allocation and retry AI advisory shortly. "
            f"Current BTC signal: {market_signals.get('bitcoin_signal', 'HOLD')}"
        ),
    }


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/advisory")
def create_advisory(payload: AdvisoryRequest, request: Request) -> dict:
    request_id = request.headers.get("x-request-id") or str(uuid4())
    started_at = datetime.now()
    logger.info("[%s] advisory request received", request_id)

    try:
        logger.info("[%s] building user profile", request_id)
        user_profile = UserProfile(
            user_id=payload.name,
            age=payload.age,
            monthly_salary=payload.salary,
            monthly_expenditure=payload.monthlyExpenses,
            current_epf_balance=payload.currentEPF,
            fixed_liabilities=payload.fixedLiabilities,
            risk_appetite=payload.riskAppetite,
            epf_deduction_rm=payload.epfDeductionRm,
            target_retirement_tier=payload.targetRetirementTier.lower(),
        )

        logger.info("[%s] running EPF analysis", request_id)
        epf_analysis = EPFCalculator.get_epf_analysis(
            user_profile,
            user_profile.target_retirement_tier,
        )

        logger.info("[%s] preparing market context", request_id)
        market_data = MarketData(
            bitcoin_price=payload.bitcoinPrice,
            bitcoin_daily_change=payload.bitcoinDailyChange,
            bitcoin_7day_avg=payload.bitcoin7DayAvg,
            bitcoin_30day_avg=payload.bitcoin30DayAvg,
            fd_rates=FD_RATES,
            epf_interest_rate=EPF_INTEREST_RATE,
            timestamp=datetime.now(),
        )

        logger.info("[%s] generating bitcoin summary", request_id)
        bitcoin_summary = BitcoinAnalyzer.get_prompt_summary(market_data)
        decision_context = _build_decision_context(epf_analysis, user_profile)
        fd_context = get_fd_prompt_context(limit=3)

        logger.info("[%s] calling ZAI model", request_id)
        advisory_source = "zai"
        advisory_label = "LIVE_ZAI"
        advisory_error = None

        # FALLBACK START: Temporary fallback path when ZAI is unavailable.
        try:
            advisory_json = get_zai_response_json(
                user_data=user_profile.getUserProfile(),
                decision_context=decision_context,
                epf_analysis=epf_analysis,
                market_data={
                    **fd_context,
                    **bitcoin_summary,
                },
            )
        except Exception as exc:
            advisory_source = "fallback"
            advisory_label = "TEMPORARY_FALLBACK"
            advisory_error = str(exc)
            logger.warning("[%s] fallback activated due to ZAI error: %s", request_id, exc)
            advisory_json = _build_temporary_fallback_advisory(
                epf_analysis=epf_analysis,
                decision_context=decision_context,
                market_signals=bitcoin_summary,
                fd_context=fd_context,
            )
        # FALLBACK END

        duration_seconds = (datetime.now() - started_at).total_seconds()
        logger.info("[%s] advisory complete in %.2fs", request_id, duration_seconds)

        return {
            "request_id": request_id,
            "advisory_source": advisory_source,
            "advisory_label": advisory_label,
            "advisory_error": advisory_error,
            "user_profile": user_profile.getUserProfile(),
            "epf_analysis": epf_analysis,
            "decision_context": decision_context,
            "market_signals": bitcoin_summary,
            "advisory_json": advisory_json,
        }
    except (ValueError, KeyError) as exc:
        logger.exception("[%s] bad request payload", request_id)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IlmuApiError as exc:
        logger.exception("[%s] ZAI client error", request_id)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ResponseParseError as exc:
        logger.exception("[%s] response parse error", request_id)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API boundary
        logger.exception("[%s] unexpected server error", request_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {exc}") from exc