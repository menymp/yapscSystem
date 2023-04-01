import json
from pathlib import Path

GRAPH_BUFF_LEN = (10, 100) #MIN MAX buffer len for display
PLOT_INTERVAL_RANGE = (20, 1000)
SERIAL_TIMEOUT = (0.01,0.5)
SERIAL_BUFFER_LEN = (50, 60)
REFRESH_RATE = (0.1, 1)

defaultConfigsStruct = {
	"graphBufferLen":30,
	"resolution":"1200x1000",
	"titleVersion":"YAPSC GUI interface v 1.0",
	"plotInterval":100,
	"serialTimeout":0.07,
	"maxLen":254,
	"refreshRate":0.5
}

def getConfigs(path = './yapscConfigs.json'):
	if not checkFileIntegrity(path):
		return None
	configDict = readConfigFile(path)
	return configDict

def checkFileIntegrity(path):
	path = Path(path)
	if not path.is_file() or not checkConfigFields(path):
		saveConfigs(defaultConfigsStruct)
	return True

def checkConfigFields(path):
	configObj = readConfigFile(path)
	#print(configObj)
	if  not (GRAPH_BUFF_LEN[0] < configObj["graphBufferLen"] <= GRAPH_BUFF_LEN[1]):
		return False
	if configObj["resolution"] == "":#ToDo: Evaluate use a regex
		return False 
	if configObj["titleVersion"] == "":#ToDo: Evaluate use a regex
		return False 
	if  not (PLOT_INTERVAL_RANGE[0] < configObj["plotInterval"] <= PLOT_INTERVAL_RANGE[1]):
		return False
	if  not (SERIAL_TIMEOUT[0] < configObj["serialTimeout"] <= SERIAL_TIMEOUT[1]):
		return False
	if  not (REFRESH_RATE[0] < configObj["refreshRate"] <= REFRESH_RATE[1]):
		return False
	return True

def readConfigFile(path):
	with open(path) as f:
		data = json.load(f)
	return data

def saveConfigs(configsObj, path = './yapscConfigs.json', indent=4):
	json_object = convertDict2JsonObj(configsObj, indent)
	with open(path, "w+") as f:
		f.seek(0)
		f.write(json_object)
		f.truncate()
	return True

def convertDict2JsonObj(dicObj, indent):
	return json.dumps(dicObj,indent=indent)