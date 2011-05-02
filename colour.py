def int_to_float(value):
    return (value + 0.5)/256.0

def float_to_int(value):
    i = int(value * 256)
    return max(min(i, 255), 0)

class Colour:
    def __init__(self, *spec):
        if len(spec) == 1:
            hex = spec[0]
            self.red = int(hex[:2], 16)/255.0
            self.green = int(hex[2:4], 16)/255.0
            self.blue = int(hex[4:], 16)/255.0
        else:
            if isinstance(spec[0], int):
                self.red, self.green, self.blue = map(int_to_float, spec)
            elif isinstance(spec[0], float):
                self.red, self.green, self.blue = spec
            else:
                raise ValueError(spec)

    def __repr__(self):
        return 'Colour(%.2f, %.2f, %.2f)' % (self.red, self.green, self.blue)

    def __add__(self, other):
        return self.blend(other)

    def __mul__(self, factor):
        r = min(self.red*factor, 1.0)
        g = min(self.green*factor, 1.0)
        b = min(self.blue*factor, 1.0)
        return Colour(r, g, b)

    def __hex__(self):
        return '%02x%02x%02x' % (
            float_to_int(self.red),
            float_to_int(self.green),
            float_to_int(self.blue))

    def rgb(self):
        return (self.red, self.green, self.blue)

    def blend(self, other, t=0.5):
        return Colour(self.red*(1.0 - t) + other.red*t,
                      self.green*(1.0 - t) + other.green*t,
                      self.blue*(1.0 - t) + other.blue*t)

black = Colour(0.0, 0.0, 0.0)
white = Colour(1.0, 1.0, 1.0)

def grey(level):
    level = float(level)
    return Colour(level, level, level)

grey25 = grey(0.25)
grey50 = grey(0.5)
grey75 = grey(0.75)

red = Colour(1.0, 0.0, 0.0)
yellow = Colour(1.0, 1.0, 0.0)
green = Colour(0.0, 1.0, 0.0)
cyan = Colour(0.0, 1.0, 1.0)
blue = Colour(0.0, 0.0, 1.0)
magenta = Colour(0.0, 1.0, 1.0)
