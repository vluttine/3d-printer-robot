'''
Software Project course
GcodeParser
Roope Kallio & Ville Luttinen
14.6.2014

This module is not used anywhere in the project.
This can be used however for creating openGL code from GCODE.
'''

import sys

def readfile(filename):
	f = open(filename,'r')
	lines = f.readlines()
	return lines
		
def parseData(data):
	layers = []
	path = []
	for line in data:
		if 'G1' in line:
			line_wos = line.split()
			x = float(line_wos[1].strip('X'))
			y = float(line_wos[2].strip('Y'))
			z = float(line_wos[3].strip('Z'))
			path.append([x,y,z])
		if 'M103' in line:
			layers.append(path)
			path = []
	return layers

def createOpenGL(layers):
	f = open('routeplanner_data/opengl.txt','w')
	for i in range(0,len(layers)):
		f.write("    glBegin(GL_LINES)\n")
		for j in range(0,len(layers[i])):
			
			f.write("    glVertex3f(%s, %s, %s)\n" %(layers[i][j][0],layers[i][j][1],layers[i][j][2]))
		f.write("    glEnd()\n")
	f.close()

def main(arguments):
	filename = sys.argv[1]
	data = readfile(filename)
	lista = parseData(data)
	createOpenGL(lista)
	
	
main(sys.argv)