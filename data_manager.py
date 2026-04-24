class DataManager:
    @staticmethod
    def get_fd_rates():
        return [
            ("Hong Leong", "3.20%", "15 Months"), ("RHB", "3.15%", "15 Months"),
            ("CIMB", "3.10%", "12 Months"), ("Affin", "3.10%", "12 Months"),
            ("AmBank", "3.05%", "12 Months"), ("Maybank", "3.00%", "12 Months"),
            ("Bank Islam", "3.00%", "12 Months"), ("UOB", "2.95%", "12 Months"),
            ("Public Bank", "2.90%", "12 Months"), ("HSBC", "2.85%", "12 Months")
        ]

    @staticmethod
    def get_bitcoin_chart_data():
        return [89000, 91000, 90500, 92000, 94000, 93000, 95000]

    @staticmethod
    def get_bitcoin_signal():
        return ("BUY", "#28a745") # Traffic light logic: #28a745 (Green)

    @staticmethod
    def get_ai_advice(income, expenses, epf_balance, tier):
        surplus = float(income) - float(expenses)
        if surplus < 500:
            return ("Savings Strategy: Your surplus is under RM500. Keeping this in a 'Savings' account is best. "
                    "It remains fully liquid and safe, giving you a buffer until you reach the RM500 minimum for Fixed Deposit.")
        elif float(epf_balance) < 20000:
            return ("EPF Focus: Your retirement fund is below the recommended safety threshold. "
                    "Prioritizing EPF contributions ensures your long-term security matches your chosen " + tier + " tier.")
        else:
            return (f"Growth Strategy ({tier} Tier): You are in a strong position! We recommend:\n"
                    "• 40% Fixed Deposit (Stability)\n"
                    "• 10% EPF (Retirement)\n"
                    "• 5% Bitcoin (Growth Potential)")