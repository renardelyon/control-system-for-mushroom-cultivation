from smbus import SMBus

import struct
import datetime

import tensorflow as tf
import numpy as np
import pandas as pd
import model_for_control as control

class GetDataInference:
	def __init__(self, 
				addr_send:list, 
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
        """ Reading float data sent by Arduino"""
		byte = data[4*index:(index+1)*4]
		aux = bytearray(byte) 
		data_float = struct.unpack('<f',aux)[0]
		return data_float

	def request_reading(self):
        """Read float data using get_float method and stored it in dictionary"""
        request = dict(humidity=[], temp=[], date=[])
        for address in self.addr_send:
            try:
                reading = self.bus.read_i2c_block_data(address, 0)
                request['humidity'].append(self.get_float(reading, 0))
                request['temp'].append(round(self.get_float(reading, 1), 2))
                request['date'].append(datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S'))
            except (OSError):
                request['date'].append(datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S'))
                for key, value in request.items():
                    request.get(key).append(float("nan"))
                    
		return request

	def control_model_initialization(self):
        """ Initialize the model weights """
		df = pd.read_csv(self.inference_csv, delimiter=";")
		self.model = control.load_model(train=df,
						   feature_names=['Temperature', 'Humidity'],
						   label_names=['Fan', 'Humidifier'])
		self.model.load_weights('./Weight/my_weight')
		return -1
		
	def inference(self, data_for_inference):
        """ 
        Make inference on the passed data
        data_for_inference: data the model needed
        """        
		preds = self.model.predict(data_for_inference)
		preds = tf.argmax(preds, axis=-1)
		preds = tf.squeeze(preds)
		self.prediction = preds.numpy().tolist()
		return self
	
	def write_to_arduino(self, preds:list):
        """ Send prediction data to Arduino through I2C communication"""
		self.bus.write_i2c_block_data(self.addr_receive, 
									self.addr_cmd, preds)
		return -1
