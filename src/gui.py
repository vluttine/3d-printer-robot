'''
Software Project course
GUI for 3D printer
Joni Saunavaara
10.6.2014
'''

import time
import pyglet
import glydget
import Tkinter
import tkFileDialog
import numpy
import itertools
import json

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays.vbo import VBO
from libtatlin.stlparser import StlParser, StlParseError
from functools import partial

import sockets  # TCP
#import parser  # SVG parser
import routeplanner  # STL router


'''
Pyglet, glydget & Tkinter variables
'''

window = pyglet.window.Window(
    fullscreen=False, resizable=True, height=600, width=800,
    vsync=1
)

# demo object rotation start values
rot = rot2 = 180
rot3 = 0


stl_filename = None
svg_file = None
points = []
# setup glydget menu
dx = 0.2
dy = -0.5
dz = 0.5

angle = 0.0
max_dim = 0.1

variable = partial(glydget.Variable, namespace=locals())

# tkinter stl load dialog
options = {}
options['defaultextension'] = '.stl'
options['filetypes'] = [('STL files', '*.stl'), ('All files', '*.*')]
options['initialdir'] = './stldata'
options['title'] = 'Open a STL file'
options['multiple'] = 0


'''
TCP send commands
'''

def routeplan(s):
    print "running route planner"
    print filename
    routeplanner.GUIRun(filename, sampling_rate._text, send_to_robot._active, angle, max_dim)

def sendHome(s):
    print "JACO: HOME"
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;GOTOHOME", "localhost", 50005)
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()

def sendGet(s):
    print "JACO: GET POINT"
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;GETPOINT", "localhost", 50005)
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()


def sendDemo(s):
    print "JACO: DEMO"
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;DODEMO", "localhost", 50005)
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()

def sendDemo2(s):
    print "JACO: DEMO2"
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;DODEMO2", "localhost", 50005)
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()


def sendQuit(s):
    print "JACO: EXIT"
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;EXIT", "localhost", 50005)
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()

def send_svg(s):
    print "JACO: SVGROUTE"
    global points
    point_string = json.dumps(points)
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    ret = clientsocket.sendMessage("1;ROUTE;"+point_string, "localhost", 50005)


    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"

    clientsocket.close()


def sendXYZ(s):
    clientsocket = sockets.TCPsocket("client", "localhost", 50004)
    print "sending coordinates:"
    print "x", dx
    print "y", dy
    print "z", dz
    try:
        ret = clientsocket.sendMessage("1;XYZ;"+str(dx)+";"+str(dy)+";"+str(dz), "localhost", 50005)
    except:
        print "FAIL"
        ret = None
    if (ret == 1):
        print "OKOK"
    else:
        print "FAIL"
    clientsocket.close()


class model:

    ''' class for STL file / 3d model '''

    def __init__(self, stl_data, batchh=None):
        ''' initialise model data'''
        vert, norm = stl_data
        self.vertices = numpy.array(vert, dtype=GLfloat)
        self.normals = numpy.array(norm, dtype=GLfloat)
        self.vertex_buffer = VBO(self.vertices, 'GL_STATIC_DRAW')
        self.normal_buffer = VBO(self.normals, 'GL_STATIC_DRAW')

        # calculate model scale
        self.corner = self.vertices.transpose().min(1)
        self.corner2 = self.vertices.transpose().max(1)
        self.scale = abs(self.corner) + abs(self.corner2)
        self.scale = max(self.scale[0], self.scale[1], self.scale[2])
        print 'STL File loaded in: ', loadtime
        print 'Object information'
        print 'corner 1: ', self.corner
        print 'corner 2: ', self.corner2
        print 'object scale: ', self.scale

    def draw(self):
        ''' draw model on screen '''
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # center the model
        glTranslate(window.width/2, window.height/2, -150)

        # scale the model
        glScale(150/self.scale, 150/self.scale, 150/self.scale)

        # draw grid and coordinate lines
        draw_grid()
        draw_xyz(0, 0, 0, -20, -20)

        # demo rotation
        glRotate(rot, 1, 0, 0)
        glRotate(rot2, 0, 1, 0)
        glRotate(rot3, 0, 0, 1)

        self.vertex_buffer.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)
        self.normal_buffer.bind()
        glNormalPointer(GL_FLOAT, 0, None)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        self.normal_buffer.unbind()
        self.vertex_buffer.unbind()

        glPopMatrix()


def setup():
    ''' openGL setup '''
    glutInit()
    glClearColor(0.1, 0.2, 0.3, 1.0)
    glClearDepth(1000.0)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glShadeModel(GL_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #lights
    glLightfv(GL_LIGHT0, GL_POSITION, (20.0, 20.0, 20.0))
    glLightfv(GL_LIGHT1, GL_POSITION, (-20.0, -20.0, -20.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (.3, .3, .3, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (.3, .3, .3, 1))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (.3, .3, .3, 1))
    #materials
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (.5, .5, .5, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (.1, .1, .1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


def draw_grid():
    ''' draws the base grid '''
    glPushMatrix()
    glTranslate(0, 0, -150)
    glRotate(rot, 1, 0, 0)
    glRotate(rot2, 0, 1, 0)
    glBegin(GL_LINES)
    for x in range(0, 31, 5):
        glVertex(x-30, 30, 0)
        glVertex(x-30, -30, 0)
        glVertex(x, -30, 0)
        glVertex(x, 30, 0)
    for y in range(0, 31, 5):
        glVertex(-30, y-30, 0)
        glVertex(30, y-30, 0)
        glVertex(30, y, 0)
        glVertex(-30, y, 0)
    glEnd()
    glPopMatrix()


def draw_xyz(origin_x, origin_y, origin_z, lenght, zlen):
    ''' draws coordinate axes to specified origin coordinates'''
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glTranslate(0, 0, -150)
    glTranslate(-origin_x, -origin_y, origin_z)
    glColor(1, 1, 1)
    glutSolidSphere(1, 10, 10)
    glRotate(rot, 1, 0, 0)
    glRotate(rot2, 0, 1, 0)
    glBegin(GL_LINES)
    # draw x axis
    glColor(1, 0, 0)
    glVertex(0.0, 0.0, 0.0)
    glVertex(-lenght, 0, 0)
    # draw y axis
    glColor(0, 0, 1)
    glVertex(0.0, 0.0, 0.0)
    glVertex(0, -lenght, 0)
    # draw z axis
    glColor(0, 1, 1)
    glVertex(0.0, 0.0, 0.0)
    glVertex(0, 0, -zlen)
    glEnd()
    # fancy arrowheads: X..
    glTranslate(-lenght, 0.0, 0.0)
    glColor(1, 0, 0)
    glRotate(-90, 0, 1, 0)
    if lenght >= 0:
        glutSolidCone(1, 2, 4, 4)
    else:
        glutSolidCone(1, -2, 4, 4)
    glRotate(90, 0, 1, 0)
    glTranslate(lenght, 0.0, 0.0)
    # Y axis arrow
    glTranslate(0.0, -lenght, 0.0)
    glColor(0, 0, 1)
    glRotate(90, 1, 0, 0)
    if lenght >= 0:
        glutSolidCone(1, 2, 4, 4)
    else:
        glutSolidCone(1, -2, 4, 4)
    glRotate(90, 1, 0, 0)
    glTranslate(0.0, -lenght, 0.0)
    # Z axis arrow
    glTranslate(0.0, 0, zlen)
    glColor(0, 1, 1)
    if zlen >= 0:
        glutSolidCone(1, 2, 4, 4)
    else:
        glutSolidCone(1, -2, 4, 4)
    glTranslate(0.0, 0.0, -zlen)
    glColor(1, 1, 1)
    #glEnd()
    glRotate(-rot2, 0, 1, 0)
    glRotate(-rot, 1, 0, 0)
    glPopMatrix()


''' Pyglet event handlers '''

@window.event
def on_draw():
    #dialog.move(10,window.height-10)
    window.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    dialog.batch.draw()
    fps_display.draw()
    model.draw(mod)
    #print svg_file
    if(svg_file != None):
        #svg_file.draw(100, 100)
        pass
    glPopMatrix()


@window.event
def on_resize(width, height):
    glViewport(0,0,width,height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1000)
    #gluPerspective(65, width / float(height), -1, 1000)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED


def update(dt):
    global rot, rot2, rot3
    #rot += .5
    #rot2 += .5
    #rot %= 360
    #rot2 %= 360
    #print rot, rot2, rot3

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global rot, rot2, rot3
    if buttons & pyglet.window.mouse.LEFT:
        rot -= 0.5*dy # x rotation
        rot2 -= 0.5*dx # y rotation
    if buttons & pyglet.window.mouse.RIGHT:
        rot3 += 0.1*dx # z rotation
        global mod
        mod.scale += 0.05*dy # zoom


def load_stl(filename):
    ''' load STL file '''
    with open(filename, 'rb') as stlfile:
        timer = time.time()
        parser = StlParser(stlfile)
        parser.load(stlfile)
        try:
            data = parser.parse(None)
        except StlParseError:
            pass
        loadtime = time.time() - timer
        return data, loadtime


def svg_dialog(a):
    ''' tkinter svg file load dialog '''
    filename = tkFileDialog.askopenfilename()
    if filename:
        #svg_file = svgbatch(filename)
        #svg_batch = svgbatch.svg2batch(filename)
        data = parser.parse_svg(filename)
        global points
        points = data
        print "loaded SVG file with", len(points), "coordinate points"
        #print points[0]
        return data
    else:
        return []


def file_dialog(a):
    ''' tkinter stl file load dialog '''
    filename = tkFileDialog.askopenfilename(**options)
    global stl_filename
    stl_filename = filename
    loadtime = 0
    if filename:
        data, loadtime = load_stl(filename)
        global mod
        mod = model(data)
    return loadtime


def quit(*args):
    pyglet.app.exit()


''' glydget menu setup '''
main_gui = glydget.Group('Main',
                        [
                            glydget.Button('Load STL file', file_dialog),
                            glydget.Button('Quit', quit)
                        ])

svg_gui = glydget.Group('SVG Options',
                        [
                            glydget.Button('Load file', svg_dialog),
                            glydget.Button('Send SVG route', send_svg)
                        ])

robot_gui = glydget.Group('Robot control',
                            [
                                glydget.Button('JACO: HOME', sendHome),
                                glydget.Button('JACO: DRAW XY AXES', sendDemo),
                                glydget.Button('JACO: DRAW SQUARE', sendDemo2),
                                glydget.Button('JACO: EXIT', sendQuit)
                            ])

coordinate_gui = glydget.Group('Robot origin coordinates [m]',
                            [
                                variable('dx'),
                                variable('dy'),
                                variable('dz'),
                                glydget.Button('Send coordinates', sendXYZ)
                            ])

sampling_rate = glydget.Entry('0.001')

sampling_rate_setting = glydget.HBox([
                                glydget.Label('sampling rate'),
                                sampling_rate,
                             ])

send_to_robot = glydget.BoolEntry()

send_setting = glydget.HBox([
                                glydget.Label('send to robot'),
                                send_to_robot,
                             ])

routeplanner_gui = glydget.Group('Routeplanner settings',
                            [
                                sampling_rate_setting,
                                variable('angle'),
                                variable('max_dim'),
                                send_setting,
                                glydget.Button('Run routeplanner', routeplan)

                            ])



dialog = glydget.Window("Menu",
                         [
                            glydget.Button('Get current point coordinates', sendGet),
                            routeplanner_gui,
                            #svg_gui,
                            robot_gui,
                            coordinate_gui,
                            main_gui

                         ])

# Main menu location (upper left corner)
dialog.move(10,window.height-10)
dialog.show()
window.push_handlers(dialog)

# File load dialog
root = Tkinter.Tk()
root.withdraw()


# init. model with stl data when starting up
while 1:
    filename = tkFileDialog.askopenfilename(**options)
    if filename:
        break
data, loadtime = load_stl(filename)
mod = model(data)


setup()
pyglet.clock.set_fps_limit(30)
fps_display = pyglet.clock.ClockDisplay()
pyglet.clock.schedule(update)
pyglet.app.run()
