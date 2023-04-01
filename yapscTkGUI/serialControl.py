import serial
import time

class serialControl():
	def __init__(self):
		self.isDrvInit = False
		pass
	
	def serialOpen(self, portPath, baudRate, timeout = 0.02, maxLen = 50):
		self.maxLen = maxLen
		self.timeout = timeout
		self.serialDrv = serial.Serial(port = portPath, baudrate = baudRate, timeout = timeout)
		self.isDrvInit = True
		pass
	
	def serialClose(self):
		if not self.isDrvInit:
			return False
		if self.serialDrv.is_open:
			self.serialDrv.close()
		pass
	
	def isOpen(self):
		if not self.isDrvInit:
			return False
		return self.serialDrv.is_open
	
	def executeCmd(self, cmd):
		if (not self.isDrvInit or not self.serialDrv.is_open):
			return "err"
		self.serialDrv.reset_input_buffer()
		self.serialDrv.write(cmd.encode())
		time.sleep(self.timeout)
		response = self.serialDrv.readline(self.maxLen).decode(encoding='UTF-8')
		self.serialDrv.reset_output_buffer()
		self.serialDrv.reset_input_buffer()
		return response
	
	def write(self, cmd):
		if (not self.isDrvInit or not self.serialDrv.is_open):
			return
		self.serialDrv.write(cmd.encode())