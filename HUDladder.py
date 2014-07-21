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

        #For drawing the bar
        self.camera = camera
        self.shader = shader
                
        self.bar = OffScreenTexture("bar", h=self.pixel_height)

        # need to do offscreentexture first so its size can be used for the following.
        self.xoffset = int((self.bar.ix - Display.INSTANCE.width) * 0.5)
        self.yoffset = int((self.bar.iy - Display.INSTANCE.height) * 0.5)

        self.sprite = pi3d.FlipSprite(camera=camera, w=self.bar.ix, h=self.bar.iy, y=ypos, z=5, flip=True)

    def get_bar_colour(self):
        if(self.degree == 0):
            return (255,255,255,255)
        elif(self.degree > 0):
            return (0,255,0,255)
        else:
            return (255,0,0,255)
    
    def get_bar_width(self):
        if(self.degree == 0):
            return 0.3
        else:
            return 0.22
    
    def get_bar_thickness(self):
        if(self.degree == 0):
            return 3
        else:
            return 2
        
    def get_bar_gap(self):
        return 0.05
    
    def get_font_size(self):
        if(self.degree == 0):
            return 0.15
        else:
            return 0.125
    
    def get_font_bar_gap(self):
        return 0.05

#    def get_font_colour(self):
#        return (50, 200, 50, 1.0)
#        return (200, 0, 0, 1.0)

    def generate_bar(self, font, shaders=[None]):
        """ *shaders* is array of [flatsh, matsh]    """

        self.genshaders = shaders
        flatsh = self.genshaders[0]
        matsh = self.genshaders[1]

        self.font = font
        
        barcolour = self.get_bar_colour()
        bar_gap = self.get_bar_gap()
        fontsize = self.get_font_size()
        font_bar_gap = self.get_font_bar_gap()
        
#        fontcolour = self.get_font_colour()

        from pi3d.Display import Display
        bar_width = self.get_bar_width() * Display.INSTANCE.width
        
        self.bar._start()
        
        bar_shape = pi3d.Plane(camera=self.camera,  w=bar_width, h=self.get_bar_thickness())
        bar_shape.set_draw_details(matsh, [], 0, 0)
        bar_shape.set_material(barcolour)
        bar_shape.position( self.xoffset,  self.yoffset, 5)            
        bar_shape.draw()
    
        degText = "%01d" % self.degree
        degStr = pi3d.String(camera=self.camera, font=font, string=degText, size=fontsize, justify='R', is_3d=False)
        degStr.position(bar_width/2 + (font_bar_gap * self.pixel_width) + self.xoffset, self.yoffset,5)
        degStr.set_shader(flatsh)
#        degStr.set_material(fontcolour)
        degStr.draw()
    
        degStr = pi3d.String(camera=self.camera, font=font, string=degText, size=fontsize, justify='C', is_3d=False)
        degStr.position((-bar_width/2) - (font_bar_gap * self.pixel_width) + self.xoffset,  self.yoffset,5)
        degStr.set_shader(flatsh)
#        degStr.set_material(fontcolour)
        degStr.draw()
        
        self.bar._end()

    def draw_bar(self, camera=None, alpha=1):
        if camera == None:
            camera = self.camera

        self.sprite.set_alpha(alpha)
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
        
        self.degstep = 10
        self.screenstep = 0.4           # ratio of screen height
        self.bar_thickness = 1          # pixels
        self.zero_bar_thickness = 2     # pixels
        self.bar_width = 0.2            # ratio of screen width
        self.bar_gap = 0.05             # ratio of screen width
        self.font_scale = 0.08          # relative to original font size
        self.font_bar_gap = 0.07        # ratio of screen width
        self.alpha = 0.8                # 0 to 1
        self.maxDegrees = 80
        

        # 2d camera for generating sprites
        self.camera = camera    #pi3d.Camera(is_3d=False)
        self.shader = shader
        
        # camera for viewing the placed sprites. Owned byt the ladder since it moves
        self.camera2d = pi3d.Camera(is_3d = False)
        
        self.flatsh = shader    #pi3d.Shader("uv_flat")
        self.matsh = pi3d.Shader("mat_flat")

        self.screen_width = Display.INSTANCE.width
        self.screen_height = Display.INSTANCE.height
 
        self.bar_count = int(math.ceil(self.maxDegrees / self.degstep))
        self.pixelsPerBar = self.screenstep * self.screen_height
        
        self.bar_pixel_height = int(Display.INSTANCE.height * 0.1)

        self.bars = []
        for i in xrange(-self.bar_count,self.bar_count+1):     #(-self.bar_count,self.bar_count):
            degstep = i * self.degstep
            bar = HUDladderBar(self.camera, self.shader, degstep, ypos=int(degstep*self.pixelsPerBar/self.degstep))

            self.bars.append(bar)

        self.inits_done = 0
        

    def _gen_ladder(self):
        """ Generate the ladder """
        for bar in self.bars:
            bar.draw_bar()
            bar.generate_bar(font=self.font, shaders=[self.flatsh, self.matsh])
        
    def gen_ladder(self):
        if self.inits_done < 1:
            self._gen_ladder()
            self.inits_done += 1
        
       
    def draw_ladder(self, roll, pitch, yaw):
        """ Draw the ladder. roll, pitch, yaw parameters in degrees"""
        if self.inits_done > 0:
            pos=0
            rot = 0
            ypos = pitch * self.pixelsPerBar / self.degstep
            pitchrange = self.degstep * 0.5 / self.screenstep
            lowpitch = pitch - pitchrange 
            highpitch = pitch + pitchrange
            
            self.camera2d.reset()
            self.camera2d.rotateZ(roll)
            self.camera2d.position((0,ypos,0))

            for bar in self.bars:
                if(bar.degree < highpitch) and (bar.degree > lowpitch):
                    bar.draw_bar(self.camera2d, alpha=self.alpha)
            
