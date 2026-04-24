class DataManager:
    @staticmethod
    def get_ranked_fd_rates():
        # Comprehensive list of 12 banks, ranked by interest rate (descending)
        rates = [
            ("Hong Leong", 3.20, "15 Months"), ("RHB", 3.15, "15 Months"),
            ("CIMB", 3.10, "12 Months"), ("Affin", 3.10, "12 Months"),
            ("AmBank", 3.05, "12 Months"), ("Maybank", 3.00, "12 Months"),
            ("Bank Islam", 3.00, "12 Months"), ("UOB", 2.95, "12 Months"),
            ("Public Bank", 2.90, "12 Months"), ("HSBC", 2.85, "12 Months"),
            ("Agrobank", 2.80, "12 Months"), ("Bank Rakyat", 2.75, "12 Months")
        ]
        return sorted(rates, key=lambda x: x[1], reverse=True)

    @staticmethod
    def get_bitcoin_chart_data():
        return [89000, 91000, 90500, 92000, 94000, 93000, 95000]

    @staticmethod
    def get_bitcoin_signal():
        # Green = Buy, Red = Sell, Yellow = Hold
        return ("BUY", "#28a745") 

    @staticmethod
    def calculate_advice(data):
        try:
            income, expenses = float(data.get("Monthly Income", 0)), float(data.get("Monthly Expenses", 0))
            surplus = income - expenses
            
            if surplus < 500:
                return f"Liquidity Strategy: Your surplus is RM{surplus:.2f}. Keep this in a 'Savings' account for full liquidity until you reach the RM500 minimum for a Fixed Deposit."
            
            # Allocation math
            fd, epf_a, btc = surplus * 0.40, surplus * 0.10, surplus * 0.05
            return (f"Allocation Plan based on your surplus of RM{surplus:.2f}:\n\n"
                    f"• Fixed Deposit (40%): RM{fd:.2f} (Stability)\n"
                    f"• EPF Contribution (10%): RM{epf_a:.2f} (Retirement)\n"
                    f"• Bitcoin (5%): RM{btc:.2f} (Growth)\n\n"
                    f"Market Action: Purchase RM{btc:.2f} worth of Bitcoin today.")
        except:
            return "Please complete the setup profile first."