'''
Created on 18 Jul 2014

@author: matt
'''
import pi3d
import array
import numeric

class LayerItems(object):
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)

    def gen_items(self, phase=None):
        statuschange = False
        for item in self.items:
            if(phase == None):
                item.gen_item()
                if(item.changed):
                    statuschange = True
            elif(item.phase == phase):
                item.gen_item()
                if(item.changed):
                    statuschange = True                
        return statuschange
       
    def draw_items(self):
#        """ Draw all items in the list.  Used when any content of the layer has changed"""
        for item in self.items:
            item.draw_item()

        
class LayerItem(object):
#    """ A 2D item on an OffScreenTexture layer with information about how, where and when to draw it.
#        Is overridden by specific item type classes"""
    
    def __init__(self, camera, shader, xpos=0, ypos=0, phase=None):
#        """ *phase* controls when to update/generate a new image on the layer. Can be used to balance processor loading""""

        from pi3d.Display import Display
    
        self.x = xpos * Display.INSTANCE.height     #position offset in screen pixels
        self.y = ypos * Display.INSTANCE.width

        self.camera = camera
        self.shader = shader
        self.phase = phase


class LayerText(LayerItem):
    def __init__(self, font, text, camera, shader=None, xpos=0, ypos=0, size=1.0, phase=None):

        super(LayerText, self).__init__(camera, shader, xpos, ypos, phase)
                        
        self.font = font
        self.text = text
        self.size = size
        
        self.last_text = ""     #remember last generated text to prevent re-generation of unchanged text        
        self.changed = False    #flag to show if text has been generated but not redrawn yet
        
        
    def _gen_text(self):
        if self.text != self.last_text:
            self.text = pi3d.String(string=self.text, camera=self.camera, font=self.font, is_3d=False, x=self.x, y=self.y, size=self.size, justify='R')
            self.text.position(self.x, self.y, 5)
            self.text.set_material((0,0,0,0))
            self.text.set_shader(self.shader)
            self.last_text = self.text
            self.changed = True
        
    def draw_item(self):
        if self.text != None:
            self.text.draw()
            self.changed = False

    def gen_item(self):
        self._gen_text()


class LayerVarText(LayerText):
    
    def __init__(self, font, text, camera, dataobj=None, attr=None, shader=None, xpos=0, ypos=0, size=1.0, phase=None):
        self.attr = attr
        self.dataobj = dataobj
        self.textformat = text
        
        super(LayerVarText, self).__init__(font, text, camera, shader, xpos, ypos, size, phase)
        
        
    def gen_item(self):
        if(self.attr != None) and (self.dataobj != None):
            value = getattr(self.dataobj, self.attr, None)
        else:
            value = None
        
        if(value != None):
            self.text = self.textformat.format(value)
        else:
            self.text = " "
        self._gen_text()
        
        
class LayerNumeric(LayerVarText):
    def __init__(self, font, text, camera, dataobj=None, attr=None, shader=None, xpos=0, ypos=0, size=1.0, phase=None, digits=3, spacing=15):
        super(LayerNumeric, self).__init__(self, font, text, camera, dataobj, attr, shader, xpos, ypos, size, phase)

        self.digits = digits
        self.spacing = spacing

        self.number = numeric.FastNumber(camera=self.camera, font=self.font, shader=self.shader, digits=self.digits, x=xpos, y=ypos, size=self.size, spacing=self.spacing)

    def _gen_text(self):
        self.number.set_number(self.text)
        self.number.generate()
        
    def draw_item(self):
        self.number.draw()
        