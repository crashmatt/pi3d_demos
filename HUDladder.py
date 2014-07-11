'''
Created on 11 Jul 2014

@author: matt
'''
import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
import math
import time

class HUDladder(object):
    '''
    classdocs
    '''


    def __init__(self, font, camera, shader):
        '''
        Constructor
        '''

        from pi3d.Display import Display
        
#        self.screenSize = screenSize
        self.font = font
               
        self.roll = 0
        self.pitch = 0
        self.heading = 0
        self.track = 0
        
        self.degstep = 15
        self.screenstep = 0.2           # ratio of screen height
        self.bar_thickness = 1          # pixels
        self.zero_bar_thickness = 2     # pixels
        self.bar_width = 0.3            # ratio of screen width
        self.bar_gap = 0.05             # ratio of screen width
        self.font_scale = 0.15          # relative to original font size
        self.font_bar_gap = 0.07        # ratio of screen width
        self.alpha = 1.0                # 0 to 1
        self.maxDegrees = 80
        
        self.upper_ladder = None
        self.lower_ladder = None
        self.center_ladder = None

        self.camera = camera    #pi3d.Camera(is_3d=False)
        self.shader = shader
        
        self.flatsh = pi3d.Shader("uv_flat")
        self.matsh = pi3d.Shader("mat_flat")

        self.screen_width = Display.INSTANCE.width
        self.screen_height = Display.INSTANCE.height
 
        self.bars = int(math.ceil(self.maxDegrees / self.degstep))
        self.pixelsPerBar = self.screenstep * self.screen_height       
        
        self.width = self.screen_width
        self.height = int(self.pixelsPerBar * self.maxDegrees / self.degstep)

        self.upper_ladder = pi3d.Layer(camera=camera, shader=shader, z=4.8, flip=True, w=self.width, h=self.height)
        self.lower_ladder = pi3d.Layer(camera=camera, shader=shader, z=4.8, flip=True, w=self.width, h=self.height)

        self.inits_done = 0
        

    def _gen_ladder(self):
        """ Generate the ladder in OffScreenTexture and Sprite """
        bar_width = self.bar_width * self.screen_width

        # generate upper ladder
        self.upper_ladder.start_layer()
        bar_shape = pi3d.Plane(camera=self.camera,  w=bar_width, h=self.bar_thickness)
        bar_shape.set_draw_details(self.matsh, [], 0, 0)
        bar_shape.set_material((50, 200, 50, 1.0))
#        bar_shape.set_alpha(0.5)

        for i in xrange(1,self.bars):
            degstep = i * self.degstep
            ypos = i * self.pixelsPerBar

            degText = "%01d" % degstep
            degStr = pi3d.String(camera=self.camera, font=self.font, string=degText, sx=0.6, sy=0.6, justify='R')  #sx=0.5, sy=0.5 self.font_scale
            degStr.position(bar_width/2 + (self.font_bar_gap * self.screen_width), ypos,5)
            degStr.set_shader(self.shader)
            degStr.set_material((50, 200, 50, 1.0))
            degStr.draw()

            degStr = pi3d.String(camera=self.camera, font=self.font, string=degText, sx=0.6, sy=0.6, justify='C')  #sx=0.5, sy=0.5 self.font_scale
            degStr.position((-bar_width/2) - (self.font_bar_gap * self.screen_width), ypos,5) # - (self.bar_gap * self.screen_width)
            degStr.set_shader(self.shader)
            degStr.set_material((50, 200, 50, 1.0))
            degStr.draw()
           
            bar_shape.position(0.0, ypos, 5)            
            bar_shape.draw()

        self.upper_ladder.end_layer()

        # generate upper ladder
        self.lower_ladder.start_layer()
        bar_shape = pi3d.Plane(camera=self.camera,  w=bar_width, h=self.bar_thickness)
        bar_shape.set_draw_details(self.matsh, [], 0, 0)
        bar_shape.set_material((50, 200, 50, 1.0))
#        bar_shape.set_alpha(0.5)

        for i in xrange(1,self.bars):
            degstep = i * -self.degstep
            ypos = self.height - (i * self.pixelsPerBar)

            degText = "%01d" % degstep
            degStr = pi3d.String(camera=self.camera, font=self.font, string=degText, sx=0.6, sy=0.6, justify='R')  #sx=0.5, sy=0.5 self.font_scale
            degStr.position(bar_width/2 + (self.font_bar_gap * self.screen_width), ypos,5)
            degStr.set_shader(self.shader)
            degStr.set_material((50, 200, 50, 1.0))
            degStr.draw()

            degStr = pi3d.String(camera=self.camera, font=self.font, string=degText, sx=0.6, sy=0.6, justify='C')  #sx=0.5, sy=0.5 self.font_scale
            degStr.position((-bar_width/2) - (self.font_bar_gap * self.screen_width), ypos,5) # - (self.bar_gap * self.screen_width)
            degStr.set_shader(self.shader)
            degStr.set_material((50, 200, 50, 1.0))
            degStr.draw()
           
            bar_shape.position(0.0, ypos, 5)            
            bar_shape.draw()

        self.lower_ladder.end_layer()
        
        self.upper_ladder.draw_layer()
        self.lower_ladder.draw_layer()
        
        
    def gen_ladder(self):
        if self.inits_done < 1:
            self._gen_ladder()
            self._gen_ladder()
            self.inits_done += 1
        
       
    def draw_ladder(self):
        if self.inits_done > 0:
            self.camera.reset()
            self.upper_ladder.draw_layer()
            self.lower_ladder.draw_layer()


#        self.flbar_shape.draw()
#        self.myStr.draw()
        
#        self.flbar_shape = pi3d.Plane(camera=self.camera, w=100, h=10)
#        self.flbar_shape.position(0,0,5)
#        self.flbar_shape.set_draw_details(self.matsh, [], 0, 0)
#        self.flbar_shape.set_material((50, 200, 50, 1.0))

#        randTxt = "ABCDEFGHIJKLMNOPQRSTUVWWYZ"
#        self.myStr = pi3d.String(camera=self.camera, font=self.font, string=randTxt, size=0.15, is_3d=False)
#        self.myStr.set_shader(self.shader)
#        self.myStr.position(100,0,5)

