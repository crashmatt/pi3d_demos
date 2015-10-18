#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Strings rendered using 
PointFontColoured - For generating a font drawn with gl_point and recoloured using
 shader uv_fontmultcoloured

PointText - Manages the collection of data for all of the strings to be drawn.
  Enables drawing all strings in one pass.
  
TextBlock - A string which has its content, position, size, rotation, colour, alpha,
 character positioning, justification etc.. defined by this.

"""
#from FastText import FastText

print("""
ESC to quit
""")

from itertools import chain
import numpy as np
import random

import demo
import pi3d

from PointFont  import PointFont
import PointText
from TextBlock import TextBlock, TextBlockColourGradient

import os
import math
import time


# A class to contain some data to display
class junk(object):
    def __init__(self):
        self.valA = 0.0
        self.fps = 0.0
        self.strA = "A moving string"
        self.angle = 0.0
        

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

HHWIDTH = HWIDTH/2

CAMERA = pi3d.Camera(is_3d=False)

font_colour = (255,255,255,255)

the_junk = junk()
text_pos = HHWIDTH
text_delta_pos = -3

working_directory = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'FreeSans.ttf'))

# Create PointFont and the text manager to use it
pointFont = PointFont(font_path, font_colour, codepoints=chain(range(32,128)) )
text = PointText.PointText(pointFont, CAMERA, max_chars=200)

#Basic static text
newtxt = TextBlock(-100, -50, 0.1, 0.0, 14, None, None, text_format="Static string", size=0.9, spacing="F", space=0.05, colour=(0.0, 1.0, 0.0, 1.0) )
text.add_text_block(newtxt)

#The next three strings are formated with data from an object.  When the object data changes and the
# text block is regenerated, the string is changed to the new data values.
moving_text = TextBlock(0, 0, 0.1, 0.0, 25, the_junk, "strA", text_format="{:s}", size=0.6, spacing="F", space=0.08, colour=(1.0, 0.0, 0.0, 1.0) )
text.add_text_block(moving_text)

newtxt = TextBlock(-150, 75, 0.1, 0.0, 18, the_junk, "valA", text_format="number: {:4.3f}", size=0.5, spacing="F", space=0.05, colour=(0.0, 0.0, 1.0, 1.0) )
text.add_text_block(newtxt)

newtxt = TextBlock(200, -200, 0.1, 0.0, 10, the_junk, "fps", text_format="fps:{:2.1f}", size=0.75, spacing="C", space=0.6, colour=(0.0, 1.0, 1.0, 1.0) )
text.add_text_block(newtxt)


textSize = 0.1
textGrowth=0.01
sizingText = TextBlock(-100, 150, 0.1, 0.0, 15, None, None, text_format="Resizing text", size=textSize, spacing="F", space=0.05, colour=(1.0, 1.0, 0.0, 1.0) )
text.add_text_block(sizingText)

# String rotation and spacing
textRotation = 0.0
rotatingText = TextBlock(-200, -150, 0.1, textRotation, 15, None, None, text_format="Rotating text", size=0.7, spacing="C", space=0.6, colour=(1.0, 1.0, 1.0, 0.5), justify=0.5 )
text.add_text_block(rotatingText)

rotatingChars = TextBlock(-300, -100, 0.1, 0.0, 15, None, None, text_format="Rotating chars", size=0.6, spacing="C", space=0.6, colour=(0.99, 0.5, 0.5, 1.0) )
text.add_text_block(rotatingChars)

spacingText = TextBlock(-350, -300, 0.1, 0.0, 10, None, None, text_format="Spacing", size=0.7, spacing="C", space=0.1, colour=(0.5, 1.0, 0.5, 1.0) )
text.add_text_block(spacingText)

#String colour and alpha
textAlpha = 0.1
alphaGrowth = 0.01
alphaText = TextBlock(-250, -300, 0.0, 90.0, 15, None, None, text_format="Alpha change", size=0.99, spacing="C", space=0.6, colour=(0.99, 0.99, 0.99, textAlpha) )
text.add_text_block(alphaText)

colourText = TextBlock(-300, -200, 1.0, 0.0, 15, None, None, text_format="Colour change", size=0.8, spacing="C", space=0.6, colour=(0.99, 0.5, 0.5, 1.0) )
text.add_text_block(colourText)

colourGradient = TextBlockColourGradient((1.0,0.0,0.0,1.0),(0.0,1.0,0.0,1.0))
gradientText = TextBlock(50, -250, 0.1, 0.0, 16, None, None, text_format="Colour Gradient", size=0.7, spacing="C", space=0.6, colour=colourGradient )
text.add_text_block(gradientText)


alphaGradient = TextBlockColourGradient((1.0,1.0,1.0,1.0),(1.0,1.0,1.0,0.25))
alphaGradientText = TextBlock(50, -100, 0.1, 0.0, 16, None, None, text_format="Alpha Gradient", size=0.7, spacing="C", space=0.6, colour=alphaGradient )
text.add_text_block(alphaGradientText)


everythingColour = TextBlockColourGradient((1-textAlpha,0.0,textAlpha,1.0),(textAlpha,0.0,1-textAlpha,1.0))
everythingText = TextBlock(100, 200, 0.1, textRotation, 15, the_junk, "angle", text_format="Angle: {:3.0f}", size=0.7, spacing="F", space=0.05, colour=everythingColour, justify=0.5 )
#everythingText = TextBlock(100, 200, 0.1, textRotation, 15, the_junk, "angle", text_format="Angle: {:2.3f}", size=0.7, spacing="C", space=0.6, colour=(1.0, 1.0, 1.0, 0.5), justify=0.5 )
text.add_text_block(everythingText)


frame_count = 0
end_time = time.time() + 1.0

while DISPLAY.loop_running():
    text_pos += text_delta_pos
    if text_pos < -HHWIDTH:
        text_delta_pos = 3
    elif text_pos > HHWIDTH:
        text_delta_pos = -3
    moving_text.set_position(x=text_pos)
    
#    moving_text.last_value = None        # a hack to trigger a redraw in a new position
    the_junk.valA += 0.01
    the_junk.valA *= 1.0123
    if the_junk.valA > 1000.0:
        the_junk.valA *= 0.01
        
    textSize += textGrowth
    if textSize > 1.0:
        textSize = 1.0
        textGrowth = -0.05
    elif textSize < 0.1:
        textSize = 0.1
        textGrowth = +0.01
        
    sizingText.set_text(size=textSize)
    
    textRotation += 1.0
    if textRotation >= 180.0:
        textRotation -= 360.0
        
    the_junk.angle = textRotation
        
    rotatingText.set_position(rot=textRotation)
    rotatingChars.set_text(char_rot=textRotation)
    
    textAlpha += alphaGrowth
    if textAlpha >= 1.0:
        textAlpha = 1.0
        alphaGrowth = -0.01
    elif textAlpha < 0.0:
        textAlpha = 0.0
        alphaGrowth = 0.02
    alphaText.colouring.set_colour(alpha=textAlpha)
    
    colour_angle = math.radians(textRotation)
    red = math.cos(colour_angle)
    blue = math.cos(colour_angle + (math.pi * 0.666) )    
    green = math.cos(colour_angle + (math.pi * 1.333) )    
    colour = [red, green , blue, 1.0]
    colourText.colouring.set_colour(colour)
    
    spacingText.set_text(space=textSize)
    
#    everythingColour.set_colour( (0.1, 0.0 , 1.0, 1.0), (1.0 , 0.0, 0.1, 1.0) )
    everythingText.set_text(space=textSize*0.25, set_pos=False, set_colour=False)
    everythingText.set_position(x=text_pos-50, y=150+(text_pos*0.2), rot=textRotation)
    everythingColour.set_colour( (1.0, textAlpha , 0.0, 1.0), (0.0, textAlpha, 1.0, 1.0) )
    
    now = time.time()
    frame_count += 1
    if now > end_time:
        end_time = now + 1.0
        the_junk.fps = frame_count
        frame_count = 0
        if the_junk.strA == "A moving string":
            the_junk.strA = "String moving"
        else: 
            the_junk.strA = "A moving string"
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


