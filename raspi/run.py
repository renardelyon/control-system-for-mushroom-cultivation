from math import isnan
from get_data_inference import GetDataInference

import os
import time
import datetime
import argparse

import tensorflow as tf
import numpy as np


def data_inference(start_time:float,
					get_inference:object,
					sleep_time:int) -> None:
	""" Predict actuator state based on enviromental physical data that is taken from DHT22 Sensor"""
	while True:
		end_time = time.time()
		delta = end_time - start_time
		request = get_inference.request_reading()
		
		if not isnan(request['humidity'][1]) and not isnan(request['temp'][1]): 
			inference_data = {'Temperature': np.array([request['temp'][1]]),
								'Humidity': np.array([request['humidity'][1]])}
			get_inference.inference(inference_data)
			
		print("elapsed time:{} prediction:{}".format(delta, get_inference.prediction))
		
		get_inference.write_to_arduino(list(get_inference.prediction))
		time.sleep(sleep_time)
	

if __name__ == "__main__":
	addr_sensor = [0x8, 0x9]
	addr_actuator = 0x7 
	addr_cmd = 0x1
	data_dir = "./data"
	data_training = "Training Data.csv"
	
	parser = argparse.ArgumentParser()
	parser.add_argument("--stop",
						action="store_true",
						help = "stop signal that was sending")
	parser.add_argument("time",
			      help="How much time needed between each signal transmission to arduino",
			      nargs='?',
			      default=-1,
			      type=int)
	args = parser.parse_args()	
	
	startTime = time.time()
	get_inference = GetDataInference(addr_sensor,
									  addr_actuator,
									  addr_cmd,
									  data_training)

	if args.stop:
		get_inference.write_to_arduino([0, 0])
		exit()
	else:
		if args.time > 0:
			sleep_time = args.time
		else:
			parser.error("There is no argument passed or passed argument had a value < 0")
	
	if get_inference.model is None:
		get_inference.control_model_initialization()

	
	data_inference(startTime, get_inference, sleep_time)
	
	
				
		
