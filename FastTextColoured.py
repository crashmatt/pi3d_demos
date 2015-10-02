""" Text rendered using a diy points class and special shader uv_spriterot.

This demo builds on the SpriteBalls demo but adds sprite image rotation, thanks
to Joel Murphy on stackoverflow. The information is used by the uv_spritemult
shader as follows

  vertices[0]   x position of centre of point relative to centre of screen in pixels
  vertices[1]   y position
  vertices[2]   z depth but fract(z) is used as a multiplier for point size
  normals[0]    rotation in radians
  normals[1]    alpha
  normals[2]    the size of the sprite square to use for texture sampling
                in this case each sprite has a patch 0.125x0.125 as there
                are 8x8 on the sheet. However normals[2] is set to 0.1 to
                leave a margin of 0.0125 around each sprite.
  tex_coords[0] distance of left side of sprite square from left side of
                texture in uv scale 0.0 to 1.0
  tex_coords[1] distance of top of sprite square from top of texture

The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
import numpy as np
from pi3d.Shape import Shape
from pi3d.shape.Points import Points
from pi3d.Texture import Texture
from pi3d.Shader import Shader
from pi3d.util.Font import Font
from encodings.rot_13 import rot13
from google.protobuf import text_format
from gettattra import *
from numpy.f2py.auxfuncs import throw_error
from __builtin__ import str
import math
from numpy import dtype

class FastTextColoured(object):
    def __init__(self, font, camera, max_chars = 100):
        """ Arguments:
        *font*:
          A PointFont object.
        *fmax_chars*:
          maximum number of chars which determines the number of points in the buffer
        """
        self.max_chars = max_chars
        self.font = font

        self.shader = Shader("shaders/uv_fontmultcoloured")
        
        self.locations = np.zeros((max_chars, 3))
        # :,2 for size range 0.0 to 0.999           

        self.normals = np.zeros((max_chars, 3))
        # :,0 for rotation
        # :,1 for red and alpha
        # :,2 for green and blue      
        self.normals[:,1] = 0.0
        self.normals[:,2] = 0.0
        self.uv = np.zeros((max_chars, 2)) # u picnum.u v

        self.text_blocks = []
        self._first_free_char = 0
        self._do_buffer_reinit = False
        
        self.text = Points(camera=camera, vertices=self.locations, normals=self.normals, tex_coords=self.uv,
                       point_size=self.font.height)
        self.text.set_draw_details(self.shader, [self.font])
            

    def regen(self):
        ##### regenerate text from text blocks
        char_index = 0
        
        #Reset all chars to zero 
#        self.normals[:,1] = 0.0

        for block in self.text_blocks:
            if (char_index + block.char_count) < self.max_chars:
                SystemError("FastText exceeded maximum characters")
            
            pos = [block.x, block.y]
            rot_vec = [math.cos(block.rot), math.sin(block.rot)]
               
            if block.data_obj != None:         
                value = block.get_value()
                if value != block.last_value:
                    block.last_value = value
                    block.set_text()
                    
  
  
    def add_text_block(self, text_block):
        if self._first_free_char + text_block.char_count >= self.max_chars:
            print("failed to allocate space in characers for " + text_block.char_count + " characters")
            return -1
        self.text_blocks.append(text_block)
        text_block.set_text_manager(self, self._first_free_char)
        text_block.set_text()
        self._first_free_char += text_block.char_count
        return 0
    
    
    def draw(self):
        if self._do_buffer_reinit == True:
            self.text.buf[0].re_init(pts=self.locations, normals=self.normals, texcoords=self.uv) # reform opengles array_buffer

        self.text.draw()
        
    def set_do_reinit(self):
        self._do_buffer_reinit = True
 
 

class TextBlock(object):
    def __init__(self, x, y, z, rot, char_count, data_obj, attr, text_format="{:s}", size=0.25, spacing="C", space=1.1, colour=(1.0,1.0,1.0,1.0) , char_rot=0.0):
        """ Arguments:
        *x, y, z*:
          As usual
        *rot*:
          TODO: rotation in unknown units??? 
        *data_obj*:
          Data object to use in text format
        *attr*:
            Attribute in data object to use in text format
        *text_format*:
            Thetext format to use including any data formattings
        *size*:
            Size of the text 0 to 0.9999
        *spacing*:
             Type of character spacing. C=Constant, M=Multiplier, F=Fixed space between chars
        *space*:
            Value to set the spacing to
        *colour*:
            drawn colour including alpha as format (0.99, 0.99, 0.99, 0.99)
        *char_rot*:
            character rotation in radians
        """
        self.x = x 
        self.y = y 
        self.z = z 
        self.rot = rot 
        self.char_count = char_count
        self.data_obj = data_obj
        self.attr = attr
        self.text_format = text_format
        self.size = size
        self.spacing = spacing
        self.space = space
        self.colour = [colour[0],colour[1],colour[2],colour[3]]
        self.char_rot = char_rot

        self.last_value = self          # hack so that static None object get initialization
        self.rotation_changed = False
        
        self._buffer_index = 0
        self._text_manager = None
        self._string_length = 0
        
        self.char_offsets = [0.0]*char_count
        
        str = self.get_string(self.get_value())
        self._string_length = len(str)
        

    def set_text_manager(self, manager, buffer_index):
        self._text_manager = manager
        self._buffer_index = buffer_index
        
    def get_value(self):
        if(self.attr != None) and (self.data_obj != None):
            return getattra(self.data_obj, self.attr, None)
        return None
        
    def get_string(self, value):        
        if(value != None):
            str = self.text_format.format(value)
            self._string_length = len(str)
            return str

        return self.text_format
    
    def set_position(self, x=None, y=None, z=None, rot=None):
        if x != None: self.x = x
        if y != None: self.y = y
        if z != None: self.z = z
        if rot != None: self.rot = rot
        
        pos = [self.x, self.y, self.size]
        
        locations = np.zeros((self.char_count, 3), dtype=np.float)
        locations[:, 0] = np.multiply(self.char_offsets, math.cos(self.rot))
        locations[:, 1] = np.multiply(self.char_offsets, math.sin(self.rot))
        locations = np.add(locations, pos)
        self._text_manager.locations[self._buffer_index:self._buffer_index+self.char_count, :] = locations
        
        self._text_manager.normals[self._buffer_index:self._buffer_index+self._string_length, 0] = self.rot + self.char_rot

        self._text_manager.set_do_reinit()
        
        
    def set_colour(self, colour=None, alpha=None):
        if colour != None:
            self.colour[0:2] = colour[0:2]
        
        if alpha != None:
            self.colour[3] = alpha
            
        #Reset alpha to zero for all characters.  Prevents displaying old chars from longer strings
        self._text_manager.normals[self._buffer_index:self._buffer_index+self.char_count, 1] = 0
                
        #Fill an array with the colour to copy to the manager normals
        #rotation is included for efficiency
        normal = np.zeros((3), dtype=np.float)
        normal[0] = self.rot + self.char_rot
        normal[1] = (self.colour[3] * 0.99) + (math.floor(self.colour[0] * 255))
        normal[2] = (self.colour[1] * 0.99) + (math.floor(self.colour[2] * 255))
        
        #Only set colour alpha for string length. Zero for non displayed characters
        self._text_manager.normals[self._buffer_index:self._buffer_index+self._string_length, :] = normal

#        normals = self._text_manager.normals
      
        
        
    def set_text(self, text_format=None, size=None, spacing=None, space=None , char_rot=None, set_pos=True, set_colour=True):
        if text_format != None: self.text_format = text_format
        if size != None: self.size = size
        if spacing != None: self.spacing = spacing
        if space != None: self.space = space
        if char_rot != None: self.char_rot = char_rot
                
        if (self.data_obj != None):
            str = self.get_string(self.get_value())
        else:
            str = self.text_format
        
        pos = 0.0
        index = 0
        
        const_width = 0.0
        vari_width = 0.0
        if self.spacing == "C":
            const_width = self._text_manager.font.height * self.size * self.space
        if self.spacing == "M":
            vari_width = self.size * self.space
        if self.spacing == "F":
            vari_width = self.size
            const_width =  (self._text_manager.font.height * self.space * self.size)        
        
        for char in str:
            glyph = self._text_manager.font.glyph_table[char]
            self._text_manager.uv[index+self._buffer_index] = glyph[0:2]
                
            char_offset = pos
            
            if self.spacing == "F":
                #center character to the right 
                char_offset += float(glyph[2]) * self.size * 0.5
            
            self.char_offsets[index] = char_offset

            spacing = (glyph[2] * vari_width) + const_width
            pos += spacing
            index += 1
            
        if set_pos:
            self.set_position()
        
        if set_colour:
            self.set_colour()

        self._text_manager.set_do_reinit()  
        
        
        