class Vector3:
	'A three dimensional vector class.'

	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x
		self.y = y
		self.z = z

	def __repr__(self):
		'Get the string representation of this Vector3.'
		return '(%s, %s, %s)' % ( self.x, self.y, self.z )

	def dropAxis( self, which = 2 ):
		'Get a complex by removing one axis of the vector3.'
		if which == 0:
			return complex( self.y, self.z )
		if which == 1:
			return complex( self.x, self.z )
		if which == 2:
			return complex( self.x, self.y )

	def maximize(self, other):
		'Maximize the Vector3.'
		self.x = max(other.x, self.x)
		self.y = max(other.y, self.y)
		self.z = max(other.z, self.z)

	def minimize(self, other):
		'Minimize the Vector3.'
		self.x = min(other.x, self.x)
		self.y = min(other.y, self.y)
		self.z = min(other.z, self.z)

