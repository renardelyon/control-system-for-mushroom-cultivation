import smbus
import time
import multiprocessing as mp

bus = smbus.SMBus(1)
address = 0x7

start_time = time.time()

class RaspiProcesses:
	def __init__(self, data):
		self.data = data
		
	def initial_data(self, n):
		for i in range(n):
			time.sleep(1)
			print(i)

	def send_data_to_arduino(self):
		def writeNumber(a):
			bus.write_byte_data(address, 0, a)
			return -1

		while True:
			for i in self.data:
				end_time = time.time()   
				writeNumber(i)
				now = - start_time + end_time
				print('time of first function: {}'.format(now))	
				time.sleep(30)
				
	def send_block_of_data(self):
		def writeData(a:list):
			bus.write_i2c_block_data(address, 0, a)
			return -1
			
		while True:
			end_time = time.time()   
			writeData(self.data)
			now = - start_time + end_time
			print('time of first function: {}'.format(now))	
			time.sleep(30)
					               
	def print_time(self):
		while True:
			end_time = time.time()
			now = - start_time + end_time
			print('time of second function: {}'.format(now))
			time.sleep(10)
	
if __name__ == '__main__':
	rasp_process = RaspiProcesses([0, 1])
	rasp_process.initial_data(10)
		
	processes = [mp.Process(target=rasp_process.send_block_of_data),
				 mp.Process(target=rasp_process.print_time)]
	try:
		for p in processes:
			p.start()
	except (KeyboardInterrupt, SystemExit):
		for p in processes:
			p.join()
		quit()
