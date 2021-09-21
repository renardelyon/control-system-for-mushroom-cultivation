import os	
import time
import argparse

from get_data_inference import GetDataInference

def data_acquisition(start_time:float, 
			data_dir:str,
			file_names:list,
			get_inference:object,
			sleep_time:int) -> None:
	""" Store data that has been logged by the sensor in csv format
	
		start_time: initial time when the function is executed
		file_names: name of files to store the data """
	csv_path = []
	for i, file_name in enumerate(file_names):
		csv_path.append(os.path.join(os.getcwd(), 'data', file_name))
		csv_file = open(csv_path[i], 'w+')
		csv_file.write("Time" + "," + "Date" + "," \
                        + "Humidity (%)" + "," + "Temp (C)" + "\n")
		csv_file.close()
       
	while True:
		endTime = time.time()
		delta = endTime-startTime

		request = get_inference.request_reading()
		for i, path in enumerate(csv_path):
			print(str(request.get('date')[i]), "date", 
                    str(int(delta)), "time",
                    str(round(request.get('humidity')[i],2)), "humidity", 
                    str(request.get('temp')[i]), "temp")
            
            #write sensor data into a csv file
			with open(os.path.join(data_dir,path), 'a') as f:
				f.write(str(int(delta)) + ","
                                + str(request.get('date')[i]) + "," 
                                + str(round(request.get('humidity')[i],2)) + ","
                                + str(request.get('temp')[i]) + "\n")
		time.sleep(sleep_time)

if __name__ == "__main__":
	addr_sensor = [0x8, 0x9]
	addr_actuator = 0x7 
	addr_cmd = 0x1
	data_dir = "./data"
	data_training = "Training Data.csv"
	
	parser = argparse.ArgumentParser()
	parser.add_argument("time",
			      help="How much time needed between each sensor signal acquisition",
			      default=-1,
			      type=int)
	args = parser.parse_args()
	
	if args.time > 0:
		sleep_time = args.time
	else:
		parser.error("There is no argument passed or passed argument had a value < 0")
	
	get_inference = GetDataInference(addr_sensor,
					addr_actuator,
					addr_cmd,
					data_training)
	startTime = time.time()
    
	file_names = ['data.csv', 'data1.csv']
	data_acquisition(startTime, 
			  data_dir,
			  file_names,
			  get_inference,
			  sleep_time)
	
