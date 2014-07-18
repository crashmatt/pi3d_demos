#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

from pi3d.util.OffScreenTexture import OffScreenTexture

import math, random, time, glob, string

#import demo
import pi3d

import numeric
from HUDladder import HUDladder
from LayerItems import layer_text
from LayerItems import layer_var_text
from LayerItems import layer_items

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
        self.pitch_rate = 10
        self.roll_rate = 3
        self.heading_rate = 1
        self.track_rate = 1
        self.track = 325
        self.airspeed = 121
        self.groundspeed = 110
        self.windspeed = 15
        self.heading = 221
        self.vertical_speed = -312        
        
    def init_graphics(self):
        """ Initialise the HUD graphics """

# Setup display and initialise pi3d
        self.DISPLAY = pi3d.Display.create(x=0, y=0, w=576, h=480, frames_per_second=self.fps)
        self.DISPLAY.set_background(0.0, 0.0, 0.0, 0)      # r,g,b,alpha

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


        print("start creating digits")

#digitsmap =

        text_camera = self.text_camera
        textFont = self.textFont
        flatsh = self.flatsh
        matsh = self.matsh
        hudFont = textFont
        
        self.testText = pi3d.String(string="BLAH BLAH", camera=self.text_camera, font=self.textFont, is_3d=False, x=0, y=0, size=0.25, justify='R')
        self.testText.set_shader(self.flatsh)
        
        
        layer_text_spacing = self.layer_text_spacing
        self.pitch_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=0, size=0.125, spacing=layer_text_spacing)
        self.roll_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=50, size=0.125, spacing=layer_text_spacing)
        self.heading_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=100, size=0.125, spacing=layer_text_spacing)
        self.track_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=150, size=0.125, spacing=layer_text_spacing)
        self.airspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=-50, size=0.125, spacing=layer_text_spacing)
        self.groundspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=100, y=-30, size=0.125, spacing=layer_text_spacing)
        self.windspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=2, x=100, y=0, size=0.125, spacing=layer_text_spacing)
        self.vertical_speed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=5, x=180, y=-200, size=0.125, spacing=layer_text_spacing)

        print("finished creating digits")

        self.staticText = []
        #draw one offscreen with matsh shader to make this work.  Why? Who knows?
        self.staticText.append( layer_text(self.textFont, text=" ", camera=self.text_camera, shader=self.matsh, xpos=1.0, ypos=1.0, size=0.125) )
        self.staticText.append( layer_text(self.textFont, text="LABEL HERE", camera=self.text_camera, shader=self.flatsh, xpos=0.0, ypos=0.0, size=0.125) )
        self.staticText.append( layer_text(self.textFont, text="LABEL THERE", camera=self.text_camera, shader=self.flatsh, xpos=0.0, ypos=-0.1, size=0.125) )
        self.staticText.append( layer_text(self.textFont, text="LABEL IT", camera=self.text_camera, shader=self.flatsh, xpos=0.0, ypos=-0.2, size=0.125) )
        #staticText.append( layer_var_text(hudFont, text="%01d", dataobj=self, attr="windspeed", camera=text_camera, shader=flatsh, xpos=0.0, ypos=-0.2, size=0.125) )

        self.statusText = []
        #draw one offscreen with matsh shader to make this work.  Why? Who knows?
        self.statusText.append( layer_text(hudFont, text=" ", camera=text_camera, shader=matsh, xpos=1.0, ypos=1.0, size=0.125) )
        self.statusText.append( layer_text(hudFont, text="LABEL NOT", camera=text_camera, shader=flatsh, xpos=0.0, ypos=0.1, size=0.125) )
        self.statusText.append( layer_var_text(hudFont, text="{:1.1f}", dataobj=self, attr="roll", camera=text_camera, shader=flatsh, xpos=0.0, ypos=0.2, size=0.125) )

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
            if(self.hud_update_frame == 0):
                self.pitch_text.set_number("%01d" % self.pitch)
                self.roll_text.set_number("%01d" % self.roll)
            elif(self.hud_update_frame == 1):    
                self.heading_text.set_number("%01d" % self.heading)
                self.track_text.set_number("%01d" % self.track)
                self.airspeed_text.set_number("%01d" % self.airspeed)
            elif(self.hud_update_frame == 2):
                self.windspeed_text.set_number("%01d" % self.av_fps)
                self.groundspeed_text.set_number("%01d" % self.groundspeed)
                self.vertical_speed_text.set_number("%01d" % self.vertical_speed)
            elif(self.hud_update_frame == 3):
                self.dataLayer.start_layer()               # Draw on the text layer
                self.pitch_text.draw()
                self.roll_text.draw()
                self.heading_text.draw()
                self.track_text.draw()
                self.airspeed_text.draw()
                self.windspeed_text.draw()
                self.groundspeed_text.draw()
                self.vertical_speed_text.draw()
                self.dataLayer.end_layer()                 # stop drawing on the text layer    
            elif(self.hud_update_frame == 4):
                self.ladder.gen_ladder()

                statuschange = False
                for text in self.staticText:
                    text.gen_text()
                    if text.changed:
                        statuschange = True
                if statuschange:
                    self.staticLayer.start_layer()
                    for text in self.staticText:
                        text.draw_text()
                    self.staticLayer.end_layer()
                self.staticText[0].text = "changed it again"

                statuschange = False
                for text in self.statusText:
                    text.gen_text()
                    if text.changed:
                        statuschange = True
                if statuschange:
                    self.statusLayer.start_layer()
                    for text in self.statusText:
                        text.draw_text()
                    self.statusLayer.end_layer()
                self.staticText[0].text = "changed it again"

      
# try glScissor for limiting extent of ladder drawing

            self.ladder.draw_ladder(self.roll, self.pitch, 0)

            self.dataLayer.draw_layer()
            self.staticLayer.draw_layer()
            self.statusLayer.draw_layer()
  
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
        self.pitch += self.pitch_rate / self.av_fps
        self.roll += self.roll_rate / self.av_fps
        # Temporary
        if(self.pitch > 70):
            self.pitch -= 140
        elif(self.pitch < -360):
            self.pitch += 360
        if(self.roll > 360):
            self.roll -= 360
        elif(self.roll < -360):
            self.roll += 360


hud=HUD()
hud.init_run()
hud.run_hud()
