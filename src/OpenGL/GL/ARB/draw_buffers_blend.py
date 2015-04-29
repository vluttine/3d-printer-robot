'''OpenGL extension ARB.draw_buffers_blend

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.draw_buffers_blend to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension builds upon the ARB_draw_buffers and
	EXT_draw_buffers2 extensions. In ARB_draw_buffers (part of OpenGL
	2.0), separate values could be written to each color buffer. This
	was further enhanced by EXT_draw_buffers2 by adding in the ability
	to enable blending and to set color write masks independently per
	color output.
	
	This extension provides the ability to set individual blend
	equations and blend functions for each color output.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/draw_buffers_blend.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.ARB.draw_buffers_blend import *
### END AUTOGENERATED SECTION