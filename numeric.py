'''
Created on 4 Jul 2014

@author: matt
'''
import pi3d


class FastNumber(object):

    def __init__(self,  font, camera=None, shader=None, x=0, y=0, size=1.0, digits=1, default=0):
        self.digits = []
#       for()



class FastDigit(object):

    def __init__(self, font, camera=None, shader=None, x=0, y=0, size=1.0, default="0"):
        self.shader = shader
        self.camera = camera
        self.size = size
        self.font = font
        self.x = x
        self.y = y
        self.digits = []
                
        self.generate_digits()
        self.set_digit(default)
        
    def generate_digits(self):
        self.digits = []
        
        for i in xrange(0,9):
            tempstr = "%0d" % i
            digit = pi3d.String(camera=self.camera, font=self.font, string=tempstr, is_3d=False, z=1, size=self.size)
            digit.translate(self.x, self.y, 1)
            digit.set_shader(self.shader)

            self.digits.append((tempstr,digit))
            
            self.digit = (" ", None)
            
    def draw(self):
        if(self.digit[1] is not None):
            self.digit[1].draw()
               
    def set_digit(self,numchar):
        if(numchar != self.digit[0]):
            for digit in self.digits:
                if(digit[0] == numchar):
                    self.digit = digit
                    continue