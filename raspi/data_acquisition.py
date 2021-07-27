import os	
import time

from get_data_inference import GetDataInference

def data_acquisition(start_time:float) -> None:
	csv_path = os.path.join(os.getcwd(), 'data', 'data.csv')
	
	csv_file = open(csv_path, 'w+')
	csv_file.write("Time" + "," + "Date" + "," \
					+ "Humidity (%)" + "," + "Temp (C)" + "\n")
	csv_file.close()
	while True:
		endTime = time.time()
		delta = endTime-startTime
		
		date, humidity, temp = get_inference.request_reading()
		
		print(str(date), "date", 
				str(int(delta)), "time",
				str(humidity), "humidity", 
				str(temp), "temp")
				
		with open(csv_path, 'a') as f:
			f.write( str(int(delta)) + ","
							+ str(date) + "," 
							+ str(humidity) + ","
							+ str(temp) + "\n")
		time.sleep(20)

if __name__ == "__main__":
	get_inference = GetDataInference(0x8, 0x7, 0x1, 
										'Data Fan Humidifier.csv')
	startTime = time.time()
	data_acquisition(startTime)
	
