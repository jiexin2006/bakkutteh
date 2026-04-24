import json

class IntelligenceArchitectEngine:
    """
    Z.AI Narrative Engine: Translates backend allocations and market data 
    into contextual, user-friendly financial justifications.
    """

    def __init__(self, fd_data_path="FD_rates&EPF_dividend.json"):
        with open(fd_data_path, 'r') as f:
            self.market_context = json.load(f)
        
        self.fd_list = self.market_context.get("fixed_deposits", [])
        self.epf_dividend = self.market_context.get("epf_dividend_rate_pct", 5.4)

    def generate_explanation(self, allocation, epf_analysis, market_signals, user_profile):
        """
        Synthesizes math into narrative. Focuses on the 'Why' behind percentages.
        """
        surplus = user_profile.get("current_surplus_rm", 0)
        age = user_profile.get("age")
        status = epf_analysis.get("status")
        priority = epf_analysis.get("priority_level")
        
        # 1. SAFETY CHECK: Zero/Negative Surplus
        if surplus <= 0:
            return self._generate_recovery_text(user_profile)

        narrative = []

        # 2. LOGIC: EPF ALLOCATION (The Retirement Anchor)
        epf_p = allocation.get("epf_percent", 0)
        if status == "Behind":
            narrative.append(
                f"We have weighted {epf_p}% of your surplus toward EPF top-ups. At a {self.epf_dividend}% "
                f"dividend, this is the most mathematically efficient way to close the gap for your "
                f"age {age} benchmark without taking on unnecessary market risk."
            )
        else:
            narrative.append(
                f"Your retirement foundation is currently on track. We've set a {epf_p}% maintenance "
                "allocation for EPF, allowing the remaining surplus to work harder in more liquid "
                "or growth-oriented categories."
            )

        # 3. LOGIC: STABILITY VS. CASH ON HAND (The Threshold Rule)
        fd_p = allocation.get("fd_percent", 0)
        eligible_fds = [fd for fd in self.fd_list if surplus >= fd["min_placement_rm"]]
        
        if eligible_fds:
            best_fd = max(eligible_fds, key=lambda x: x["interest_rate_pct"])
            narrative.append(
                f"For capital protection, {fd_p}% is allocated to {best_fd['bank_name']}. "
                f"Their {best_fd['interest_rate_pct']}% rate offers the best 'lock-in' value "
                f"for a monthly surplus of RM {surplus}."
            )
        else:
            min_req = min(fd["min_placement_rm"] for fd in self.fd_list)
            narrative.append(
                f"While {fd_p}% was targeted for Fixed Deposits, current bank minimums start at RM {min_req}. "
                f"Since your surplus is RM {surplus}, we've redistributed these funds into your 'Cash on Hand' "
                "reserve. This keeps your capital liquid and ready for deployment once your balance grows."
            )

        # 4. LOGIC: RISK BRAKE (Market Signal vs. Personal Safety)
        crypto_p = allocation.get("crypto_percent", 0)
        btc_sig = market_signals.get("bitcoin_signal", "HOLD")
        confidence = market_signals.get("bitcoin_confidence", 0)

        if btc_sig == "Bullish" and priority in ["Critical", "High"]:
            narrative.append(
                "Note: Bitcoin signals are positive, but our 'Safety Brake' has capped crypto at 0%. "
                f"With a '{priority}' priority for your retirement gap, we cannot justify high-risk "
                "volatility until your baseline is secured."
            )
        elif crypto_p > 0:
            confidence_note = "with high confidence" if confidence > 0.7 else "as a tactical experiment"
            narrative.append(
                f"We've allocated a controlled {crypto_p}% to digital assets {confidence_note} to "
                "capture market momentum, while staying strictly within your risk-appetite limits."
            )

        return " ".join(narrative)

    def _generate_recovery_text(self, user_profile):
        gap = user_profile.get('fixed_liabilities_rm', 0) - user_profile.get('monthly_salary_rm', 0)
        if gap > 0:
            return (f"Your expenses currently exceed income by RM {gap}. Our immediate focus is a "
                    "liability audit to restore positive cash flow. Investment tiers will unlock "
                    "once a monthly surplus is generated.")
        return ("Your budget is currently at a break-even point. We recommend prioritizing a "
                "liquid 'Cash on Hand' buffer of at least RM 1,000 before committing to locked assets.")