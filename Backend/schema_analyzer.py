from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any

from Backend.epf_calculator import EPFCalculator
from Backend.models import UserProfile


class SchemaValidationError(ValueError):
    """Raised when request payload validation fails."""


@dataclass
class ValidationIssue:
    """Single validation issue in schema error response format."""

    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "message": self.message}


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SCHEMA_PATH = DATA_DIR / "user-input-schema.json"


def _load_input_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
    with SCHEMA_PATH.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


USER_INPUT_SCHEMA = _load_input_schema()
REQUIRED_FIELDS: list[str] = USER_INPUT_SCHEMA.get("required_fields", [])


def _is_number(value: Any) -> bool:
    # bool is a subclass of int, so explicitly reject it.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_required_fields(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in payload or payload[field] is None:
            issues.append(ValidationIssue(field=field, message=f"{field} is required"))


def _validate_types(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    if "user_id" in payload and not isinstance(payload["user_id"], str):
        issues.append(ValidationIssue(field="user_id", message="user_id must be a string"))

    if "age" in payload and not _is_integer(payload["age"]):
        issues.append(ValidationIssue(field="age", message="age must be an integer"))

    for field in ["monthly_salary_rm", "fixed_liabilities_rm", "current_epf_balance_rm"]:
        if field in payload and not _is_number(payload[field]):
            issues.append(ValidationIssue(field=field, message=f"{field} must be a number"))

    if "target_retirement_tier" in payload and not isinstance(payload["target_retirement_tier"], str):
        issues.append(
            ValidationIssue(
                field="target_retirement_tier",
                message="target_retirement_tier must be a string",
            )
        )

    if "risk_appetite" in payload and not isinstance(payload["risk_appetite"], str):
        issues.append(ValidationIssue(field="risk_appetite", message="risk_appetite must be a string"))


def _validate_ranges_and_enums(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    age = payload.get("age")
    if _is_integer(age) and not (18 <= age <= 70):
        issues.append(ValidationIssue(field="age", message="age must be between 18 and 70"))

    salary = payload.get("monthly_salary_rm")
    if _is_number(salary) and float(salary) <= 0:
        issues.append(
            ValidationIssue(field="monthly_salary_rm", message="Monthly salary must be greater than 0 RM")
        )

    liabilities = payload.get("fixed_liabilities_rm")
    if _is_number(liabilities) and float(liabilities) < 0:
        issues.append(
            ValidationIssue(field="fixed_liabilities_rm", message="Fixed liabilities must be 0 or greater RM")
        )

    epf_balance = payload.get("current_epf_balance_rm")
    if _is_number(epf_balance) and float(epf_balance) < 0:
        issues.append(
            ValidationIssue(
                field="current_epf_balance_rm",
                message="Current EPF balance must be 0 or greater RM",
            )
        )

    valid_tiers = {"Basic", "Adequate", "Enhanced"}
    tier = payload.get("target_retirement_tier")
    if isinstance(tier, str) and tier not in valid_tiers:
        issues.append(
            ValidationIssue(
                field="target_retirement_tier",
                message="target_retirement_tier must be one of: Basic, Adequate, Enhanced",
            )
        )

    valid_risk = {"High", "Medium", "Low"}
    risk = payload.get("risk_appetite")
    if isinstance(risk, str) and risk not in valid_risk:
        issues.append(
            ValidationIssue(
                field="risk_appetite",
                message="risk_appetite must be one of: High, Medium, Low",
            )
        )


def _validate_business_rules(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    salary = payload.get("monthly_salary_rm")
    liabilities = payload.get("fixed_liabilities_rm")

    if not _is_number(salary) or not _is_number(liabilities):
        return

    monthly_surplus = float(salary) - float(liabilities)
    if monthly_surplus < 0:
        issues.append(
            ValidationIssue(
                field="fixed_liabilities_rm",
                message=(
                    f"Fixed liabilities (RM {float(liabilities):.2f}) exceed monthly salary "
                    f"(RM {float(salary):.2f}). You have no surplus to invest. "
                    "Please reduce expenses first."
                ),
            )
        )


def validate_payload(payload: dict[str, Any]) -> list[ValidationIssue]:
    """Validate request payload using schema requirements.

    Returns a list of issues. Empty list means valid payload.
    """
    issues: list[ValidationIssue] = []
    _validate_required_fields(payload, issues)
    _validate_types(payload, issues)
    _validate_ranges_and_enums(payload, issues)
    _validate_business_rules(payload, issues)
    return issues


def build_error_response(issues: list[ValidationIssue]) -> dict[str, Any]:
    return {
        "status": 400,
        "error": {
            "message": "Validation failed",
            "errors": [issue.to_dict() for issue in issues],
        },
    }


def _risk_to_profile(risk_appetite: str) -> str:
    mapping = {
        "High": "Aggressive",
        "Medium": "Moderate",
        "Low": "Conservative",
    }
    return mapping[risk_appetite]


def analyze_user_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Analyze payload according to data/user-input-schema.json contract.

    Response shape is API-friendly and includes validation errors as status 400,
    otherwise status 200 with EPF analysis metrics.
    """
    issues = validate_payload(payload)
    if issues:
        return build_error_response(issues)

    age = int(payload["age"])
    monthly_salary_rm = float(payload["monthly_salary_rm"])
    fixed_liabilities_rm = float(payload["fixed_liabilities_rm"])
    current_epf_balance_rm = float(payload["current_epf_balance_rm"])
    target_retirement_tier = str(payload["target_retirement_tier"])
    risk_appetite = str(payload["risk_appetite"])

    monthly_surplus_rm = monthly_salary_rm - fixed_liabilities_rm
    target_epf_level = EPFCalculator.normalize_target_tier(target_retirement_tier)

    user_profile = UserProfile(
        age=age,
        monthly_salary=monthly_salary_rm,
        monthly_expenditure=0.0,
        current_epf_balance=current_epf_balance_rm,
        fixed_liabilities=fixed_liabilities_rm,
        risk_appetite=_risk_to_profile(risk_appetite),
    )

    epf_report = EPFCalculator.generate_epf_report(
        user_profile=user_profile,
        target_retirement_tier=target_retirement_tier,
    )
    surplus_parking = EPFCalculator.recommend_surplus_parking(
        monthly_surplus_rm=monthly_surplus_rm,
        deficit_percentage=float(epf_report["deficit_percentage"]),
    )

    return {
        "status": 200,
        "data": {
            "user_id": payload["user_id"],
            "age": age,
            "monthly_salary_rm": monthly_salary_rm,
            "fixed_liabilities_rm": fixed_liabilities_rm,
            "current_epf_balance_rm": current_epf_balance_rm,
            "target_retirement_tier": target_retirement_tier,
            "target_epf_level": target_epf_level,
            "risk_appetite": risk_appetite,
            "monthly_surplus_rm": monthly_surplus_rm,
            "epf_analysis": {
                "basic_target_rm": epf_report["basic_target_rm"],
                "adequate_target_rm": epf_report["adequate_target_rm"],
                "enhanced_target_rm": epf_report["enhanced_target_rm"],
                "selected_target_rm": epf_report["selected_target_rm"],
                "deficit_rm": epf_report["deficit_rm"],
                "deficit_percentage": epf_report["deficit_percentage"],
                "status": epf_report["status"],
                "priority_level": epf_report["priority_level"],
                "status_enum": epf_report["status_enum"],
            },
            "surplus_parking_strategy": {
                "strategy": surplus_parking["strategy"],
                "fd_eligible": surplus_parking["fd_eligible"],
                "bitcoin_eligible": surplus_parking["bitcoin_eligible"],
                "epf_amount_rm": surplus_parking["epf_amount_rm"],
                "savings_amount_rm": surplus_parking["savings_amount_rm"],
                "reason": surplus_parking["reason"],
                "risk_note": surplus_parking["risk_note"],
            },
        },
    }


def parse_and_analyze_json(request_body: str) -> dict[str, Any]:
    """Helper for API handlers that receive raw JSON body text."""
    try:
        payload = json.loads(request_body)
    except json.JSONDecodeError:
        return {
            "status": 400,
            "error": {
                "message": "Validation failed",
                "errors": [{"field": "body", "message": "Request body must be valid JSON"}],
            },
        }

    if not isinstance(payload, dict):
        return {
            "status": 400,
            "error": {
                "message": "Validation failed",
                "errors": [{"field": "body", "message": "Request body must be a JSON object"}],
            },
        }

    return analyze_user_payload(payload)
