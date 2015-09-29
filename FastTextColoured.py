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

        self.text = None
        
        self.text_blocks = []
        
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
            value = block.get_value()
                        
            if value != block.last_value:
                block.last_value = value

                # Set alpha for whole text block to zero. Hides old strings that are longer than new ones
                self.normals[char_index:char_index+block.char_count,1] = 0.0
                
                str = block.get_string(value)
                            
                index = 0
                for char in str:
                    ind = index + char_index
                                   
                    glyph = self.font.glyph_table[char]
                    self.uv[ind] = glyph[0:2]
                    
                    char_pos = pos
                    if block.spacing == "F":
                        offset = float(glyph[2]) * block.size * 0.5
                        rot = rot_vec
                        char_pos += np.multiply(offset, rot)

                    self.locations[ind][0] = char_pos[0]
                    self.locations[ind][1] = char_pos[1]
                    self.locations[ind][2] = block.size
                    
                    # Set alpha
                    self.normals[ind][0] = block.rot + block.char_rot
                    self.normals[ind][1] = (block.colour[3] * 0.99) + (math.floor(block.colour[0] * 255))
                    self.normals[ind][2] = (block.colour[1] * 0.99) + (math.floor(block.colour[2] * 255))
                    
                    spacing = 0.0
                    if block.spacing == "C":
                        spacing = self.font.height * block.size * block.space
                    if block.spacing == "M":
                        spacing = glyph[2] * block.size * block.space
                    if block.spacing == "F":
                        spacing = (glyph[2] * block.size) + (self.font.height * block.space * block.size)
                    spacing = np.multiply(spacing, rot_vec)
                    pos = np.add(pos, spacing)
                    index += 1
            
            elif block.rotation_changed:
                #Set the rotation of the block 
                self.normals[char_index:char_index+block.char_count,0] = block.rot
                   
            char_index = char_index + block.char_count
                    
        self.text.buf[0].re_init(pts=self.locations, normals=self.normals, texcoords=self.uv) # reform opengles array_buffer
  
    def add_text_block(self, text_block):
        self.text_blocks.append(text_block)
        return len(self.text_blocks) - 1
    
    def set_text_block_position_xy(self, index, x, y):
        if index >= len(self.text_blocks):
            return
        block = self.text_blocks[index]
        block.x = x
        block.y = y
        
    def set_text_block_rotation(self, index, rot):
        if index >= len(self.text_blocks):
            return
        self.text_blocks[index].rot = rot

    def draw(self):
        self.text.draw()
 
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
        self.colour = colour
        self.char_rot = char_rot

        self.last_value = self          # hack so that static None object get initialization
        self.rotation_changed = False
        
        
    def get_value(self):
        if(self.attr != None) and (self.data_obj != None):
            return getattra(self.data_obj, self.attr, None)
        return None
        
                 
    def get_string(self, value):        
        if(value != None):
            return self.text_format.format(value)

        return self.text_format
        
