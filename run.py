from smbus import SMBus

import struct
import time
import datetime
import os

addr = 0x8
bus = SMBus(1)

csv_path = os.path.join(os.getcwd(), 'data', 'data.csv')
csv_file = open(csv_path, 'w+')

csv_file.write("Time" + "," + "Date" + "," \
				+ "Humidity (%)" + "," + "Temp (C)" + "\n")

startTime = time.time()

def get_float(data, index):
	byte = data[4*index:(index+1)*4]
	aux = bytearray(byte) 
	data_float = struct.unpack('<f',aux)[0]
	return data_float

def request_reading():
	try:
		reading = bus.read_i2c_block_data(addr, 0)
		humidity = get_float(reading, 0)
		temp = round(get_float(reading, 1), 2)
		date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
	except (OSError):
		date = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
		nan = [float("nan")]*3
		date, humidity, temp = nan
	
	return date, humidity, temp
	

while True:
	time.sleep(60)
	endTime = time.time()
	delta = endTime-startTime
	
	print(str(request_reading()[0]), "date", 
			str(int(delta)), "time",
			str(request_reading()[1]), "humidity", 
			str(request_reading()[2]), "temp")
	try: 
		csv_file.write( str(int(delta)) + ","
						+ str(request_reading()[0]) + "," 
						+ str(request_reading()[1]) + ","
						+ str(request_reading()[2]) + "\n")
	except (KeyboardInterrupt, SystemExit):
		csv_file.close()

