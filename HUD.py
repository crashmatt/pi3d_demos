#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

from pi3d.util.OffScreenTexture import OffScreenTexture

import math, random, time, glob, string, pickle

import ConfigParser

#import demo
import pi3d

import numeric
from HUDladder import HUDladder
from LayerItems import LayerText
from LayerItems import LayerVarText
from LayerItems import LayerItems
from LayerItems import LayerNumeric
from LayerItems import LayerShape
from ScreenGrid import ScreenScale

from Box2d import Box2d

import HUDConfig as HUDConfig

print("=====================================================")
print("press escape to escape")
print("move this terminal window to top of screen to see FPS")
print("=====================================================")



class HUD(object):
    def __init__(self):

        
        self.hud_update_frames = 4
        
        self.layer_text_spacing = 16
        
        self.fps = 25
        
        self.init_vars()
        self.init_graphics()
        self.init_run()

    def init_vars(self):
        self.pitch = 0
        self.roll = 0
        self.pitch_rate = 5
        self.roll_rate = 3
        self.heading_rate = 15
        self.track_rate = 1
        self.track = 325
        self.tas = 131              # true airspeed
        self.ias = 121              # indicated airspeed
        self.aspd_rate = 1
        self.groundspeed = 110
        self.windspeed = 15
        self.heading = 221
        self.vertical_speed = -3.12
        self.asl = 1024             #altitude above sea level
        self.agl = 880              #altitude above ground level
        self.ahl = 880              #altitude above home level
        
#        self.climb_rate = 2.24
        
    def init_graphics(self):
        """ Initialise the HUD graphics """

# Setup display and initialise pi3d
        self.DISPLAY = pi3d.Display.create(x=0, y=0, w=576, h=480, frames_per_second=self.fps)
        self.DISPLAY.set_background(0.0, 0.0, 0.0, 0)      # r,g,b,alpha
        
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


        print("start creating ladder")
        self.ladder = HUDladder(font=self.hudFont, camera=self.hud_camera, shader=self.flatsh)
        print("end creating ladder")


        print("start creating layers")

#digitsmap =

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
        
        x,y = self.grid.get_grid_pixel(0, 6)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:3.0f}", dataobj=self,  attr="heading", digits=3, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='C') )

        x,y = self.grid.get_grid_pixel(18, 5)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:+04.0f}", dataobj=self,  attr="agl", digits=4, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='L') )

        x,y = self.grid.get_grid_pixel(-19, 5)
        self.dynamic_items.add_item( LayerNumeric(camera=text_camera, font=textFont, shader=flatsh, 
                                                 text="{:03.0f}", dataobj=self,  attr="tas", digits=4, phase=0,
                                                  x=x, y=y, size=0.125, spacing=layer_text_spacing, justify='R') )


        self.static_items = LayerItems()
        #First item with matsh to make it work.  Don't know why.  It just is.
        
        x,y = self.grid.get_grid_pixel(19, 5)   
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh, 
                                                     line_colour=(0,255,0,0.7), fill_colour=(0,0,0,0.75), 
                                                     w=layer_text_spacing*8, h=25, x=x, y=y, z=6, line_thickness=1, justify='L')) )
        
#        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.matsh, 
#                                              text=" ", xpos=1.0, ypos=1.0, size=0.125) )

#        x,y = self.grid.get_grid_pixel(12, 0)
#        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
#                                              text="ptch", x=x, y=y, size=0.1) )
        
#        x,y = self.grid.get_grid_pixel(12, 1)
#        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
#                                              text="roll", x=x, y=y, size=0.1) )
        
#        x,y = self.grid.get_grid_pixel(-2, 6)
#        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
#                                              text="hdg", x=x, y=y, size=0.1) )
        x,y = self.grid.get_grid_pixel(0, 6)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh,
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,2),
                                                     w=layer_text_spacing*3.5, h=25, x=x+5, y=y, z=6, 
                                                     line_thickness=1, justify='C')) )

        
        x,y = self.grid.get_grid_pixel(12, 5)
        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
                                              text="AGL", x=x, y=y, size=0.1) )
        
        
        x,y = self.grid.get_grid_pixel(-12, 5)
        self.static_items.add_item( LayerText(self.textFont, camera=self.text_camera, shader=self.flatsh, 
                                              text="TAS", x=x, y=y, size=0.1) )
        x,y = self.grid.get_grid_pixel(-18, 5)
        self.static_items.add_item( LayerShape(Box2d(camera=self.text_camera, shader=matsh, 
                                                     line_colour=(0,255,0,0.75), fill_colour=(0,0,0,0.75), 
                                                     w=120, h=25, x=x, y=y, z=6, line_thickness=1, justify='R')) )



        self.status_items = LayerItems()
        #First item with matsh to make it work.  Don't know why.  It just is.
        self.status_items.add_item( LayerText(hudFont, camera=text_camera, shader=matsh, 
                                              text=" ", x=1.0, y=1.0, size=0.125, phase=0) )
        x,y = self.grid.get_grid_pixel(0, 6)
        self.status_items.add_item( LayerText(hudFont, camera=text_camera, shader=flatsh, 
                                              text="MODE", x=x, y=y, size=0.1, phase = 1) )
        
#        self.status_items.add_item( LayerVarText(hudFont, text="{:+1.1f}", dataobj=self, attr="pitch", camera=text_camera, shader=flatsh, xpos=0.0, ypos=0.2, size=0.125, phase = 2) )

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
                if(self.status_items.gen_items(self.hud_update_frame)):
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
        self.store_hud_config()
        quit()


    def update(self):
        frametime = 1 / self.av_fps
        self.pitch += self.pitch_rate * frametime
        self.roll += self.roll_rate * frametime
        self.agl += self.vertical_speed * frametime
        self.heading += self.heading_rate * frametime
        self.tas += self.aspd_rate * frametime
        self.ias += self.aspd_rate * frametime
        
        # Temporary
        if(self.pitch > 70):
            self.pitch -= 140
        elif(self.pitch < -360):
            self.pitch += 360
        
        if(self.roll > 360):
            self.roll -= 360
        elif(self.roll < -360):
            self.roll += 360

        if(self.heading > 360):
            self.heading -= 360
        elif(self.heading < 0):
            self.heading -= 360
            
    def store_hud_config(self):
        config = ConfigParser.ConfigParser()
        config.add_section("static_layer")
        
        with open('hud.cfg', 'wb') as configfile:
            config.write(configfile)
    
hud=HUD()
hud.init_run()
hud.run_hud()
