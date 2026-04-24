import json
import os

class DataManager:
    @staticmethod
    def get_fd_rates():
        # Sorted by best ROI
        return [("Hong Leong", "3.20%", "15 Months"), ("Maybank", "3.00%", "12 Months")]

    @staticmethod
    def get_bitcoin_data():
        try:
            path = os.path.join('data', 'Bitcoin_ContextHistory_For_ZAI.json')
            with open(path, 'r') as file:
                data = json.load(file)
            return [e['Close'] for e in data[-10:]]
        except:
            return [89000, 89500, 89200, 90000] # Fallback data

    @staticmethod
    def get_ai_advice():
        return "AI Analysis: Based on your surplus, we recommend a balanced allocation.\nFD provides stability for your safety net, while the 5% Bitcoin allocation captures growth trends."