def getAreaLoop(loop):
	'Get the area of a complex polygon.'
	areaLoopDouble = 0.0
	for pointIndex, point in enumerate(loop):
		pointEnd  = loop[(pointIndex + 1) % len(loop)]
		areaLoopDouble += point.real * pointEnd.imag - pointEnd.real * point.imag
	return 0.5 * areaLoopDouble

def getAreaLoopAbsolute(loop):
	'Get the absolute area of a complex polygon.'
	return abs(getAreaLoop(loop))

def getAwayPoints(points):
	'Get a path with only the points that are far enough away from each other.'
	radius = 1
	awayPoints = []
	oneOverOverlapDistance = 1000.0 / radius
	pixelDictionary = {}
	for point in points:
		x = int(point.real * oneOverOverlapDistance)
		y = int(point.imag * oneOverOverlapDistance)
		if not getSquareIsOccupied(pixelDictionary, x, y):
			awayPoints.append(point)
			pixelDictionary[(x, y)] = None
	return awayPoints

def getDotProduct(firstComplex, secondComplex):
	'Get the dot product of a pair of complexes.'
	return firstComplex.real * secondComplex.real + firstComplex.imag * secondComplex.imag

def getDotProductPlusOne( firstComplex, secondComplex ):
	'Get the dot product plus one of the x and y components of a pair of Vector3s.'
	return 1.0 + getDotProduct( firstComplex, secondComplex )

def getHalfSimplifiedLoop( loop, remainder ):
	'Get the loop with half of the points inside the channel removed.'
	radius = 1
	if len(loop) < 2:
		return loop
	channelRadius = radius * .01
	simplified = []
	addIndex = 0
	if remainder == 1:
		addIndex = len(loop) - 1
	for pointIndex in xrange(len(loop)):
		point = loop[pointIndex]
		if pointIndex % 2 == remainder or pointIndex == addIndex:
			simplified.append(point)
		elif not isWithinChannel( channelRadius, pointIndex, loop ):
			simplified.append(point)
	return simplified

def getIsInFilledRegion(loops, point):
	'Determine if the point is in the filled region of the loops.'
	return getNumberOfIntersectionsToLeftOfLoops(loops, point) % 2 == 1


def getLeftPoint(points):
	'Get the leftmost complex point in the points.'
	leftmost = 987654321.0
	leftPointComplex = None
	for pointComplex in points:
		if pointComplex.real < leftmost:
			leftmost = pointComplex.real
			leftPointComplex = pointComplex
	return leftPointComplex
    
def getNumberOfIntersectionsToLeft(loop, point):
	'Get the number of intersections through the loop for the line going left.'
	numberOfIntersectionsToLeft = 0
	for pointIndex in xrange(len(loop)):
		firstPointComplex = loop[pointIndex]
		secondPointComplex = loop[(pointIndex + 1) % len(loop)]
		xIntersection = getXIntersectionIfExists(firstPointComplex, secondPointComplex, point.imag)
		if xIntersection != None:
			if xIntersection < point.real:
				numberOfIntersectionsToLeft += 1
	return numberOfIntersectionsToLeft

def getNumberOfIntersectionsToLeftOfLoops(loops, point):
	'Get the number of intersections through the loop for the line starting from the left point and going left.'
	totalNumberOfIntersectionsToLeft = 0
	for loop in loops:
		totalNumberOfIntersectionsToLeft += getNumberOfIntersectionsToLeft(loop, point)
	return totalNumberOfIntersectionsToLeft

def getSimplifiedLoop( loop):
	'Get loop with points inside the channel removed.'
	if len(loop) < 2:
		return loop
	simplificationMultiplication = 256
	maximumIndex = len(loop) * simplificationMultiplication
	pointIndex = 1
	while pointIndex < maximumIndex:
		oldLoopLength = len(loop)
		loop = getHalfSimplifiedLoop( loop, 0 )
		loop = getHalfSimplifiedLoop( loop, 1 )
		pointIndex += pointIndex
	return getAwayPoints( loop)

def getSimplifiedLoops( loops):
	'Get the simplified loops.'
	simplifiedLoops = []
	for loop in loops:
		simplifiedLoops.append( getSimplifiedLoop( loop) )
	return simplifiedLoops

def getSquareIsOccupied( pixelDictionary, x, y ):
	'Determine if a square around the x and y pixel coordinates is occupied.'
	squareValues = []
	for xStep in xrange(x - 1, x + 2):
		for yStep in xrange(y - 1, y + 2):
			if (xStep, yStep) in pixelDictionary:
				return True
	return False

def getXIntersectionIfExists( beginComplex, endComplex, y ):
	'Get the x intersection if it exists.'
	if ( y > beginComplex.imag ) == ( y > endComplex.imag ):
		return None
	endMinusBeginComplex = endComplex - beginComplex
	return ( y - beginComplex.imag ) / endMinusBeginComplex.imag * endMinusBeginComplex.real + beginComplex.real

def isWiddershins(polygonComplex):
	'Determine if the complex polygon goes round in the widdershins direction.'
	return getAreaLoop(polygonComplex) > 0.0

def isWithinChannel( channelRadius, pointIndex, loop ):
	'Determine if the the point is within the channel between two adjacent points.'
	point = loop[pointIndex]
	behindSegmentComplex = loop[(pointIndex + len(loop) - 1) % len(loop)] - point
	behindSegmentComplexLength = abs( behindSegmentComplex )
	if behindSegmentComplexLength < channelRadius:
		return True
	aheadSegmentComplex = loop[(pointIndex + 1) % len(loop)] - point
	aheadSegmentComplexLength = abs( aheadSegmentComplex )
	if aheadSegmentComplexLength < channelRadius:
		return True
	behindSegmentComplex /= behindSegmentComplexLength
	aheadSegmentComplex /= aheadSegmentComplexLength
	absoluteZ = getDotProductPlusOne( aheadSegmentComplex, behindSegmentComplex )
	if behindSegmentComplexLength * absoluteZ < channelRadius:
		return True
	return aheadSegmentComplexLength * absoluteZ < channelRadius

class LoopLayer:
	'Loops with a z.'
	def __init__(self, z):
		'Initialize.'
		self.loops = []
		self.z = z

	def __repr__(self):
		'Get the string representation of this loop layer.'
		return '%s, %s' % (self.z, self.loops)


