# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12WKa4e0N7b9SHt9PQWBNARQYb4UbXrai
"""

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanAbsoluteError
from tensorflow.keras.callbacks import Callback

# Load the California Housing dataset
housing = fetch_california_housing()
data = pd.DataFrame(housing.data, columns=housing.feature_names)
data['PRICE'] = housing.target

# Display the number of samples in the dataset
num_samples = len(data)
print("Number of samples in the dataset:", num_samples)

# Check if the dataset has at least 1000 samples
if num_samples < 1000:
    raise ValueError("Dataset must have at least 1000 samples.")

# Select features and target variable
features = data.drop('PRICE', axis=1)
target = data['PRICE']

# Use MinMaxScaler to scale the features
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(features_scaled, target, test_size=0.2, random_state=42)

# Reshape the data for LSTM (3D input required)
x_train = x_train.reshape((x_train.shape[0], 1, x_train.shape[1]))
x_test = x_test.reshape((x_test.shape[0], 1, x_test.shape[1]))

# Calculate the threshold for MAE (10% of the scale of data)
scale = np.max(y_train) - np.min(y_train)
threshold_mae = 0.1 * scale
print("Threshold for MAE:", threshold_mae)

# Custom callback to stop training when both MAE and val MAE are below the threshold
class ThresholdCallback(Callback):
    def __init__(self, threshold):
        super(ThresholdCallback, self).__init__()
        self.threshold = threshold

    def on_epoch_end(self, epoch, logs=None):
        if logs.get('mae') < self.threshold and logs.get('val_mae') < self.threshold:
            print(f"\nReached MAE threshold ({self.threshold}). Stopping training.")
            self.model.stop_training = True

# Build the LSTM model
model = Sequential([
    LSTM(50, input_shape=(x_train.shape[1], x_train.shape[2])),
    Dense(1)
])

# Compile the model with specified learning rate and loss function
optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss=MeanAbsoluteError(), metrics=['mae'])

# Train the model with the custom callback
history = model.fit(x_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=2, callbacks=[ThresholdCallback(threshold_mae)])

# Evaluate the model
test_loss, test_mae = model.evaluate(x_test, y_test, verbose=0)

# Calculate Mean Absolute Error (MAE) in percentage of the scale of the data
mae_percentage = test_mae / scale * 100

print(f'Mean Absolute Error (MAE) on Test Set: {mae_percentage:.2f}% of the scale of the data')