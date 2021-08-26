import os	
import time

from get_data_inference import GetDataInference

def data_acquisition(start_time:float, file_names:list) -> None:
	"""
        create empty csv file and filled it with data that
        has been taken from DHT22 Sensor
        
        start_time: initial time when the function is executed
        file_names: name of files to store the data
    """
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
                    str(request.get('humidity')[i]), "humidity", 
                    str(request.get('temp')[i]), "temp")
            
            #write sensor data into a csv file
            with open(path, 'a') as f:
                f.write(str(int(delta)) + ","
                                + str(request.get('date')[i]) + "," 
                                + str(request.get('humidity')[i]) + ","
                                + str(request.get('temp')[i]) + "\n")
        time.sleep(1800)

if __name__ == "__main__":
	get_inference = GetDataInference([0x8, 0x9], 0x7, 0x1, 'Training Data.csv')
	startTime = time.time()
	data_acquisition(startTime)
	
