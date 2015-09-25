#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Sprites rendered using a diy points class and special shader uv_spriterot.


The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
from FastText import FastText
print("""
ESC to quit
####################################################
Any key to increase temperature but..
####################################################
i key toggles interaction between bugs
s key toggles spinning or align with velocity vector
""")

from itertools import chain
import numpy as np
import random

import demo
import pi3d

from PointFont  import PointFont
import FastText

import os
import math
import time

class junk(object):
    def __init__(self):
        self.valA = 0.0
        self.fps = 0.0

        self.strA = "Moving string"
        

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

CAMERA = pi3d.Camera(is_3d=False)

font_colour = (255,255,255,255)

the_junk = junk()
text_pos = HWIDTH

working_directory = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'FreeSans.ttf'))
#        self.warningFont = pi3d.Font(font_path, (255,0,0,255))
pointFont = PointFont(font_path, font_colour, codepoints=chain(range(32,128)) )
text = FastText.FastText(pointFont, CAMERA)


moving_text = FastText.TextBlock(0, 0, 0.1, 0.0, 25, the_junk, "strA", text_format="{:s}", size=0.6, spacing="F", space=0.08, alpha=1.0)
text.add_text_block(moving_text)

newtxt = FastText.TextBlock(-100, -50, 0.1, 0.0, 14, None, None, text_format="Static string", size=0.9, spacing="F", space=0.05, alpha=1.0)
text.add_text_block(newtxt)

newtxt = FastText.TextBlock(-150, 75, 0.1, 0.0, 18, the_junk, "valA", text_format="number: {:4.3f}", size=0.5, spacing="F", space=0.05, alpha=1.0)
text.add_text_block(newtxt)

newtxt = FastText.TextBlock(-250, -200, 0.1, 0.0, 10, the_junk, "fps", text_format="fps: {:2.1f}", size=0.75, spacing="C", space=0.6, alpha=1.0)
text.add_text_block(newtxt)

textSize = 0.1
sizingText = FastText.TextBlock(-100, 150, 0.1, 0.0, 15, None, None, text_format="Resizing text", size=0.5, spacing="F", space=0.05, alpha=1.0)
text.add_text_block(sizingText)

frame_count = 0
end_time = time.time() + 1.0

while DISPLAY.loop_running():
    text_pos -= 3
    if text_pos < -HWIDTH:
        text_pos = HWIDTH
    moving_text.x = text_pos
    moving_text.last_value = None        # a hack to trigger a redraw in a new position
    the_junk.valA += 0.01
    the_junk.valA *= 1.0123
    if the_junk.valA > 1000.0:
        the_junk.valA *= 0.01
        
    textSize += 0.01
    if textSize > 0.99:
        textSize = 0.1
        
    sizingText.size = textSize
    sizingText.last_value = sizingText  # a hack to trigger a redraw in a new size
    
    now = time.time()
    frame_count += 1
    if now > end_time:
        end_time = now + 1.0
        the_junk.fps = frame_count
        frame_count = 0
    
#    the_junk.valA = random.uniform(-1000.0, 1000.0)
    text.regen()
    text.draw()
    
#    if frame_num % 10 == 0:
#      uv[ix[0],:] = np.random.randint(0, 7, (ix[0].shape[0], 2)) * 0.125 + 0.0125


    k = KEYBOARD.read()
    if k > -1:
        if k == 27:
            KEYBOARD.close()
            DISPLAY.stop()
            break


