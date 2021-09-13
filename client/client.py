import argparse
import os
import socket
import sys

import numpy as np
import pandas as pd
import tqdm

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
    print(filename)
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


def run_send_receive(filename: str) -> None:
    send(filename)
    receive()
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

    if len(sys.argv) <= 1:
        raise TypeError('Please input some argument')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_forecast = subparsers.add_parser("forecast",
                                            help="Forecast the temperature value")
    group_forecast = parser_forecast.add_mutually_exclusive_group()
    group_forecast.add_argument("-y", action="store_true")
    group_forecast.add_argument("-n", action="store_true")

    parser_request = subparsers.add_parser("request",
                                           help="Request data from raspberry pi")
    group_request = parser_request.add_mutually_exclusive_group()
    group_request.add_argument("--control", action="store_true",
                               help='Request data from controlled system')
    group_request.add_argument("--natural", action="store_true",
                               help='Request data from uncontrolled system')

    args = parser.parse_args()

    if args.subparser_name == "request":
        if args.control:
            run_send_receive(filenames[0])
        elif args.natural:
            run_send_receive(filenames[1])
        else:
            parser.error("The following arguments required: -control or -natural")

    if args.subparser_name == "forecast":
        if args.y:
            data, predict = model_train(csv_path)
            data1, data2 = model_predict(data, predict)
            plot_data(data1, data2)
        elif args.n:
            data_ = dataframe_to_array(csv_path)
            plot_data(data1=data_)
        else:
            parser.error("The following arguments required: -y or -n")
