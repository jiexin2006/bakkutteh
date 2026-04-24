import json
import os

class DataManager:
    @staticmethod
    def get_fd_rates():
        return [("Hong Leong", "3.20%", "15 Months"), ("Maybank", "3.00%", "12 Months")]

    @staticmethod
    def get_bitcoin_data():
        return [89000, 91000, 90500, 92000] 

    @staticmethod
    def get_ai_advice(income, expenses, epf_balance, tier):
        surplus = float(income) - float(expenses)
        
        if surplus < 500:
            return ("Your monthly surplus is below RM500. We suggest parking this in a 'Savings' account. "
                    "This keeps your money safe and accessible while you build up to the RM500 minimum needed for a Fixed Deposit.")
        
        elif float(epf_balance) < 20000:
            return ("Prioritize EPF: Your current balance is below the safety threshold for your tier. "
                    "Adding to your EPF ensures long-term retirement security.")
        
        else:
            return (f"Strategy for '{tier}' tier:\n\n"
                    "• 40% Fixed Deposit (Stability)\n"
                    "• 10% EPF (Retirement)\n"
                    "• 5% Bitcoin (Growth)\n\n"
                    "We recommend this balance because your surplus is healthy and your EPF is on track.")