from PID import PID
import _thread
from machine import Pin
import utime

class State():
    ENABLED = 1
    DISABLED = 0

class Mode():
    STEP_DIR = 0
    USB_CTRL = 1

class DrvState():
    OK = 0
    ERR = 1


class servoController():
	def __init__(self, enable_Pin, status_Pin, encoderRef, motorRef, stepDirRef, serialRef, eepromRef):
		self.QuadratureEnc = encoderRef
		self.MotorInterface = motorRef
		self.StepDirInterface = stepDirRef
		self.SerialUART = serialRef
		self.EEPROMDrv = eepromRef
		
		self.enable_Pin = Pin(enable_Pin, mode=Pin.IN, pull=Pin.PULL_UP)
		self.status_Pin = Pin(status_Pin, mode=Pin.IN, pull=Pin.PULL_UP)
		self.hwState = State.DISABLED
		#thread lock for critical sections under two core threads
		#related to memory read and write
		#each critical variable has a lock 
		self.spLock1 = _thread.allocate_lock() # for error value
		self.spLock2 = _thread.allocate_lock() # for setpoint value
		self.spLock3 = _thread.allocate_lock() # for stepDir register
		self.spLock4 = _thread.allocate_lock() # for encoder register
		self.spLock5 = _thread.allocate_lock() # for pid values
		self.spLock6 = _thread.allocate_lock() # for EEPROM read write
		self.spLock7 = _thread.allocate_lock() # for controller state
		self.spLock8 = _thread.allocate_lock() # for controller mode
		self.spLock9 = _thread.allocate_lock() # for pid output direction
		self.spLock10 = _thread.allocate_lock() # for pid output direction
		#at power up, by default mode is set to STEP_DIR and error is set to 0
		self.error = 0
		
		self.mode = Mode.STEP_DIR
		self.state = State.ENABLED
		
		#load values from eeprom at startup
		self.configValues = self.getEepromConfigs()
		self.PID_Controller = PID(Kp = self.configValues[0], Kd = self.configValues[1], Ki = self.configValues[2],  scale='us')
		self.PID_Controller.sample_time = self.configValues[3]
		self.PID_Controller.setpoint = self.StepDirInterface.getEncoderPos()
		
		if(self.configValues[6]):
			self.direction = True
		else:
			self.direction = False
		
		self.PID_Controller.auto_mode = False
		#ToDo review for posible death zero response near 0v and if max output value can be scaled down
		self.PID_Controller.output_limits = (self.configValues[4] , self.configValues[5]) # (0 , 65534)
		self.state = State.ENABLED
		
		self.stepDirVal = 0
		self.encoderVal = 0
		
		pass	
	
	def saveCurrentConfigs(self):
		self.setEEPROMPidValues("kp", self.PID_Controller.Kp)
		self.setEEPROMPidValues("kd", self.PID_Controller.Kd)
		self.setEEPROMPidValues("ki", self.PID_Controller.Ki)
		self.setEEPROMPidValues("t", self.PID_Controller.sample_time )
		self.setEEPROMPidValues("l", self.PID_Controller.output_limits[0])
		self.setEEPROMPidValues("h", self.PID_Controller.output_limits[1])
		self.setEEPROMPidValues("d", 1 if self.direction else 0) #ToDo: review better way to store
		pass
	
	def loadCurrentConfigs(self):
		self.configValues = self.getEepromConfigs()
		self.PID_Controller.Kp = self.configValues[0]
		self.PID_Controller.Kd = self.configValues[1]
		self.PID_Controller.Ki = self.configValues[2]
		
		if(self.configValues[6]):
			self.direction = True
		else:
			self.direction = False
		
		self.PID_Controller.sample_time = self.configValues[3]
		self.PID_Controller.output_limits = (self.configValues[4] , self.configValues[5]) # (0 , 65534)
		pass
    
	def getEepromConfigs(self):
		if(self.EEPROMDrv.checkAvailableEeprom()): #check for memory detected at i2c Bus
			print("EEPROM found,begining header test...")
		else:
			raise Exception('EEPROM not detected')
		
		if(not self.EEPROMDrv.checkForInitHeaders()):
			print("EEPROM config sector without format, attempting to format...")
			if(not self.EEPROMDrv.formatArea()):
				raise Exception('EEPROM format attempt unsuccesfull')
			print("EEPROM format success")
		
		print("EEPROM reading config values")
		configs = self.EEPROMDrv.getConfigs()
		print(configs)
		return configs
	
		#######################################################################################
		#Calculates the current difference between setpoint and current position of encoder
		#depending on mode, the setpoint will be updated from stepDir
		#Note: simple PID does not work with negative flank as far as i could check, an absolute error must be used
		#######################################################################################
	def calculateEncoder(self):
		if self.getState() == State.DISABLED:
			return 0
		self.spLock1.acquire()
		if(self.getMode() == Mode.STEP_DIR):
			self._readStepDirReg()
		pos = self._readEncoderReg()
		setpoint = self.getSetpoint()
		self.error = setpoint - pos #calculate error
		self.spLock1.release()
		return setpoint - abs(self.error) #return setpoint plus current abs error to normalize
	
	def _readStepDirReg(self):
		self.spLock3.acquire()
		self.stepDirVal = self.StepDirInterface.getEncoderPos()
		self.PID_Controller.setpoint = self.StepDirInterface.getEncoderPos()
		self.spLock3.release()
		return self.stepDirVal
	
	def _readEncoderReg(self):
		self.spLock4.acquire()
		self.encoderVal = self.QuadratureEnc.getEncoderPos()
		self.spLock4.release()
		return self.encoderVal
	
	def _getHwState(self):
		if(self.enable_Pin.value() == DrvState.OK and self.status_Pin.value() == DrvState.OK):
			return DrvState.OK
		else:
			return DrvState.ERR
		return DrvState.ERR
		
	
	def getCurrentDirection(self):
		self.spLock9.acquire()
		value = self.direction
		self.spLock9.release()
		return value
	
	def setCurrentDirection(self, direction):
		self.spLock9.acquire()
		self.direction = direction
		self.spLock9.release()
		
        #
        #tasks to be done for error calculation, pid response calculation and output response 
        #
	def executeControlAction(self):
		if self.getState() == State.DISABLED or self._getHwState() != DrvState.OK:
			self.PID_Controller.auto_mode = False
			return
		else:
			self.PID_Controller.auto_mode = True
		self.spLock10.acquire()
		#print(self.encoderVal)
		#utime.sleep(1)
		pos = self.calculateEncoder()
		if(self.error >= 0): #handle direction of the error
			direction = self.getCurrentDirection()
		else:
			direction = not self.getCurrentDirection()
		#print(pos)
		response = self.PID_Controller(pos) #composite pos with setpoint to absolute response
		self.setOutput(direction, response)
		self.spLock10.release()
		#print("kl")
		pass
    
		#
		#gets setpoint current value
		#
	def getSetpoint(self):
		self.spLock2.acquire()
		value = self.PID_Controller.setpoint
		self.spLock2.release()
		return value
	
		#
		#if mode is control from serial, the setpoint will be updated to val
		#
	def setSetpoint(self, val):
		self.spLock2.acquire()
		if(self.mode == Mode.USB_CTRL):
			self.PID_Controller.setpoint = val
		self.spLock2.release()
		
		#
		#gets current error
		#
	def getError(self):
		self.spLock1.acquire()
		value = self.error
		self.spLock1.release()
		return value
	
	def getKeepalive(self):
		return "SERVO_OK"
	
	def getStepDirVal(self):
		self.spLock3.acquire()
		value = self.stepDirVal
		self.spLock3.release()
		return value

	def setStepDirVal(self, value):
		if(self.getMode() != Mode.USB_CTRL):
			return
		self.setState(State.DISABLED)
		self.spLock3.acquire()
		self.StepDirInterface.setEncoderPos(value)
		self.spLock3.release()
    
	def getEncoderVal(self):
		self.spLock4.acquire()
		value = self.encoderVal
		self.spLock4.release()
		return value
	
	def setEncoderVal(self, value):
		if(self.getMode() != Mode.USB_CTRL):
			return
		self.setState(State.DISABLED)
		self.spLock4.acquire()
		print(value)
		self.QuadratureEnc.setEncoderPos(value)
		self.spLock4.release()
	
	def getOutput(self):
		self.spLock5.acquire()
		direction, speed = self.MotorInterface.getOutput()
		self.spLock5.release()
		return speed, direction
    
	def setOutput(self, direction, value):
		self.spLock5.acquire()
		if self._getHwState() == DrvState.OK:
			self.MotorInterface.setOutput(direction,int(value))
		else:
			self.MotorInterface.setOutput(False,0)
		self.spLock5.release()
    
	def getPidData(self):
		self.spLock10.acquire()
		value = self.PID_Controller.tunings
		sampleTime = self.PID_Controller.sample_time
		outLimits = self.PID_Controller.output_limits
		self.spLock10.release()
		return value, sampleTime, outLimits
	
	def setPidData(self, parameter, val):
		self.spLock10.acquire()
		if parameter == 'p':
			self.PID_Controller.Kp = val
		elif parameter == 'd':
			self.PID_Controller.Kd = val
		elif parameter == 'i':
			self.PID_Controller.Ki = val
		elif parameter == 'sample_time':
			self.PID_Controller.sample_time = val
		elif parameter == 'limits':
			tokens = val.split('-')
			valHigh = int(tokens[1])
			valLow = int(tokens[0])
			if (valHigh >= valLow):
				limits = (valLow , valHigh)
				self.PID_Controller.output_limits  = limits
		self.spLock10.release()
	
	def getEEPROMPidValues(self):
		self.spLock6.acquire()
		value = self.EEPROMDrv.getConfigs()
		self.spLock6.release()
		return value
	
	def setEEPROMPidValues(self, parameter, val):
		self.spLock6.acquire()
		self.EEPROMDrv.setConfigParameter(parameter, val)
		self.spLock6.release()
		pass
    
	def getState(self):
		self.spLock7.acquire()
		value = self.state
		self.spLock7.release()
		return value
	
	def setState(self, state):
		self.spLock7.acquire()
		if state == State.ENABLED:
			self.state = state
			if self.getMode() == Mode.STEP_DIR:
				self.setSetpoint(self._readStepDirReg()) #as safety setpoint to current pos
			self.PID_Controller.auto_mode = True
		elif state == State.DISABLED:
			self.state = state
			self.PID_Controller.auto_mode = False
			self.setOutput(False, 0)
		self.spLock7.release()
	
	def getMode(self):
		self.spLock8.acquire()
		value = self.mode
		self.spLock8.release()
		return value
	
	def setMode(self, mode):
		self.spLock8.acquire()
		self.mode = mode
		self.spLock8.release()
	
	def writeSerial(self, msg):
		self.SerialUART.writeOutput(msg)
	
	def readSerial(self):
		return self.SerialUART.waitForCommand()