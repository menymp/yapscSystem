'''
		matplotlib.use('TkAgg')
		# prepare data
		data = {
			'1': -11.27,
			'2': -11.16,
			'3': -10.46,
			'4': -7.5,
			'5': -5.26,
			'6': 11.27,
			'7': 11.16,
			'8': 10.46,
			'9': 7.5,
			'10': 11.27,
			'11': 11.16,
			'12': 10.46,
			'13': 7.5,
			'14': 5.26,
			'15': 11.27,
			'16': 11.16,
			'17': 10.46,
			'18': 7.5,
			'19': 5.26,
			'20': 0.0
		}
		
		data2 = {
			'1': -1,
			'2': -2,
			'3': -3,
			'4': -4,
			'5': -5,
			'6': 1,
			'7': 2,
			'8': 3,
			'9': 4,
			'10': 5,
			'11': 1,
			'12': 1,
			'13': 1,
			'14': 1,
			'15': 1,
			'16': 3,
			'17': 3,
			'18': 3,
			'19': 3,
			'20': 0.0
		}
		
		languages = data.keys()
		popularity = data.values()
		
		x = data2.keys()
		y = data2.values()
		
		# create a figure
		#figure = Figure(figsize=(6, 4), dpi=100)
		figure = Figure(figsize=(7.7, 4), dpi=100)
		# create FigureCanvasTkAgg object
		figure_canvas = FigureCanvasTkAgg(figure, self.window)
		
		navFrame = LabelFrame(self.window, text="nav")
		navFrame.grid(column=0, row=10, columnspan=4)
		# create the toolbar
		NavigationToolbar2Tk(figure_canvas, navFrame)
		
		# create axes
		axes = figure.add_subplot()
		
		# create the barchart
		axes.plot(languages, popularity)
		axes.set_title('Time')
		axes.set_ylabel('value')
		axes.grid()
		
		
		# create the barchart
		axes.plot(x, y, dashes=[4, 4])
		
		figure_canvas.get_tk_widget().grid(column=0, row=9, columnspan=4)
		
		#dataframe = plot
		pass
'''

	def _renderGraphs(self):
		#in one graph setpoint and encoder
		self.axes.clear()
		self.axes2.clear()
		self.axes.plot(self.encoderX, self.encoderY, label="Encoder")
		self.axes.plot(self.setpointX, self.setpointY, label="Setpoint", dashes=[4, 4])
		self.axes.legend()
		#in the other output and error
		self.axes2.plot(self.outputX, self.outputY, label="Output") #ToDo: change form
		self.axes2.plot(self.errorX, self.errorY, label="Error", dashes=[4, 4]) #ToDo: change form
		self.axes2.legend()
		
		self.figure_canvas.draw()
		self.figure_canvas2.draw()
		pass
	
	def _initGraphData(self):
		#toDo: set len as property
		self.encoderY = [0 for i in range(0, 30)] 
		self.encoderX = list(range(0, 30))
		self.setpointY = [0 for i in range(0, 30)] 
		self.setpointX = list(range(0, 30))
		self.errorY = [0 for i in range(0, 30)] 
		self.errorX = list(range(0, 30))
		self.outputY = [0 for i in range(0, 30)] 
		self.outputX = list(range(0, 30))
	
	def _buildMatplotLibGraph(self):
		
		matplotlib.use('TkAgg')
		# prepare data
		
		self._initGraphData()
		
		# create a figure
		#figure = Figure(figsize=(6, 4), dpi=100)
		self.figure = Figure(figsize=(7.7, 4), dpi=100)
		self.figure2 = Figure(figsize=(7.7, 2), dpi=100)
		# create FigureCanvasTkAgg object
		self.figure_canvas = FigureCanvasTkAgg(self.figure, self.window)
		self.figure_canvas2 = FigureCanvasTkAgg(self.figure2, self.window)
		navFrame = LabelFrame(self.window, text="nav")
		navFrame.grid(column=0, row=11, columnspan=4)
		# create the toolbar
		NavigationToolbar2Tk(self.figure_canvas, navFrame)
		
		# create axes
		self.axes = self.figure.add_subplot()
		self.axes.set_title('Time')
		self.axes.set_ylabel('value')
		self.axes.grid()
		self.line1, = self.axes.plot(self.encoderX, self.encoderY, label="Encoder")
		self.line2, = self.axes.plot(self.setpointX, self.setpointY, label="Setpoint", dashes=[4, 4])
		self.axes.legend()
		
		self.axes2 = self.figure2.add_subplot()
		self.axes2.set_title('Time')
		self.axes2.set_ylabel('value')
		self.axes2.grid()
		
		self.figure_canvas.get_tk_widget().grid(column=0, row=9, columnspan=4)
		self.figure_canvas2.get_tk_widget().grid(column=0, row=10, columnspan=4)
		# create the initial plot
		self._renderGraphs()
		
		self.animate = animation.FuncAnimation(self.figure, self._animateFig1, init_func=self._animateInitFig1, interval = 20, blit = True)
		#dataframe = plot
		pass
	
	def _animateFig1(self, i):
		self.lockDraw1.acquire()
		self.line1.set_data(self.encoderX, self.encoderY)
		self.figure.gca().relim() #ToDo: check for data and update ToDo2: Check why did i wrote this ToDo in the first place!!!!! NVM i figured it out :v
		self.figure.gca().autoscale_view()
		self.lockDraw1.release()
		return self.line1,
	
	def _animateInitFig1(self):
		self.line1.set_data([], [])
		return self.line1,