'''
Under construction, maybe is not a good idea at all since is not expected to change a controller
that easy
'''
from PID import PID

CONTROLLER_PID = 1

class BaseController():
    missing::::
        self.PID_Controller.setpoint
        response = self.PID_Controller(pos)
    
    getters:
    		value = self.PID_Controller.tunings
		sampleTime = self.PID_Controller.sample_time
		outLimits = self.PID_Controller.output_limits

    setters:
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
    

class PID_Controller(BaseController):
    def __init__(self, type, configValues, initialSetpoint):
        self.PID_Controller = PID(Kp = configValues[0], Kd = configValues[1], Ki = configValues[2],  scale='us')
        self.PID_Controller.sample_time = self.configValues[3]
        self.PID_Controller.setpoint = initialSetpoint
        self.PID_Controller.auto_mode = False
        self.PID_Controller.output_limits = (self.configValues[4] , self.configValues[5])

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