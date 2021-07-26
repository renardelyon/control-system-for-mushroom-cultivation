
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.preprocessing import StandardScaler


class Data:
    def __init__(self, data, features):
        self.features = features
        self.scaler = StandardScaler()
        self.df = pd.DataFrame(data=data, columns=features)
        self.train_df = pd.DataFrame(columns=features)
        self.test_df = pd.DataFrame(columns=features)

    def normalization(self):
        self.scaler.fit(self.df.loc[:, self.features])
        self.df.loc[:, self.features] = self.scaler.transform(
            self.df.loc[:, self.features])
        print('Data has been normalized')
        return self

    def split(self):
        # length of df
        n = len(self.df)

        # split train and test data
        self.train_df = self.df[0:int(n * 0.8)]
        self.test_df = self.df[int(n * 0.8):]

        print('Data has been splitted')
        return None

    def denormalization(self, x):
        """ x is data that wanted to be denormalized"""
        inversed = self.scaler.inverse_transform(x)
        inversed = np.squeeze(inversed)

        return inversed


class WindowGenerator:
    def __init__(self, input_width, label_width, shift,
                 train_df, label_columns=None):
        self.train_df = train_df

        self.label_columns = label_columns
        if label_columns is not None:
            self.label_columns_indices = {name: i for i, name in
                                          enumerate(label_columns)}
        self.columns_indices = {name: i for i, name in
                                enumerate(train_df.columns)}
        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift

        self.total_windows_size = input_width + shift
        self.label_start = self.total_windows_size - self.label_width

        self.data = []

    def split_window(self, features):
        inputs = features[:, :self.input_width, :]
        labels = features[:, self.label_start:, :]
        if self.label_columns is not None:
            labels = tf.stack([labels[:, :, self.columns_indices[name]]
                               for name in self.label_columns], axis=-1)

        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])

        return inputs, labels

    def make_dataset(self, data):
        data = np.array(data, dtype=np.float32)
        ds = tf.keras.preprocessing.timeseries_dataset_from_array(
            data=data,
            targets=None,
            sequence_length=self.total_windows_size,
            sequence_stride=1,
            shuffle=True,
            batch_size=32, )

        ds = ds.map(self.split_window)

        return ds

    @property
    def train(self):
        return self.make_dataset(self.train_df)

    def __repr__(self):
        return '\n'.join([
            f'Total window size: {self.total_windows_size}',
            f'Label column name(s): {self.label_columns}'])


class TrainPredict:
    def __init__(self, window, EPOCHS=20):
        self.model = None
        self.EPOCHS = EPOCHS
        self.window = window

    def build_model(self, OUT_STEPS, num_features):
        self.model = tf.keras.Sequential([
            tf.keras.layers.LSTM(32, return_sequences=False),
            # Shape => [batch, out_steps*features]
            tf.keras.layers.Dense(OUT_STEPS * num_features,
                                  kernel_initializer=tf.initializers.zeros()),
            # Shape => [batch, out_steps, features]
            tf.keras.layers.Reshape([OUT_STEPS, num_features])])

        return self

    def compile_and_fit(self, patience=4):
        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss',
                                                          patience=patience,
                                                          mode='min')

        self.model.compile(loss=tf.losses.MeanSquaredError(),
                           optimizer=tf.optimizers.Adam(),
                           metrics=[tf.metrics.MeanAbsoluteError()])

        history = self.model.fit(self.window.train, epochs=self.EPOCHS,
                                 callbacks=[early_stopping])
        return history

    def inference(self, X):
        pred = self.model.predict(X)
        return pred
