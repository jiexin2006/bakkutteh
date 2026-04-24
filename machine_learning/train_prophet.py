import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

df = pd.read_csv('Cleaned_BitcoinHistory_For_ML.csv')
prophet_df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

m = Prophet(daily_seasonality=True)
m.fit(prophet_df)

future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)

fig1 = m.plot(forecast)

plt.show() 
fig1.savefig('btc_prophet_forecast.png')
print("Forecast image saved!")