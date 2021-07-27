from smbus import SMBus

import struct
import datetime

import tensorflow as tf
import numpy as np
import pandas as pd
import model_for_control as control

class GetDataInference:
	def __init__(self, 
				addr_send, 
				addr_receive, 
				addr_cmd, 
				inference_csv):
		self.model = None
		self.prediction = []
		self.addr_send  = addr_send
		self.addr_receive = addr_receive
		self.addr_cmd = addr_cmd
		self.inference_csv = inference_csv
		self.bus = SMBus(1)
	
	@staticmethod
	def get_float(data, index):
		byte = data[4*index:(index+1)*4]
		aux = bytearray(byte) 
		data_float = struct.unpack('<f',aux)[0]
		return data_float

	def request_reading(self):
		try:
			reading = self.bus.read_i2c_block_data(self.addr_send, 0)
			humidity = self.get_float(reading, 0)
			temp = round(self.get_float(reading, 1), 2)
			date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
		except (OSError):
			date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
			nan = [float("nan")]*3
			date, humidity, temp = nan
		
		return date, humidity, temp

	def control_model_initialization(self):
		df = pd.read_csv(self.inference_csv, delimiter=";")
		self.model = control.load_model(train=df,
						   feature_names=['Temperature', 'Humidity'],
						   label_names=['Fan', 'Humidifier'])
		self.model.load_weights('./Weight/my_weight')
		return -1
		
	def inference(self, data_for_inference):
		import tensorflow as tf
		preds = self.model.predict(data_for_inference)
		preds = tf.argmax(preds, axis=-1)
		preds = tf.squeeze(preds)
		self.prediction = preds.numpy().tolist()
		return self
	
	def write_to_arduino(self, preds:list):
		self.bus.write_i2c_block_data(self.addr_receive, 
									self.addr_cmd, preds)
		return -1
