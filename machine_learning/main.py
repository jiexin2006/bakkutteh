import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from advisor_logic import final_advisor_logic
#USER SAFETY CHECK
user_age = 25
user_current_epf = 15000  # Example balance
# EPF 2026 Basic Savings Target for age 25 is RM 11,000
epf_target = 11000 

user_status = "On Track" if user_current_epf >= epf_target else "Behind"

df = pd.read_csv('Cleaned_BitcoinHistory_For_ML.csv')
model = load_model('btc_model.h5') 

features = ['Close', '7_Day_MA', '30_Day_MA', 'Daily_Volatility_%']
last_30_days = df[features].tail(30).values

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(df[features].values) 
last_30_scaled = scaler.transform(last_30_days)
last_30_scaled = np.expand_dims(last_30_scaled, axis=0) 

# Predict tomorrow's price
prediction_scaled = model.predict(last_30_scaled)
current_price = df['Close'].iloc[-1]
predicted_price = scaler.inverse_transform([[prediction_scaled[0][0], 0, 0, 0]])[0][0]
ml_change = (predicted_price - current_price) / current_price

recommendation = final_advisor_logic(ml_change, user_status)

print("-" * 30)
print("AI FINANCIAL INTELLIGENCE ADVISOR")
print("-" * 30)
print(f"User Status: {user_status} (Balance: RM{user_current_epf})")
print(f"AI Market Forecast: {ml_change*100:.2f}% change predicted.")
print(f"CONCLUSION: {recommendation}")
print("-" * 30)