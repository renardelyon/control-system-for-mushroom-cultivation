import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from typing import Tuple

from forecasting import Data, TrainPredict, WindowGenerator


def model_train(path: str, OUT_STEPS=20) -> Tuple[object, object]:
    df = pd.read_csv(path)
    df = df.dropna()
    df.drop(columns='Date', inplace=True)

    array_data = df[['Humidity (%)', 'Temp (C)']].to_numpy()

    data = Data(array_data, ['Humidity', 'Temp'])
    data.normalization().split()

    wide_window = WindowGenerator(
        train_df=data.train_df.copy(),
        input_width=100, label_width=OUT_STEPS, shift=OUT_STEPS,
        label_columns=['Temp'])

    train_predict = TrainPredict(wide_window)
    tf.keras.backend.clear_session()
    num_features = data.train_df.shape[-1]
    train_predict.build_model(OUT_STEPS, num_features).compile_and_fit()

    return data, train_predict


def model_predict(data: object, predict: object) -> Tuple[np.ndarray, np.ndarray]:
    data_for_pred = np.expand_dims(data.test_df, axis=0)
    pred = predict.inference(data_for_pred)

    data1 = data.denormalization(data_for_pred)
    data2 = data.denormalization(pred)

    return data1, data2


def plot_data(data1: np.ndarray, data2: np.ndarray):
    data1_length = data1.shape[0]
    data2_length = data2.shape[0]

    data_slice = slice(0, data1_length)
    pred_slice = slice(data1_length, None)

    comb = np.vstack((data1, data2))

    data_indices = np.arange(len(comb))[data_slice]
    pred_indices = np.arange(len(comb))[pred_slice]

    fig, ax = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    for i in range(2):
        ax[i].plot(data_indices, comb[:, i][data_slice],
                   label='Data', marker='.', zorder=-10)
        if i != 0:
            ax[i].scatter(pred_indices, comb[:, 1][pred_slice],
                          marker='X', edgecolors='k', label='Predictions',
                          c='#ff7f0e', s=64)
        ax[i].legend(loc="best")

    for i, (ax_, name) in enumerate(zip(ax.flat, ['Humidity (%)', 'Temperature (C)'])):
        if i == 1:
            ax_.set(xlabel='Time', ylabel=name)
        else:
            ax_.set(ylabel=name)


    plt.show()
