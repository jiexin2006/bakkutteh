"""Bitcoin analysis placeholder module.

This version loads historical Bitcoin data from the attached `data/` folder and
exposes a placeholder predictive-model interface for a future trained model.
The public API stays compatible with the rest of the app, but the actual model
prediction is intentionally delegated to another script.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from models import MarketData, BitcoinSignal, BitcoinAnalysis
from config import BITCOIN_THRESHOLDS, CONFIDENCE_THRESHOLDS


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BITCOIN_CSV_PATH = DATA_DIR / "Cleaned_BitcoinHistory_For_ML.csv"
BITCOIN_JSON_PATH = DATA_DIR / "Bitcoin_ContextHistory_For_ZAI.json"


@dataclass
class BitcoinFeatureSet:
    """Feature payload prepared from the data folder and live market inputs."""

    current_price: float
    seven_day_ma: float
    thirty_day_ma: float
    daily_change_pct: float
    daily_volatility_pct: float
    seven_day_momentum_pct: float
    historical_rows: int


class PlaceholderBitcoinPredictiveModel:
    """Placeholder interface for the future trained predictive model."""

    def predict(self, features: BitcoinFeatureSet) -> BitcoinAnalysis:
        raise NotImplementedError(
            "Bitcoin prediction is a placeholder. A trained GLM model will be wired in a separate script."
        )


class BitcoinAnalyzer:
    """Loads Bitcoin history from the data folder and prepares model inputs."""

    _predictive_model: PlaceholderBitcoinPredictiveModel = PlaceholderBitcoinPredictiveModel()

    @staticmethod
    def load_context_history() -> list[dict]:
        """Load context history from the attached JSON file."""
        if not BITCOIN_JSON_PATH.exists():
            return []

        with BITCOIN_JSON_PATH.open("r", encoding="utf-8") as file_handle:
            history = json.load(file_handle)

        return history if isinstance(history, list) else []

    @staticmethod
    def load_training_history() -> list[dict]:
        """Load cleaned Bitcoin history from the attached CSV file."""
        if not BITCOIN_CSV_PATH.exists():
            return []

        rows: list[dict] = []
        with BITCOIN_CSV_PATH.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                rows.append(row)

        return rows

    @staticmethod
    def _safe_float(value: object, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @classmethod
    def build_feature_set(cls, market_data: MarketData) -> BitcoinFeatureSet:
        """Combine live market input with historical data from the data folder."""
        history_rows = cls.load_training_history()
        context_rows = cls.load_context_history()

        latest_row = history_rows[-1] if history_rows else {}
        latest_context = context_rows[-1] if context_rows else {}

        seven_day_ma = cls._safe_float(
            latest_row.get("7_Day_MA", latest_context.get("7_Day_MA", market_data.bitcoin_7day_avg)),
            market_data.bitcoin_7day_avg,
        )
        thirty_day_ma = cls._safe_float(
            latest_row.get("30_Day_MA", latest_context.get("30_Day_MA", market_data.bitcoin_30day_avg)),
            market_data.bitcoin_30day_avg,
        )
        daily_volatility_pct = cls._safe_float(
            latest_row.get("Daily_Volatility_%", latest_context.get("Daily_Volatility_%", abs(market_data.bitcoin_daily_change))),
            abs(market_data.bitcoin_daily_change),
        )
        seven_day_momentum_pct = cls._safe_float(
            latest_row.get("7_Day_Momentum_%", latest_context.get("7_Day_Momentum_%", market_data.bitcoin_daily_change)),
            market_data.bitcoin_daily_change,
        )

        return BitcoinFeatureSet(
            current_price=market_data.bitcoin_price,
            seven_day_ma=seven_day_ma,
            thirty_day_ma=thirty_day_ma,
            daily_change_pct=market_data.bitcoin_daily_change,
            daily_volatility_pct=daily_volatility_pct,
            seven_day_momentum_pct=seven_day_momentum_pct,
            historical_rows=len(history_rows),
        )

    @classmethod
    def set_predictive_model(cls, model: PlaceholderBitcoinPredictiveModel) -> None:
        """Replace the placeholder model with a trained model later."""
        cls._predictive_model = model

    @classmethod
    def predict_with_model(cls, features: BitcoinFeatureSet) -> BitcoinAnalysis:
        """Delegate to the injected predictive model."""
        return cls._predictive_model.predict(features)

    @staticmethod
    def _fallback_analysis(market_data: MarketData, features: BitcoinFeatureSet) -> BitcoinAnalysis:
        """Return a safe placeholder analysis until the real model is plugged in."""
        trend = "Neutral"
        signal = BitcoinSignal.HOLD
        confidence = CONFIDENCE_THRESHOLDS["low"]

        if market_data.bitcoin_7day_avg > market_data.bitcoin_30day_avg and market_data.bitcoin_daily_change > 0:
            trend = "Mildly Bullish"
            signal = BitcoinSignal.HOLD
            confidence = 0.35
        elif market_data.bitcoin_7day_avg < market_data.bitcoin_30day_avg and market_data.bitcoin_daily_change < 0:
            trend = "Mildly Bearish"
            signal = BitcoinSignal.HOLD
            confidence = 0.35

        reasoning = (
            "Placeholder analysis using data from the attached Bitcoin history files. "
            f"Loaded {features.historical_rows} historical rows; predictive inference is deferred to a trained model."
        )

        return BitcoinAnalysis(
            signal=signal,
            confidence_score=confidence,
            trend=trend,
            reasoning=reasoning,
        )

    @classmethod
    def analyze_trend(cls, market_data: MarketData) -> BitcoinAnalysis:
        """Prepare features from the dataset and attempt model inference."""
        features = cls.build_feature_set(market_data)

        try:
            return cls.predict_with_model(features)
        except NotImplementedError:
            return cls._fallback_analysis(market_data, features)

    @classmethod
    def get_prompt_summary(cls, market_data: MarketData) -> dict:
        """Return a compact Bitcoin payload for prompting and downstream reasoning."""
        analysis = cls.analyze_trend(market_data)
        return {
            "bitcoin_signal": analysis.signal.value,
            "bitcoin_confidence": round(float(analysis.confidence_score), 2),
            "bitcoin_trend": analysis.trend,
        }

    @staticmethod
    def calculate_confidence_level(confidence_score: float) -> str:
        """Convert confidence score to readable level."""
        if confidence_score >= CONFIDENCE_THRESHOLDS["high"]:
            return "HIGH"
        if confidence_score >= CONFIDENCE_THRESHOLDS["medium"]:
            return "MEDIUM"
        return "LOW"


PLACEHOLDER_IMPLEMENTATION = True
