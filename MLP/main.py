import numpy as np
import matplotlib.pyplot as plt

from train_model import DataModelProcessing


def plot_model(log_history):
    f, ax = plt.subplots(1, 2, figsize=(12, 4))
    _ = f.suptitle('Accuracy and Loss', fontsize=12)
    f.subplots_adjust(top=0.85, wspace=0.3)

    epochs = list(range(1, len(log_history.history['loss']) + 1))

    ax[0].plot(epochs, log_history.history['loss'], label='Train Loss')
    ax[0].set_xticks(np.arange(0, len(epochs), 5))
    ax[0].set_ylabel('Loss Value')
    ax[0].set_xlabel('Epoch')
    ax[0].set_title('Loss')
    _ = ax[0].legend(loc="best")

    ax[1].plot(epochs, log_history.history['Fan_accuracy'], label='Fan Accuracy')
    ax[1].plot(epochs, log_history.history['Humidifier_accuracy'],
               label='Humidifier Accuracy')
    ax[1].set_xticks(np.arange(0, len(epochs), 5))
    ax[1].set_ylabel('Accuracy')
    ax[1].set_xlabel('Epoch')
    ax[1].set_title('Accuracy')
    _ = ax[1].legend(loc="best")
    plt.show()


if __name__ == '__main__':
    processing = DataModelProcessing('Data Fan Humidifier.csv')
    train, test = processing.split_data()
    processing.create_feature_layers(train)
    history = processing.train_model()
    processing.save_model('./Weight/my_weight')
    plot_model(history)
