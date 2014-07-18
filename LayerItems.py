'''
Created on 18 Jul 2014

@author: matt
'''
import pi3d
import array

class layer_items(object):
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)

    def gen_items(self):
        statuschange = False
        for item in items.texts:
            item.get_text()
            if(item.changed):
                statuschange = True
        return statuschange
    
    def draw_items(self):
        for item in self.items:
            item.draw_text()
        
class layer_item(object):
    def __init__(self, camera, shader=None, xpos=0, ypos=0):
        from pi3d.Display import Display
    
        self.x = xpos * Display.INSTANCE.height     #position offset in screen pixels
        self.y = ypos * Display.INSTANCE.width

        self.camera = camera
        self.shader = shader
                

class layer_text(layer_item):
    def __init__(self, font, text, camera, shader=None, xpos=0, ypos=0, size=1.0):

        super(layer_text, self).__init__(camera, shader, xpos, ypos)
                        
        self.font = font
        self.value = None
        self.text = text
        self.size = size
        
        self.last_text = ""     #remember last generated text to prevent re-generation of unchanged text        
        self.changed = False    #flag to show if text has been generated but not redrawn yet
        
#        self.gen_text()

    def _gen_text(self):
        if self.text != self.last_text:
            self.text = pi3d.String(string=self.text, camera=self.camera, font=self.font, is_3d=False, x=self.x, y=self.y, size=self.size, justify='R')
            self.text.position(self.x, self.y, 5)
            self.text.set_material((0,0,0,0))
            self.text.set_shader(self.shader)
            self.last_text = self.text
            self.changed = True
        
    def gen_text(self):
        self._gen_text()
        
    def draw_text(self):
        if self.text != None:
            self.text.draw()
            self.changed = False
            
    def draw_item(self):
        self.draw_text()

    def gen_item(self):
        self.gen_text()


class layer_var_text(layer_text):
    def __init__(self, font, text, camera, dataobj=None, attr=None, shader=None, xpos=0, ypos=0, size=1.0):
        self.attr = attr
        self.dataobj = dataobj
        self.textformat = text
        
        super(layer_var_text, self).__init__(font, text, camera, shader, xpos, ypos, size)
        
        
    def gen_text(self):
        if(self.attr != None) and (self.dataobj != None):
            value = getattr(self.dataobj, self.attr, None)
        else:
            value = None
        
        if(value != None):
            self.text = self.textformat.format(value)
        else:
            self.text = " "
        self._gen_text()
        # = string.Formatter.format(self, format_string)
