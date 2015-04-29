from optparse import OptionParser
from skeinforge import euclidean
import routeplanner

class TestCase:
	"""Test case class for other testcases that inherit it."""
	def run(self):
		"""Set up and run test case and return result."""
		self.name = self.__class__.__name__
		self.result = True
		self.run_tests()
		self.teardown()
		return self.result
	
	def run_tests(self):
		"""Run tests. Set result False if fails appear."""
		pass
		
	def teardown(self):
		"""Print result."""
		if self.result == True:
			print self.name + "\t\t[ PASS ]"
		else:
			print self.name + "\t\t[ FAIL ]"

class test_getMaxX(TestCase):
	"""Test getMaxX."""
	small_loop = [complex(2,-2),complex(3,2),complex(-7,5)]
	big_loop = [complex(0,0),complex(0,1),complex(0,2),complex(1,3),complex(1,4),complex(2,5),complex(3,5),complex(4,5),complex(4,0),complex(4,-1),complex(0,0)]
	
	def run_tests(self):
		self.returns_right_value(self.small_loop,3)
		self.returns_right_value(self.big_loop,4)
		
	def returns_right_value(self,loop,right_value):
		if routeplanner.getMaxX(loop) != right_value:
			self.result = False

class test_getMaxY(TestCase):
	"""Test getMaxY."""
	small_loop = [complex(2,-2),complex(3,2),complex(-7,5)]
	big_loop = [complex(0,0),complex(0,1),complex(0,2),complex(1,3),complex(1,4),complex(2,5),complex(3,5),complex(4,5),complex(4,0),complex(4,-1),complex(0,0)]
	
	def run_tests(self):
		self.returns_right_value(self.small_loop,5)
		self.returns_right_value(self.big_loop,5)
		
	def returns_right_value(self,loop,right_value):
		if routeplanner.getMaxY(loop) != right_value:
			self.result = False

class test_getMinX(TestCase):
	"""Test getMinX."""
	small_loop = [complex(2,-2),complex(3,2),complex(-7,5)]
	big_loop = [complex(0,0),complex(0,1),complex(0,2),complex(1,3),complex(1,4),complex(2,5),complex(3,5),complex(4,5),complex(4,0),complex(4,-1),complex(0,0)]
	
	def run_tests(self):
		self.returns_right_value(self.small_loop,-7)
		self.returns_right_value(self.big_loop,0)
		
	def returns_right_value(self,loop,right_value):
		if routeplanner.getMinX(loop) != right_value:
			self.result = False

class test_getMinY(TestCase):
	"""Test getMinY."""
	small_loop = [complex(2,-2),complex(3,2),complex(-7,5)]
	big_loop = [complex(0,0),complex(0,1),complex(0,2),complex(1,3),complex(1,4),complex(2,5),complex(3,5),complex(4,5),complex(4,0),complex(4,-1),complex(0,0)]
	
	def run_tests(self):
		self.returns_right_value(self.small_loop,-2)
		self.returns_right_value(self.big_loop,-1)
		
	def returns_right_value(self,loop,right_value):
		if routeplanner.getMinY(loop) != right_value:
			self.result = False

class test_removeCR(TestCase):
	"""Test removeCR function."""
	array = ["sdfwewef\r\nasdfwef","fwewefwe\rasdfasdfw","\rasdfasfd","sdfasdf\r","asfwfe"]
	empty_array = []
	
	def run_tests(self):
		self.handles_empty_array()
		self.output_doesnt_contain_CR(self.array)
	
	def handles_empty_array(self):
		try:
			routeplanner.removeCR(self.empty_array)
		except:
			self.result = False
		
	def output_doesnt_contain_CR(self, array):
		new_array = routeplanner.removeCR(array)
		for item in new_array:
			if "\r" in item:
				self.result = False
			
if __name__ == "__main__":
	"""Option parser interface."""
	tests = ""
	parser = OptionParser()
	parser.add_option("-t", "--tests", dest="tests",
					  help="select testlist")
	(options, args) = parser.parse_args()
	
	"""Testlists"""
	routeplanner_tests = [test_getMaxX(),test_getMaxY(),test_getMinX(),test_getMinY(),test_removeCR()]
	gui_tests = []
	robot_tests = []
	
	"""Test decision"""
	if options.tests == "routeplanner_tests":
		tests = routeplanner_tests
	if options.tests == "gui_tests":
		tests = gui_tests
	if options.tests == "robot_tests":
		tests = robot_tests
	if options.tests == "all":
		tests = routeplanner_tests + gui_tests + robot_tests
	
	"""Run tests"""
	if options.tests and len(tests) > 0:
		for test in tests:
			test.run()