from smbus import SMBus
from math import isnan

import numpy as np
import tensorflow as tf
import pandas as pd
import struct
import time
import datetime
import os
import model_for_control as control


addr_send = 0x8
addr_receive = 0x7
addr_cmd = 0x1
bus = SMBus(1)

csv_path = os.path.join(os.getcwd(), 'data', 'data.csv')
csv_file = open(csv_path, 'w+')

csv_file.write("Time" + "," + "Date" + "," \
				+ "Humidity (%)" + "," + "Temp (C)" + "\n")

startTime = time.time()
prediction = []

def get_float(data, index):
	byte = data[4*index:(index+1)*4]
	aux = bytearray(byte) 
	data_float = struct.unpack('<f',aux)[0]
	return data_float

def request_reading():
	try:
		reading = bus.read_i2c_block_data(addr_send, 0)
		humidity = get_float(reading, 0)
		temp = round(get_float(reading, 1), 2)
		date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
	except (OSError):
		date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
		nan = [float("nan")]*3
		date, humidity, temp = nan
	
	return date, humidity, temp

def control_model_initialization():
	csv_path = "Data Fan Humidifier.csv"
	df = pd.read_csv(csv_path, delimiter=";")
	model = control.load_model(train=df,
                       feature_names=['Temperature', 'Humidity'],
                       label_names=['Fan', 'Humidifier'])
	model.load_weights('./Weight/my_weight')
	return model

def inference(prediction):
    preds = tf.argmax(prediction, axis=-1)
    preds = tf.squeeze(preds)
    #preds = tf.math.add(preds, 50)
    return preds.numpy().tolist()

def write_to_arduino(preds:list):
	bus.write_i2c_block_data(addr_receive, 0x1, preds)
	return -1


if __name__ == "__main__":
	model = control_model_initialization()
	while True:
		endTime = time.time()
		delta = endTime-startTime
		
		date, humidity, temp = request_reading()
		
		print(str(date), "date", 
				str(int(delta)), "time",
				str(humidity), "humidity", 
				str(temp), "temp")
		try: 
			csv_file.write( str(int(delta)) + ","
							+ str(request_reading()[0]) + "," 
							+ str(request_reading()[1]) + ","
							+ str(request_reading()[2]) + "\n")
		except (KeyboardInterrupt, SystemExit):
			csv_file.close()
		
		if not isnan(humidity) and not isnan(temp): 
			inference_data = {'Temperature': np.array([temp]),
								'Humidity': np.array([humidity])}
			prediction = model.predict(inference_data)
			binary_preds = inference(prediction)
		write_to_arduino(preds=list(binary_preds))
		time.sleep(10)
				
		
