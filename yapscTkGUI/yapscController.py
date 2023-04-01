from threading import Thread
from threading import Lock
from threading import Event
from events import Events
import time
from serialControl import serialControl



class yapscController():
	def __init__(self, configsObj):
		self._createEventHandlers()
		self.readConfigs(configsObj)
		self._initSerial()
		self._initUITask()
		self.pollStateTasks = []
		self.isTaskRunning = False
		self.closeFlag = False
		
		pass
	
	######################################
	#create Controller events
	######################################
	def _createEventHandlers(self):
		self.controllerEvents = ('onError_pollCommand')
		self.events = Events(self.controllerEvents)
		pass
	
	def initPoll(self):
		#self.stopEvent = Event()
		#self.spinLockComm = Lock()
		self.taskReadUi = Thread(target=self.pollDeviceStates)
		self.taskReadUi.start()
		pass
	
	def _initSerial(self):
		self.serialW = serialControl()
		pass
	
	#######
	# get ports in windows
	#import serial.tools.list_ports
	#ports = serial.tools.list_ports.comports()
	#for port, desc, hwid in sorted(ports):
    #    print("{}: {} [{}]".format(port, desc, hwid))
	#
	#
	
	def initComm(self, serialPort, baudRate):
		#connStr = str(serialPort) expect compatibility with linux, add a device detector com
		self.serialW.serialOpen(portPath = serialPort, baudRate = baudRate, timeout = self.serialTimeout, maxLen = self.maxLen)
		pass
	
	def isComOpen(self):
		return self.serialW.isOpen()
	
	def readConfigs(self, configsObj):
		self.serialTimeout = configsObj["serialTimeout"]
		self.maxLen = configsObj["maxLen"]
		self.refreshRate = configsObj["refreshRate"]
		pass
	
	def _initUITask(self):
		self.stopEvent = Event()
		self.spinLockComm = Lock()
		#self.taskReadUi = Thread(target=self.pollDeviceStates)
		pass
	
	#adds a new command to be executed with poll states and the ref to refresh data
	def addPollState(self, command, responseRef):
		self.pollStateTasks.append([command, responseRef])
		pass
	
	def _executePollTask(self, command, responseRef):
		try:
			response = self.executeCmd(command)
			responseRef( response)
		except Exception as e:
			self._onError_pollCommand(command , e)
		pass
	
	#ToDo: check what to do with this information
	def _onError_pollCommand(self, command, exceptMsg):
		errDict = {
			"command":command,
			"log":exceptMsg,
		}
		self.events.onError_pollCommand(self, errDict)
		pass
	
	def pollDeviceStates(self):
		#run task loop until stop executin signal is set
		print("background poll daemon started...")
		self.isTaskRunning = True
		while(self.stopEvent.is_set() == False):
			time.sleep(self.refreshRate)
			if not self.serialW.isOpen():
				continue
			for command, responseRef in self.pollStateTasks:
				self._executePollTask(command, responseRef)
			pass
		self.closeFlag = False
		self.serialW.serialClose()
		#print("background poll daemon stopped...")
		self.stopEvent.clear()
		self.isTaskRunning = False
		print("background poll daemon stopped...")
	
	def stopExecution(self):
		if self.isTaskRunning == True:
			self.stopEvent.set() #signal pollDeviceState to stop current execution
			self.closeFlag = True
			#time.sleep(1)
			#print("stopping")
			#while (self.stopEvent.is_set()): #wait for safe thread stop
			#	#while self.closeFlag:
			#	time.sleep(1)
			#	print(self.stopEvent.is_set())
			#	pass
			#print("stopped")
		#if self.serialW.isOpen():
		#
		#	#self.serialW.serialClose()
		return True
	
	def executeCmd(self, cmd):
		#lock control over serial for multithread
		self.spinLockComm.acquire()
		retVal = self.serialW.executeCmd(cmd)
		self.spinLockComm.release()
		return retVal
		