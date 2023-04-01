#main logic for yapscController interface
#menymp 2023

from yapscState import yapscState
# from yapscGui import yapscGui

# yapscGuiObj = yapscGui()

# connState = 1

# def connectClick(self, connObj):
	# global connState
	# print("cyka")
	# print("attempt to connect: "+connObj["port"]+" "+ connObj["baud"])
	# if(connState):
		# connectResult = {
			# "state":"connected",
			# "log":"correctly connected",
			# "comm":"1"
		# }
		# connState = 0
	# else:
		# connectResult = {
			# "state":"disconnected",
			# "log":"disconnected",
			# "comm":"1"
		# }
		# connState = 1
	# self.setCommState(connectResult)
	# self.pushEncoderValue(3)
	# self.pushSetpointValue(-3)
	# self.pushErrorValue(3)
	# self.pushOutputValue(-3)
	# self.setCurrentValues(initObj)
	# pass

# def closeClick(self):
	# print("blyat")
	# pass

#ToDo: an object will act as a bridge for yapscController and yapscGui
#
#     yapscGui ---- update Something ---->     yapscState ------ sends command -----> yapscController
#              <--- updates apperance ------               <------- gets response ----
#

# initObj = {
	# "state":0,
	# "mode":1,
	# "setpoint":"2",
	# "samplet":"3",
	# "outlow":"4",
	# "outhigh":"5",
	# "outspeed":"6",
	# "encoder":"7",
	# "kp":"8",
	# "kd":"9",
	# "ki":"10"
# }

if __name__ == "__main__":
	yapscObj = yapscState()
	yapscObj.uiLoop()
	#yapscGuiObj.events.onClick_connect += connectClick
	#yapscGuiObj.events.onClick_close   += closeClick
	#yapscGuiObj.setErrorLabel(-550)
	#yapscGuiObj.mainloop()
	pass