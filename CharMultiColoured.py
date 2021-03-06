#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Characters rendered using a diy points class and special shader uv_fontmulti.

This demo builds on the SpriteMulti demo (based on SpriteBalls), thanks
to Paddy for the idea and many others for helping Paddy.

Uses uv_fontmult shader as follows:

  vertices[0]   x position of centre of point relative to centre of screen in pixels
  vertices[1]   y position
  vertices[2]   z depth but fract(z) is used as a multiplier for point size
  normals[0]    rotation in radians
  normals[1]    alpha
  normals[2]    the size of the sprite square to use for texture sampling
                in this case each sprite has a patch 0.0625x0.0625 as there
                are 16x16 on the glyph map. However normals[2] is set to 0.057 to
                leave a margin around each font glyph.
  tex_coords[0] distance of left side of sprite square from left side of
                texture in uv scale 0.0 to 1.0
  tex_coords[1] distance of top of sprite square from top of texture

The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
print("""
ESC to quit
####################################################
Any key to increase temperature but..
####################################################
i key toggles interaction between bugs
s key toggles spinning or align with velocity vector
""")
import numpy as np
import random

import demo
import pi3d

import PointFontColoured

import os
import math


MAX_BUGS = 100
MIN_BUG_SIZE = 32.0 # z value is used to determine point size
MAX_BUG_SIZE = 128.0
MAX_BUG_VELOCITY = 3.0

min_size = float(MIN_BUG_SIZE) / MAX_BUG_SIZE
max_size = 1.0

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30, samples=4)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

CAMERA = pi3d.Camera(is_3d=False)
shader = pi3d.Shader("shaders/uv_fontmultcoloured")

working_directory = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'FreeSansBold.ttf'))
font = PointFontColoured.PointFontColoured(font_path, codepoints=range(32,255))   #usr/share/fonts/truetype/freefont/

img = font
#img = pi3d.Texture("textures/atlas01.png")

loc = np.zeros((MAX_BUGS, 3))
loc[:,0] = np.random.uniform(-HWIDTH, HWIDTH, MAX_BUGS)
loc[:,1] = np.random.uniform(-HHEIGHT, HHEIGHT, MAX_BUGS)
loc[:,2] = 0.99
#loc[:,2] = np.random.normal((min_size + max_size) / 2.0,
#                            (max_size - min_size) / 5.0,
#                            MAX_BUGS) + np.random.randint(1, 8, MAX_BUGS)
vel = np.random.uniform(-MAX_BUG_VELOCITY, MAX_BUG_VELOCITY, (MAX_BUGS, 2))

dia = np.remainder(loc[:,2], 1.0) * MAX_BUG_SIZE
mass = dia * dia
radii = np.add.outer(dia, dia) / 7.0 # should be / 2.0 this will make bugs 'touch' when nearer

rot = np.zeros((MAX_BUGS, 3))   # :,0 for rotation
rot[:,1] = 0.5 + 128.0         # :,1 for red and alpha
rot[:,2] = 0.5 + 128.0          # :,1 for green and blue

uv = np.zeros((MAX_BUGS, 2)) # u picnum.u v
uv[:,:] = 0.0125 # all start off same. uv is top left corner of square

bugs = pi3d.Points(camera=CAMERA, vertices=loc, normals=rot, tex_coords=uv,
                   point_size=MAX_BUG_SIZE)
bugs.set_draw_details(shader, [img])

temperature = 0.9
interact = True
spin = False
frame_num = 0

while DISPLAY.loop_running():
  bugs.draw()
  frame_num += 1
  ##### bounce off walls
  ix = np.where(loc[:,0] < -HWIDTH) # off left side
  vel[ix,0] = np.abs(vel[ix,0]) * temperature # x component +ve
  ix = np.where(loc[:,0] > HWIDTH) # off right
  vel[ix,0] = np.abs(vel[ix,0]) * -temperature # vx -ve
  ix = np.where(loc[:,1] < -HHEIGHT)
  vel[ix,1] = np.abs(vel[ix,1]) * temperature
  ix = np.where(loc[:,1] > HHEIGHT)
  vel[ix,1] = np.abs(vel[ix,1]) * -temperature
  vel[:,1] -= 0.01 # slight downward drift
  loc[:,0:2] += vel[:,:] # adjust x,y positions by velocities
  ##### rotate
  if spin:
#    rot[:,0] += rot[:,1] * 0.4
    rot[:,0] = 0
  else: # tween towards direction of travel
    rot[:,0] +=  ((np.arctan2(vel[:,1], vel[:,0]) + 1.571 - rot[:,0])
                        % 6.283 - 3.142) * 0.2
  ##### re_init
  bugs.buf[0].re_init(pts=loc, normals=rot, texcoords=uv) # reform opengles array_buffer
  ##### trend towards net cooling
  temperature = temperature * 0.99 + 0.009 # exp smooth towards 0.9


  ##### bounce off each other. Work increases as square of N
  if interact:
    d1 = np.subtract.outer(loc[:,0], loc[:,0]) # array of all the x diffs
    d2 = np.subtract.outer(loc[:,1], loc[:,1]) # array of all the y diffs
    ix = np.where((np.hypot(d1, d2) - radii) < 0.0) # index of all overlaps
    non_dup = np.where(ix[0] < ix[1]) # remove double count and 'self' overlaps
    ix = (ix[0][non_dup], ix[1][non_dup]) # remake slimmed down index
    dx = d1[ix[0], ix[1]] # separation x component
    dy = d2[ix[0], ix[1]] # sep y
    D = dx / dy # component ratio
    R = mass[ix[1]] / mass[ix[0]] # mass ratio
    # minor fudge factor to stop them sticking to each other if dx or dy == 0
    delta2y = 2 * (D * vel[ix[0],0] + vel[ix[0],1] -
                   D * vel[ix[1],0] - vel[ix[1],1]) / (
                  (1.0 + D * D) * (R + 1)) * temperature - dy * 0.01
    delta2x = D * delta2y - dx * 0.01 # x component from direction
    delta1y = -1.0 * R * delta2y # other ball using mass ratio
    delta1x = -1.0 * R * D * delta2y
    vel[ix[0],0] += delta1x # update velocities
    vel[ix[0],1] += delta1y
    vel[ix[1],0] += delta2x
    vel[ix[1],1] += delta2y
    
    idx = frame_num % MAX_BUGS
    uv[idx,:] = np.random.randint(0, 15, (2)) * 0.0625
    value = np.random.uniform(0.75, 0.99)
    value += np.floor(np.random.uniform(0.25, 1.0) * 255)
    rot[idx,1] = value
    value = np.random.uniform(0.25, 0.99)
    value += np.floor(np.random.uniform(0.25, 1.0) * 255)
    rot[idx,2] = value
    loc[idx,2] = np.random.uniform(0.2, 0.99)


  k = KEYBOARD.read()
  if k > -1:
    temperature *= 1.05
    vel *= np.random.uniform(1.01, 1.03, vel.shape)
    if k == ord('i'):
      interact = not interact
    if k == ord('s'):
      spin = not spin
    if k == 27:
      KEYBOARD.close()
      DISPLAY.stop()
      break


