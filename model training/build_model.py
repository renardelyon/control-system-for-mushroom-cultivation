import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from tensorflow.keras import layers
from tensorflow.keras.regularizers import L2
from tensorflow.keras.losses import SparseCategoricalCrossentropy


class DataModelProcessing:
    def __init__(self, csv_path,
                 feature_names=None,
                 label_names=None):
        if feature_names is None:
            feature_names = ['Temperature', 'Humidity']
        if label_names is None:
            label_names = ['Fan', 'Humidifier']
        self.csv_path = csv_path
        self.feature_names = feature_names
        self.label_names = label_names
        self.train_features = {}
        self.train_labels = {}
        self.val_features = {}
        self.val_labels = {}
        self.feature_layers = None
        self.model = None

    def split_data(self, val_size=0.1, test_size=0.5):
        df = pd.read_csv(self.csv_path, delimiter=';')
        train, val = train_test_split(df, test_size=val_size)
        val, test = train_test_split(df, test_size=test_size)
        return train, val, test

    def feature_label(self, train, val):
        self.train_features = {name: np.array(value) for name, value in train.items()}
        self.train_labels = {name: self.train_features.pop(name) for name in self.label_names}

        self.val_features = {name: np.array(value) for name, value in val.items()}
        self.val_labels = {name: self.val_features.pop(name) for name in self.label_names}

        return "feature and label for training has been created"

    def create_feature_layers(self):
        feature_columns = [tf.feature_column.numeric_column(name,
                                                            normalizer_fn=lambda x: (x - self.train_features[
                                                                name].mean()) /
                                                            self.train_features[name].std())
                           for name in self.feature_names]

        self.feature_layers = layers.DenseFeatures(feature_columns)
        return 'feature layers had been created'

    def train_model(self, epochs):
        inputs = {name: tf.keras.Input(shape=(1,), name=name)
                  for name in self.feature_names}
        x = self.feature_layers(inputs)
        x = layers.Dense(64, activation='relu', kernel_regularizer=L2(0.1))(x)
        x = layers.Dense(32, activation='relu')(x)

        fan_preds = layers.Dense(2, activation='softmax', name='Fan')(x)
        humidifier_preds = layers.Dense(2, activation='softmax', name='Humidifier')(x)
        self.model = tf.keras.Model(dict(inputs), [fan_preds, humidifier_preds])

        callbacks = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10, verbose=1)

        self.model.compile(optimizer='adam',
                           loss={
                               'Fan': SparseCategoricalCrossentropy(),
                               'Humidifier': SparseCategoricalCrossentropy()
                           },
                           metrics=['accuracy'])
        history = self.model.fit(x=self.train_features, y=self.train_labels,
                                 validation_data=(self.val_features, self.val_labels),
                                 epochs=epochs, batch_size=5, callbacks=[callbacks])
        return history

    def model_evaluate(self, test):
        features = {name: np.array(value) for name, value in test.items()}
        labels = {name: features.pop(name) for name in self.label_names}
        metrics = self.model.evaluate(x=features, y=labels, batch_size=5)
        return metrics

    def save_model(self, model_filename):
        self.model.save_weights(model_filename)
