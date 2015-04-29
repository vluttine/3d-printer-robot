import stl

def getCraftedText( fileName, repository=None):
	"Get carved text."
	carving = stl.getCarving(fileName)
	repository = CarveRepository()
	return CarveSkein().getCarvedSVG( carving, repository )

class CarveRepository:
	"A class to handle the carve settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		self.edgeWidthOverHeight = 1.8
		self.importCoarseness = 1.0
		self.layerHeight = 0.4


class CarveSkein:
	"A class to carve a carving."
	def getCarvedSVG(self, carving, repository):
		"Parse gnu triangulated surface text and store the carved gcode."
		layerHeight = repository.layerHeight
		edgeWidth = repository.edgeWidthOverHeight * layerHeight
		carving.setCarveLayerHeight(layerHeight)
		# carving.importRadius = 2
		loopLayers = carving.getCarveBoundaryLayers()
		f = open('routeplanner_data/vertices.txt','w')
		f2 = open('routeplanner_data/coordinates.txt','w')
		for loopLayer in loopLayers:
			for loop in loopLayer.loops:
				f2.write("<layer>\n")
				f.write("    glBegin(GL_LINE_LOOP)\n")
				for i in range (0,len(loop)):
					f.write("    glVertex3f(%s, %s, %s)\n" %(loop[i].real,loop[i].imag, loopLayer.z))
					f2.write("%s,%s,%s\n" %(loop[i].real,loop[i].imag, loopLayer.z))
				f.write("    glEnd()\n")
		f2.close()
		f.close()
		return loopLayers
