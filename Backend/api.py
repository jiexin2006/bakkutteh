from __future__ import annotations

from datetime import datetime
import logging
import json
from pathlib import Path
from uuid import uuid4
from typing import Any
from live_data import fetch_live_bitcoin

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


class SavedUserProfileRequest(BaseModel):
    user_data: dict[str, str]


class SelectProfileRequest(BaseModel):
    profile_id: str


app = FastAPI(title="Bakkutteh Financial Advisor API", version="1.0.0")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAVED_USER_DATA_PATH = DATA_DIR / "bakkutteh_user_data.json"

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


def _default_profile_store() -> dict[str, Any]:
    return {
        "profiles": [],
        "active_profile_id": None,
    }


def _normalize_profile_store(raw_payload: Any) -> dict[str, Any]:
    store = _default_profile_store()

    if not isinstance(raw_payload, dict):
        return store

    profiles_payload = raw_payload.get("profiles")
    if isinstance(profiles_payload, list):
        normalized_profiles = []
        for item in profiles_payload:
            if not isinstance(item, dict):
                continue
            user_data = item.get("user_data")
            profile_id = item.get("id")
            if not isinstance(user_data, dict):
                continue
            if not isinstance(profile_id, str) or not profile_id.strip():
                profile_id = str(uuid4())
            normalized_profiles.append(
                {
                    "id": profile_id,
                    "user_data": user_data,
                    "saved_at": item.get("saved_at") or datetime.now().isoformat(),
                }
            )
        store["profiles"] = normalized_profiles
        active_profile_id = raw_payload.get("active_profile_id")
        if isinstance(active_profile_id, str):
            store["active_profile_id"] = active_profile_id
        return store

    # Backward compatibility for old single-profile shape.
    legacy_user_data = raw_payload.get("user_data")
    if isinstance(legacy_user_data, dict):
        migrated_profile_id = str(uuid4())
        store["profiles"] = [
            {
                "id": migrated_profile_id,
                "user_data": legacy_user_data,
                "saved_at": raw_payload.get("saved_at") or datetime.now().isoformat(),
            }
        ]
        store["active_profile_id"] = migrated_profile_id

    return store


def _read_profile_store() -> dict[str, Any]:
    if not SAVED_USER_DATA_PATH.exists():
        return _default_profile_store()

    with SAVED_USER_DATA_PATH.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    return _normalize_profile_store(payload)


def _write_profile_store(store: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with SAVED_USER_DATA_PATH.open("w", encoding="utf-8") as file_handle:
        json.dump(store, file_handle, indent=2)


def _active_profile_from_store(store: dict[str, Any]) -> dict[str, Any] | None:
    active_profile_id = store.get("active_profile_id")
    profiles = store.get("profiles") or []
    if not isinstance(active_profile_id, str):
        return None

    for profile in profiles:
        if isinstance(profile, dict) and profile.get("id") == active_profile_id:
            return profile
    return None


def _load_saved_user_data() -> dict[str, str] | None:
    store = _read_profile_store()
    active_profile = _active_profile_from_store(store)
    if not isinstance(active_profile, dict):
        return None
    user_data = active_profile.get("user_data")
    return user_data if isinstance(user_data, dict) else None


def _save_user_data(user_data: dict[str, str]) -> None:
    store = _read_profile_store()
    profiles = store.get("profiles") or []
    active_profile = _active_profile_from_store(store)

    if isinstance(active_profile, dict):
        active_profile["user_data"] = user_data
        active_profile["saved_at"] = datetime.now().isoformat()
    else:
        new_profile_id = str(uuid4())
        profiles.append(
            {
                "id": new_profile_id,
                "user_data": user_data,
                "saved_at": datetime.now().isoformat(),
            }
        )
        store["active_profile_id"] = new_profile_id

    store["profiles"] = profiles
    _write_profile_store(store)


def _profile_label(profile: dict[str, Any]) -> str:
    user_data = profile.get("user_data")
    if isinstance(user_data, dict):
        name = user_data.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return "Unnamed Profile"


def _build_bitcoin_market_data() -> MarketData:
    """Build MarketData: uses live MYR price, or ML-predicted price if unavailable."""

    live_data = fetch_live_bitcoin()

    history_rows = BitcoinAnalyzer.load_training_history()
    latest_row = history_rows[-1] if history_rows else {}

    # Load baseline historical data
    bitcoin_price_usd = float(latest_row.get("Close", 47500) or 47500)
    bitcoin_7day_avg = float(latest_row.get("7_Day_MA", bitcoin_price_usd) or bitcoin_price_usd)
    bitcoin_30day_avg = float(latest_row.get("30_Day_MA", bitcoin_price_usd) or bitcoin_price_usd)
    bitcoin_daily_change = float(latest_row.get("7_Day_Momentum_%", latest_row.get("Daily_Volatility_%", 0.0)) or 0.0)

    # Create baseline market data for the model
    baseline_market_data = MarketData(
        bitcoin_price=bitcoin_price_usd,
        bitcoin_price_myr=bitcoin_price_usd * 4.5,
        bitcoin_daily_change=bitcoin_daily_change,
        bitcoin_7day_avg=bitcoin_7day_avg,
        bitcoin_30day_avg=bitcoin_30day_avg,
        fd_rates=FD_RATES,
        epf_interest_rate=EPF_INTEREST_RATE,
        timestamp=datetime.now(),
        price_source="baseline",
    )

    # Determine price source: live data or ML prediction
    if live_data and 'current_price_myr' in live_data:
        # Use live price
        final_price_usd = float(live_data.get('current_price_usd', bitcoin_price_usd))
        final_price_myr = float(live_data['current_price_myr'])
        price_source = "live"
        print(f"[LIVE DATA] Using live Bitcoin price: RM{final_price_myr}")
    else:
        # Use ML model's predicted price
        model_result = BitcoinAnalyzer.generate_model_result(baseline_market_data)
        final_price_usd = float(model_result.forecast_price)
        final_price_myr = final_price_usd * 4.5
        price_source = "predicted"
        print(f"[PREDICTED] Using ML model predicted price: RM{final_price_myr} (Live data unavailable)")

    return MarketData(
        bitcoin_price=final_price_usd,
        bitcoin_price_myr=final_price_myr,
        bitcoin_daily_change=bitcoin_daily_change,
        bitcoin_7day_avg=bitcoin_7day_avg,
        bitcoin_30day_avg=bitcoin_30day_avg,
        fd_rates=FD_RATES,
        epf_interest_rate=EPF_INTEREST_RATE,
        timestamp=datetime.now(),
        price_source=price_source,
    )


@app.get("/api/fd-rankings")
def get_fd_rankings(limit: int = 6) -> dict:
    """Return verified FD rankings from the backend data file."""
    fd_context = get_fd_prompt_context(limit=limit)
    return {
        "epf_dividend_rate_pct": fd_context["epf_dividend_rate_pct"],
        "verified_market_rates": fd_context["verified_market_rates"],
    }


@app.get("/api/saved-profile")
def get_saved_profile() -> dict:
    saved_profile = _load_saved_user_data()
    return {"user_data": saved_profile}


@app.put("/api/saved-profile")
def save_profile(payload: SavedUserProfileRequest) -> dict:
    _save_user_data(payload.user_data)
    return {"status": "saved", "path": str(SAVED_USER_DATA_PATH)}


@app.delete("/api/saved-profile")
def reset_saved_profile() -> dict:
    store = _read_profile_store()
    active_profile_id = store.get("active_profile_id")
    profiles = store.get("profiles") or []

    if isinstance(active_profile_id, str):
        profiles = [
            profile
            for profile in profiles
            if isinstance(profile, dict) and profile.get("id") != active_profile_id
        ]

    store["profiles"] = profiles
    store["active_profile_id"] = profiles[0].get("id") if profiles else None

    if not profiles and SAVED_USER_DATA_PATH.exists():
        SAVED_USER_DATA_PATH.unlink()
    elif profiles:
        _write_profile_store(store)

    return {"status": "reset"}


@app.get("/api/profiles")
def get_profiles() -> dict:
    store = _read_profile_store()
    profiles = store.get("profiles") or []

    return {
        "active_profile_id": store.get("active_profile_id"),
        "profiles": [
            {
                "id": profile.get("id"),
                "name": _profile_label(profile),
                "saved_at": profile.get("saved_at"),
                "user_data": profile.get("user_data"),
            }
            for profile in profiles
            if isinstance(profile, dict)
        ],
    }


@app.post("/api/profiles/select")
def select_profile(payload: SelectProfileRequest) -> dict:
    store = _read_profile_store()
    profiles = store.get("profiles") or []
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("id") == payload.profile_id:
            store["active_profile_id"] = payload.profile_id
            _write_profile_store(store)
            return {"status": "selected", "active_profile_id": payload.profile_id}

    raise HTTPException(status_code=404, detail="Profile not found")


@app.put("/api/profiles/{profile_id}")
def update_profile(profile_id: str, payload: SavedUserProfileRequest) -> dict:
    store = _read_profile_store()
    profiles = store.get("profiles") or []

    for profile in profiles:
        if isinstance(profile, dict) and profile.get("id") == profile_id:
            profile["user_data"] = payload.user_data
            profile["saved_at"] = datetime.now().isoformat()
            _write_profile_store(store)
            return {"status": "updated", "profile_id": profile_id}

    profiles.append(
        {
            "id": profile_id,
            "user_data": payload.user_data,
            "saved_at": datetime.now().isoformat(),
        }
    )
    store["profiles"] = profiles
    store["active_profile_id"] = profile_id
    _write_profile_store(store)
    return {"status": "created", "profile_id": profile_id}


@app.post("/api/profiles")
def create_profile(payload: SavedUserProfileRequest) -> dict:
    store = _read_profile_store()
    profiles = store.get("profiles") or []

    new_profile_id = str(uuid4())
    profiles.append(
        {
            "id": new_profile_id,
            "user_data": payload.user_data,
            "saved_at": datetime.now().isoformat(),
        }
    )
    store["profiles"] = profiles
    store["active_profile_id"] = new_profile_id
    _write_profile_store(store)

    return {"status": "created", "profile_id": new_profile_id}


@app.get("/api/bitcoin-advisory")
def get_bitcoin_advisory() -> dict:
    """Return chart data and model output for the dashboard Bitcoin card."""
    bitcoin_market_data = _build_bitcoin_market_data()
    return BitcoinAnalyzer.get_dashboard_payload(bitcoin_market_data)


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