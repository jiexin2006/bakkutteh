import json

class IntelligenceArchitectEngine:
    """
    Z.AI Narrative Engine: Translates backend allocations and market data 
    into a structured JSON response for the Z.AI interface.
    """

    def __init__(self, fd_data_path="FD_rates&EPF_dividend.json"):
        # Load the market context (Bank FD rates and EPF dividend)
        with open(fd_data_path, 'r') as f:
            self.market_context = json.load(f)
        
        self.fd_list = self.market_context.get("fixed_deposits", [])
        self.epf_dividend = self.market_context.get("epf_dividend_rate_pct", 5.4)

    def generate_explanation(self, allocation_json, epf_analysis_json, market_signals, user_profile):
        """
        Processes the raw JSON output from the EPFAnalysisCalculator and Allocation logic.
        """
        # 1. Extract context from the EPF-Calculator.py output
        status = epf_analysis_json.get("status")
        priority = epf_analysis_json.get("priority_level")
        deficit_pct = epf_analysis_json.get("deficit_percentage")
        age = epf_analysis_json.get("age")
        
        # 2. Extract profile and allocation data
        surplus = user_profile.get("current_surplus_rm", 0)
        epf_p = allocation_json.get("epf_percent", 0)
        fd_p = allocation_json.get("fd_percent", 0)
        crypto_p = allocation_json.get("crypto_percent", 0)
        
        # 3. Handle Zero/Negative Surplus (Recovery Mode)
        if surplus <= 0:
            return self._generate_recovery_json(user_profile)

        narrative_parts = []
        
        # --- RULE: EPF REASONING (The Anchor) ---
        if status == "Behind":
            narrative_parts.append(
                f"Your plan allocates {epf_p}% of your surplus to EPF top-ups. This is a strategic "
                f"choice to address your {deficit_pct}% retirement deficit for your age {age} "
                f"benchmark using the guaranteed {self.epf_dividend}% dividend."
            )
        else:
            narrative_parts.append(
                f"With your retirement targets on track for age {age}, we've set a {epf_p}% "
                "EPF maintenance weighting, allowing you to focus more on growth and liquidity."
            )

        # --- RULE: FD VS. CASH ON HAND (The Threshold Rule) ---
        eligible_fds = [fd for fd in self.fd_list if surplus >= fd["min_placement_rm"]]
        
        if eligible_fds:
            best_fd = max(eligible_fds, key=lambda x: x["interest_rate_pct"])
            narrative_parts.append(
                f"To protect your principal, {fd_p}% is directed to {best_fd['bank_name']}. "
                f"At {best_fd['interest_rate_pct']}%, it offers the best 'lock-in' value for your "
                f"current RM {surplus} surplus."
            )
        else:
            # Pivot logic for surplus below bank minimums
            min_req = min(fd["min_placement_rm"] for fd in self.fd_list)
            narrative_parts.append(
                f"Fixed Deposits currently require a minimum placement starting at RM {min_req}. "
                f"Because your surplus is RM {surplus}, we've redistributed that {fd_p}% allocation "
                "into your 'Cash on Hand' reserve to maintain total liquidity."
            )

        # --- RULE: SAFETY BRAKE (Market Signal vs. Personal Safety) ---
        btc_sig = market_signals.get("bitcoin_signal", "HOLD")
        if btc_sig == "Bullish" and priority in ["Critical", "High"]:
            narrative_parts.append(
                f"Risk Alert: While crypto signals are Bullish, our safety engine has enforced a 0% cap. "
                f"Your '{priority}' priority gap must be reduced before high-risk assets are unlocked."
            )
        elif crypto_p > 0:
            narrative_parts.append(
                f"A tactical {crypto_p}% has been allocated to digital assets to capture "
                "upward market momentum within your established risk limits."
            )

        # Return structured JSON-ready dictionary
        return {
            "status": "success",
            "display_data": {
                "reasoning_text": " ".join(narrative_parts),
                "safety_priority": priority,
                "recommended_action": self._get_action(status),
                "allocation_breakdown": allocation_json
            }
        }

    def _get_action(self, status):
        """Helper to suggest the next physical step."""
        if status == "Behind":
            return "Enable EPF Self-Contribution via the i-Akaun portal."
        return "Review high-yield liquidity options and market trends."

    def _generate_recovery_json(self, user_profile):
        """Standardized response for financial distress scenarios."""
        return {
            "status": "recovery_mode",
            "display_data": {
                "reasoning_text": "Expenses currently exceed income. Focus on a liability audit.",
                "safety_priority": "Critical",
                "recommended_action": "Pause all investments and re-evaluate monthly subscriptions.",
                "allocation_breakdown": {"cash_on_hand": 100}
            }
        }