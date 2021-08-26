from math import isnan
from get_data_inference import GetDataInference

import time
import datetime

import tensorflow as tf
import numpy as np

def data_inference(start_time:float) -> None:
    """ Predict actuator state based on enviromental physical data that is taken from DHT22 Sensor"""
	while True:
		end_time = time.time()
		delta = end_time - start_time
		request = get_inference.request_reading()
		
		if not isnan(request['humidity'][0]) and not isnan(request['temp'][0]): 
			inference_data = {'Temperature': np.array([request['temp'][0]]),
								'Humidity': np.array([request['humidity'][0]])}
			get_inference.inference(inference_data)
			
		print("elapsed time:{} prediction:{}".format(delta, get_inference.prediction))
		
		get_inference.write_to_arduino(list(get_inference.prediction))
		time.sleep(60)
	

if __name__ == "__main__":
	startTime = time.time()
	get_inference = GetDataInference([0x8, 0x9], 0x7, 0x1, 'Data Fan Humidifier.csv')
	if get_inference.model is None:
		get_inference.control_model_initialization()
	
	data_inference(startTime)
	
	
				
		
