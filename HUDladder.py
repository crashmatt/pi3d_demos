'''
Created on 11 Jul 2014

@author: matt
'''
import pi3d
from pi3d.util.OffScreenTexture import OffScreenTexture
import math
import time


class HUDladderBar(object):
    def __init__(self, camera, shader, degree, ypos, scrnheight=0.1):
        self.degree = degree

        from pi3d.Display import Display
        
        self.pixel_height = int(scrnheight * Display.INSTANCE.height)
        self.pixel_width = Display.INSTANCE.width


        self.camera = camera
        self.shader = shader
                
#        self.bar = pi3d.Layer(camera=camera, shader=shader, z=4.8, flip=True, h=self.pixel_height)
        self.bar = OffScreenTexture("bar", h=self.pixel_height)

        # need to do offscreentexture first so its size can be used for the following.
#        self.height3d = float(self.pixel_height) / float(Display.INSTANCE.height)
#        self.width3d = float(self.bar.iy) / float(Display.INSTANCE.width)
        self.height3d = 0.4
        self.width3d = 0.03
        
        self.xoffset = int((self.bar.ix - Display.INSTANCE.width) * 0.5)
        self.yoffset = int((self.bar.iy - Display.INSTANCE.height) * 0.5)

        self.sprite = pi3d.FlipSprite(camera=camera, w=self.bar.ix, h=self.bar.iy, y=ypos, z=5, flip=True)
#       self.sprite = pi3d.FlipSprite(camera=camera, w=self.width3d, h=self.height3d, z=5, flip=True)
#        self.plane = pi3d.Plane(camera=camera, w=self.bar.ix, h=self.bar.iy, z=5, ry=math.radians(180))
#        self.plane = pi3d.Plane(camera=camera, w=self.width3d, h=self.height3d, z=5) #ry=math.radians(180)


    def generate_bar(self, font, barcolour=(50, 200, 50, 1.0), fontcolour=(50, 200, 50, 1.0), shaders=[None], width=0.3, thickness = 2, bar_gap=0.05, font_bar_gap=0.07, strscale=0.6):
        """ *shaders* is array of [flatsh, matsh]    """

        self.genshaders = shaders
        flatsh = self.genshaders[0]
        matsh = self.genshaders[1]

        self.font = font

        from pi3d.Display import Display
        bar_width = width * Display.INSTANCE.width
        
#        self.bar.start_layer()
        self.bar._start()
        
        bar_shape = pi3d.Plane(camera=self.camera,  w=bar_width, h=thickness)
        bar_shape.set_draw_details(matsh, [], 0, 0)
        bar_shape.set_material(barcolour)
    #        bar_shape.set_alpha(0.5)
        bar_shape.position( self.xoffset,  self.yoffset, 5)            
        bar_shape.draw()
    
        degText = "%01d" % self.degree
        degStr = pi3d.String(camera=self.camera, font=font, string=degText, sx=0.6, sy=0.6, justify='R')  #sx=0.5, sy=0.5 self.font_scale
        degStr.position(bar_width/2 + (font_bar_gap * self.pixel_width) + self.xoffset, self.yoffset,5)
        degStr.set_shader(flatsh)
        degStr.set_material(fontcolour)
        degStr.draw()
    
        degStr = pi3d.String(camera=self.camera, font=font, string=degText, sx=0.6, sy=0.6, justify='C')  #sx=0.5, sy=0.5 self.font_scale
        degStr.position((-bar_width/2) - (font_bar_gap * self.pixel_width) + self.xoffset,  self.yoffset,5) # - (self.bar_gap * self.screen_width)
        degStr.set_shader(flatsh)
        degStr.set_material(fontcolour)
        degStr.draw()
        
        self.bar._end()
#        self.bar.end_layer()

    def draw_bar(self, camera=None):
#        self.bar.draw_layer()
#        self.sprite.draw(self.shader, [self.bar])
        if camera == None:
            camera = self.camera

        self.sprite.draw(self.shader, [self.bar], camera = camera)



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

        # 2d camera for generating sprites
        self.camera = camera    #pi3d.Camera(is_3d=False)
        self.shader = shader
        
        # camera for viewing the placed sprites
        self.camera2d = pi3d.Camera(is_3d = False)
        self.camera3d = pi3d.Camera()
        
        self.flatsh = shader    #pi3d.Shader("uv_flat")
        self.matsh = pi3d.Shader("mat_flat")

        self.screen_width = Display.INSTANCE.width
        self.screen_height = Display.INSTANCE.height
 
        self.bar_count = int(math.ceil(self.maxDegrees / self.degstep))
        self.pixelsPerBar = self.screenstep * self.screen_height
        
        self.bar_pixel_height = int(Display.INSTANCE.height * 0.1)

        self.bars = []
        for i in xrange(-2,3):     #(-self.bar_count,self.bar_count):
            degstep = i * self.degstep
            bar = HUDladderBar(self.camera, self.shader, degstep, ypos=int(degstep*self.pixelsPerBar/self.degstep))
            self.bars.append(bar)

#        self.bar = pi3d.Layer(camera=camera, shader=shader, z=4.8, flip=True)
        self.bar = HUDladderBar(self.camera, self.shader, 1, ypos=0 )

        self.inits_done = 0
        

    def _gen_ladder(self):
        """ Generate the ladder in OffScreenTexture and Sprite """        
        self.bar.generate_bar(font=self.font, shaders=[self.flatsh, self.matsh])
        self.bar.draw_bar()
        self.bar.generate_bar(font=self.font, shaders=[self.flatsh, self.matsh])

        for bar in self.bars:
            bar.generate_bar(font=self.font, shaders=[self.flatsh, self.matsh])
            bar.draw_bar()
            bar.generate_bar(font=self.font, shaders=[self.flatsh, self.matsh])
            
#        for bar in self.bars:
#            bar.draw_bar()

#        self.bar.generate_bar(font=self.font, shaders = [self.flatsh, self.matsh])
        
        
    def gen_ladder(self):
        if self.inits_done < 1:
            self._gen_ladder()
            self.inits_done += 1
        
       
    def draw_ladder(self):
        if self.inits_done > 0:
            pos=0
            rot = 0
            self.camera2d.reset()
            self.camera2d.position((0,5,0))
            self.camera2d.rotateZ(25)
#            self.bar.draw_bar(self.camera2d)
            for bar in self.bars:
                bar.draw_bar(self.camera2d)
            
#            self.camera2d.reset()
#