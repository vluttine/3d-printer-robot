import face
import triangle_mesh
from skeinforge.vector3 import Vector3


def addFacesGivenText( stlText, triangleMesh, vertexIndexTable ):
	"Add faces given stl text."
	lines = getTextLines( stlText )
	vertexes = []
	for line in lines:
		if line.find('vertex') != - 1:
			vertexes.append( getVertexGivenLine(line) )
	addFacesGivenVertexes( triangleMesh, vertexIndexTable, vertexes )

def addFacesGivenVertexes( triangleMesh, vertexIndexTable, vertexes ):
	"Add faces given stl text."
	for vertexIndex in xrange( 0, len(vertexes), 3 ):
		triangleMesh.faces.append( getFaceGivenLines( triangleMesh, vertexIndex, vertexIndexTable, vertexes ) )

def getCarving(fileName=''):
	"Get the triangle mesh for the stl file."
	if fileName == '':
		return None
	stlData = getFileText(fileName, True, 'rb')
	if stlData == '':
		return None
	triangleMesh = triangle_mesh.TriangleMesh()
	vertexIndexTable = {}
	numberOfVertexStrings = stlData.count('vertex')
	requiredVertexStringsForText = max( 2, len( stlData ) / 8000 )
	addFacesGivenText( stlData, triangleMesh, vertexIndexTable )
	return triangleMesh

def getFaceGivenLines( triangleMesh, vertexStartIndex, vertexIndexTable, vertexes ):
	"Add face given line index and lines."
	faceGivenLines = face.Face()
	faceGivenLines.index = len( triangleMesh.faces )
	for vertexIndex in xrange( vertexStartIndex, vertexStartIndex + 3 ):
		vertex = vertexes[vertexIndex]
		vertexUniqueIndex = len( vertexIndexTable )
		if str(vertex) in vertexIndexTable:
			vertexUniqueIndex = vertexIndexTable[ str(vertex) ]
		else:
			vertexIndexTable[ str(vertex) ] = vertexUniqueIndex
			triangleMesh.vertexes.append(vertex)
		faceGivenLines.vertexIndexes.append( vertexUniqueIndex )
	return faceGivenLines

def getFloat(floatString):
	"Get the float, replacing commas if necessary because an inferior program is using a comma instead of a point for the decimal point."
	try:
		return float(floatString)
	except:
		return float( floatString.replace(',', '.') )

def getVertexGivenLine(line):
	"Get vertex given stl vertex line."
	splitLine = line.split()
	return Vector3( getFloat(splitLine[1]), getFloat( splitLine[2] ), getFloat( splitLine[3] ) )

def getFileText(fileName, printWarning=True, readMode='r'):
	'Get the entire text of a file.'
	try:
		file = open(fileName, readMode)
		fileText = file.read()
		file.close()
		return fileText
	except IOError:
		if printWarning:
			print('The file ' + fileName + ' does not exist.')
	return ''

def getTextLines(text):
	'Get the all the lines of text of a text.'
	if '\r' in text:
		text = text.replace('\r', '\n').replace('\n\n', '\n')
	textLines = text.split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines
