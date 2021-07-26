import socket
import tqdm
import os
import time

from forecasting_train_inference import model_predict, plot_data, model_train

SEPARATOR = "<SEPARATOR>"
HEADER = 64
BUFFER_SIZE = 4096
# the ip address or hostname of the server, the receiver
SERVER = "192.168.43.148"
# the port, let's use 5001
PORT = 5050
# the name of file we want to send, make sure it exists
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive():
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
    client.close()


def send(msg):
    message = msg.encode("utf-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("utf-8")
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


if __name__ == "__main__":
    send("SEND_DATA")
    receive()
    time.sleep(5)
    csv_path = "data.csv"
    data, predict = model_train(csv_path)
    data1, data2 = model_predict(data, predict)
    plot_data(data1, data2)

