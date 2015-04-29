'''
Software Project course
Jaco API
Heikki Korhonen & Joni Saunavaara
10.6.2014
'''

from ctypes import *
import sockets
import json
from time import sleep

'''
First the API exports all the necessary the data structures
and data types from Linux based .so-files.
There are also all the necessary initiations for data structures.
'''


class POSITION_TYPE(Structure):
    _fields_ = [
        ('NOMOVEMENT_POSITION', c_int),
        ('CARTESIAN_POSITION', c_int),
        ('ANGULAR_POSITION', c_int),
        ('RETRACTED_POSITION', c_int),
        ('PREDEFINED_POSITION_1', c_int),
        ('PREDEFINED_POSITION_2', c_int),
        ('PREDEFINED_POSITION_3', c_int),
        ('CARTESIAN_VELOCITY', c_int),
        ('ANGULAR_VELOCITY', c_int),
        ('PREDEFINED_POSITION_4', c_int),
        ('PREDEFINED_POSITION_5', c_int),
        ('ANY_TRAJECTORY', c_int),
        ('TIME_DELAY', c_int)
    ]

    def __init__(self):
        self.NOMOVEMENT_POSITION = 0
        self.CARTESIAN_POSITION = 1
        self.ANGULAR_POSITION = 2
        self.CARTESIAN_VELOCITY = 7
        self.ANGULAR_VELOCITY = 8
        self.ANY_TRAJECTORY = 11
        self.TIME_DELAY = 12


class HAND_MODE(Structure):
    _fields_ = [
        ('HAND_NOMOVEMENT', c_int),
        ('POSITION_MODE', c_int),
        ('VELOCITY_MODE', c_int),
        ('NO_FINGER', c_int),
        ('ONE_FINGER', c_int),
        ('TWO_FINGER', c_int),
        ('THREEFINGER', c_int)
    ]


class ARMLATERALITY(Structure):
    _fields_ = [
        ('RIGHTHAND', c_int),
        ('LEFTHAND', c_int)
    ]


class Limitation(Structure):
    _fields_ = [
        ('speedParameter1', c_float),
        ('speedParameter2', c_float),
        ('speedParameter3', c_float),
        ('forceParameter1', c_float),
        ('forceParameter2', c_float),
        ('forceParameter3', c_float),
        ('accelerationParameter1', c_float),
        ('accelerationParameter2', c_float),
        ('accelerationParameter3', c_float)
    ]

    def __init__(self):
        self.speedParameter1 = 0
        self.speedParameter2 = 0
        self.speedParameter3 = 0
        self.forceParameter1 = 0
        self.forceParameter2 = 0
        self.forceParameter3 = 0
        self.accelerationParameter1 = 0
        self.accelerationParameter2 = 0
        self.accelerationParameter3 = 0


class SensorsInfo(Structure):
    _fields_ = [
        ('Voltage', c_float),
        ('Current', c_float),
        ('AccerelationX', c_float),
        ('AccerelationY', c_float),
        ('AccerelationZ', c_float),
        ('ActuatorTemp1', c_float),
        ('ActuatorTemp2', c_float),
        ('ActuatorTemp3', c_float),
        ('ActuatorTemp4', c_float),
        ('ActuatorTemp5', c_float),
        ('ActuatorTemp6', c_float),
        ('FingerTemp1', c_float),
        ('FingerTemp2', c_float),
        ('FingerTemp3', c_float)
    ]


class CartesianInfo(Structure):
    _fields_ = [
        ('X', c_float),
        ('Y', c_float),
        ('Z', c_float),
        ('ThetaX', c_float),
        ('ThetaY', c_float),
        ('ThetaZ', c_float)
    ]

    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.ThetaX = 0
        self.ThetaY = 0
        self.ThetaZ = 0


class AngularInfo(Structure):
    _fields_ = [
        ('Actuator1', c_float),
        ('Actuator2', c_float),
        ('Actuator3', c_float),
        ('Actuator4', c_float),
        ('Actuator5', c_float),
        ('Actuator6', c_float)
    ]

    def __init__(self):
        self.Actuator1 = 0
        self.Actuator2 = 0
        self.Actuator3 = 0
        self.Actuator4 = 0
        self.Actuator5 = 0
        self.Actuator6 = 0


class FingerPosition(Structure):
    _fields_ = [
        ('Finger1', c_float),
        ('Finger2', c_float),
        ('Finger3', c_float)
    ]

    def __init__(self):
        self.Finger1 = 0
        self.Finger2 = 0
        self.Finger2 = 0


class CartesianPosition(Structure):
    _fields_ = [
        ('Coordinates', CartesianInfo),
        ('Fingers', FingerPosition)
    ]


class AngularPosition(Structure):
    _fields_ = [
        ('Actuators', AngularInfo),
        ('Fingers', FingerPosition)
    ]


class UserPosition(Structure):
    _fields_ = [
        ('Type', c_int),
        ('Delay', c_float),
        ('CartesianPosition', CartesianInfo),
        ('Actuators', AngularInfo),
        ('HandMode', c_int),
        ('Fingers', FingerPosition)
    ]

    def __init__(self):
        self.Type = 0  # CARTERTESIAN_POSITION
        self.HandMode = 0  # HAND_NOMOVEMENT
        self.CartesianPosition.__init__()
        self.Actuators.__init__()
        self.Fingers.__init__()
        self.Delay = 0


class TrajectoryPoint(Structure):
    _fields_ = [
        ('Position', UserPosition),
        ('LimitationsActive', c_int),
        ('Limitations', Limitation)
    ]

    def __init__(self):
        self.LimitationsActive = 0
        self.Position.__init__()
        self.Limitations.__init__()


class TrajectoryFIFO(Structure):
    _fields_ = [
        ('TrajectoryCount', c_uint),
        ('UsedPercentage', c_float),
        ('MaxSize', c_uint)
    ]


class SingularityVector(Structure):
    _fields_ = [
        ('TranslationSingularityCount', c_int),
        ('OrientationSingularityCount', c_int),
        ('TranslationSingularityDistance', c_float),
        ('OrientationSingularityDistance', c_float),
        ('RepulsionVector', CartesianInfo)
    ]


class JoystickCommand(Structure):
    _fields_ = [
        ('ButtonValue', c_int),
        ('InclineLeftRight', c_float),
        ('InclineForwardBackward', c_float),
        ('Rotate', c_float),
        ('MoveLeftRight', c_float),
        ('MoveForwardBackward', c_float),
        ('PushPull', c_float)
    ]


class ClientConfigurations(Structure):
    _fields_ = [
        ('ClientID', c_char),
        ('ClientName', c_char),
        ('Organization', c_char),
        ('Serial', c_char),
        ('Model', c_char),
        ('MaxLinearSpeed', c_float),
        ('MaxAngularSpeed', c_float),
        ('MaxLinearAcceleration', c_float),
        ('MaxAngularAcceleration', c_float),
        ('MaxForce', c_float),
        ('Sensibility', c_float)
    ]


class Jaco():

    def __init__(self):
        '''Opens the .so-files and activates all the necessary initations'''
        self.com = CDLL("Kinova.DLL.CommLayer.dll")
        self.jaco = CDLL("Kinova.API.UsbCommandLayer.dll")
        print "InitAPI():", self.jaco.InitAPI()
        print "StartControlApi():", self.jaco.StartControlAPI()
        print "SetCartesianControl():", self.jaco.SetCartesianControl()
        self.position = CartesianPosition()
        self.angpos = AngularPosition()
        self.sendtrajectory = TrajectoryPoint()

    def getCarPosition(self):
        '''
        In this function API gets the CarPosition information from the robot
        '''

        print "In getCarPosition"
        self.jaco.GetCartesianPosition.argtypes = [POINTER(CartesianPosition)]
        self.jaco.GetCartesianPosition(self.position)
        print "Coordinates"
        print self.position.Coordinates.X
        print self.position.Coordinates.Y
        print self.position.Coordinates.Z
        print "Theta"
        print self.position.Coordinates.ThetaX
        print self.position.Coordinates.ThetaY
        print self.position.Coordinates.ThetaZ

    def getAngPosition(self):
        '''
        API gets the AngularPosition information from the robot
        and specifies the command to pointer
        '''

        print "In getAngPosition"
        self.jaco.GetAngularPosition.argtypes = [POINTER(AngularPosition)]
        self.jaco.GetAngularPosition(self.angpos)

    def sendPosition(self, x, y, z):
        '''
        API specifies the command to pointer and sets
        all the speedparameters and also the thetas for the hand.
        '''

        print "In SendPosition"
        self.jaco.SendAdvanceTrajectory.argtypes = [TrajectoryPoint]

        self.sendtrajectory.Limitations.speedParameter1 = 0.08
        self.sendtrajectory.Limitations.speedParameter2 = 0.6
        self.sendtrajectory.Limitations.speedParameter3 = 0.08

        self.sendtrajectory.Position.CartesianPosition.X = x
        self.sendtrajectory.Position.CartesianPosition.Y = y
        self.sendtrajectory.Position.CartesianPosition.Z = z

        self.sendtrajectory.Position.CartesianPosition.ThetaX = 1.53015184402
        self.sendtrajectory.Position.CartesianPosition.ThetaY = 1.04940390587
        self.sendtrajectory.Position.CartesianPosition.ThetaZ = 0.0722067132592

        print self.sendtrajectory.Position.CartesianPosition.X
        print self.sendtrajectory.Position.CartesianPosition.Y
        print self.sendtrajectory.Position.CartesianPosition.Z

        print self.sendtrajectory.Position.CartesianPosition.ThetaX
        print self.sendtrajectory.Position.CartesianPosition.ThetaY
        print self.sendtrajectory.Position.CartesianPosition.ThetaZ

        self.sendtrajectory.LimitationsActive = 1
        self.sendtrajectory.Position.Type = 1
        self.sendtrajectory.Position.HandMode = 0

        print "SendBasicTrajectory():",
        print self.jaco.SendAdvanceTrajectory(self.sendtrajectory)


if __name__ == "__main__":
    '''
    Calls the class Jaco and determines sockets for GUI and API.
    Also determines the origin points
    '''

    j = Jaco()
    soc_gui = sockets.TCPsocket("server", "localhost", 50005)
    soc_own = sockets.TCPsocket("client", "localhost", 50010)
    j.getCarPosition()
    originX = 0.05
    originY = -0.65
    originZ = 0.13

    while (True):

        while (True):  # wait forever
            message = soc_gui.getMessage()
            if (message[0] == "1"):
                break
            else:
                pass
        soc_own.sendMessage("ACK", "localhost", 50002)

        if (message[1] == "ROUTE"):
            '''
            Gets the message from socket and loads the json-packet.
            Sends the hand to origin
            '''

            print "ROUTE"
            data = message[2]
            # print data
            data = json.loads(data)
            # print data
            j.sendPosition(
                originX + data[0][0], originY + data[0][1], originZ + 0.05)
            # j.sendPosition(originX+data[0][0], originY+data[0][1],
            # originZ+data[0][2] + 0.05) #Enable Z coordinates

            routeX = 0
            routeY = 0
            routeZ = 0

            for xyz in data:
                '''Prints the route from socket'''

                routeX = xyz[0]
                routeY = xyz[1]
                routeZ = xyz[2]

                # try to compensate for tilted Z axis
                # Z changes approx. 0.125 cm per 1 cm of Y movement
                fixZ = OriginZ + (12.5 * routeY)  # or 12.5 m / m

                print "RECV x", routeX, "y", routeY, "z", routeZ
                j.sendPosition(
                    originX + routeX, originY + routeY, fixZ
                    )
                # j.sendPosition(originX+routeX, originY+routeY,
                # OriginZ+routeZ)  #Enable Z coordinates
                j.sendPosition(
                    originX + routeX, originY + routeY, fixZ + 0.05
                    )
                # j.sendPosition(originX+routeX, originY+routeY, originZ+routeZ
                # + 0.05)   #Enable Z coordinates
                soc_2planer = sockets.TCPsocket("client", "localhost", 50003)
                soc_2planer.sendMessage("ACK", "localhost", 50003)
                soc_2planer.close()

        if (message[1] == "GOTOHOME"):
            print "jaco going home"
            print "MoveHome():", j.jaco.MoveHome()

        if (message[1] == "XYZ"):

            if (float(message[2]) == originX):
                print "X:", originX
            elif (abs(float(message[2]) - originX) <= 0.5):
                print "changing jaco X origin from", originX, "to", message[2]
                originX = float(message[2])
            else:
                print "too large difference in coordinates,",
                print "ignoring change in X!"

            if (float(message[3]) == originY):
                print "Y:", originY
            elif (abs(float(message[3]) - originY) <= 0.5):
                print "changing jaco Y origin from", originY, "to", message[3]
                originY = float(message[3])
            else:
                print "too large difference in coordinates,",
                print "ignoring change in Y!"

            if (float(message[4]) == originZ):
                print "Z:", originZ
            elif (abs(float(message[4]) - originZ) <= 0.5):
                print "changing jaco Z origin from", originZ, "to", message[4]
                originZ = float(message[4])
            else:
                print "too large difference in coordinates,",
                print "ignoring change in Z!"

        if (message[1] == "DODEMO"):
            print "Jaco drawing coordinate axes"
            demoX = 0
            demoY = 0

            # Drawing x & y axis
            j.sendPosition(originX - 0.10, originY, originZ + 0.25)
            j.sendPosition(originX - 0.06, originY, originZ + 0.15)
            j.sendPosition(originX - 0.05, originY, originZ + 0.05)
            for x in range(-15, 16, 1):
                demoX = float(x) / 500.0
                j.sendPosition(originX + demoX, originY, originZ + 0.05)
                j.sendPosition(originX + demoX, originY, originZ + 0.05)
                j.sendPosition(originX + demoX, originY, originZ + 0.05)
                j.sendPosition(originX + demoX, originY, originZ + 0.00)
                j.sendPosition(originX + demoX, originY, originZ + 0.05)
            demoX = 0
            demoY = 0
            j.sendPosition(originX, originY - 0.10, originZ + 0.25)
            j.sendPosition(originX, originY - 0.06, originZ + 0.15)
            j.sendPosition(originX, originY - 0.05, originZ + 0.05)
            for y in range(-15, 16, 1):
                demoY = float(y) / 500.0
                j.sendPosition(originX, originY + demoY, originZ + 0.05)
                j.sendPosition(originX, originY + demoY, originZ + 0.05)
                j.sendPosition(originX, originY + demoY, originZ + 0.05)
                j.sendPosition(originX, originY + demoY, originZ + 0.00)
                j.sendPosition(originX, originY + demoY, originZ + 0.05)

        if (message[1] == "DODEMO2"):
            print "jaco drawing a square"
            demoX = 0
            demoY = 0

            # draw a square x = +- 0.05, y = +-0.05
            for y in range(-1, 2, 2):
                demoY = float(y) / 20.0
                for x in range(-10, 11, 1):
                    demoX = float(x) / 100.0 / 2
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.05)
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.00)
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.05)
            for x in range(-1, 2, 2):
                demoX = float(x) / 20.0
                for y in range(-10, 11, 1):
                    demoY = float(y) / 100.0 / 2
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.05)
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.00)
                    j.sendPosition(
                        originX + demoX, originY + demoY, originZ + 0.05)

        if (message[1] == "EXIT"):
            print "jaco exiting"
            break

    j.jaco.CloseAPI()
    soc_gui.close()
