#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals



import math, random, time, glob

import demo
import pi3d

print("=====================================================")
print("press escape to escape")
print("move this terminal window to top of screen to see FPS")
print("=====================================================")

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=0, y=0, w=576, h=480, frames_per_second=25.0)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.5)      # r,g,b,alpha

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
flat2dsh = pi3d.Shader("2d_flat")

#Create textures
shapeimg = pi3d.Texture("textures/straw1.jpg")

#fonts
ladderFont = pi3d.Font("fonts/FreeSans.ttf", (50,200,50,255))   #load ttf font and set the font colour to 'raspberry'
hudFont = pi3d.Font("fonts/FreeSans.ttf", (50,200,50,255))      #load ttf font and set the font colour to 'raspberry'

bar_dist = 5
ladder_step = 15
ladder_sides = 6
ladder_thickness = 0.006
ladder_zero_thickness = 0.1
ladder_text_xpos = 1.0


#build the bar shapes
upper_bars = pi3d.MergeShape(camera = fpv_camera)
lower_bars = pi3d.MergeShape(camera = fpv_camera)
bar_text = pi3d.MergeShape(camera = fpv_camera)

acylinder = pi3d.Cylinder(camera=fpv_camera, radius=ladder_thickness, height=1.5, sides=ladder_sides)

# x=0, y=0, z=0, 
center_bar = pi3d.Cylinder(camera=fpv_camera, radius=ladder_zero_thickness, height=1.5, sides=ladder_sides, sx=0, sy=0, sz=0)

bar_steps = int(180 / ladder_step)

for step in xrange(1, bar_steps):
    angle = step*ladder_step
    ypos = bar_dist * math.sin(math.radians(angle))
    zpos = bar_dist * math.cos(math.radians(angle))
    upper_bars.add(acylinder, x=0, y=ypos, z=zpos, rx=0, ry=-angle, rz=90)
    lower_bars.add(acylinder, x=0, y=-ypos, z=zpos, rx=0, ry=angle, rz=90)
    
    num_str = "%01d" % angle
    ladder_str = pi3d.String(camera=fpv_camera, font=ladderFont, string=num_str, sx=0.005, sy=0.005)
    bar_text.add(ladder_str, x=ladder_text_xpos, y=ypos, z=zpos, rx=-angle, ry=0, rz=0)
    bar_text.add(ladder_str, x=-ladder_text_xpos, y=ypos, z=zpos, rx=-angle, ry=0, rz=0)

    num_str = "%01d" % -angle
    ladder_str = pi3d.String(camera=fpv_camera, font=ladderFont, string=num_str, sx=0.005, sy=0.005)
    bar_text.add(ladder_str, x=ladder_text_xpos, y=-ypos, z=zpos, rx=angle, ry=0, rz=0)
    bar_text.add(ladder_str, x=-ladder_text_xpos, y=-ypos, z=zpos, rx=angle, ry=0, rz=0)
    

upper_bars.position(0.0, 0.0, 0)
upper_bars.set_draw_details(matsh, [], 1.0, 0.1)
upper_bars.set_material((0, 100, 0, 0.5))
upper_bars.set_alpha(0.5)

lower_bars.position(0.0, 0.0, 0)
lower_bars.set_draw_details(matsh, [], 1.0, 0.1)
lower_bars.set_material((100, 0, 0, 0.5))
lower_bars.set_alpha(0.1)

center_bar.position(0, 0, bar_dist*2)
center_bar.set_draw_details(matsh, [], 1.0, 0.1)
center_bar.set_material((128, 128, 128, 0.5))
center_bar.set_alpha(1)

bar_text.position(0.0, 0.0, 0)
bar_text.set_draw_details(flatsh, [], 1.0, 0.1)
#bar_text.set_material((100, 0, 0, 0.5))
bar_text.set_alpha(0.1)

light_shape = pi3d.Cylinder(camera=fpv_camera, radius=0.1, height=0.1, sides=36, rx=90, ry=0, rz=0)
light_shape.position(0, 0, 1.5)
light_shape.set_draw_details(matsh, [shapeimg], 1.0, 0.1)
light_shape.set_material((100, 0, 0, 0.5))
light_shape.set_alpha(0.1)

roll_string = pi3d.String(camera=hud_camera, font=hudFont, string="0000")
roll_string.translate(1.2, 0.5, 2)
roll_string.set_shader(flatsh)

pitch_string = pi3d.String(camera=hud_camera, font=hudFont, string="0000")
pitch_string.translate(1.2, 0.7, 2)
pitch_string.set_shader(flatsh)

mystring = pi3d.String(camera=hud_camera, font=hudFont, string="HUD TEST - 123456789")
mystring.translate(0.0, 0.0, 2)
mystring.set_shader(flatsh)

tick = 0
av_fps = 25
i_n=0
spf = 1.0 # seconds per frame, i.e. water image change
next_time = time.time() + spf
pitch = 0
roll = 0
pitch_rate = 30

# Fetch key presses.
mykeys = pi3d.Keyboard()
fr = 0


timestamp = time.clock()

# Display scene and rotate shape
while DISPLAY.loop_running():

  text_camera.reset(is_3d=False)
  hud_camera.reset(is_3d=True)
  fpv_camera.reset(is_3d=True)
  fpv_camera.rotate(pitch,0,0)

#  light_shape.draw()
  upper_bars.draw()
  lower_bars.draw()
  bar_text.draw()
  center_bar.draw()
  
#  upper_bars.rotateToZ(0) 
#  lower_bars.rotateToZ(0) 
#  light_shape.rotateToZ(0) 
#  bar_text.rotateToX(0)
  center_bar.rotateToX(0)

  pstr = "%01d" % pitch
  pitch_string = pi3d.String(camera=hud_camera, font=hudFont, string=pstr)
  pitch_string.translate(1.2, 0.7, 2)
  pitch_string.set_shader(flatsh)

  pitch_string.draw()
  mystring.draw()
  roll_string.draw()

  if time.time() > next_time:
    next_time = time.time() + spf
    av_fps = av_fps*0.9 + tick/spf*0.1 # exp smooth moving average
    print(av_fps, " FPS, ", pitch, " pitch")
    tick = 0
    
  pitch += pitch_rate / av_fps

  tick += 1
  
  roll += 1
  
  # Temporary
  if(pitch > 180):
      pitch -= 180
  elif(pitch < -180):
      pitch += 180

  #pi3d.screenshot("/media/E856-DA25/New/fr%03d.jpg" % fr)
  #fr += 1

  k = mykeys.read()
  if k==112:
    pi3d.screenshot("water1.jpg")
  elif k==27:
    mykeys.close()
    DISPLAY.destroy()
    break

quit()
