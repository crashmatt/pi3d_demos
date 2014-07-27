'''
Created on 27 Jul 2014

@author: matt
'''

from Box2d import Box2d
import pi3d
from LayerItems import LayerItem

class Indicator(LayerItem):
    '''
    Indicator base class
    '''

    def __init__(self, dataobj, attr, x=0, y=0, phase=None, indmax=1, indmin=0, z=1, camera=None, shader=None ):
        '''
        Constructor
        *dataobj* is the object that the data pointer uses to show data
        *attr* is the attribute name in the object
        '''
        super(Indicator, self).__init__(camera=camera, shader=shader, x=x, y=y, phase=phase)
        
        self.dataobj = dataobj
        self.attr = attr
        
        self.max = indmax
        self.min = indmin
        self.y = z
        
        self.value = getattr(dataobj, attr, None)
        self.bezel=None
                
    def draw_bezel(self):
        self.bezel.draw()

        

class LinearIndicator(Indicator):
    def __init__(self, camera, flatsh, matsh, dataobj, attr, indmax=1, indmin=0, x=0, y=0, z=3, 
                 width=20, length=100, orientation="V",
                 line_colour=(255,255,255,255), fill_colour=(0,0,0,255), line_thickness = 1, 
                 needle_img="default_needle.img", phase=0):
        '''
        *width* width of the indicator
        *length* length of the indicator
        *orientation* 'V' for vertical 'H' for horizontal
        length and width is rotated with orientation
        '''
        super(LinearIndicator, self).__init__(dataobj, attr, x=x, y=y, phase=phase, indmax=indmax, indmin=indmin, z=z, camera=camera, shader=matsh )
        
        self.width = width
        self.length = length
        self.orientation = orientation
        self.line_colour = line_colour
        self.fill_colour = fill_colour
        self.line_thickness = line_thickness
        self.camera = camera
        self.matsh = matsh
        self.flatsh = flatsh
        self.x = x
        self.y = y
        self.z = z
        
        
        self.bezel = Box2d(camera=self.camera, w=self.width, h=self.length, d=1.0,
                         x=self.x, y=self.y, z=self.z,
                         line_colour=self.line_colour, fill_colour=self.fill_colour, 
                         line_thickness=self.line_thickness,  shader=matsh, justify='C')

        self.needle_texture = pi3d.Texture(needle_img)
        
        self.needle = pi3d.ImageSprite(camera=self.camera, texture=self.needle_texture, shader=flatsh, 
                                       w=self.needle_texture.ix, h=self.needle_texture.iy, 
                                       x=self.x, y=self.y, z=0.5, name="needle")
        
    def draw_item(self):
        self.needle.draw()