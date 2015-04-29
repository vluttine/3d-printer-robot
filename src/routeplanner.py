'''
Software Project course
Routeplanner
Roope Kallio & Ville Luttinen
14.6.2014

This module takes in a stl file and designs the printing route for robot.
'''

import sockets, sys
from optparse import OptionParser
from skeinforge import carve
from skeinforge import euclidean
import math

class Coordinate:
	"""Coordinate point"""
	x = None
	y = None
	z = None

	def __init__(self, x, y, z):
		"""Set coordinate point."""
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

def scaleCoordinates(coordinates):
	"""Divide each coordinate with absolute maximum x or y which ever is greater. Then divide with 15.
	Return scaled coordinates."""
	maximum = 0
	for coordinate in coordinates:
		if abs(coordinate.x) > maximum:
			maximum = abs(coordinate.x)
		if abs(coordinate.y) > maximum:
			maximum = abs(coordinate.y)
	for coordinate in coordinates:
		coordinate.x = coordinate.x / maximum / 15
		coordinate.y = coordinate.y / maximum / 15
	return coordinates

def scaleLoopLayers(loopLayers,maxDimension):
	"""Get absolute maximum real or imag which ever is greater. Then scale so that the absolute maximum of reals and images is maxDimension.
	Return scaled loopLayers."""
	scaledLoopLayers = []
	maximum = 0
	for loopLayer in loopLayers:
		for loop in loopLayer.loops:
			for coordinate in loop:
				if abs(coordinate.real) > maximum:
					maximum = abs(coordinate.real)
				if abs(coordinate.imag) > maximum:
					maximum = abs(coordinate.imag)
	for loopLayer in loopLayers:
		scaledLoops = []
		for loop in loopLayer.loops:
			scaledLoop = []
			for coordinate in loop:
				x = coordinate.real / (maximum / float(maxDimension))
				y = coordinate.imag / (maximum / float(maxDimension))
				scaledLoop.append(complex(x,y))
				
			scaledLoops.append(scaledLoop)
			
		scaledLoopLayer = euclidean.LoopLayer(loopLayer.z)
		scaledLoopLayer.loops = scaledLoops
		
		scaledLoopLayers.append(scaledLoopLayer)
	return scaledLoopLayers
	
def calcCoordinates(filename):
	"""Use skeinforges carve to read stl file and carve prefaces of the object.
	Return loopLayers."""
	f = open("routeplanner_data/vertices.txt", 'w')
	f.close()
	f = open("routeplanner_data/coordinates.txt", 'w')
	f.close()
	return carve.getCraftedText(filename)


def readCoordinates(filename):
	"""Read coordinates from a file.
	Return coordinates."""
	coordinates = []
	f = open(filename, 'r')
	for line in f.readlines():
		coordinate = line.strip('\n').split(',')
		if len(coordinate) == 3:
			new_coordinate = Coordinate(coordinate[0],coordinate[1],coordinate[2])
			coordinates.append(new_coordinate)
	f.close()
	coordinates = scaleCoordinates(coordinates)
	return coordinates

def sendCoordinate(coordinate):
	"""Send route to robot via TCP."""
	client2Robot = sockets.TCPsocket("client","localhost",50005)
	messageSent = 0
	while messageSent == 0:
		messageSent = client2Robot.sendMessage("1;ROUTE;%s" %(str(coordinate)), "localhost", 50005)
	client2Robot.close()


def sendCoordinates2RobotInterface(fullRoute):
	"""Send routes by each layer. Enter is required for next layer."""
	server2Robot = sockets.TCPsocket("server","localhost",50003)
	layerIndex = 0
	for layer in fullRoute:
		layerIndex += 1
		for route in layer:
			first = True
			coordinate_string = "["
			for coordinate in route:
				if not first:
					coordinate_string = coordinate_string + ", "
				first = False
				coordinate_string = coordinate_string + "[%f, %f, %f]" %(coordinate.x, coordinate.y, coordinate.z)
			coordinate_string = coordinate_string + "]"
			sendCoordinate(coordinate_string)
			while server2Robot.getMessage()[0] != "ACK":
				pass
		print "Sent layer " + str(layerIndex)
		print "Press Enter to proceed."
		raw_input()
	print "Sent all layers."
	server2Robot.close()

def getFilledLayer(loopLayer, sampling_rate):
	"""Calculate filling of layer from loop layers. Sample the layer by sampling rate.
	Return routes for the layer."""
	routes = []
	firstInside = True
	firstOutside = False
	z = loopLayer.z
	[maxX, maxY, minX, minY] = getLayerMaxesAndMins(loopLayer)
	x = minX-sampling_rate
	while x <= maxX+sampling_rate:
		y = minY
		while y <= maxY:
			if euclidean.getIsInFilledRegion(loopLayer.loops, complex(x,y)):
				if firstInside:
					route = [Coordinate(x,y,z)]
					firstInside = False
				else:
					route.append(Coordinate(x,y,z))
				firstOutside = True
			else:
				if firstOutside:
					if len(route)>2:
						route = [route[0],route[-1]]  #Take only start and end points
					routes.append(route)
					firstOutside = False
				firstInside = True
			y += sampling_rate
		x += sampling_rate
	return routes

def rotateCoordinates(fullRoute,angle):
	"""Rotate coordinates by an angle over y-axel.
	Return fullRoute."""
	for routes in fullRoute:
		for route in routes:
			for point in route:
				angleRads = float(angle)*math.pi/180
				point.x = math.cos(angleRads)*point.x+0*point.y+math.sin(angleRads)*point.z
				point.y = 0*point.x+1*point.y+0*point.z
				point.z = -math.sin(angleRads)*point.x+0*point.y+math.cos(angleRads)*point.z
	return fullRoute
				

def writeVertices(fullRoutes):
	"""Write routes to file in openGL form. Use this for debugging."""
	f = open('routeplanner_data/vertices2.txt','w')
	for routes in fullRoutes:
		for route in routes:
			f.write("    glBegin(GL_LINE_LOOP)\n")
			for point in route:
				f.write("    glVertex3f(%s, %s, %s)\n" %(point.x, point.y, point.z))
			f.write("    glEnd()\n")
	f.close()

def getLayerMaxesAndMins(loopLayer):
	"""Get boundaries of the layer.
	Return max and y values of loopLayer reals and imags."""
	maxXlist = []
	maxYlist = []
	minXlist = []
	minYlist = []
	for loop in loopLayer.loops:
		maxXlist.append(getMaxX(loop))
		maxYlist.append(getMaxY(loop))
		minXlist.append(getMinX(loop))
		minYlist.append(getMinY(loop))
	maxX = max(maxXlist)
	maxY = max(maxYlist)
	minX = min(minXlist)
	minY = min(minYlist)
	return [maxX, maxY, minX, minY]
	
def getMaxX(loop):
	"""Return max real."""
	for point in loop:
		try:
			if point.real > max:
				max = point.real
		except NameError:
			max = point.real
	return max

def getMaxY(loop):
	"""Return max imag."""
	for point in loop:
		try:
			if point.imag > max:
				max = point.imag
		except NameError:
			max = point.imag
	return max

def getMinX(loop):
	"""Return min real."""
	for point in loop:
		try:
			if point.real < min:
				min = point.real
		except NameError:
			min = point.real
	return min

def getMinY(loop):
	"""Return min imag."""
	for point in loop:
		try:
			if point.imag < min:
				min = point.imag
		except NameError:
			min = point.imag
	return min
			
def GUIRun(filename, samplingRate, send, angle, maxDim):
	"""GUI-interface for running routeplanner.
	Return 1."""
	try:
		float(samplingRate)
	except:
		print "Sampling rate must be a float."
		return 0
	print "Sampling rate: " + str(samplingRate)
	print "Angle: " + str(angle)
	print "Maximum dimension: " + str(maxDim)
	print "Send to robot: " + str(send)
	main(filename, float(samplingRate), send, angle, maxDim)
	return 1

def removeCR(array):
	"""Remove carriage return characters from an array of strings.
	Return array without CR characters."""
	newArray = []
	for item in array:
		item = item.replace("\r","")
		newArray.append(item)
	return newArray


def testCarving():
	"""Test skeinforge craft with two test files.
	Return True if test passes and false if test fails."""
	print "Testing carving stldata/test.stl file..."
	f = open("routeplanner_data/Carve coordinates.txt",'r')
	original = removeCR(f.readlines())
	f.close()
	calcCoordinates("stldata/test.stl")
	coordinates = readCoordinates("routeplanner_data/coordinates.txt")
	
	f = open("routeplanner_data/coordinates.txt",'r')
	result = removeCR(f.readlines())
	f.close()
	
	if len(original) == len(result):
		for i in range(0,len(original)):
			if not original[i] == result[i]:
				return False
	else:
		return False

	print "Testing carving stldata/top.stl file..."
	f = open("routeplanner_data/Carve coordinates2.txt",'r')
	original = removeCR(f.readlines())
	f.close()
	calcCoordinates("stldata/top.stl")
	coordinates = readCoordinates("routeplanner_data/coordinates.txt")
	
	f = open("routeplanner_data/coordinates.txt",'r')
	result = removeCR(f.readlines())
	f.close()
	
	if len(original) == len(result):
		for i in range(0,len(original)):
			if not original[i] == result[i]:
				return False
	else:
		return False

	return True
	

def main(filename, sampling_rate, send, angle,max_dimension):
	"""Main."""
	loopLayers = calcCoordinates(filename)
	print "Scaling layers..."
	loopLayers = scaleLoopLayers(loopLayers,max_dimension)
	fullRoute = []
	layerIndex = 0
	print "Calculating layers..."
	for loopLayer in loopLayers:
		layerIndex += 1
		fullRoute.append(getFilledLayer(loopLayer, sampling_rate))
		print "Layer " + str(layerIndex) + " done."
	#writeVertices(fullRoute) # Use for debugging routes
	
	if angle != 0:
		fullRoute = rotateCoordinates(fullRoute,angle)
	
	if send:
		print "Send route to robot..."
		sendCoordinates2RobotInterface(fullRoute)

	print "Done. Routeplanner will now close."
	
if __name__ == "__main__":
	"""Option parser interface."""
	parser = OptionParser()
	parser.add_option("-f", "--file", dest="filename",
					  help="select stl file", metavar="FILE")
	parser.add_option("-t", "--test_carving", action="store_true", dest="test", default=False,
					  help="test carving")
	parser.add_option("-s", "--sampling_rate", dest="sampling_rate", default=0.0001,
					  help="set sampling_rate")
	parser.add_option("-d", "--send", action="store_true", dest="send", default=False,
					  help="send to robot interface")
	parser.add_option("-r", "--rotate", dest="angle", default=0.0,
					  help="enable rotating and set angle in degrees")
	parser.add_option("-m", "--max_dimension", dest="max_dimension", default=0.1,
					  help="set maximum dimension")
					  
	(options, args) = parser.parse_args()
	
	if options.test == True:
		result = testCarving()
		if result == True:
			print "[ PASS ]"
			sys.exit(1)
		if result == False:
			print "[ FAIL ]"
			sys.exit(0)
	
	if options.sampling_rate:
		try:
			float(options.sampling_rate)
		except:
			print "Error: Give float as sampling rate"
			sys.exit(0)
	
	if options.filename:
		main(options.filename, float(options.sampling_rate), options.send,options.angle,options.max_dimension)

