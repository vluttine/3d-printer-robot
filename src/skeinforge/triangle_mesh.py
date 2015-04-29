from skeinforge.vector3 import Vector3
from skeinforge import euclidean
import math

def getCarveIntersectionFromEdge(edge, vertexes, z):
	'Get the complex where the carve intersects the edge.'
	firstVertex = vertexes[ edge.vertexIndexes[0] ]
	firstVertexComplex = firstVertex.dropAxis()
	secondVertex = vertexes[ edge.vertexIndexes[1] ]
	secondVertexComplex = secondVertex.dropAxis()
	zMinusFirst = z - firstVertex.z
	up = secondVertex.z - firstVertex.z
	return zMinusFirst * ( secondVertexComplex - firstVertexComplex ) / up + firstVertexComplex

def getLoopsFromCorrectMesh( edges, faces, vertexes, z ):
	'Get loops from a carve of a correct mesh.'
	remainingEdgeTable = getRemainingEdgeTable(edges, vertexes, z)
	remainingValues = remainingEdgeTable.values()
	loops = []
	while isPathAdded( edges, faces, loops, remainingEdgeTable, vertexes, z ):
		pass
	return loops

def getLoopLayerAppend(loopLayers, z):
	'Get next z and add extruder loops.'
	loopLayer = euclidean.LoopLayer(z)
	loopLayers.append(loopLayer)
	return loopLayer

def getNextEdgeIndexAroundZ(edge, faces, remainingEdgeTable):
	'Get the next edge index in the mesh carve.'
	for faceIndex in edge.faceIndexes:
		face = faces[faceIndex]
		for edgeIndex in face.edgeIndexes:
			if edgeIndex in remainingEdgeTable:
				return edgeIndex
	return -1

def getOrientedLoops(loops):
	'Orient the loops which must be in descending order.'
	for loopIndex, loop in enumerate(loops):
		leftPoint = euclidean.getLeftPoint(loop)
		isInFilledRegion = euclidean.getIsInFilledRegion(loops[: loopIndex] + loops[loopIndex + 1 :], leftPoint)
		if isInFilledRegion == euclidean.isWiddershins(loop):
			loop.reverse()
	return loops

def getPath( edges, pathIndexes, loop, z ):
	'Get the path from the edge intersections.'
	path = []
	for pathIndexIndex in xrange( len( pathIndexes ) ):
		pathIndex = pathIndexes[ pathIndexIndex ]
		edge = edges[ pathIndex ]
		carveIntersection = getCarveIntersectionFromEdge( edge, loop, z )
		path.append( carveIntersection )
	return path

def getRemainingEdgeTable(edges, vertexes, z):
	'Get the remaining edge hashtable.'
	remainingEdgeTable = {}
	if len(edges) > 0:
		if edges[0].zMinimum == None:
			for edge in edges:
				setEdgeMaximumMinimum(edge, vertexes)
	for edgeIndex in xrange(len(edges)):
		edge = edges[edgeIndex]
		if (edge.zMinimum < z) and (edge.zMaximum > z):
			remainingEdgeTable[edgeIndex] = edge
	return remainingEdgeTable

def isPathAdded( edges, faces, loops, remainingEdgeTable, vertexes, z ):
	'Get the path indexes around a triangle mesh carve and add the path to the flat loops.'
	if len( remainingEdgeTable ) < 1:
		return False
	pathIndexes = []
	remainingEdgeIndexKey = remainingEdgeTable.keys()[0]
	pathIndexes.append( remainingEdgeIndexKey )
	del remainingEdgeTable[remainingEdgeIndexKey]
	nextEdgeIndexAroundZ = getNextEdgeIndexAroundZ( edges[remainingEdgeIndexKey], faces, remainingEdgeTable )
	while nextEdgeIndexAroundZ != - 1:
		pathIndexes.append( nextEdgeIndexAroundZ )
		del remainingEdgeTable[ nextEdgeIndexAroundZ ]
		nextEdgeIndexAroundZ = getNextEdgeIndexAroundZ( edges[ nextEdgeIndexAroundZ ], faces, remainingEdgeTable )
	if len( pathIndexes ) < 3:
		print('Dangling edges, will use intersecting circles to get import layer at height %s' % z)
		del loops[:]
		return False
	loops.append( getPath( edges, pathIndexes, vertexes, z ) )
	return True

def setEdgeMaximumMinimum(edge, vertexes):
	'Set the edge maximum and minimum.'
	beginIndex = edge.vertexIndexes[0]
	endIndex = edge.vertexIndexes[1]
	if beginIndex >= len(vertexes) or endIndex >= len(vertexes):
		print('Warning, there are duplicate vertexes in setEdgeMaximumMinimum in triangle_mesh.')
		print('Something might still be printed, but there is no guarantee that it will be the correct shape.' )
		edge.zMaximum = -987654321.0
		edge.zMinimum = -987654321.0
		return
	beginZ = vertexes[beginIndex].z
	endZ = vertexes[endIndex].z
	edge.zMinimum = min(beginZ, endZ)
	edge.zMaximum = max(beginZ, endZ)

def sortLoopsInOrderOfArea(isDescending, loops):
	'Sort the loops in the order of area according isDescending.'
	loops.sort(key=euclidean.getAreaLoopAbsolute, reverse=isDescending)

class TriangleMesh( ):
	'A triangle mesh.'
	def __init__(self):
		'Add empty lists.'
		self.elementNode = None
		self.edges = []
		self.faces = []
		self.isCorrectMesh = True
		self.loopLayers = []
		self.vertexes = []

	def getCarveBoundaryLayers(self):
		'Get the boundary layers.'
		if self.getMinimumZ() == None:
			return []
		halfHeight = 0.5 * self.layerHeight
		self.zoneArrangement = ZoneArrangement(self.layerHeight, self.getTransformedVertexes())
		layerTop = self.cornerMaximum.z - halfHeight * 0.5
		z = self.cornerMinimum.z + halfHeight
		while z < layerTop:
			getLoopLayerAppend(self.loopLayers, z).loops = self.getLoopsFromMesh(self.zoneArrangement.getEmptyZ(z))
			z += self.layerHeight
		return self.loopLayers

	def getLoopsFromMesh( self, z ):
		'Get loops from a carve of a mesh.'
		originalLoops = []
		self.setEdgesForAllFaces()
		if self.isCorrectMesh:
			originalLoops = getLoopsFromCorrectMesh( self.edges, self.faces, self.getTransformedVertexes(), z )
		if len( originalLoops ) < 1:
			originalLoops = getLoopsFromUnprovenMesh( self.edges, self.faces, self.importRadius, self.getTransformedVertexes(), z )
		loops = euclidean.getSimplifiedLoops(originalLoops)
		sortLoopsInOrderOfArea(True, loops)
		return getOrientedLoops(loops)

	def getMinimumZ(self):
		'Get the minimum z.'
		self.cornerMaximum = Vector3(-987654321.0, -987654321.0, -987654321.0)
		self.cornerMinimum = Vector3(987654321.0, 987654321.0, 987654321.0)
		transformedVertexes = self.getTransformedVertexes()
		if len(transformedVertexes) < 1:
			return None
		for point in transformedVertexes:
			self.cornerMaximum.maximize(point)
			self.cornerMinimum.minimize(point)
		return self.cornerMinimum.z

	def getTransformedVertexes(self):
		'Get all transformed vertexes.'
		if self.elementNode == None:
			return self.vertexes

	def setCarveLayerHeight( self, layerHeight ):
		'Set the layer height.'
		self.layerHeight = layerHeight

	def setEdgesForAllFaces(self):
		'Set the face edges of all the faces.'
		edgeTable = {}
		for face in self.faces:
			face.setEdgeIndexesToVertexIndexes( self.edges, edgeTable )


class ZoneArrangement:
	'A zone arrangement.'
	def __init__(self, layerHeight, vertexes):
		'Initialize the zone interval and the zZone table.'
		self.zoneInterval = layerHeight / math.sqrt(len(vertexes)) / 1000.0
		self.zZoneSet = set()
		for point in vertexes:
			zoneIndexFloat = point.z / self.zoneInterval
			self.zZoneSet.add(math.floor(zoneIndexFloat))
			self.zZoneSet.add(math.ceil(zoneIndexFloat ))

	def getEmptyZ(self, z):
		'Get the first z which is not in the zone table.'
		zoneIndex = round(z / self.zoneInterval)
		if zoneIndex not in self.zZoneSet:
			return z
		zoneAround = 1
		while 1:
			zoneDown = zoneIndex - zoneAround
			if zoneDown not in self.zZoneSet:
				return zoneDown * self.zoneInterval
			zoneUp = zoneIndex + zoneAround
			if zoneUp not in self.zZoneSet:
				return zoneUp * self.zoneInterval
			zoneAround += 1
