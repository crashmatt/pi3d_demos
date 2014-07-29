#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals


import math, random, time, string

#import demo
import pi3d

from HUDladder import HUDladder
from LayerItems import LayerText
from LayerItems import LayerVarText
from LayerItems import LayerItems
from LayerItems import LayerNumeric
from LayerItems import LayerShape
from LayerItems import LayerDynamicShape
from ScreenGrid import ScreenScale

from Indicator import LinearIndicator
from Indicator import DirectionIndicator

from Box2d import Box2d

import HUDConfig as HUDConfig
import os

print("=====================================================")
print("press escape to escape")
print("=====================================================")



class HUD(object):
    def __init__(self):

        self.working_directory = os.getcwd()
        print("Working directory = " + self.working_directory)
               
        self.hud_update_frames = 4
        
        self.layer_text_spacing = 14
        
        self.fps = 20
        
        self.init_vars()
        self.init_graphics()
        self.init_run()

    def init_vars(self):
        self.pitch = 0
        self.roll = 0
        self.pitch_rate = -2
        self.roll_rate = 3
        self.heading_rate = 15
        self.track_rate = 1
        self.track = 325
        self.tas = 131              # true airspeed
        self.ias = 121              # indicated airspeed
        self.aspd_rate = 1
        self.groundspeed = 300
        self.windspeed = 15
        self.heading = 221
        self.home = 120
        self.home_dist = 50
        self.home_dist_scaled = 0
        self.home_dist_units = "m"
        self.vertical_speed = -3.12
        self.asl = 1024             #altitude above sea level
        self.agl = 880              #altitude above ground level
        self.ahl = 880              #altitude above home level
        self.slip = 0
        
#        self.climb_rate = 2.24
        
    def init_graphics(self):
        """ Initialise the HUD graphics """

# Setup display and initialise pi3d
        self.DISPLAY = pi3d.Display.create(x=0, y=0, w=640, h=480, frames_per_second=self.fps)
        self.DISPLAY.set_background(0.0, 0.0, 0.0, 0)      # r,g,b,alpha
        
        self.background_colour=(0,0,0,255)
        self.background_distance=2000
        
        self.grid = ScreenScale(0.025,0.075)

        self.fpv_camera = pi3d.Camera.instance()
        self.text_camera = pi3d.Camera(is_3d=False)
        self.hud_camera = self.text_camera

        #setup textures, light position and initial model position

        self.fpv_light = pi3d.Light((0, 0, 1))

        #create shaders
        #shader = pi3d.Shader("uv_reflect")
        self.matsh = pi3d.Shader("mat_flat")  #For fixed color
        self.flatsh = pi3d.Shader("uv_flat")

        #Create layers
        self.dataLayer = pi3d.Layer(camera=self.text_camera, shader=self.flatsh, z=4.8, flip=True)
        self.statusLayer = pi3d.Layer(camera=self.text_camera, shader=self.flatsh, z=4.8, flip=True)
        self.staticLayer = pi3d.Layer(camera=self.text_camera, shader=self.flatsh, z=4.8, flip=True)

        #Create textures

        print("start creating fonts")
        #fonts
        #hudFont = pi3d.Font("fonts/FreeSans.ttf", (50,255,50,220))
        self.hudFont = pi3d.Font("fonts/FreeSansBold.ttf", (50,255,50,220))   #usr/share/fonts/truetype/freefont/
        self.ladderFont = self.hudFont
        self.textFont = self.hudFont

        print("end creating fonts")
        
        print("start creating indicators")
        #Explicit working directory path done so that profiling works correctly. Don't know why. It just is.
        needle_path = os.path.abspath(os.path.join(self.working_directory, 'default_needle.img'))

        x,y = self.grid.get_grid_pixel(14, 0)
        self.VSI = LinearIndicator(self.text_camera, self.flatsh, self.matsh, self, "vertical_speed", 
                                   indmax=200, indmin=-200, x=x, y=y, z=3, width=18, length=180, 
                                   orientation="V", line_colour=(255,255,255,255), fill_colour=(0,0,0,0.5), 
                                   line_thickness = 1, needle_img=needle_path)

        #Add slip indicator.  Scale is in degrees
        x,y = self.grid.get_grid_pixel(0, -6)
        self.slip_indicator = LinearIndicator(self.text_camera, self.flatsh, self.matsh, self, "slip", 
                                              indmax=5, indmin=-5, x=x, y=y, z=3, width=21, length=250, 
                                              orientation="H", line_colour=(255,255,255,255), fill_colour=(0,0,0,0.75), 
                                              line_thickness = 1, needle_img=needle_path)
        print("end creating indicators")


        print("start creating ladder")
        self.ladder = HUDladder(font=self.hudFont, camera=self.hud_camera, shader=self.flatsh)
        print("end creating ladder")

        self.background = pi3d.Plane(w=self.DISPLAY.width, h=self.DISPLAY.height, z=self.background_distance,
                                camera=self.hud_camera, name="background", )
        self.background.set_draw_details(self.matsh, [], 0, 0)
        self.background.set_material(self.background_colour)

        print("start creating layers")

        text_camera = self.text_camera
        textFont = self.textFont
        flatsh = self.flatsh
        matsh = self.matsh
        hudFont = textFont        
        layer_text_spacing = self.layer_text_spacing
        
        self.dynamic_items = LayerItems()
        
 #       x,y = self.grid.get_grid_pixel(18, 0)
 #       self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
 #                                                 text="{:+02.0f}", dataobj=self,  attr="pitch", digits=3, phase=0, 
 #                                                 x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='L') )

#        x,y = self.grid.get_grid_pixel(18, 1)
#        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
#                                                 text="{:+03.0f}", dataobj=self,  attr="roll", digits=4, phase=0,
#                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='L') )
        # Heading number
        x,y = self.grid.get_grid_pixel(5, 5)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:3.0f}", dataobj=self,  attr="heading", digits=3, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='C') )
        # Altitude above ground
        x,y = self.grid.get_grid_pixel(15, 5)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:+04.0f}", dataobj=self,  attr="agl", digits=4, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='R') )
        # True airspeed number
        x,y = self.grid.get_grid_pixel(-19, 5)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:03.0f}", dataobj=self,  attr="tas", digits=3, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='R') )

        # Home distance number
        x,y = self.grid.get_grid_pixel(-6, 5)
        self.home_distance_number = LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:03.0f}", dataobj=self,  attr="home_dist_scaled", digits=4, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='R')
        self.dynamic_items.add_item( self.home_distance_number )

        #Groundspeed
        x,y = self.grid.get_grid_pixel(-19, 4)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:03.0f}", dataobj=self,  attr="groundspeed", digits=3, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='R') )

        #Vertical speed
        x,y = self.grid.get_grid_pixel(13, 3)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:+03.0f}", dataobj=self,  attr="vertical_speed", digits=4, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='C') )
        
        self.dynamic_items.add_item( LayerDynamicShape(self.VSI, phase=0) )
        
        self.dynamic_items.add_item( LayerDynamicShape(self.slip_indicator, phase=0) )
        
                #Explicit working directory path done so that profiling works correctly. Don't know why. It just is.
        pointer_path = os.path.abspath(os.path.join(self.working_directory, 'default_pointer.png'))
        
        #heading pointer
        x,y = self.grid.get_grid_pixel(9, 5)
        self.dynamic_items.add_item( DirectionIndicator(text_camera, self.flatsh, self.matsh, dataobj=self, attr="heading", 
                                                        x=x, y=y, z=3, pointer_img=pointer_path, phase=2) )
        #Home pointer
        x,y = self.grid.get_grid_pixel(-7, 5)
        self.dynamic_items.add_item( DirectionIndicator(text_camera, self.flatsh, self.matsh, dataobj=self, attr="home", 
                                                        x=x, y=y, z=3, pointer_img=pointer_path, phase=2) )


        self.static_items = LayerItems()
        #First item with matsh to make it work.  Don't know why.  It just is. But maybe not anymore!
        
        x,y = self.grid.get_grid_pixel(19, 5)   
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh, 
                                                     line_colour=(0,255,0,0.7), fill_colour=(0,0,0,0.75), 
                                                     w=layer_text_spacing*8, h=25, x=x, y=y, z=6, line_thickness=1, justify='L')) )
        
        self.static_items.add_item( LayerShape(self.VSI.bezel) )
        self.static_items.add_item( LayerShape(self.slip_indicator.bezel) )
        

        #Heading text box
        x,y = self.grid.get_grid_pixel(5, 5)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh,
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,2),
                                                     w=layer_text_spacing*3.5, h=25, x=x+5, y=y, z=6, 
                                                     line_thickness=1, justify='C')) )

        #Home distance text box
        x,y = self.grid.get_grid_pixel(-2, 5)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh,
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,2),
                                                     w=layer_text_spacing*8, h=25, x=x-5, y=y, z=6, 
                                                     line_thickness=1, justify='C')) )

        #AGL text box
        x,y = self.grid.get_grid_pixel(13, 5)
        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
                                              text="agl", x=x, y=y, size=0.1) )
        
        #True airspeed label
        x,y = self.grid.get_grid_pixel(-14, 5)
        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
                                              text="tas", x=x, y=y, size=0.1) )

        #groundspeed label
        x,y = self.grid.get_grid_pixel(-14, 4)
        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
                                              text="gspd", x=x, y=y, size=0.1) )
        
        # True airspeed text box
        x,y = self.grid.get_grid_pixel(-19, 5)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh, 
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,0.75), 
                                                     w=120, h=25, x=x, y=y, z=6, line_thickness=1, justify='R')) )
        # Groundspeed text box
        x,y = self.grid.get_grid_pixel(-19, 4)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh, 
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,0.75), 
                                                     w=120, h=25, x=x, y=y, z=6, line_thickness=1, justify='R')) )



        self.status_items = LayerItems()
#        #First item with matsh to make it work.  Don't know why.  It just is.
#        self.status_items.add_item( LayerText(hudFont, camera=text_camera, shader=matsh, 
#                                              text=" ", x=1.0, y=1.0, size=0.125, phase=0) )
        x,y = self.grid.get_grid_pixel(0, 6)
        self.status_items.add_item( LayerText(hudFont, camera=text_camera, shader=flatsh, 
                                              text="MODE", x=x, y=y, size=0.1, phase = 1) )
        
        # Home distance units
        x,y = self.grid.get_grid_pixel(-1, 5)
        self.status_items.add_item( LayerVarText(hudFont, text="{:s}", dataobj=self, attr="home_dist_units", camera=text_camera, shader=flatsh, x=x, y=y, z=0.5, size=0.125, phase=None) )

        print("finished creating layers")


    def init_run(self):

        self.tick = 0
        self.av_fps = self.fps
        #i_n=0
        self.spf = 1.0 # seconds per frame, i.e. water image change
        self.next_time = time.time() + self.spf

        # Fetch key presses.
        self.mykeys = pi3d.Keyboard()
        #fr = 0

        self.hud_update_frame = 0
        self.timestamp = time.clock()

#        self.frameCount = 0

    def run_hud(self):
        """ run the HUD main loop """
        while self.DISPLAY.loop_running():
            self.dynamic_items.gen_items(self.hud_update_frame)

            if(self.hud_update_frame == 2):
                self.dataLayer.start_layer()               # Draw on the text layer
                self.dynamic_items.draw_items()
                self.dataLayer.end_layer()                 # stop drawing on the text layer    
            elif(self.hud_update_frame == 3):
                if(self.status_items.gen_items(phase=None)):
                    self.statusLayer.start_layer()
                    self.status_items.draw_items()
                    self.statusLayer.end_layer()
                
            elif(self.hud_update_frame == 4):
                self.ladder.gen_ladder()

                if self.static_items.gen_items():
                    self.staticLayer.start_layer()
                    self.static_items.draw_items()
                    self.ladder.draw_center()
                    self.staticLayer.end_layer()

            
      
# try glScissor for limiting extent of ladder drawing

            self.background.draw()
            self.ladder.draw_ladder(self.roll, self.pitch, 0)

            self.dataLayer.draw_layer()
            self.statusLayer.draw_layer()
            self.staticLayer.draw_layer()
  
            if time.time() > self.next_time:
                self.next_time = time.time() + self.spf
                self.av_fps = self.av_fps*0.9 + self.tick/self.spf*0.1 # exp smooth moving average
#                print(av_fps, " FPS, ", pitch, " pitch")
                self.tick = 0
    
            self.tick += 1
  
            self.hud_update_frame += 1
            if(self.hud_update_frame > self.hud_update_frames):
                self.hud_update_frame = 0
  

            #pi3d.screenshot("/media/E856-DA25/New/fr%03d.jpg" % fr)
  #          frameCount += 1

            k = self.mykeys.read()
            if k==27:
                self.mykeys.close()
                self.dataLayer.delete_buffers()
                self.staticLayer.delete_buffers()
                self.statusLayer.delete_buffers()
                self.DISPLAY.destroy()
                break

            self.update()
        quit()

    def update(self):
        self.simulate()
        self.home_dist_scale()
    
    def home_dist_scale(self):
        if(self.home_dist >=1000):
            self.home_dist_scaled = self.home_dist * 0.001
            self.home_dist_units = "km"
            if(self.home_dist_scaled > 9.9):
                self.home_distance_number.textformat = "{:02.1f}"
            else:
                self.home_distance_number.textformat = "{:01.2f}"
        else:
            self.home_dist_scaled = int(self.home_dist)
            self.home_dist_units = "m"
            self.home_distance_number.textformat = "{:03.0f}"
        
    def simulate(self):
        frametime = 1 / self.av_fps
        self.pitch += self.pitch_rate * frametime
        self.roll += self.roll_rate * frametime
        self.agl += self.vertical_speed * frametime
        self.heading += self.heading_rate * frametime
        self.tas += self.aspd_rate * frametime
        self.ias += self.aspd_rate * frametime
        self.vertical_speed =  random.randrange(-200, 200, 1)
        self.slip = float(random.randrange(-50,50)) * 0.1
        self.home += self.heading_rate * frametime
        self.home_dist += self.groundspeed *(1/3.6) * frametime
        
            
        # Temporary
        if(self.pitch > 70):
            self.pitch -= 140
        elif(self.pitch < -70):
            self.pitch += 140
        
        if(self.roll > 360):
            self.roll -= 360
        elif(self.roll < -360):
            self.roll += 360

        if(self.heading > 360):
            self.heading -= 360
        elif(self.heading < 0):
            self.heading -= 360
            
        if(self.home > 360):
            self.home -= 360
        elif(self.home < 0):
            self.home -= 360
            

    
hud=HUD()
hud.init_run()
hud.run_hud()
