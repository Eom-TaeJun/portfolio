import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, SimpleRNN, LayerNormalization, MultiHeadAttention, Dropout, Add, Flatten

# Load the data
df = pd.read_csv('fed_funds_rate.csv', index_col='observation_date', parse_dates=True)
df = df.dropna()

# Prepare the data for machine learning
df['target'] = df['FEDFUNDS'].shift(-1)
df = df.dropna()

# Create lagged features
for i in range(1, 13):
    df[f'lag_{i}'] = df['FEDFUNDS'].shift(i)

df = df.dropna()

X = df.drop(['FEDFUNDS', 'target'], axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Reshape data for deep learning models
X_train_3d = X_train.values.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test_3d = X_test.values.reshape((X_test.shape[0], X_test.shape[1], 1))

# --- Simple RNN ---
print("--- Simple RNN ---")
model_rnn = Sequential([
    SimpleRNN(50, activation='relu', input_shape=(X_train_3d.shape[1], X_train_3d.shape[2])),
    Dense(1)
])
model_rnn.compile(optimizer='adam', loss='mse')
model_rnn.fit(X_train_3d, y_train, epochs=50, verbose=0)
predictions_rnn = model_rnn.predict(X_test_3d)
mse_rnn = mean_squared_error(y_test, predictions_rnn)
print(f"Simple RNN Mean Squared Error: {mse_rnn}")

# --- LSTM ---
print("\n--- LSTM ---")
model_lstm = Sequential([
    LSTM(50, activation='relu', input_shape=(X_train_3d.shape[1], X_train_3d.shape[2])),
    Dense(1)
])
model_lstm.compile(optimizer='adam', loss='mse')
model_lstm.fit(X_train_3d, y_train, epochs=50, verbose=0)
predictions_lstm = model_lstm.predict(X_test_3d)
mse_lstm = mean_squared_error(y_test, predictions_lstm)
print(f"LSTM Mean Squared Error: {mse_lstm}")

# --- Transformer ---
print("\n--- Transformer ---")

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Attention and Normalization
    x = LayerNormalization(epsilon=1e-6)(inputs)
    x = MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = Dropout(dropout)(x)
    res = Add()([x, inputs])

    # Feed Forward Part
    x = LayerNormalization(epsilon=1e-6)(res)
    x = Dense(ff_dim, activation="relu")(x)
    x = Dropout(dropout)(x)
    x = Dense(inputs.shape[-1])(x)
    return Add()([x, res])


def build_transformer_model(
    input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout=0, mlp_dropout=0
):
    inputs = keras.Input(shape=input_shape)
    x = inputs
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)

    x = Flatten()(x)
    for dim in mlp_units:
        x = Dense(dim, activation="relu")(x)
        x = Dropout(mlp_dropout)(x)
    outputs = Dense(1)(x)
    return keras.Model(inputs, outputs)


input_shape = (X_train_3d.shape[1], X_train_3d.shape[2])

model_transformer = build_transformer_model(
    input_shape,
    head_size=256,
    num_heads=4,
    ff_dim=4,
    num_transformer_blocks=4,
    mlp_units=[128],
    mlp_dropout=0.4,
    dropout=0.25,
)

model_transformer.compile(
    loss="mean_squared_error",
    optimizer=keras.optimizers.Adam(learning_rate=1e-4)
)

model_transformer.fit(X_train_3d, y_train, epochs=50, verbose=0)

predictions_transformer = model_transformer.predict(X_test_3d)
mse_transformer = mean_squared_error(y_test, predictions_transformer)
print(f"Transformer Mean Squared Error: {mse_transformer}")


print("\n--- Model Comparison ---")
print(f"ARIMA MSE: 5.41")
print(f"Random Forest with PCA MSE: 0.32")
print(f"Simple RNN MSE: {mse_rnn}")
print(f"LSTM MSE: {mse_lstm}")
print(f"Transformer MSE: {mse_transformer}")