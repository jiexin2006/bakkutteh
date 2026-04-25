"""Bitcoin analysis module driven by the trained H5 model when available.

The analyzer reads the historical CSV in `machine_learning/`, attempts to load
`btc_model.h5`, and falls back to a deterministic heuristic if TensorFlow is
not installed in the current environment.
"""

from __future__ import annotations

import csv
import json
import importlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from models import MarketData, BitcoinSignal, BitcoinAnalysis
from config import CONFIDENCE_THRESHOLDS


logger = logging.getLogger("bakkutteh.bitcoin")

ML_DIR = Path(__file__).resolve().parent.parent / "machine_learning"
BITCOIN_CSV_PATH = ML_DIR / "Cleaned_BitcoinHistory_For_ML.csv"
BITCOIN_MODEL_PATH = ML_DIR / "btc_model.h5"


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


@dataclass
class BitcoinModelResult:
    """Prediction output derived from the H5 model or a fallback heuristic."""

    signal: BitcoinSignal
    confidence_score: float
    trend: str
    reasoning: str
    current_price: float
    forecast_price: float
    forecast_change_pct: float
    crypto_data: list[dict[str, Any]]
    model_source: str


class BitcoinPredictiveModelUnavailable(RuntimeError):
    """Raised when the H5 model cannot be loaded in the current environment."""


class BitcoinPredictiveModel:
    """Wrapper around the trained H5 model."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._load_error: Exception | None = None

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        if self._load_error is not None:
            raise BitcoinPredictiveModelUnavailable(str(self._load_error)) from self._load_error

        try:
            tensorflow_keras_models = importlib.import_module("tensorflow.keras.models")
            load_model = getattr(tensorflow_keras_models, "load_model")
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            self._load_error = exc
            raise BitcoinPredictiveModelUnavailable(
                "TensorFlow is not installed, so btc_model.h5 cannot be loaded right now."
            ) from exc

        if not BITCOIN_MODEL_PATH.exists():
            self._load_error = FileNotFoundError(f"Missing model file: {BITCOIN_MODEL_PATH}")
            raise BitcoinPredictiveModelUnavailable(str(self._load_error)) from self._load_error

        try:
            self._model = load_model(str(BITCOIN_MODEL_PATH), compile=False)
            return self._model
        except Exception as exc:  # pragma: no cover - runtime dependent
            self._load_error = exc
            raise BitcoinPredictiveModelUnavailable(f"Could not load btc_model.h5: {exc}") from exc

    def predict(self, features: np.ndarray) -> np.ndarray:
        model = self._load_model()
        return np.asarray(model.predict(features, verbose=0))


class BitcoinAnalyzer:
    """Loads Bitcoin history from the data folder and prepares model inputs."""

    _predictive_model: BitcoinPredictiveModel = BitcoinPredictiveModel()

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

    @staticmethod
    def _fit_min_max(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        minimums = np.min(values, axis=0)
        maximums = np.max(values, axis=0)
        spans = np.where(maximums - minimums == 0, 1.0, maximums - minimums)
        return minimums, maximums, spans

    @staticmethod
    def _scale(values: np.ndarray, minimums: np.ndarray, spans: np.ndarray) -> np.ndarray:
        return (values - minimums) / spans

    @staticmethod
    def _inverse_close(value: float, minimums: np.ndarray, spans: np.ndarray) -> float:
        return float(value * spans[0] + minimums[0])

    @staticmethod
    def _format_date_label(date_value: str) -> str:
        try:
            from datetime import datetime

            parsed = datetime.strptime(date_value, "%Y-%m-%d")
            return parsed.strftime("%m/%d")
        except Exception:
            return date_value

    @classmethod
    def build_feature_set(cls, market_data: MarketData) -> BitcoinFeatureSet:
        """Combine live market input with historical data from the data folder."""
        history_rows = cls.load_training_history()
        latest_row = history_rows[-1] if history_rows else {}

        seven_day_ma = cls._safe_float(
            latest_row.get("7_Day_MA", market_data.bitcoin_7day_avg),
            market_data.bitcoin_7day_avg,
        )
        thirty_day_ma = cls._safe_float(
            latest_row.get("30_Day_MA", market_data.bitcoin_30day_avg),
            market_data.bitcoin_30day_avg,
        )
        daily_volatility_pct = cls._safe_float(
            latest_row.get("Daily_Volatility_%", abs(market_data.bitcoin_daily_change)),
            abs(market_data.bitcoin_daily_change),
        )
        seven_day_momentum_pct = cls._safe_float(
            latest_row.get("7_Day_Momentum_%", market_data.bitcoin_daily_change),
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
    def set_predictive_model(cls, model: Any) -> None:
        """Replace the placeholder model with a trained model later."""
        cls._predictive_model = model

    @classmethod
    def _predict_with_model(cls, sequence: np.ndarray) -> np.ndarray:
        return cls._predictive_model.predict(sequence)

    @classmethod
    def _build_model_inputs(cls, history_rows: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        feature_names = ["Close", "7_Day_MA", "30_Day_MA", "Daily_Volatility_%"]
        matrix = np.array(
            [
                [
                    cls._safe_float(row.get(name), 0.0)
                    for name in feature_names
                ]
                for row in history_rows
            ],
            dtype=float,
        )
        minimums, maximums, spans = cls._fit_min_max(matrix)
        scaled = cls._scale(matrix, minimums, spans)
        return matrix, scaled, minimums, spans

    @classmethod
    def _build_crypto_series(cls, history_rows: list[dict], forecast_price: float | None = None) -> list[dict[str, Any]]:
        recent_rows = history_rows[-6:] if len(history_rows) >= 6 else history_rows[:]
        base_date = datetime.now().date()
        total_points = len(recent_rows)
        series = [
            {
                "time": (base_date - timedelta(days=(total_points - index - 1))).strftime("%-m/%-d"),
                "price": round(cls._safe_float(row.get("Close"), 0.0), 2),
            }
            for index, row in enumerate(recent_rows)
        ]
        if forecast_price is not None:
            series.append({"time": (base_date + timedelta(days=1)).strftime("%-m/%-d"), "price": round(float(forecast_price), 2)})
        return series

    @classmethod
    def _fallback_result(cls, market_data: MarketData, history_rows: list[dict]) -> BitcoinModelResult:
        trend = "Neutral"
        signal = BitcoinSignal.HOLD

        if market_data.bitcoin_7day_avg > market_data.bitcoin_30day_avg and market_data.bitcoin_daily_change > 0:
            trend = "Bullish"
            signal = BitcoinSignal.BUY
        elif market_data.bitcoin_7day_avg < market_data.bitcoin_30day_avg and market_data.bitcoin_daily_change < 0:
            trend = "Bearish"
            signal = BitcoinSignal.SELL

        confidence = 0.35 if signal is BitcoinSignal.HOLD else 0.55
        current_price = market_data.bitcoin_price
        forecast_change_pct = market_data.bitcoin_daily_change
        forecast_price = current_price * (1 + (forecast_change_pct / 100.0))

        return BitcoinModelResult(
            signal=signal,
            confidence_score=confidence,
            trend=trend,
            reasoning=(
                "TensorFlow is unavailable, so the Bitcoin advisory is using the "
                f"latest market heuristic over {len(history_rows)} historical rows."
            ),
            current_price=current_price,
            forecast_price=forecast_price,
            forecast_change_pct=forecast_change_pct,
            crypto_data=cls._build_crypto_series(history_rows, forecast_price),
            model_source="heuristic_fallback",
        )

    @classmethod
    def generate_model_result(cls, market_data: MarketData) -> BitcoinModelResult:
        """Return a model-driven Bitcoin advisory payload."""
        history_rows = cls.load_training_history()
        if len(history_rows) < 30:
            return cls._fallback_result(market_data, history_rows)

        matrix, scaled, minimums, spans = cls._build_model_inputs(history_rows)
        last_window = scaled[-30:]
        model_input = np.expand_dims(last_window, axis=0)

        try:
            prediction_scaled = cls._predict_with_model(model_input)
            predicted_close_scaled = float(np.asarray(prediction_scaled).reshape(-1)[0])
            predicted_close_scaled = float(np.clip(predicted_close_scaled, 0.0, 1.0))
            predicted_price = cls._inverse_close(predicted_close_scaled, minimums, spans)
            current_price = cls._safe_float(history_rows[-1].get("Close"), market_data.bitcoin_price)
            forecast_change_pct = ((predicted_price - current_price) / current_price) * 100.0 if current_price else 0.0

            if forecast_change_pct >= 2.0:
                signal = BitcoinSignal.BUY
                trend = "Bullish"
            elif forecast_change_pct <= -2.0:
                signal = BitcoinSignal.SELL
                trend = "Bearish"
            else:
                signal = BitcoinSignal.HOLD
                trend = "Neutral"

            confidence = min(0.95, max(0.35, abs(forecast_change_pct) / 10.0))

            return BitcoinModelResult(
                signal=signal,
                confidence_score=confidence,
                trend=trend,
                reasoning=(
                    "btc_model.h5 predicted the next close using the last 30 rows "
                    "of Close/MA/volatility features."
                ),
                current_price=current_price,
                forecast_price=predicted_price,
                forecast_change_pct=forecast_change_pct,
                crypto_data=cls._build_crypto_series(history_rows, predicted_price),
                model_source="btc_model.h5",
            )
        except BitcoinPredictiveModelUnavailable as exc:
            logger.warning("Bitcoin model unavailable, using heuristic fallback: %s", exc)
            return cls._fallback_result(market_data, history_rows)
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.warning("Bitcoin model prediction failed, using heuristic fallback: %s", exc)
            return cls._fallback_result(market_data, history_rows)

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
        model_result = cls.generate_model_result(market_data)
        return BitcoinAnalysis(
            signal=model_result.signal,
            confidence_score=model_result.confidence_score,
            trend=model_result.trend,
            reasoning=model_result.reasoning,
        )

    @classmethod
    def get_prompt_summary(cls, market_data: MarketData) -> dict:
        """Return a compact Bitcoin payload for prompting and downstream reasoning."""
        analysis = cls.analyze_trend(market_data)
        return {
            "bitcoin_signal": analysis.signal.value,
            "bitcoin_confidence": round(float(analysis.confidence_score), 2),
            "bitcoin_trend": analysis.trend,
        }

    @classmethod
    def get_dashboard_payload(cls, market_data: MarketData) -> dict:
        """Return chart data and signal labels for the dashboard API."""
        model_result = cls.generate_model_result(market_data)
        signal_label = f"{model_result.signal.value} Signal Active"
        if model_result.signal is BitcoinSignal.HOLD:
            signal_label = "HOLD Signal Active"
        
        # Create price status message
        price_status = "Live Market Data"
        if market_data.price_source == "predicted":
            price_status = "Predicted Price (Live data currentlyunavailable)"
        
        return {
            "bitcoin_signal": model_result.signal.value,
            "bitcoin_signal_label": signal_label,
            "bitcoin_confidence": round(float(model_result.confidence_score), 2),
            "bitcoin_trend": model_result.trend,
            "forecast_change_pct": round(float(model_result.forecast_change_pct), 2),
            "forecast_price": round(float(model_result.forecast_price), 2),
            "current_price": round(float(model_result.current_price), 2),
            "current_price_myr": round(float(market_data.bitcoin_price_myr), 2),
            "price_source": market_data.price_source,
            "price_status": price_status,
            "crypto_data": model_result.crypto_data,
            "model_source": model_result.model_source,
        }

    @staticmethod
    def calculate_confidence_level(confidence_score: float) -> str:
        """Convert confidence score to readable level."""
        if confidence_score >= CONFIDENCE_THRESHOLDS["high"]:
            return "HIGH"
        if confidence_score >= CONFIDENCE_THRESHOLDS["medium"]:
            return "MEDIUM"
        return "LOW"


PLACEHOLDER_IMPLEMENTATION = False
