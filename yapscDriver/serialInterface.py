#serial interface
#

from machine import UART, Pin
import time

class serialInterface():
    def __init__(self, uartId, baudrate, txPin, rxPin, maxCmdInput = 30, timeout = 700):
        self.uartObj = UART(uartId, baudrate=baudrate, tx=Pin(txPin), rx=Pin(rxPin), timeout = timeout)
        self.rxStr = ""
        self.maxInputCmd = maxCmdInput
        pass
    
    def waitForCommand(self):
        tmpArr = []
        self.rxStr = ""
        if self.uartObj.any():
            byte = self.uartObj.readline(self.maxInputCmd)
            if byte is not None:
                self.rxStr += byte.decode('utf-8')
                self.rxStr = self.rxStr.replace('\n','')
                self.rxStr = self.rxStr.replace('\t','')
                self.rxStr = self.rxStr.replace('\r','')
                tmpArr = self.rxStr.split(',', 6)
        return tmpArr
    
    def writeOutput(self, stringOut):
        rxData = bytes(stringOut, 'utf-8')
        self.uartObj.write(rxData)
        