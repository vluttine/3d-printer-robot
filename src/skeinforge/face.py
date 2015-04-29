class Edge:
	"An edge of a triangle mesh."
	def __init__(self):
		"Set the face indexes to None."
		self.faceIndexes = []
		self.vertexIndexes = []
		self.zMaximum = None
		self.zMinimum = None

	def addFaceIndex( self, faceIndex ):
		"Add first None face index to input face index."
		self.faceIndexes.append( faceIndex )

	def getFromVertexIndexes( self, edgeIndex, vertexIndexes ):
		"Initialize from two vertex indices."
		self.index = edgeIndex
		self.vertexIndexes = vertexIndexes[:]
		self.vertexIndexes.sort()
		return self


class Face:
	"A face of a triangle mesh."
	def __init__(self):
		"Initialize."
		self.edgeIndexes = []
		self.index = None
		self.vertexIndexes = []

	def setEdgeIndexesToVertexIndexes( self, edges, edgeTable ):
		"Set the edge indexes to the vertex indexes."
		if len(self.edgeIndexes) > 0:
			return
		for triangleIndex in xrange(3):
			indexFirst = ( 3 - triangleIndex ) % 3
			indexSecond = ( 4 - triangleIndex ) % 3
			vertexIndexFirst = self.vertexIndexes[ indexFirst ]
			vertexIndexSecond = self.vertexIndexes[ indexSecond ]
			vertexIndexPair = [ vertexIndexFirst, vertexIndexSecond ]
			vertexIndexPair.sort()
			edgeIndex = len( edges )
			if str( vertexIndexPair ) in edgeTable:
				edgeIndex = edgeTable[ str( vertexIndexPair ) ]
			else:
				edgeTable[ str( vertexIndexPair ) ] = edgeIndex
				edge = Edge().getFromVertexIndexes( edgeIndex, vertexIndexPair )
				edges.append( edge )
			edges[ edgeIndex ].addFaceIndex( self.index )
			self.edgeIndexes.append( edgeIndex )
