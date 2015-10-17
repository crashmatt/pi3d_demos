""" Text block used to update contents of buffers used to draw gl_point font characters.

"""
import numpy as np

from gettattra import *
from __builtin__ import str
import math
import colorsys
import PointText as FastTextColoured


class TextBlockColour(object):
    def __init__(self, colour=(1.0, 1.0, 1.0, 1.0), textBlock=None):
        self.colour = [colour[0],colour[1],colour[2],colour[3]]
        self.textBlock = textBlock

    def recolour(self):
        self.set_colour()
        
    def set_colour(self, colour=None, alpha=None):
        if colour != None:
            self.colour[0:2] = colour[0:2]
        
        if alpha != None:
            self.colour[3] = alpha

        textBlock = self.textBlock
        manager = textBlock._text_manager
                    
        #Reset alpha to zero for all characters.  Prevents displaying old chars from longer strings
        manager.normals[textBlock._buffer_index:textBlock._buffer_index+textBlock.char_count, 1] = 0
                
        #Fill an array with the colour to copy to the manager normals
        #rotation is included for efficiency
        normal = np.zeros((3), dtype=np.float)
        normal[0] = textBlock.rot + textBlock.char_rot
        normal[1] = (self.colour[3] * 0.99) + (math.floor(self.colour[0] * 255))
        normal[2] = (self.colour[1] * 0.99) + (math.floor(self.colour[2] * 255))
        
        #Only set colour alpha for string length. Zero for non displayed characters
        manager.normals[textBlock._buffer_index:textBlock._buffer_index+textBlock._string_length, :] = normal


class TextBlockColourGradient(TextBlockColour):
    def __init__(self, colour1, colour2, textBlock=None):
        self.colour1 = colour1
        self.colour2 = colour2
        self.textBlock = textBlock
    
    def set_colour(self, colour1=None, colour2=None):
        ''' Colour each character with a gradient from colour1 to colour2
        Interpolate hsv instead of rgb since it is a more natural change.
        This is quite processor intensive so not intended to be dynamic
        Only compatible with static text, reposition will result in default colour
        '''
        if colour1 != None:
            self.colour1 = colour1
        if colour2 != None:
            self.colour2 = colour2
            
        if self.textBlock == None:
            return
            
        colour1 = self.colour1
        colour2 = self.colour2

        textBlock = self.textBlock        
        manager = textBlock._text_manager
            
        hsv1 = colorsys.rgb_to_hsv(colour1[0], colour1[1], colour1[2])
        hsv2 = colorsys.rgb_to_hsv(colour2[0], colour2[1], colour2[2])
            
        normal = np.zeros((3), dtype=np.float)
        normal[0] = textBlock.rot + textBlock.char_rot
                
        for index in range(0,textBlock._string_length):
            h = np.interp(index, [0,textBlock._string_length], [hsv1[0], hsv2[0]])
            s = np.interp(index, [0,textBlock._string_length], [hsv1[1], hsv2[1]])
            v = np.interp(index, [0,textBlock._string_length], [hsv1[2], hsv2[2]])
            a = np.interp(index, [0,textBlock._string_length], [colour1[3], colour2[3]])
            rgb = colorsys.hsv_to_rgb(h, s, v)
            normal[1] = (a * 0.99) + (rgb[0] * 255)
            normal[2] = (rgb[1] * 0.99) + (rgb[2] * 255)
            
            #Only set colour alpha for string length. Zero for non displayed characters
            manager.normals[textBlock._buffer_index+index, :] = normal
             


class TextBlock(object):
    def __init__(self, x, y, z, rot, char_count, data_obj, attr, text_format="{:s}", size=0.25, spacing="C", space=1.1, colour=(1.0,1.0,1.0,1.0) , char_rot=0.0, justify=0.0):
        """ Arguments:
        *x, y, z*:
          As usual
        *rot*:
          rotation in degrees
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
            character rotation in degrees
        *justify*:
            Justification position. 0.0=Right, 1.0=Left, 0.5=Center
        """
        self.x = x 
        self.y = y 
        self.z = z 
        self.rot = math.radians(rot) 
        self.char_count = char_count
        self.data_obj = data_obj
        self.attr = attr
        self.text_format = text_format
        self.size = size
        self.spacing = spacing
        self.space = space
        
        #If the colour is a tuple initialize it a plain colour
        #Otherwise use a TextBlockColour object and its textBlock reference to this TextBlock
        if isinstance(colour, tuple):
            self.colouring = TextBlockColour(colour, self)
        else:
            self.colouring = colour
            self.colouring.textBlock = self
            
        self.char_rot = math.radians(char_rot)
        self.justify = justify
 
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
        if rot != None: self.rot = math.radians(rot)
        
        size_pos, __  = math.modf(self.size)
        size_pos += math.trunc(self.z * 10.0)   # depth has resolution of 0.1m and range of 25.5m
        pos = [self.x, self.y, size_pos]
        
        locations = np.zeros((self.char_count, 3), dtype=np.float)
        locations[:, 0] = np.multiply(self.char_offsets, math.cos(self.rot))
        locations[:, 1] = np.multiply(self.char_offsets, math.sin(self.rot))
        locations = np.add(locations, pos)
        self._text_manager.locations[self._buffer_index:self._buffer_index+self.char_count, :] = locations
        
        self._text_manager.normals[self._buffer_index:self._buffer_index+self._string_length, 0] = self.rot + self.char_rot

        self._text_manager.set_do_reinit()
        
        
    def recolour(self):
        self.colouring.recolour()
      
    #===========================================================================
    #   
    # def set_colour_gradient(self, colour1, colour2, alpha1=None, alpha2=None):
    #     ''' Colour each character with a gradient from colour1 to colour2
    #     Interpolate hsv instead of rgb since it is a more natural change.
    #     This is quite processor intensive so not intended to be dynamic
    #     Only compatible with static text, reposition will result in default colour
    #     '''
    #     hsv1 = colorsys.rgb_to_hsv(colour1[0], colour1[1], colour1[2])
    #     hsv2 = colorsys.rgb_to_hsv(colour2[0], colour2[1], colour2[2])
    #         
    #     normal = np.zeros((3), dtype=np.float)
    #     normal[0] = self.rot + self.char_rot
    #     
    #     if alpha1 == None:
    #         alpha1 = self.colour[3]
    #     if alpha2 == None:
    #         alpha2 = alpha1
    #     
    #     for index in range(0,self._string_length):
    #         h = np.interp(index, [0,self._string_length], [hsv1[0], hsv2[0]])
    #         s = np.interp(index, [0,self._string_length], [hsv1[1], hsv2[1]])
    #         v = np.interp(index, [0,self._string_length], [hsv1[2], hsv2[2]])
    #         a = np.interp(index, [0,self._string_length], [alpha1, alpha2])
    #         rgb = colorsys.hsv_to_rgb(h, s, v)
    #         normal[1] = (a * 0.99) + (rgb[0] * 255)
    #         normal[2] = (rgb[1] * 0.99) + (rgb[2] * 255)
    #         
    #         #Only set colour alpha for string length. Zero for non displayed characters
    #         self._text_manager.normals[self._buffer_index+index, :] = normal
    #    
    #===========================================================================
        
    def set_text(self, text_format=None, size=None, spacing=None, space=None , char_rot=None, set_pos=True, set_colour=True):
        if text_format != None: self.text_format = text_format
        if size != None: self.size = size
        if spacing != None: self.spacing = spacing
        if space != None: self.space = space
        if char_rot != None: self.char_rot = math.radians(char_rot)
                
        #If there is no data object then use the simple static string value
        if (self.data_obj != None):
            value = self.get_value()
            str = self.get_string(value)
            self.last_value = value
        else:
            str = self.text_format
        self._string_length =len(str)
         
        pos = 0.0
        index = 0
        
        const_width = 0.0
        vari_width = 0.0
        if self.spacing == "C":
            const_width = 64.0 * self.size * self.space
        if self.spacing == "M":
            vari_width = self.size * self.space
        if self.spacing == "F":
            vari_width = self.size
            const_width =  (64.0 * self.space * self.size)        
        
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
        
        #Justification
        self.char_offsets = np.add(self.char_offsets, (pos - spacing) * -self.justify)         
        
        if set_pos:
            self.set_position()
        
        if set_colour:
            self.recolour()
            
        self._text_manager.set_do_reinit()  
        
        
        