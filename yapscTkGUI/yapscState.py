#this object will act as action in relation to GUI interface changes
#or incoming data

from yapscConfigs import *
from yapscController import yapscController
from yapscGui import yapscGui
from serialPortUtills import serial_ports

class yapscState():
	def __init__(self):
		self._readConfigs()
		self._routeGuiEvents()
		self.maxInitAttempts = 4
		pass	
	
	def _readConfigs(self):
		self.configsObj = getConfigs()
		self.yapscControllerRef = yapscController(self.configsObj)
		self.yapscGuiRef = yapscGui(self.configsObj)
		serialPathsObj = serial_ports() #adds detected ports to GUI, works on linux and Windows
		self.yapscGuiRef.addSerialPaths(serialPathsObj)
		pass
	
	def uiLoop(self):
		self.yapscGuiRef.mainloop()
	
	#('onClick_connect','onClick_close','onChange_mode','onChange_state','onChange_direction','onClick_eeprom','onClick_ctrlCmd')
	def _routeGuiEvents(self):
		self.yapscGuiRef.events.onClick_connect += self.connectHandler
		self.yapscGuiRef.events.onClick_close += self.closeSignal
		self.yapscGuiRef.events.onChange_mode += self.modeHandler
		self.yapscGuiRef.events.onChange_state += self.stateHandler
		self.yapscGuiRef.events.onChange_direction += self.dirHandler
		self.yapscGuiRef.events.onClick_eeprom += self.eepromHandler
		self.yapscGuiRef.events.onClick_ctrlCmd += self.ctrlCmdHandler
		pass
	
	def modeHandler(self, modeObj):
		cmd="set,mode,"+str(modeObj["mode"])+"\n"
		response = self.yapscControllerRef.executeCmd(cmd)
		self.yapscGuiRef.appendLog(response)
		pass
	
	def stateHandler(self, stateObj):
		cmd="set,state,"+str(stateObj["state"])+"\n"
		response = self.yapscControllerRef.executeCmd(cmd)
		self.yapscGuiRef.appendLog(response)
		pass
	
	def dirHandler(self, dirObj):
		#check if not needed
		pass
	
	def eepromHandler(self, eepromObj):
		cmd = ""
		if eepromObj["command"] == "LOAD":
			cmd = "configs,load\n"
		elif eepromObj["command"] == "SAVE":
			cmd = "configs,save\n"
		elif eepromObj["command"] == "READ":
			cmd = "configs,print\n"
		response = self.yapscControllerRef.executeCmd(cmd)
		print(response)
		self.yapscGuiRef.appendLog(response)
		pass
	
	#"command":cmd,
	#"type":type
	def ctrlCmdHandler(self, cmdObj):
		cmd="get,keepalive\n"
		type=""
		if cmdObj["type"] == "Setpoint" and cmdObj["command"] == "READ":
			cmd="get,setpoint\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			self.yapscGuiRef.setValue(cmdObj["type"], int(respArr[1]))
		if cmdObj["type"] == "Setpoint" and cmdObj["command"] == "WRITE":
			cmd="set,setpoint,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "encoder" and cmdObj["command"] == "READ":
			cmd="get,encoder\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			#print(response)
			respArr = response.split(':')
			self.yapscGuiRef.setValue(cmdObj["type"], int(respArr[1]))
		if cmdObj["type"] == "encoder" and cmdObj["command"] == "WRITE":
			cmd="set,encoder,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "SampleTime" and cmdObj["command"] == "READ":
			cmd="get,PID\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			self.yapscGuiRef.setValue(cmdObj["type"], int(respArr[4]))
		if cmdObj["type"] == "SampleTime" and cmdObj["command"] == "WRITE":
			cmd="set,PID,sample_time,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "OutLimits" and cmdObj["command"] == "READ":
			cmd="get,PID\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			self.yapscGuiRef.setValue(cmdObj["type"], eval(respArr[5]))
		if cmdObj["type"] == "OutLimits" and cmdObj["command"] == "WRITE":
			#print("limits: " + str(cmdObj["value"]))
			cmd="set,PID,limits,"+str(cmdObj["value"][0])+"-"+str(cmdObj["value"][1])+"\n"
			#print(cmd)
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "OutSpeed" and cmdObj["command"] == "READ":
			cmd="get,output\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			valueArr = respArr[1].split(",")
			self.yapscGuiRef.setValue(cmdObj["type"], (int(valueArr[0]),int(valueArr[0])))
		if cmdObj["type"] == "OutSpeed" and cmdObj["command"] == "WRITE":
			cmd="set,output,"+str(cmdObj["value"])+","+str(cmdObj[3])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "Kp" and cmdObj["command"] == "READ":
			cmd="get,PID\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			#print("kp read:" + respArr[1])
			self.yapscGuiRef.setValue(cmdObj["type"], float(respArr[1]))
		if cmdObj["type"] == "Kp" and cmdObj["command"] == "WRITE":
			cmd="set,PID,p,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			#print("kp write: " + cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "Kd" and cmdObj["command"] == "READ":
			cmd="get,PID\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			#print("kd read:" + respArr[2])
			#print("pid: "+response)
			self.yapscGuiRef.setValue(cmdObj["type"], float(respArr[3]))
		if cmdObj["type"] == "Kd" and cmdObj["command"] == "WRITE":
			cmd="set,PID,d,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			#print("kd write: " + cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "Ki" and cmdObj["command"] == "READ":
			cmd="get,PID\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			respArr = response.split(':')
			#print("kd read:" + respArr[3])
			#print("pid: "+response)
			self.yapscGuiRef.setValue(cmdObj["type"], float(respArr[2]))
		if cmdObj["type"] == "Ki" and cmdObj["command"] == "WRITE":
			cmd="set,PID,i,"+str(cmdObj["value"])+"\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			#print("ki write: " + cmd)
			self.yapscGuiRef.appendLog(response)
		if cmdObj["type"] == "BaseDir" and cmdObj["command"] == "WRITE":
			cmd="invert,direction\n"
			response = self.yapscControllerRef.executeCmd(cmd)
			self.yapscGuiRef.appendLog(response)
			respArr = response.split(':')
			#self.yapscGuiRef.setValue(cmdObj["type"], respArr[1])
		pass

		
	def connectHandler(self, connObj):
		if not self.yapscControllerRef.isComOpen():
			try:
				#attempt to connect to com
				self.yapscControllerRef.initComm(connObj["port"], connObj["baud"])
			except:
				self.closeSignal()
				self.yapscGuiRef.appendLog("Error connecting to " + str(connObj["port"]))
			
			if self.initProcess():
				stateS = "connected"
			else:
				stateS = "disconnected"
				self.closeSignal()
				self.yapscGuiRef.appendLog("Could not read initial values from " + str(connObj["port"]))
			
		else:
			stateS = "disconnected"
			self.closeSignal()
		
		connectResult = {
			"state":stateS,
			"log":"correctly " + stateS,
			"comm":connObj["port"]
		}
		self.yapscGuiRef.setCommState(connectResult)
		pass
	
	def initProcess(self):
		result = False
		if self.getInitialValues():
			self._initUpdateSecuenceProcedures()
			self.yapscControllerRef.initPoll()
			result = True
		return result
	
	def getInitialValues(self):
		### read everithing related from microcontroller
		attempts = 0
		result = False
		while (attempts <= self.maxInitAttempts):
			try:
				stateStr = self.yapscControllerRef.executeCmd("get,state\n").split(':')[1]
				#print("stateS " +str(stateStr)+" "+str(stateStr[1]))
				modeStr = self.yapscControllerRef.executeCmd("get,mode\n").split(':')[1]
				#print("modeS " +str(modeStr)+" "+ str(modeStr[1]))
				setpointStr = self.yapscControllerRef.executeCmd("get,setpoint\n").split(':')[1]
				encoderStr = self.yapscControllerRef.executeCmd("get,encoder\n").split(':')[1]
				#[kp,kd,ki,sampleT, outLimits]
				pidDataArr = self.yapscControllerRef.executeCmd("get,PID\n").split(':')
				outParr = self.yapscControllerRef.executeCmd("get,output\n").split(':')
				outArr = outParr[1].split(',')
				outLimitsArr = pidDataArr[5].replace("(","").replace(")","").split(",")
				 
				#print(pidDataArr)
				#print(outArr)
				#print(outLimitsArr)
				valuesObj = {
					"state":int(stateStr),
					"mode":int(modeStr),
					"setpoint":int(setpointStr),
					"samplet":int(pidDataArr[4]),
					"outlow":int(outLimitsArr[0]),
					"outhigh":int(outLimitsArr[1]),
					"outspeed":int(outArr[0]),
					"encoder":int(setpointStr),
					"kp":float(pidDataArr[1]),
					"kd":float(pidDataArr[2]),
					"ki":float(pidDataArr[3]),
				}
				print(valuesObj)
				self.yapscGuiRef.setCurrentValues(valuesObj)
				result = True
				break
			except:
				#a failed attempt to read configs, 4 consecutive attempts lead to a total failure
				attempts = attempts + 1
		return result
	
	def _initUpdateSecuenceProcedures(self):
		#self.yapscControllerRef.addPollState("get,keepalive\n",self._integrityCheck) #integrity check
		#self.yapscControllerRef.addPollState("get,error\n",self._setErrorParse)
		#self.yapscControllerRef.addPollState("get,encoder\n",self._pushEncoderParse)
		#self.yapscControllerRef.addPollState("get,setpoint\n",self._pushSetpointParse)
		#self.yapscControllerRef.addPollState("get,error\n",self._pushErrorValue)
		#self.yapscControllerRef.addPollState("get,output\n",self._pushOutputParse)
		self.yapscControllerRef.addPollState("get,stateValues\n",self._getStateValues)
		pass
	
	def waitForResponse():
		pass
	
	def _getStateValues(self, args):
		#integrity check
		#print(args)
		if not "SERVO_OK" in args:
			raise Exception('wrong signal')
		
		respArr = args.split(':')
		#print(args)
		if len(respArr) != 7 or respArr[0] != "stateValues":
			raise Exception('format error')
		
		#parse output value as special case for sign
		outArgs = respArr[5].split(',')
		if len(outArgs) != 2:
			raise Exception('format error')
		if ("True" in outArgs[1]):
			dir = True
		elif ("False" in outArgs[1]):
			dir = False
		else:
			raise Exception('direction arg unknown')
		
		if ("True" in respArr[6]):
			basedir = True
		elif ("False" in respArr[6]):
			basedir = False
		else:
			raise Exception('base direction arg unknown')
		#get sign
		if dir:
			outVal = -int(outArgs[0])
		else:
			outVal = int(outArgs[0])
		
		#parse state values for GUI plot
		stateValObj = {
			"encoder":int(respArr[3]),
			"setpoint":int(respArr[4]),
			"output":outVal,
			"error":int(respArr[2])
		}
		#print(stateValObj)
		#update GUI data plot
		self.yapscGuiRef.pushStateValues(stateValObj)
		self.yapscGuiRef.setValue("OutSpeed",(outVal, dir))
		self.yapscGuiRef.setValue("BaseDir",str(basedir))
		pass
	
	def _integrityCheck(self, args):
		#print("integrity: "+str(args))
		if not "SERVO_OK" in args:
			raise Exception('wrong signal')
		pass
	
	def _setErrorParse(self, args):
		respArr = args.split(':')
		if (respArr[0]=="error"):
			self.yapscGuiRef.setErrorLabel(respArr[1])
	
	def _pushEncoderParse(self, args):
		respArr = args.split(':')
		if (respArr[0]=="encoder"):
			self.yapscGuiRef.pushEncoderValue(int(respArr[1]))
	
	def _pushSetpointParse(self, args):
		respArr = args.split(':')
		if (respArr[0]=="setpoint"):
			#print("setpointval: " + str(int(respArr[1])))
			self.yapscGuiRef.pushSetpointValue(int(respArr[1]))
	
	def _pushErrorValue(self, args):
		respArr = args.split(':')
		if (respArr[0]=="error"):
			#print("errval: " + str(respArr[1]))
			self.yapscGuiRef.pushErrorValue(int(respArr[1]))
		
	def _pushOutputParse(self, args):
		respArr = args.split(':')
		#print("outresp: "+str(respArr))
		if (respArr[0]!= "output"):
			return
		outArgs = respArr[1].split(',')
		if len(outArgs) != 2:
			return
		if (bool(outArgs[1])):
			outVal = -int(outArgs[0])
		else:
			outVal = int(outArgs[0])
		#print("out: " + str(outVal))
		self.yapscGuiRef.pushOutputValue(outVal) #ToDo: test if factible to update output here, line below
		self.yapscGuiRef.setValue("OutSpeed",(outVal, int(outArgs[0])))
	
	def closeSignal(self):
		self.yapscControllerRef.stopExecution()