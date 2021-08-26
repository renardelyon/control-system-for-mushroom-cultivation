import socket

import numpy as np
import tqdm
import os
import time
import pandas as pd
import argparse

from forecasting_train_inference import model_predict, plot_data, model_train

SEPARATOR = "<SEPARATOR>"
HEADER = 64
BUFFER_SIZE = 4096
# the ip address or hostname of the server, the receiver
SERVER = "192.168.43.148"
# the port
PORT = 5050

ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive() -> None:
    """ receiving file from server"""
    received = client.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            bytes_read = client.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))
    


def send(msg: str) -> None:
    """ sending string messages to server """
    message = msg.encode("utf-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("utf-8")
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def run_send_receive(filenames: list) -> None:
    for filename in filenames:
        send(filename)
        receive()
        time.sleep(1)
    client.close()


def dataframe_to_array(path: str) -> np.ndarray:
    """ convert pandas dataframe to numpy array """
    df = pd.read_csv(path)
    df = df.dropna()
    df.drop(columns='Date', inplace=True)

    array_data = df[['Humidity (%)', 'Temp (C)']].to_numpy()
    return array_data


if __name__ == "__main__":
    csv_path = "data.csv"
    
    filenames = ["./data/data.csv", "./data/data1.csv"]
    run_send_receive(filenames)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--forecast", action="store_true",
                        help="Forecast the temperature value")
    args = parser.parse_args()

    if args.forecast:
        data, predict = model_train(csv_path)
        data1, data2 = model_predict(data, predict)
        plot_data(data1, data2)
    else:
        data_ = dataframe_to_array(csv_path)
        plot_data(data1=data_)



