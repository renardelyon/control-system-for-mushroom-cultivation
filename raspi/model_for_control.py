import numpy as np
import tensorflow as tf
import pandas as pd


from tensorflow.keras import layers
from tensorflow.keras.losses import SparseCategoricalCrossentropy


def load_model(train, label_names, feature_names):
    features = {name: np.array(value) for name, value in train.items()}
    labels = {name: features.pop(name) for name in label_names}

    feature_columns = [tf.feature_column.numeric_column(name,
                                                        normalizer_fn=lambda val: (val - features[name].mean()) /
                                                                                  features[name].std())
                       for name in feature_names]

    feature_layers = layers.DenseFeatures(feature_columns)

    inputs = {name: tf.keras.Input(shape=(1,), name=name)
              for name in feature_names}
    x = feature_layers(inputs)
    x = layers.Dense(32, activation='relu', )(x)

    fan_preds = layers.Dense(2, activation='softmax', name='Fan')(x)
    humidifier_preds = layers.Dense(2, activation='softmax', name='Humidifier')(x)
    model_for_loading = tf.keras.Model(dict(inputs), [fan_preds, humidifier_preds])

    model_for_loading.compile(optimizer='adam',
                              loss={
                                  'Fan': SparseCategoricalCrossentropy(),
                                  'Humidifier': SparseCategoricalCrossentropy()
                              },
                              metrics=['accuracy'])
    return model_for_loading



