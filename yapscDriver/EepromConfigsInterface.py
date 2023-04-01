import uos
import struct
from machine import I2C, Pin
from eeprom_i2c import EEPROM, T24C256

class EepromConfigsInterface():
	def __init__(self, sclPin, sdaPin, baseId, eepromModel = T24C256, offsetAddress = 0):
		self.i2c = I2C(baseId, scl=Pin(sclPin, Pin.OPEN_DRAIN), sda=Pin(sdaPin, Pin.OPEN_DRAIN))
		self.eepromModel = eepromModel
		self.eep = EEPROM(self.i2c, eepromModel)
		
		#memory organization
		self.offsetAddress = offsetAddress
		self.kpAddr = self.offsetAddress + 5
		self.paddr1 = self.offsetAddress + 13
		self.kdAddr = self.offsetAddress + 14
		self.paddr2 = self.offsetAddress + 22
		self.kiAddr = self.offsetAddress + 23
		self.paddr3 = self.offsetAddress + 31
		self.samp_t = self.offsetAddress + 32
		self.paddr4 = self.offsetAddress + 40
		self.low_sc = self.offsetAddress + 41
		self.paddr5 = self.offsetAddress + 49
		self.hig_sc = self.offsetAddress + 50
		self.paddr6 = self.offsetAddress + 58
		self.dir_mo = self.offsetAddress + 59
		self.endCfg = self.offsetAddress + 60
	
	def checkAvailableEeprom(self, verbose = False):
		nchips, minNum = self.eep.scan(verbose, self.eepromModel)
		return nchips
	def checkForInitHeaders(self):
		#an specific header will be placed in address to see if the eeprom already
		#has valid data.
		#validate the data integrity, if not proced to reset EEPROM contents
		#get word conf as a header start from dir 0x100 to dir 0x104
		#check for 5 bytearray of conf word
		try:
			readBuff = bytearray([0,0,0,0,0])
			self.eep.readwrite(self.offsetAddress,readBuff,True)
			#print(readBuff)
			if("confg" != readBuff.decode()):
				return False
			#read first 8 bytearray of Kp float value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.kpAddr,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr1,readBuff,True)
			if("," != readBuff.decode()):
				return False
			#read first 8 bytearray of Kd float value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.kdAddr,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr2,readBuff,True)
			if("," != readBuff.decode()):
				return False	
			#read first 8 bytearray of Ki float value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.kiAddr,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr3,readBuff,True)	
			if("," != readBuff.decode()):
				return False
			#read first 8 bytearray of sample time value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.samp_t,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr4,readBuff,True)		
			if("," != readBuff.decode()):
				return False
			#read first 8 bytearray of low scale value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.low_sc,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr5,readBuff,True)	
			if("," != readBuff.decode()):
				return False
			#read first 8 bytearray of high scale value
			readBuff = bytearray([0,0,0,0,0,0,0,0])
			self.eep.readwrite(self.hig_sc,readBuff,True)
			#read a padding ',' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.paddr6,readBuff,True)
			if("," != readBuff.decode()):
				return False
			#read first 1 bytearray of direction
			readBuff = bytearray([0])
			self.eep.readwrite(self.dir_mo,readBuff,True)
			#read a end '#' value
			readBuff = bytearray([0])
			self.eep.readwrite(self.endCfg,readBuff,True)	
			if("#" != readBuff.decode()):
				return False
			return True
		except:
			return False
	
	def formatArea(self):
		#write conf header
		readBuff = bytearray("confg",'utf-8')
		self.eep.readwrite(self.offsetAddress,readBuff,False)
		#zeros for kp address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.kpAddr,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr1,readBuff,False)
		#zeros for kd address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.kdAddr,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr2,readBuff,False)
		#zeros for ki address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.kiAddr,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr3,readBuff,False)	
		#zeroes for sample time address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.samp_t,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr4,readBuff,False)		
		#zeroes for low scale address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.low_sc,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr5,readBuff,False)	
		#zeroes for high scale address
		readBuff = bytearray([0,0,0,0,0,0,0,0])
		self.eep.readwrite(self.hig_sc,readBuff,False)
		#write a padding ',' value
		readBuff = bytearray(",",'utf-8')
		self.eep.readwrite(self.paddr6,readBuff,False)
		#zeroes for direction address
		readBuff = bytearray(1)
		self.eep.readwrite(self.dir_mo,readBuff,False)
		#write a end '#' value
		readBuff = bytearray("#",'utf-8')
		self.eep.readwrite(self.endCfg,readBuff,False)
		return self.checkForInitHeaders()
	
	
	def getConfigs(self):
		outConfigs = []
		outConfigs.append(self._getConfigValue(self.kpAddr,8,'d'))
		outConfigs.append(self._getConfigValue(self.kdAddr,8,'d'))
		outConfigs.append(self._getConfigValue(self.kiAddr,8,'d'))
		outConfigs.append(self._getConfigValue(self.samp_t,8,'q'))
		outConfigs.append(self._getConfigValue(self.low_sc,8,'q'))
		outConfigs.append(self._getConfigValue(self.hig_sc,8,'q'))
		#print(outConfigs)
		outConfigs.append(self._getConfigValue(self.dir_mo,1,'B'))
		return outConfigs
	
	def _getConfigValue(self, offsetAddr, buffLen, valueStructType):
		readBuff = bytearray(buffLen)
		self.eep.readwrite(offsetAddr,readBuff,True)
		#print("confg:")
		#print(offsetAddr)
		#print(readBuff)
		#print(buffLen)
		#print(valueStructType)
		return struct.unpack(valueStructType,readBuff)[0]
	
	def setConfigParameter(self , parameter, val):
		if(parameter == 'fm' and val == 1):
			self.formatArea()
		if(parameter == 'kp'):
			writeBuff = struct.pack('d', val)
			self.eep.readwrite(self.kpAddr,writeBuff,False)
		if(parameter == 'kd'):
			writeBuff = struct.pack('d', val)#double 8 bytearray
			self.eep.readwrite(self.kdAddr,writeBuff,False)
		if(parameter == 'ki'):
			writeBuff = struct.pack('d', val)
			self.eep.readwrite(self.kiAddr,writeBuff,False)
		if(parameter == 't'):
			writeBuff = struct.pack('q', val)# long long 8 bytearray
			self.eep.readwrite(self.samp_t,writeBuff,False)
		if(parameter == 'l'):
			writeBuff = struct.pack('q', val)
			self.eep.readwrite(self.low_sc,writeBuff,False)
		if(parameter == 'h'):
			writeBuff = struct.pack('q', val)
			self.eep.readwrite(self.hig_sc,writeBuff,False)
		if(parameter == 'd'):
			writeBuff = struct.pack('B', val)# unsigned char 1 byte
			self.eep.readwrite(self.dir_mo,writeBuff,False)
		pass