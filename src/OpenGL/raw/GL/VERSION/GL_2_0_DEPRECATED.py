'''Autogenerated by get_gl_extensions script, do not edit!'''
from OpenGL import platform as _p, constants as _cs, arrays
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_VERSION_GL_2_0'
def _f( function ):
    return _p.createFunction( function,_p.GL,'GL_VERSION_GL_2_0',True)
_p.unpack_constants( """GL_VERTEX_PROGRAM_TWO_SIDE 0x8643
GL_POINT_SPRITE 0x8861
GL_COORD_REPLACE 0x8862
GL_MAX_TEXTURE_COORDS 0x8871""", globals())
glget.addGLGetConstant( GL_VERTEX_PROGRAM_TWO_SIDE, (1,) )
glget.addGLGetConstant( GL_POINT_SPRITE, (1,) )
glget.addGLGetConstant( GL_MAX_TEXTURE_COORDS, (1,) )

