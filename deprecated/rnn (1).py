# -*- coding: utf-8 -*-
"""RNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YOH7QD0VgbUTqfg3dWCQHCsFPLYyrLD4
"""

import numpy as np

# Simulation parameters
N = 8  # Number of particles
timesteps = 1500  # Number of simulation time steps
dt = 1e-1  # Timestep
alpha = 0.5  # cubic coupling
beta = 0.1  # quartic coupling

# Add costom module to temporary drive
!cp "/content/drive/MyDrive/Colab Notebooks/simulation.py" "/content/simulation.py"

import simulation

qs, ps = simulation.integration(N, timesteps, dt, alpha, beta)

qs_mean = np.mean(qs)
qs_std = np.std(qs)

def preprocess(X):
  X = (X - qs_mean) / qs_std
  return X

def postprocess(X):
  X = X * qs_std + qs_mean
  return X

preprocess(qs);

window_size = 5
X, y = simulation.make_sequences(qs, window_size)

from sklearn.model_selection import train_test_split

train_size = 0.55
val_size = 0.15
test_size = 0.3

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=val_size, shuffle=False)
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=test_size/(1-val_size), shuffle=False)

from tensorflow import keras
from keras.models import Sequential
from keras.layers import InputLayer, LSTM, Dropout, Dense, SimpleRNN, GRU
from keras.callbacks import ModelCheckpoint
from keras.losses import MeanSquaredError
from keras.metrics import RootMeanSquaredError
from keras.optimizers import Adam
# from keras.backend import set_floatx

# set_floatx('float64')

model = Sequential()
model.add(InputLayer((window_size, N)))
model.add(GRU(10, activation="tanh"))
# model.add(Dropout(0.01))
model.add(Dense(N))

model.summary()

# cp = ModelCheckpoint('model/', save_best_only=True)
model.compile(loss="mse", optimizer=Adam(learning_rate=0.01), metrics=[RootMeanSquaredError()])

epochs = 30
batchsize = 40

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=batchsize, verbose = 0)

# from tensorflow.keras.models import load_model
# model = load_model('model/')

test_pred = np.copy(X_test[0])

for k in range(len(X_test)-window_size):
    pred = model.predict(test_pred[np.newaxis, -window_size:], verbose=0)
    test_pred = np.concatenate((test_pred, pred), axis = 0)

test_pred = postprocess(test_pred)
qs = postprocess(qs)

import matplotlib.pyplot as plt

for particles in range(N):
    plt.plot(qs[- X_test.shape[0]:, particles], color="tab:blue")
    plt.plot(test_pred[:, particles], color="tab:orange")

    # Set labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title("lstm")
    plt.ylim(-1, 1)

    # Show the plot
    plt.show()
