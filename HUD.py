#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals



import math, random, time, glob

import demo
import pi3d
import numeric

print("=====================================================")
print("press escape to escape")
print("move this terminal window to top of screen to see FPS")
print("=====================================================")


bar_dist = 5
ladder_step = 15
ladder_thickness = 0.01
ladder_zero_thickness = 0.02
ladder_text_xpos = 1.0
ladder_text_size = 0.004
ladder_length = 1.5

pitch = 0
roll = 0
pitch_rate = 20
roll_rate = 12
heading_rate = 1
track_rate = 1
track = -5
airspeed = 121
groundspeed = 110
windspeed = 15

heading = 121
vertical_speed = -312

hud_update_frames = 4
hud_text_spacing = 16

fps = 25

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=0, y=0, w=576, h=480, frames_per_second=fps)
DISPLAY.set_background(0.0, 0.0, 0.0, 1)      # r,g,b,alpha

fpv_camera = pi3d.Camera.instance()
hud_camera = pi3d.Camera()
text_camera = pi3d.Camera(is_3d=False)

#setup textures, light position and initial model position
#pi3d.Light((5, -5, 8))
fpv_light = pi3d.Light((0, 0, 1))

#create shaders
#shader = pi3d.Shader("uv_reflect")
matsh = pi3d.Shader("mat_flat")  #For fixed color
flatsh = pi3d.Shader("uv_flat")
#textsh = pi3d.Shader("uv_flat")

#Create textures
#shapeimg = pi3d.Texture("textures/straw1.jpg")

print("start creating fonts")
#fonts
hudFont = pi3d.Font("fonts/FreeSans.ttf", (50,200,50,255))

ladderFont = hudFont
textFont = hudFont

print("end creating fonts")


print("start creating ladder")
#build the bar shapes
upper_bars = pi3d.MergeShape(camera = fpv_camera)
lower_bars = pi3d.MergeShape(camera = fpv_camera)
center_bars = pi3d.MergeShape(camera = fpv_camera)
bar_text = pi3d.MergeShape(camera = fpv_camera)

#acylinder = pi3d.Cylinder(camera=fpv_camera, radius=ladder_thickness, height=ladder_length, sides=ladder_sides)
bar_shape = pi3d.Plane(camera=fpv_camera,  w=ladder_length, h=ladder_thickness)

bar_steps = int(180 / ladder_step)

for step in xrange(1, bar_steps):
   angle = step*ladder_step
   ypos = bar_dist * math.sin(math.radians(angle))
   zpos = bar_dist * math.cos(math.radians(angle))
   
   upper_bars.add(bar_shape, x=0, y=ypos, z=zpos, rx=-angle, ry=0, rz=0)
   lower_bars.add(bar_shape, x=0, y=-ypos, z=zpos, rx=angle, ry=0, rz=0)
   
   num_str = "%01d" % angle
   ladder_str = pi3d.String(camera=fpv_camera, font=ladderFont, string=num_str, sx=ladder_text_size, sy=ladder_text_size)
   bar_text.add(ladder_str, x=ladder_text_xpos, y=ypos, z=zpos, rx=-angle, ry=0, rz=0)
   bar_text.add(ladder_str, x=-ladder_text_xpos, y=ypos, z=zpos, rx=-angle, ry=0, rz=0)

   num_str = "%01d" % -angle
   ladder_str = pi3d.String(camera=fpv_camera, font=ladderFont, string=num_str, sx=ladder_text_size, sy=ladder_text_size)
   bar_text.add(ladder_str, x=ladder_text_xpos, y=-ypos, z=zpos, rx=angle, ry=0, rz=0)
   bar_text.add(ladder_str, x=-ladder_text_xpos, y=-ypos, z=zpos, rx=angle, ry=0, rz=0)

center_bars.add(bar_shape, x=0, y=0, z=bar_dist, rx=0, ry=0, rz=0)
ladder_str = pi3d.String(camera=fpv_camera, font=ladderFont, string="0", sx=ladder_text_size, sy=ladder_text_size)
bar_text.add(ladder_str, x=ladder_text_xpos, y=0, z=bar_dist, rx=0, ry=0, rz=0)
bar_text.add(ladder_str, x=-ladder_text_xpos, y=0, z=bar_dist, rx=0, ry=0, rz=0)


upper_bars.position(0.0, 0.0, 0)
upper_bars.set_draw_details(matsh, [], 1.0, 0.1)
upper_bars.set_material((0, 100, 0, 0.5))
upper_bars.set_alpha(0.5)

lower_bars.position(0.0, 0.0, 0)
lower_bars.set_draw_details(matsh, [], 1.0, 0.1)
lower_bars.set_material((100, 0, 0, 0.5))
lower_bars.set_alpha(0.1)

center_bars.position(0, 0, 0)
center_bars.set_draw_details(matsh, [], 1.0, 0.1)
center_bars.set_material((128, 128, 128, 0.5))
center_bars.set_alpha(1)

bar_text.position(0.0, 0.0, 0)
bar_text.set_draw_details(flatsh, [], 1.0, 0.1)
#bar_text.set_material((100, 0, 0, 0.5))
bar_text.set_alpha(0.1)

print("end creating ladder")


print("start creating digits")
pitch_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=0, size=0.15, spacing=hud_text_spacing)
roll_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=50, size=0.15, spacing=hud_text_spacing)
heading_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=100, size=0.15, spacing=hud_text_spacing)
track_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=150, size=0.15, spacing=hud_text_spacing)
airspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=-50, size=0.15, spacing=hud_text_spacing)
groundspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=3, x=180, y=-100, size=0.15, spacing=hud_text_spacing)
windspeed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=2, x=180, y=-150, size=0.15, spacing=hud_text_spacing)
vertical_speed_text = numeric.FastNumber(camera=text_camera, font=textFont, shader=flatsh, digits=5, x=180, y=-200, size=0.15, spacing=hud_text_spacing)

print("finished creating digits")

tick = 0
av_fps = fps
#i_n=0
spf = 1.0 # seconds per frame, i.e. water image change
next_time = time.time() + spf

# Fetch key presses.
mykeys = pi3d.Keyboard()
fr = 0

hud_update_frame = 0
timestamp = time.clock()

# Display scene and rotate shape
while DISPLAY.loop_running():
  fpv_camera.reset(is_3d=True)
  
  fpv_camera.rotate(0,0,roll)
  fpv_camera.rotate(pitch,0,0)

  pitch_text.set_number("%01d" % pitch)
  roll_text.set_number("%01d" % roll)
  
  heading_text.set_number("%01d" % heading)
  track_text.set_number("%01d" % track)
  airspeed_text.set_number("%01d" % airspeed)
  windspeed_text.set_number("%01d" % windspeed)
  groundspeed_text.set_number("%01d" % groundspeed)
  vertical_speed_text.set_number("%01d" % vertical_speed)

  pitch_text.draw()
  roll_text.draw()
  
  heading_text.draw()
  track_text.draw()
  airspeed_text.draw()
  windspeed_text.draw()
  groundspeed_text.draw()
  vertical_speed_text.draw()

#  light_shape.draw()
  bar_text.draw()
  upper_bars.draw()
  lower_bars.draw()
  center_bars.draw()


  if time.time() > next_time:
    next_time = time.time() + spf
    av_fps = av_fps*0.9 + tick/spf*0.1 # exp smooth moving average
    print(av_fps, " FPS, ", pitch, " pitch")
    tick = 0
    
  tick += 1

  pitch += pitch_rate / av_fps
  roll += roll_rate / av_fps
  
  hud_update_frame += 1
  if(hud_update_frame > hud_update_frames):
      hud_update_frame = 0
  
  # Temporary
  if(pitch > 360):
      pitch -= 360
  elif(pitch < -360):
      pitch += 360
  if(roll > 360):
      roll -= 360
  elif(roll < -360):
      roll += 360

  #pi3d.screenshot("/media/E856-DA25/New/fr%03d.jpg" % fr)
  #fr += 1

  k = mykeys.read()
  if k==27:
    mykeys.close()
    DISPLAY.destroy()
    break

quit()
