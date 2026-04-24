import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

df = pd.read_csv('Cleaned_BitcoinHistory_For_ML.csv')
features = ['Close', '7_Day_MA', '30_Day_MA', 'Daily_Volatility_%']
data = df[features].values

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

def create_sequences(data, seq_length=30):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])
    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data)
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

model = Sequential([
    # First LSTM layer with 50 neurons
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2), # This "shuts off" 20% of neurons to prevent memorization
    
    # Second LSTM layer
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    
    # Output Layers
    Dense(25),
    Dense(1) # The final predicted price
])

model.compile(optimizer='adam', loss='mean_squared_error')

print("Starting training...")
history = model.fit(
    X_train, y_train, 
    batch_size=32, 
    epochs=10, 
    validation_data=(X_test, y_test)
)

model.save('btc_model.h5')
print("Model saved as btc_model.h5")

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Learning Progress')
plt.legend()
plt.show()