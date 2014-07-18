#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

from pi3d.util.OffScreenTexture import OffScreenTexture

import math, random, time, glob

#import demo
import pi3d

import numeric
from HUDladder import HUDladder

print("=====================================================")
print("press escape to escape")
print("move this terminal window to top of screen to see FPS")
print("=====================================================")


class hud_text():
    def __init__(self, font, text, camera, hud=None, attr=None, shader=None, xpos=0, ypos=0, size=1.0):
        from pi3d.Display import Display
                
        self.attr = attr
        self.hud = hud
        self.font = font
        self.camera = camera
        self.flatsh = shader
        self.value = None
        self.text = text
        self.size = size
        
        self.x = xpos * Display.INSTANCE.height
        self.y = ypos * Display.INSTANCE.width
        
        self.last_formatted_text = ""
        self.changed = False
        self.gen_text()

    def gen_text(self):
        if(self.attr != None) and (self.hud != None):
            value = hud.getattr(self.hud, self.attr, None)
        else:
            value = None

        #if value == None:
        #    txt = self.text
        #else:
        #    txt = self.text % value
        txt = self.text

        if txt != self.last_formatted_text: #getattr(self, "last_formatted_text", ""):
            self.text = pi3d.String(string=self.text, camera=self.camera, font=self.font, is_3d=False, x=self.x, y=self.y, size=self.size, justify='R')
            self.text.position(self.x, self.y, 5)
            self.text.set_material((0,0,0,0))
            self.text.set_shader(self.flatsh)
            self.last_formatted_text = self.text
            self.changed = True
        
        
    def draw_text(self):
        if self.text != None:
            self.text.draw()
            self.changed = False
        

bar_dist = 5
ladder_step = 15
ladder_thickness = 0.01
ladder_zero_thickness = 0.02
ladder_text_xpos = 1.0
ladder_text_size = 0.004
ladder_length = 1.5

pitch = 0
roll = 0
pitch_rate = 10
roll_rate = 3
heading_rate = 1
track_rate = 1
track = 325
airspeed = 121
groundspeed = 110
windspeed = 15

heading = 221
vertical_speed = -312

hud_update_frames = 4
hud_text_spacing = 16

fps = 25

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=0, y=0, w=576, h=480, frames_per_second=fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 0)      # r,g,b,alpha

fpv_camera = pi3d.Camera.instance()
text_camera = pi3d.Camera(is_3d=False)
hud_camera = text_camera

#setup textures, light position and initial model position

fpv_light = pi3d.Light((0, 0, 1))

#create shaders
#shader = pi3d.Shader("uv_reflect")
matsh = pi3d.Shader("mat_flat")  #For fixed color
flatsh = pi3d.Shader("uv_flat")

#Create layers
dataLayer = pi3d.Layer(camera=text_camera, shader=flatsh, z=4.8, flip=True)
statusLayer = pi3d.Layer(camera=text_camera, shader=flatsh, z=4.8, flip=True)

#Create textures

print("start creating fonts")
#fonts
#hudFont = pi3d.Font("fonts/FreeSans.ttf", (50,255,50,220))
hudFont = pi3d.Font("fonts/FreeSansBold.ttf", (50,255,50,220))   #usr/share/fonts/truetype/freefont/


ladderFont = hudFont
textFont = hudFont

print("end creating fonts")


print("start creating ladder")
                  
ladder = HUDladder(font=hudFont, camera=hud_camera, shader=flatsh)


print("end creating ladder")


print("start creating digits")

#digitsmap =

pitch_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=0, size=0.125, spacing=hud_text_spacing)
roll_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=50, size=0.125, spacing=hud_text_spacing)
heading_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=100, size=0.125, spacing=hud_text_spacing)
track_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=150, size=0.125, spacing=hud_text_spacing)
airspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=-50, size=0.125, spacing=hud_text_spacing)
groundspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=100, y=-30, size=0.125, spacing=hud_text_spacing)
windspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=2, x=100, y=0, size=0.125, spacing=hud_text_spacing)
vertical_speed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=5, x=180, y=-200, size=0.125, spacing=hud_text_spacing)

print("finished creating digits")

statusText = []
statusText.append( hud_text(hudFont, text=" ", camera=text_camera, shader=matsh, xpos=1.0, ypos=1.0, size=0.125) )
statusText.append( hud_text(hudFont, text="LABEL HERE", camera=text_camera, shader=flatsh, xpos=0.0, ypos=0.0, size=0.125) )
statusText.append( hud_text(hudFont, text="LABEL THERE", camera=text_camera, shader=flatsh, xpos=0.0, ypos=-0.1, size=0.125) )
statusText.append( hud_text(hudFont, text="LABEL IT", camera=text_camera, shader=flatsh, xpos=0.0, ypos=-0.2, size=0.125) )

tick = 0
av_fps = fps
#i_n=0
spf = 1.0 # seconds per frame, i.e. water image change
next_time = time.time() + spf

# Fetch key presses.
mykeys = pi3d.Keyboard()
#fr = 0

hud_update_frame = 0
timestamp = time.clock()

frameCount = 0

# Display scene and rotate shape
while DISPLAY.loop_running():

  if(hud_update_frame == 0):
      pitch_text.set_number("%01d" % pitch)
      roll_text.set_number("%01d" % roll)
  elif(hud_update_frame == 1):    
      heading_text.set_number("%01d" % heading)
      track_text.set_number("%01d" % track)
      airspeed_text.set_number("%01d" % airspeed)
  elif(hud_update_frame == 2):
      windspeed_text.set_number("%01d" % av_fps)
      groundspeed_text.set_number("%01d" % groundspeed)
      vertical_speed_text.set_number("%01d" % vertical_speed)
  elif(hud_update_frame == 3):    
      dataLayer.start_layer()               # Draw on the text layer
      pitch_text.draw()
      roll_text.draw()
      heading_text.draw()
      track_text.draw()
      airspeed_text.draw()
      windspeed_text.draw()
      groundspeed_text.draw()
      vertical_speed_text.draw()
      dataLayer.end_layer()                 # stop drawing on the text layer    

      statuschange = False
      for text in statusText:
          text.gen_text()
          if text.changed:
              statuschange = True
      if statuschange:
          statusLayer.start_layer()
          for text in statusText:
              text.draw_text()
          statusLayer.end_layer()

      ladder.gen_ladder()
      
# try glScissor for limiting extent of ladder drawing

  ladder.draw_ladder(roll, pitch, 0)

  dataLayer.draw_layer()
  statusLayer.draw_layer()
  
  if time.time() > next_time:
    next_time = time.time() + spf
    av_fps = av_fps*0.9 + tick/spf*0.1 # exp smooth moving average
#    print(av_fps, " FPS, ", pitch, " pitch")
    tick = 0
    
  tick += 1

  pitch += pitch_rate / av_fps
  roll += roll_rate / av_fps
  
  hud_update_frame += 1
  if(hud_update_frame > hud_update_frames):
      hud_update_frame = 0
  
  # Temporary
  if(pitch > 70):
      pitch -= 140
  elif(pitch < -360):
      pitch += 360
  if(roll > 360):
      roll -= 360
  elif(roll < -360):
      roll += 360

  #pi3d.screenshot("/media/E856-DA25/New/fr%03d.jpg" % fr)
  frameCount += 1

  k = mykeys.read()
  if k==27:
    mykeys.close()
    dataLayer.delete_buffers()
    DISPLAY.destroy()
    break

quit()
