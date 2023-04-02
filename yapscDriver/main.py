#encoder driver under test menymp jan 2023
from machine import Pin, PWM

#system libs
import machine
import utime
import _thread
import gc #garbage collector

#specific wrapper libs
from encoder import quadraturePioEncoder
from motorDriver import motorDriver
from stepDirInterface import stepDirInterface
from serialInterface import serialInterface
from EepromConfigsInterface import EepromConfigsInterface
from servoController import servoController

#this task will perform the serial handling
def core1_task(servoObj):
    utime.sleep(1)
    while(True):
        #utime.sleep(1)
        #print("wait")
        commandExecute(servoObj)

#Configure interfaces and main servo object
def initServoInterface():
    encoder = quadraturePioEncoder(2,3)  #quadrature encoder on pins 2 and 3
    stepDirObj = stepDirInterface(18,19) #step dir interface for cnc control on 18 and 19 pins
    serialObj = serialInterface(uartId = 1, baudrate = 9600, txPin = 4, rxPin= 5) #serial uart pins 4 and 5
    eeprObj = EepromConfigsInterface(sclPin = 27, sdaPin = 26, baseId = 1) #eeprom i2c memory on pin 27 and 26
    motorOutObj = motorDriver(pin_A = 16,pin_B = 17,frequency = 80_000) #pwm differential interface running at 80 Khz at pins 16 and 17
    
    #pass every initialization as a reference
    servoObj = servoController(enable_Pin = 12, status_Pin = 13, encoderRef = encoder, motorRef = motorOutObj, stepDirRef = stepDirObj, serialRef = serialObj, eepromRef = eeprObj)
    return servoObj

#ToDo
#current expected cmds
#get error
#get set input step dir register
#get set input encoder register
#get set output speed dir
#
#by default logic will expect control from step dir, if usb connected, mode can be changed to expect setpoint to be modified
#
#get set pid constants from eeprom, only by user an eeprom write operation will be performed
#get set pid constants kp kd ki
#get set start stop
#get set mode stepDir, usb control
#get keepalive
def commandExecute(servoObj):
    cmdArray = []
    #utime.sleep(0.2)
    gc.collect()
    while(len(cmdArray) == 0):
        cmdArray = servoObj.readSerial()
        utime.sleep(0.01)
        
    try:
        print(cmdArray)
        if(cmdArray[0] == "get" and cmdArray[1] == "error"):
            #get current error OK
            servoObj.writeSerial("error:" + str(servoObj.getError()) + "\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "keepalive"):
            #get keepalive response OK
            servoObj.writeSerial(servoObj.getKeepalive()+"\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "stateValues"):
            #get state values for graph and
            keepaliveR = servoObj.getKeepalive()
            setpoint = servoObj.getSetpoint()
            tmpArr = servoObj.getOutput()
            encVal = servoObj.getEncoderVal()
            errVal = servoObj.getError()
            baseDir = servoObj.getCurrentDirection()
            servoObj.writeSerial("stateValues:"+keepaliveR+":"+str(errVal)+":"+str(encVal)+":"+str(setpoint)+":"+str(tmpArr[0])+","+str(tmpArr[1])+":"+str(baseDir)+"\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "stepDir"):
            #get stepdir register OK
            servoObj.writeSerial("stepDir:"+str(servoObj.getStepDirVal())+"\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "encoder"):
            #get encoder register OK
            servoObj.writeSerial("encoder:"+str(servoObj.getEncoderVal())+"\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "encoder"):
            #set encoder register 
            servoObj.setEncoderVal(int(cmdArray[2]))
            servoObj.writeSerial("encoder:OK\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "output"):
            #get output speed and dir OK
            tmpArr = servoObj.getOutput()
            servoObj.writeSerial("output:"+str(tmpArr[0])+","+str(tmpArr[1])+"\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "output"):
            #set output speed and dir OK only if controller disabled
            servoObj.setOutput(bool(cmdArray[2]),int(cmdArray[3]))
            servoObj.writeSerial("output:OK\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "direction"):
            #get direction OK
            setpoint = servoObj.getCurrentDirection()
            servoObj.writeSerial("direction:"+str(setpoint)+"\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "direction"):
            #set direction OK
            servoObj.setCurrentDirection(int(cmdArray[2]))
            servoObj.writeSerial("direction:OK\n")
        elif(cmdArray[0] == "invert" and cmdArray[1] == "direction"):
            #set direction OK
            valDir = servoObj.getCurrentDirection()
            servoObj.setCurrentDirection(not valDir)
            servoObj.writeSerial("direction:"+str(servoObj.getCurrentDirection())+"\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "setpoint"):
            #get setpoint OK
            setpoint = servoObj.getSetpoint()
            servoObj.writeSerial("setpoint:"+str(setpoint)+"\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "setpoint"):
            #set setpoint OK
            servoObj.setSetpoint(int(cmdArray[2]))
            servoObj.writeSerial("setpoint:OK\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "PID"):
            #set pid constant and dir cmdArray[2] = p, d or i, sample OK
            if(cmdArray[2]) in ['p','d','i']:
                value = float(cmdArray[3])
            elif(cmdArray[2]) in ['sample_time']:
                value = int(cmdArray[3])
            else:
                value = cmdArray[3]
            servoObj.setPidData(cmdArray[2],value)
            servoObj.writeSerial("PID:OK\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "PID"):
            #get current PID values kp kd ki and sample_time OK
            pidData, sample_time, outLimits = servoObj.getPidData()
            servoObj.writeSerial("PID:"+str(pidData[0])+":"+str(pidData[1])+":"+str(pidData[2])+":"+str(sample_time)+ ":" + str(outLimits) + "\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "EEPROM"):
            #get current PID EEPROM values OK
            values = servoObj.getEEPROMPidValues()
            servoObj.writeSerial("EEPROM:"+str(values)+"\n")#ToDo change for eeprom values ,
        elif(cmdArray[0] == "set" and cmdArray[1] == "EEPROM"):
            #set current PID values OK
            if cmdArray[2] in ["kp", "kd","ki"]:
                value = float(cmdArray[3])
            else:
                value = int(cmdArray[3])
            servoObj.setEEPROMPidValues(cmdArray[2],value)
            servoObj.writeSerial("EEPROM:OK\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "state"):
            #set state start or stop OK
            servoObj.writeSerial("state:"+str(servoObj.getState())+"\n")
        elif(cmdArray[0] == "configs" and cmdArray[1] == "load"):
            #read eeprom configs and update state OK
            servoObj.loadCurrentConfigs()
            servoObj.writeSerial("configs:OK\n")
        elif(cmdArray[0] == "configs" and cmdArray[1] == "save"):
            #write current state to eeprom configs OK
            servoObj.saveCurrentConfigs()
            servoObj.writeSerial("configs:OK\n")
        elif(cmdArray[0] == "configs" and cmdArray[1] == "print"):
            #print config total values OK
            configs = servoObj.getEepromConfigs()
            servoObj.writeSerial("configs:"+str(configs)+"\n")#ToDo change concat values with ,
        elif(cmdArray[0] == "set" and cmdArray[1] == "state"):
            #get state start or stop OK
            servoObj.setState(int(cmdArray[2]))
            servoObj.writeSerial("state:OK\n")
        elif(cmdArray[0] == "set" and cmdArray[1] == "mode"):
            #set controlMode stepDir, usb control OK
            servoObj.setMode(int(cmdArray[2]))
            servoObj.writeSerial("mode:OK\n")
        elif(cmdArray[0] == "get" and cmdArray[1] == "mode"): #OK
            servoObj.writeSerial("mode:"+str(servoObj.getMode())+"\n")
        else:
            servoObj.writeSerial("ERR")
    except Exception as e: 
        print(e)
    pass

#ToDo	
#main task will perform startup initialization and critical time control updates
if __name__ == "__main__":
    servoObj = initServoInterface()
    _thread.start_new_thread(core1_task, (servoObj,)) #start second core thread
    utime.sleep(1)
    while(True):
        #utime.sleep(1)
        gc.collect()
        #print(gc.mem_free())
        servoObj.executeControlAction()
        utime.sleep(0.01)
        #print("nh")