#GUI constructor for yapscInterface
from tkinter import *
from tkinter.ttk import *
from events import Events
import tkinter as tk
import matplotlib
from threading import Lock
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from matplotlib import style

#ToDo: cleanup unused methods, end of first stage
#ToDo: bug with encoder data write
class yapscGui():
	def __init__(self, configsObj):
		self.setGlobalConfigs(configsObj)
		self._createEventHandlers()
		self._constructGraphics()
		self._buildMatplotLibGraph()
		self.lockDraw1 = Lock()
		pass
	
	def setGlobalConfigs(self, configsObj):
		self.graphBufferLen = configsObj["graphBufferLen"]
		self.resolution = configsObj["resolution"]
		self.titleVersion = configsObj["titleVersion"]
		self.plotInterval = configsObj["plotInterval"]
		pass
	
	######################################
	#create GUI events
	######################################
	def _createEventHandlers(self):
		guiEvents = ('onClick_connect','onClick_close','onChange_mode','onChange_state','onChange_direction','onClick_eeprom','onClick_ctrlCmd')
		self.events = Events(guiEvents)
		pass
	
	######################################
	#builds current graphics for the model
	######################################
	def _constructGraphics(self):
		#create main window
		self.window = Tk()
		self.window.geometry(self.resolution )#width, height
		self.window.title(self.titleVersion)
		self.window.protocol("WM_DELETE_WINDOW", self._onClick_close)
		
		#create controls for the comm Labelframe section
		commframe = LabelFrame(self.window, width=500, height=500, text="comm")
		commframe.grid(column=0, row=0)
		#create comm gui parts
		self.btnConnectSerial = Button(commframe, text="connect", command=self._onClick_connect)
		self.btnConnectSerial.grid(column=0, row=0)
		#create comm spinbox
		#self.spinComm = Spinbox(commframe, from_=0, to=100, width=5)
		#self.spinComm.grid(column=1, row=0)
		
		#create combo port box
		self.comboCom = Combobox(commframe)
		#self.comboCom.current(0) #set the selected item
		self.comboCom.grid(column=1, row=0)
		#create lbl message for connection
		self.connLblMsg = Label(commframe, text="disconnected...")
		self.connLblMsg.grid(column=0, row=1, columnspan=2)
		#combo for selecting baud rate speed
		self.combo = Combobox(commframe)
		self.combo['values']= (9600, 19200, 38400, 57600, 115200, "Text")
		self.combo.current(0) #set the selected item
		self.combo.grid(column=0, row=2, columnspan=2)
		
		#mode select frame
		modeframe = LabelFrame(self.window, width=500, height=500, text="mode")
		modeframe.grid(column=0, row=1)
		self.modeVar = IntVar()
		self.modeVar.set(1)
		radModeStepDir = Radiobutton(modeframe,command = self._onChange_mode,variable = self.modeVar,text='STEP DIR', value=1)
		radModeStepDir.pack()
		radModeUsb = Radiobutton(modeframe,command = self._onChange_mode,variable = self.modeVar,text='USB', value=0)
		radModeUsb.pack()
		
		#state select frame
		stateframe = LabelFrame(self.window, width=500, height=500, text="state")
		stateframe.grid(column=0, row=2)
		self.stateVar = IntVar()
		self.stateVar.set(1)
		radStateEnable = Radiobutton(stateframe,command = self._onChange_state, variable = self.stateVar, text='ENABLED',value = 1)
		radStateEnable.pack()
		radStateDisable = Radiobutton(stateframe,command = self._onChange_state, variable = self.stateVar,text='DISABLED', value = 0)
		radStateDisable.pack()
		
		#state select frame
		controlPidFrame = LabelFrame(self.window, width=500, height=500, text="configurations")
		controlPidFrame.grid(column=1, row=0, rowspan=4)
		
		setpointLblMsg = Label(controlPidFrame, text="Setpoint: ")
		setpointLblMsg.grid(column=0, row=0)
		#read setpoint
		btnSetpointRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("Setpoint", "READ", self.setpointS.get()))
		btnSetpointRead.grid(column=1, row=0)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnSetpointWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("Setpoint", "WRITE", self.setpointS.get()))
		btnSetpointWrite.grid(column=2, row=0)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.setpointS = StringVar()
		self.setpointS.set("0")
		self.spinSetpoint = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.setpointS,  width=5)
		self.spinSetpoint.grid(column=3, row=0)
		#spinSetpoint.pack(side='left', padx = 1, pady = 1, fill=tk.X)	
		btnSetpointderInc = Button(controlPidFrame, text="<-", command=lambda: self._incSetpoint())
		btnSetpointderInc.grid(column=4, row=0)																					
		btnSetpointizqInc = Button(controlPidFrame, text="->", command=lambda: self._decSetpoint())
		btnSetpointizqInc.grid(column=5, row=0)
		#lbl error text
		errtxtLblMsg = Label(controlPidFrame, text="error: ")
		errtxtLblMsg.grid(column=0, row=1)
		#errtxtLblMsg.pack(side=tk.LEFT)
		#lbl error value
		self.errvalLblMsg = Label(controlPidFrame, text="0.0")
		self.errvalLblMsg.grid(column=3, row=1)
		#errvalLblMsg.pack(side=tk.LEFT)		
		############################################
		sampletLblMsg = Label(controlPidFrame, text="Sample time: ")
		sampletLblMsg.grid(column=0, row=2)
		#read setpoint
		btnSampletRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("SampleTime", "READ", self.sampletS.get()))
		btnSampletRead.grid(column=1, row=2)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnSampletWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("SampleTime", "WRITE", self.sampletS.get()))
		btnSampletWrite.grid(column=2, row=2)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.sampletS = StringVar()
		self.sampletS.set("0")
		self.spinSamplet = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.sampletS, width=5)
		self.spinSamplet.grid(column=3, row=2)
		#spinSetpoint.pack(side='left', padx = 1, pady = 1, fill=tk.X)	
		############################################
		outlowLblMsg = Label(controlPidFrame, text="Out limit low: ")
		outlowLblMsg.grid(column=0, row=3)
		#read setpoint
		btnoutlowRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("OutLimits", "READ", (int(self.outlowS.get()), int(self.outhighS.get()))))
		btnoutlowRead.grid(column=1, row=3)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnoutlowWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("OutLimits", "WRITE", (int(self.outlowS.get()), int(self.outhighS.get()))))
		btnoutlowWrite.grid(column=2, row=3)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.outlowS = StringVar()
		self.outlowS.set("0")
		self.spinoutlow = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.outlowS, width=5)
		self.spinoutlow.grid(column=3, row=3)
		#spinSetpoint.pack(side='left', padx = 1, pady = 1, fill=tk.X)	
		############################################
		outhighLblMsg = Label(controlPidFrame, text="Out limit high: ")
		outhighLblMsg.grid(column=0, row=4)
		#read setpoint
		btnouthighRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("OutLimits", "READ", (int(self.outlowS.get()), int(self.outhighS.get()))))
		btnouthighRead.grid(column=1, row=4)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnouthighWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("OutLimits", "WRITE", (int(self.outlowS.get()), int(self.outhighS.get()))))
		btnouthighWrite.grid(column=2, row=4)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.outhighS = StringVar()
		self.outhighS.set("0")
		self.spinouthigh = Spinbox(controlPidFrame, from_=0, to=999999999,  textvariable = self.outhighS, width=5)
		self.spinouthigh.grid(column=3, row=4)
		#spinSetpoint.pack(side='left', padx = 1, pady = 1, fill=tk.X)		
		############################################
		outspeedLblMsg = Label(controlPidFrame, text="Output speed dir: ")
		outspeedLblMsg.grid(column=0, row=5)
		#read setpoint
		btnoutspeedRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("OutSpeed", "READ", self.outspeedS.get(), self.dirVar.get()))
		btnoutspeedRead.grid(column=1, row=5)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnoutspeedWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("OutSpeed", "WRITE", self.outspeedS.get(), self.dirVar.get()))
		btnoutspeedWrite.grid(column=2, row=5)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.outspeedS = StringVar()
		self.outspeedS.set("0")
		self.spinoutspeed = Spinbox(controlPidFrame, from_=0,  textvariable = self.outspeedS, to=999999999, width=5)
		self.spinoutspeed.grid(column=3, row=5)
		#spinSetpoint.pack(side='left', padx = 1, pady = 1, fill=tk.X)	
		self.dirVar = IntVar()
		self.dirVar.set(1)
		radoutdirTrueEnable = Radiobutton(controlPidFrame,command = self._onChange_direction, variable = self.dirVar, text='DIR A', value=1)	
		radoutdirTrueEnable.grid(column=4, row=5)	
		radoutdirFalseEnable = Radiobutton(controlPidFrame,command = self._onChange_direction, variable = self.dirVar,text='DIR B', value=0)	
		radoutdirFalseEnable.grid(column=5, row=5)	
		############################################
		encoderLblMsg = Label(controlPidFrame, text="Encoder: ")
		encoderLblMsg.grid(column=0, row=6)
		#read setpoint
		btnencoderRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("encoder", "READ", self.encoderS.get()))
		btnencoderRead.grid(column=1, row=6)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		btnencoderWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("encoder", "WRITE", self.encoderS.get()))
		btnencoderWrite.grid(column=2, row=6)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.encoderS = StringVar()
		self.encoderS.set("0")
		self.spinencoder = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.encoderS, width=5)
		self.spinencoder.grid(column=3, row=6)		
		############################################
		kpLblMsg = Label(controlPidFrame, text="Kp: ")
		kpLblMsg.grid(column=0, row=7)
		#read setpoint
		kpRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("Kp", "READ", self.kpS.get()))
		kpRead.grid(column=1, row=7)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		kpWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("Kp", "WRITE", self.kpS.get()))
		kpWrite.grid(column=2, row=7)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.kpS = StringVar()
		self.kpS.set("0")
		self.spinkp = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.kpS, width=5)
		self.spinkp.grid(column=3, row=7)	
		############################################
		kdLblMsg = Label(controlPidFrame, text="Kd: ")
		kdLblMsg.grid(column=0, row=8)
		#read setpoint
		kdRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("Kd", "READ", self.kdS.get()))
		kdRead.grid(column=1, row=8)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		kdWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("Kd", "WRITE", self.kdS.get()))
		kdWrite.grid(column=2, row=8)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.kdS = StringVar()
		self.kdS.set("0")
		self.spinkd = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.kdS, width=5)
		self.spinkd.grid(column=3, row=8)
		############################################
		kiLblMsg = Label(controlPidFrame, text="Ki: ")
		kiLblMsg.grid(column=0, row=9)
		#read setpoint
		kiRead = Button(controlPidFrame, text="Read", command=lambda: self._onClick_ctrlCmd("Ki", "READ", self.kiS.get()))
		kiRead.grid(column=1, row=9)
		#btnSetpointRead.pack(side='left', padx = 1, pady = 1)
		#read setpoint
		kiWrite = Button(controlPidFrame, text="Write", command=lambda: self._onClick_ctrlCmd("Ki", "WRITE", self.kiS.get()))
		kiWrite.grid(column=2, row=9)
		#btnSetpointWrite.pack(side='left', padx = 1, pady = 1)
		#create comm spinbox
		self.kiS = StringVar()
		self.kiS.set("0")
		self.spinki = Spinbox(controlPidFrame, from_=0, to=999999999, textvariable = self.kiS, width=5)
		self.spinki.grid(column=3, row=9)
		#######
		#controls for change base direction at runtime
		invertDirBtn = Button(controlPidFrame, text="Invert", command=lambda: self._onClick_ctrlCmd("BaseDir","WRITE",0))
		invertDirBtn.grid(column=4,row=6)
		self.dirLabel = Label(controlPidFrame, text = "dir: ")
		self.dirLabel.grid(column=4,row=7)
		############################################
		eepromFrame = LabelFrame(self.window, width=500, height=500, text="EEPROM")
		eepromFrame.grid(column=0, row=3)
		#read setpoint
		btnEepromLoad = Button(eepromFrame, text="EEPROM LOAD", command=lambda: self._onClick_eeprom("LOAD"))
		btnEepromLoad.grid(column=0, row=0)
		#read setpoint
		btnEepromSave = Button(eepromFrame, text="EEPROM SAVE", command=lambda: self._onClick_eeprom("SAVE"))
		btnEepromSave.grid(column=0, row=1)
		#read setpoint
		btnEepromRead = Button(eepromFrame, text="EEPROM READ", command=lambda: self._onClick_eeprom("READ"))
		btnEepromRead.grid(column=0, row=2)
		
		############################################
		logFrame = LabelFrame(self.window, width=500, height=500, text="Log")
		logFrame.grid(column=3, row=0, rowspan=4)
		#read setpoint
		self.logText = Text(logFrame, width=60, height=15)
		self.logText.grid(column=0, row=0)
		#
		btnClearLog = Button(logFrame, text="Clear", command=lambda: self.logText.delete('1.0', END))
		btnClearLog.grid(column=0, row=1)
		pass
	
	def _incSetpoint(self):
		#ToDo: set increments with ui control
		#makes an attempt to increment by 1 the value, then read the value, if OK the ui will be updated
		self._onClick_ctrlCmd("Setpoint", "WRITE", self.setpointS.get() + 1)
		self._onClick_ctrlCmd("Setpoint", "READ", self.setpointS.get())
		pass
	
	def _decSetpoint(self):
		#ToDo: set increments with ui control
		#makes an attempt to increment by 1 the value, then read the value, if OK the ui will be updated
		self._onClick_ctrlCmd("Setpoint", "WRITE", self.setpointS.get() - 1)
		self._onClick_ctrlCmd("Setpoint", "READ", self.setpointS.get())
		pass
		
	def pushEncoderValue(self, value):
		self.lockDraw1.acquire()
		self.encoderY.insert(0,value)
		self.encoderY.pop()
		self.lockDraw1.release()
		#self._renderGraphs()
		pass
	
	def pushSetpointValue(self, value):
		self.setpointY.insert(0,value)
		self.setpointY.pop()
		#self._renderGraphs()
		pass
	
	def pushErrorValue(self, value):
		self.errorY.insert(0, value)
		self.errorY.pop()
		#self._renderGraphs()
		pass
	
	def pushOutputValue(self, value):
		self.outputY.insert(0, value)
		self.outputY.pop()
		#self._renderGraphs()
		pass
	
	def pushStateValues(self, objValues):
		self.pushEncoderValue(objValues["encoder"])
		self.pushSetpointValue(objValues["setpoint"])
		self.pushErrorValue(objValues["error"])
		self.pushOutputValue(objValues["output"])
		self.setErrorLabel(str(objValues["error"]))
		pass
	
	def _initGraphData(self):
		self.encoderY = [0 for i in range(0, self.graphBufferLen)] 
		self.encoderX = list(range(0, self.graphBufferLen))
		self.setpointY = [0 for i in range(0, self.graphBufferLen)] 
		self.setpointX = list(range(0, self.graphBufferLen))
		self.errorY = [0 for i in range(0, self.graphBufferLen)] 
		self.errorX = list(range(0, self.graphBufferLen))
		self.outputY = [0 for i in range(0, self.graphBufferLen)] 
		self.outputX = list(range(0, self.graphBufferLen))
	
	def _buildMatplotLibGraph(self):
		self._initGraphData()
		
		style.use('ggplot')
		fig = plt.figure(figsize=(11, 5), dpi=100)#7.7
		self.ax1 = fig.add_subplot(2, 1, 1)
		self.ax2 = fig.add_subplot(2, 1, 2)
		self.line, = self.ax1.plot(self.encoderX, self.encoderY, color = "black", label="Encoder")
		self.line2, = self.ax1.plot(self.setpointX, self.setpointY, color = "red", label="Setpoint") #to see with dots add , 'r', marker='o'
		self.ax1.legend()
		self.line3, = self.ax2.plot(self.errorX, self.errorY, color = "blue", label="Error")
		self.line4, = self.ax2.plot(self.outputX, self.outputY, color = "green", label="Output") #to see with dots add , 'r', marker='o'	
		self.ax2.legend()
		plotcanvas = FigureCanvasTkAgg(fig, self.window)
		plotcanvas.get_tk_widget().grid(column=0, row=11, columnspan=4)
		self.animate = animation.FuncAnimation(fig, self._animate, interval=self.plotInterval, blit=False)
		pass
	
	def _animate(self, i):
		#ser.reset_input_buffer()
		#data = ser.readline().decode("utf-8")
		#data_array = data.split(',')
		#yvalue = float(data_array[1])
		#yar.append(99-i)
		#xar.append(i)
		self.lockDraw1.acquire()
		self.line.set_data(self.encoderX, self.encoderY)
		self.line2.set_data(self.setpointX, self.setpointY)
		self.ax1.relim()
		self.ax1.autoscale()
		self.line3.set_data(self.errorX, self.errorY)
		self.line4.set_data(self.outputX, self.outputY)
		self.ax2.relim()
		self.ax2.autoscale()
		self.lockDraw1.release()
		#self.ax1.set_xlim(0, i+1)
	
	def _onClick_connect(self):
		connDict = {
			"port":self.comboCom.get(),
			"baud":self.combo.get()
		}
		self.events.onClick_connect( connDict)
		pass
	
	def setErrorLabel(self, err):
		self.errvalLblMsg.configure(text = err)
		pass
	
	def setCurrentValues(self, valuesObj):
		self.stateVar.set(valuesObj["state"])
		self.modeVar.set(valuesObj["mode"])
		self.setpointS.set(valuesObj["setpoint"])
		self.sampletS.set(valuesObj["samplet"])
		self.outlowS.set(valuesObj["outlow"])
		self.outhighS.set(valuesObj["outhigh"])
		self.outspeedS.set(valuesObj["outspeed"])
		self.encoderS.set(valuesObj["encoder"])
		self.kpS.set(valuesObj["kp"])
		self.kdS.set(valuesObj["kd"])
		self.kiS.set(valuesObj["ki"])
		pass
	
	def setValue(self, type, value):
		if(type == "state"):
			self.stateVar.set(value)
		elif(type == "mode"):
			self.modeVar.set(value)
		elif(type == "Setpoint"):
			self.setpointS.set(value)
		elif(type == "SampleTime"):
			self.sampletS.set(value)
		elif(type == "OutLimits"):
			self.outlowS.set(value[0])
			self.outhighS.set(value[1])
		elif(type == "OutSpeed"):
			self.outspeedS.set(value[0])
			self.dirVar.set(value[1])
		elif(type == "encoder"):
			self.encoderS.set(value)
		elif(type == "Kp"):
			self.kpS.set(value)
		elif(type == "Kd"):
			self.kdS.set(value)
		elif(type == "Ki"):
			self.kiS.set(value)
		elif(type == "BaseDir"):
			self.dirLabel.configure(text=value)
		pass
		#{
		#	"state":"connected",
		#	"log":"result"
		#	"comm":"1"
		#}
	def setCommState(self, connStateDict):
		if connStateDict["state"] == "connected":
			self.comboCom["state"] = tk.DISABLED
			self.combo["state"]=tk.DISABLED
			self.connLblMsg.config(text = "connected to com " + connStateDict["comm"])
			self.btnConnectSerial.configure(text = "disconnect")
			self.logText.insert(END,connStateDict["log"] +"\n")
		else:
			self.comboCom["state"] = tk.NORMAL
			self.combo["state"]=tk.NORMAL
			self.connLblMsg.config(text = "disconnected...")
			self.btnConnectSerial.configure(text = "connect")
			self.logText.insert(END,connStateDict["log"] +"\n")
		pass
	
	def appendLog(self, cmd):
		cmdN = cmd.replace('\n','')
		self.logText.insert("1.0",cmdN +"\n")
	
	def _onClick_close(self):
		#self.animate.pause()
		self.events.onClick_close()
		self.window.destroy()
		print("bye")
		exit()
		pass
	
	def _onChange_mode(self):
		modeDict = {
			"mode":self.modeVar.get()
		}
		self.events.onChange_mode(modeDict)
		pass
	
	def _onChange_state(self):
		stateDict = {
			"state":self.stateVar.get()
		}
		self.events.onChange_state(stateDict)
		pass
	
	def _onChange_direction(self):
		directionDict = {
			"direction":self.stateVar.get()
		}
		self.events.onChange_direction( directionDict)
		pass
	
	def _onClick_eeprom(self, arg):
		eepromDict = {
			"command":arg
		}
		self.events.onClick_eeprom( eepromDict)
		pass
	
	def _onClick_ctrlCmd(self, type, cmd, value, value2 = 0):
		ctrlDict = {
			"command":cmd,
			"type":type,
			"value":value,
			"value2":value2
		}
		self.events.onClick_ctrlCmd( ctrlDict)
		pass
	
	def addSerialPaths(self, paths):
		self.comboCom['values']= paths
		self.comboCom.current(0)
		pass
	
	def mainloop(self):
		self.window.mainloop()
