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
DISPLAY = pi3d.Display.create(x=0, y=0, w=640, h=480, frames_per_second=25.0)
DISPLAY.set_background(0.0, 0.0, 0.0, 0.5)      # r,g,b,alpha

#setup textures, light position and initial model position
pi3d.Light((5, -5, 8))
#create shaders
#shader = pi3d.Shader("uv_reflect")
matsh = pi3d.Shader("mat_flat")  #For fixed color
flatsh = pi3d.Shader("uv_flat")

#Create textures
shapeimg = pi3d.Texture("textures/straw1.jpg")

myshape = pi3d.MergeShape()
#camera, light, radius, height,sides,name,scalex,scaley,scalez,rotx,roty,rotz

acylinder = pi3d.Cylinder(radius=0.006, height=2.5, sides=4)
bar_dist = 5
for step in xrange(-18, 18):
    ypos = bar_dist * math.sin(math.radians(step*10))
    zpos = bar_dist * math.cos(math.radians(step*10))
    myshape.add(acylinder, x=0, y=ypos, z=zpos, rx=0, ry=0, rz=90)

myshape.position(0.0, 0.0, 0)
myshape.set_draw_details(matsh, [], 1.0, 0.1)
myshape.set_material((0, 100, 0, 0.5))

#mywater = pi3d.LodSprite(w=250.0, h=250.0, n=6)
#mywater.set_draw_details(matsh, [waterbump[0], shapeshine], 14.0, 0.6)
#mywater.set_material((0.1, 0.25, 0.3))
#mywater.set_fog((0.4, 0.6, 0.8, 0.0),100)
#mywater.rotateToX(85.0)
#mywater.position(10.0, -2.0, 0.0)

arialFont = pi3d.Font("fonts/FreeSans.ttf", (50,200,50,255))   #load ttf font and set the font colour to 'raspberry'
mystring = pi3d.String(font=arialFont, string="Now the Raspberry Pi really does rock")
mystring.translate(0.0, 0.0, 2)
mystring.set_shader(flatsh)

tick = 0
av_fps = 0
i_n=0
spf = 0.1 # seconds per frame, i.e. water image change
next_time = time.time() + spf
pitch = 0
pitch_rate = 10

# Fetch key presses.
mykeys = pi3d.Keyboard()
fr = 0

CAMERA = pi3d.Camera.instance()
# Display scene and rotate shape
while DISPLAY.loop_running():

  myshape.draw()
#  myshape.rotateIncX(0.5)

  CAMERA.reset()
  CAMERA.rotate(pitch,0,0)

  mystring.draw()

  if time.time() > next_time:
    next_time = time.time() + spf
    pitch += pitch_rate * spf
    av_fps = av_fps*0.9 + tick/spf*0.1 # exp smooth moving average
    print(av_fps,"FPS")
    tick = 0

  tick += 1

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
