'''
Created on 31 Jan 2022

@author: paul
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`
  A CMYK colour can be denormalised by adding back black, providing the same colour as
  just the CMY components.

  Imagine a CMY colour representation in a 3d space, with each of C,M,Y on a range
  between 0 and 100 being the axis values.  Here, White is CMY(0,0,0) and Black is 
  CMY(100,100,100)

  Any CMY colour C0 may be mixed if it falls on a line between two existing palette 
  colours C1, & C2.  The mixing ratio would be determined by the lenth of the 
  line segments  C1 -> C0 -> C2 
  
  If it does not fall along a line C1->C2, C0 cannot be mixed directly.  However,
  consider a 3rd palette colour C3, having C0 within the triangle C1->C2->C3:
  
    If the direction vector d0 from C3->C0 passes through C0 to intersect with
    the direction vector d1 from C1->C2, then if we use C1 and C2 to mix colour
    P at the intersection point, then C0 will fall on the line C3->P, and we
    can then mix C0 using P and C3.
    
    Unfortunately, the nature of 3d space makes actual intersection improbable,
    but we can still find the closest match by minimising the distance.
  
'''
import grok
import math
from zope import schema
from zope.interface import Interface


class RGB:
    """  A simple RGB encapsulation
    """
    red = 0
    green = 0
    blue = 0

    def __init__(self, r=0, g=0, b=0):
        self.red = int(round(r))
        self.green = int(round(g))
        self.blue = int(round(b))

    def hex(self):
        return "#{:02X}{:02X}{:02X}".format(self.red, self.green, self.blue)


class IVECTOR3(Interface):
    x = schema.Float(title=u"X", description=u"The X axis component")
    y = schema.Float(title=u"Y", description=u"The Y axis component")
    z = schema.Float(title=u"Z", description=u"The Z axis component")


class ICMYK(Interface):
    name = schema.TextLine(title=u"Name")
    cyan = schema.Int(title=u"Cyan", description=u"The Cyan component of a CMYK colour", min=0, max=100)
    magenta = schema.Int(title=u"Magenta", description=u"The Magenta component of a CMYK colour", min=0, max=100)
    yellow = schema.Int(title=u"Yellow", description=u"The Yellow component of a CMYK colour", min=0, max=100)
    black = schema.Int(title=u"Black", description=u"The Black component of a CMYK colour", min=0, max=100)
    to_mix = schema.TextLine(title=u"To Mix", description=u'Instructions to mix this colour')
    density = schema.Float(title=u"Density", description=u"The colour density to white density ratio", min=0.0, default=1.0)


class VECTOR3(grok.Model):
    x = 0
    y = 0
    z = 0
    ofs = None
    length = 0.0
    name = ""
    
    def __init__(self, x=0, y=0, z=0, distance=0, name="v"):
        self.x = x
        self.y = y
        self.z = z
        self.length = distance
        self.name = name

    def __repr__(self):
        return "{}({:.2f},{:.2f},{:.2f})".format(self.name, self.x, self.y, self.z)

    def as_cmyk(self, name="", to_mix="", density=1.0):
        if not name: name = self.name
        return CMYK(self.x*100.0, self.y*100.0, self.z*100.0, name=name, to_mix=to_mix, density=density)

    def as_list(self):
        return [self.x, self.y, self.z]

    def distance(self, to):
        '''  Calculate the distance between self and 'to'
        '''
        p1 = self.as_list()
        p2 = to.as_list()
        dx = [x - y for x,y in zip(p1,p2)]
        ssq = sum([x*x for x in dx])
        dist = math.sqrt(ssq) if ssq else 0
#        print("Distance between %s and %s is %.2f" % (str(c1), str(c2), dist))
        return dist
    
    def direction(self, p1):
        '''  Direction vector from self to p1
        '''        
        dist = p1.distance(self)
        vector = p1.subtract(self)
        if dist:
            return vector.divide(dist)
        return vector
        
    def dot(self, p1):
        ''' Calculate the dot product between self and p1
        '''
        v1 = self.as_list()
        v2 = p1.as_list()
        return sum([a*b for a,b in zip(v1,v2)])

    def add(self, p1):
        return VECTOR3(self.x+p1.x, self.y+p1.y, self.z+p1.z, self.length+p1.length)
    
    def subtract(self, p1):
        dist = self.distance(p1)
        return VECTOR3(self.x-p1.x, self.y-p1.y, self.z-p1.z, dist)

    def cross(self, vector3):
        ''' Here, we assume self and cmyk to be vectors.
            The cross product between two vectors in 3d space is the vector
            which is simultaneously perpendicular to both vectors.            
        '''
        a = self.as_list()
        b = vector3.as_list()
        return VECTOR3(*[a[1]*b[2]-a[2]*b[1], 
                         a[2]*b[0]-a[0]*b[2], 
                         a[0]*b[1]-a[1]*b[0]])

    def multiply(self, ratio):
        """ Multiply self by a ratio
        """
        return VECTOR3(self.x * ratio, self.y * ratio, self.z * ratio, self.length * ratio)
    
    def divide(self, ratio):
        """ Divide self by a ratio
        """
        if ratio:
            return self.multiply(1.0/ratio)
        else:
            raise ValueError("VECTOR3::divide(ratio) attempted division by zero")    


class MixInstruction():
    parts = None
    args = None
    
    def __init__(self, name1, name2, t):
        self.args = [name1, name2, t]
        self.parts = []
        parts_a = 1 - t
        parts_b = t
        if parts_a == 1:
            self.parts.append([1, name1])
        elif parts_b == 1:
            self.parts.append([1, name2])
        else:
            if parts_a > parts_b:
                parts_a /= parts_b
                parts_b = 1
                while parts_a + 1 < 3:
                    parts_a *= 2
                    parts_b *= 2
            else:
                parts_b /= parts_a
                parts_a = 1
                while parts_b + 1 < 3:
                    parts_a *= 2
                    parts_b *= 2
            self.parts.append([parts_a, name1])
            self.parts.append([parts_b, name2])

    def __repr__(self):
        instructions = ""
        for part, name in self.parts:
            if instructions: instructions += " to "
            instructions += "{:.2f}".format(part) + " parts of (" + name + ")"
        return instructions
    
    def as_list(self):
        return self.args
    

class Projection():
    ''' Defines a projection from point c0 to a point P perpendicular to the line between
        c1 and c2.
    '''
    delta = 100
    
    v0 = VECTOR3()
    v1 = VECTOR3()
    v2 = VECTOR3()
    
    P = VECTOR3()
    D = 0.5
    density = 1.0
    

    def __init__(self, c0, c1, c2):
        ''' Vector c1 and c2 represent two palette colours, and we want to
            find the closest point to c0 on the line between c1 and c2.
            We also want to ensure that this point is not outside the bounds
            of the line.
        '''
        vectors = c0.as_vector3(), c1.as_vector3(), c2.as_vector3()
        v0, v1, v2 = self.v0, self.v1, self.v2 = vectors
        
        d = v1.direction(v2)
        v = v0.subtract(v1)
        # print("direction d=%s" % str(d))
        # print("direction v=%s" % str(v))
        t = v.dot(d)
        self.P = v1.add(d.multiply(t))
        q = v1.distance(v2)
        self.m = self.P.distance(v1) / q if q else 0
        
        self.density = c1.density * (1 - self.m) + c2.density * self.m
        self.D = self.m / self.density if self.density else self.m
        
        self.delta = v0.distance(self.P)
        print("Point=%s;  t=%.4f; delta=%.4f" % (str(self.P), self.m, self.delta))

    def __repr__(self):
        return ("projection({} -> {} -> {})\n   closest={}, t={:.2f}, delta={:.2f}"
                .format(self.v1, self.v0, self.v2, self.P, self.m, self.delta))
        
    def __lt__(self, other):
        if self.in_range():
            return self.delta < other.delta if other.in_range() else True
        return False
    
    def in_range(self):
        return self.m >= 0 and self.m <= 1

    def mixing(self, name=None):
        if not self.in_range(): return "Failed to find mixing solution"
        if not name: name = self.v2.name
        return MixInstruction(self.v1.name, name, self.D)

    
class Interim():
    
    v0 = VECTOR3()
    v1 = VECTOR3()
    v2 = VECTOR3()
    v3 = VECTOR3()

    P0 = VECTOR3()
    P1 = VECTOR3()

    delta = 100
    D = 0.5
    density = 1.0
    Px = None
    
    def __init__(self, c0, c1, c2, c3):
        ''' Given 3 palette colours c1, c2, c3, c0 is the required colour.
            Determine direction d0 = c1 -> c0, and d1 = c2 -> c3
            Find the closest points P0 and P1 on vectors d0 and d1
            where c1 -> c0 -> P1 and c2 -> P1 -> c3
            
            line from c2 to c3  = c2 + ti v1
            line from c1 to c0  = c1 + tj v0
            
            
        '''
#        print("c1=%s; c2=%s; c3=%s" % (str(c1), str(c2), str(c3)))
        vectors = c0.as_vector3(), c1.as_vector3(), c2.as_vector3(), c3.as_vector3()
        v0, v1, v2, v3 = self.v0, self.v1, self.v2, self.v3 = vectors
        
        d0 = v1.direction(v0)        # The direction of v0
        d1 = v2.direction(v3)
        
        # v0 = c0.subtract(c1)
        # v1 = c2.subtract(c3)
        #  v0 = c1 + t0 * d0
        #  v1 = c2 + t1 * d1
        #
        #  n = d0 x d1
        #
        #  t0 = (c2 - c1) . n1 / (d1 . n1)    : n1 = d1 x n
        #  t1 = (c1 - c2) . n0 / (d1 . n0)    : n0 = d0 x n
        
        n = d1.cross(d0)               # n is the vector perpendicular to both v0 & v1
        
        n0 = d0.cross(n)
        n1 = d1.cross(n)

        d0xn1 = d0.dot(n1)
        d1xn0 = d1.dot(n0)

        t0 = v2.subtract(v1).dot(n1) / d0xn1 if d0xn1 else 0        
        self.P0 = v1.add(d0.multiply(t0))    #  c1 -> c0 -> P0
        q0 = v0.distance(v1)
        self.m0 =  self.P0.distance(v1) / q0 if q0 else 0 
    
        t1 = v1.subtract(v2).dot(n0) / d1xn0 if d1xn0 else 0        
        self.P1 = v2.add(d1.multiply(t1))    # c2 -> P1 -> c3
        q1 = v3.distance(v2)
        self.m1 =  self.P1.distance(v2) / q1 if q1 else 0
        
        if min(self.P0.as_list()) >= 0 and min(self.P1.as_list()) >= 0 and self.m0 > 1:
            self.delta = self.P0.distance(self.P1)
            self.density = c2.density * (1 - self.m1) + c3.density * self.m1
            self.D = self.m1 / self.density if self.density else self.m1
            self.Px = Projection(c0, c1, self.P1.as_cmyk(self.P1.name, "", density=self.density))
            # print('target %s' % (c0.as_cmyk()))
            # print("%s -> %s -> %s (%.2f[%.2f])" % (c2.as_cmyk(), self.P1.as_cmyk(), c3.as_cmyk(), self.m1, t1))
            # print("%s -> %s -> %s (%.2f[%.2f])" % (c1.as_cmyk(), c0.as_cmyk(), self.P0.as_cmyk(), self.m0, t0))
            # print('  -> projected: %s (delta=%.2f)' % (self.Px.P.as_cmyk(), self.Px.delta))
            if not self.Px.in_range() or not self.in_range():
                self.Px= None

    def __repr__(self):
        return ("interim({}->{}->{}) m0={:.2f};\n  Px={}"
                .format(self.v2, self.P0, self.v3, self.m0, self.Px))

    def __lt__(self, other):
        if self.Px:
            return self.Px.delta < other.Px.delta if other.Px else True
        return False

    def in_range(self):
        if not self.Px: return False
        return self.m1 > 0 and self.m1 < 1

    def mixing(self):
        if not self.in_range(): return "Failed to find mixing solution"
        return MixInstruction(self.v2.name, self.v3.name, self.D)

# class CMYK_dict(grok.Adapter):
#     grok.adapts(ICMYK)
#     grok.provides(IDICT)
#
#     def __new__(cls, cmyk):
#         return dict(c=cmyk.cyan, m=cmyk.magenta, y=cmyk.yellow, k=cmyk.black,
#                     name=cmyk.name, mix=cmyk.to_mix.as_list() if cmyk.to_mix else [],
#                     density=cmyk.density)

class CMYK(grok.Model):
    """  Represents a CMYK colour.   Several methods provide for conversion
       to or from RGB, or other ways to manipulate the colour.
    """
    grok.implements(ICMYK)
    
    name = ""
    cyan = 0
    magenta = 0
    yellow = 0
    black = 0
    to_mix = ""
    density = 1.0
    
    def __init__(self, c=0,m=0,y=0,k=0, name="", to_mix=None, density=1.0):
        self.name = name
        self.cyan = int(c)
        self.magenta = int(m)
        self.yellow = int(y)
        self.black = int(k)
        self.to_mix = to_mix or ""
        self.density = density
        
    def __repr__(self):
        return "{}({},{},{},{})".format(self.name, int(self.cyan), int(self.magenta), int(self.yellow), int(self.black))

    def mixing(self, text):
        self.to_mix = text

    def normalise(self):
        '''  Extract the black pigment from cyan, magenta and yellow
             in equal quantities, and add it back as the [k] component.
             
             This method acts on the current colour, and alters its representation.
        '''
        k = min([100, self.cyan, self.magenta, self.yellow])
        self.cyan -= k
        self.magenta -= k
        self.yellow -= k
        self.black += k
        
        return self
        
    def denormalise(self):
        '''  Remove the black pigment component by adding back equal quantities of
             cyan, magenta and yellow

        ???
        c = self.cyan + self.black
        m = self.magenta + self.black
        y = self.yellow + self.black
        '''
        k = self.black
        if self.black:
            c = self.cyan + k 
            m = self.magenta + k
            y = self.yellow + k
            return CMYK(c,m,y,0,self.name)
        return self
    
    def subtract(self, cmyk):
        '''  Subtract cmyk from the current colour, and return a new denormalised colour
            Could have negative colour values returned
        '''
        c1 = self.denormalise()
        c2 = cmyk.denormalise()
        return CMYK(c1.cyan - c2.cyan, c1.magenta - c2.magenta, c1.yellow - c2.yellow, 0)

    def as_vector3(self):
        c = self.denormalise()
        return VECTOR3(c.cyan/100.0, c.magenta/100.0, c.yellow/100.0, name=self.name)

    def add(self, cmyk):
        '''  Add cmyk to the current colour, and return a new denormalised colour
        '''
        c1 = self.denormalise()
        c2 = cmyk.denormalise()
        return CMYK(c1.cyan + c2.cyan, c1.magenta + c2.magenta, c1.yellow + c2.yellow, 0)

    def coverage(self, ratio, parts):
        """ Calculate the amount of additional coverage gained by adding parts of 
            a pigment having an initial percent coverage.
            
            It is impossible to attain 100% coverage by adding layers of a pigment 
            having less than 100% coverage.  It is possible to get very close though,
            since each addition covers progressively more of the uncovered area.
        """
        if ratio > 1:
            raise ValueError("coverage: ratio should be <= 1")
        if ratio == 1:
            ratio = 0.999999
        init = 1.0 / (1 - float(ratio))
        coverage = 1 - 1/math.pow(init, parts)
        print("coverage for {} parts of p[{}] = {}".format(parts, round(ratio,2), coverage))
        return coverage
        
    def to_rgb(self):
        '''  Return an RGB colour by converting from CMYK
        '''
        k = min(self.black,100) / 100.0
        c = min(self.cyan,100)/100.0
        m = min(self.magenta,100)/100.0
        y = min(self.yellow,100)/100.0
        
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        
        return RGB(r,g,b)

    def from_rgb(self, rgb=None, name=""):
        '''  Create a new CMYK colour from an RGB colour
        '''
        if type(rgb) is RGB:
            r, g, b = rgb.red/255.0, rgb.green/255.0, rgb.blue/255.0
            k = 1 - max(r, g, b)
            f = 1.0 - k
            
            self.cyan = int(round(100 * ((1 - r - k) / f if f else 0)))
            self.magenta = int(round(100 * ((1 - g - k) / f if f else 0)))
            self.yellow = int(round(100 * ((1 - b - k) / f if f else 0)))
            self.black = int(round(100 * k))
            self.name = name
        else:
            raise ValueError("CMYK::from_rgb(rgb) parameter is of an incorrect class")

    def rgbstring(self):
        rgb = self.to_rgb()
        return u"rgb({},{},{})".format(rgb.red, rgb.green, rgb.blue)

    def mix(self, cmyk, parts):
        """ Mix [parts] parts of cmyk with the current colour, return a new denormalised colour
          - check:
              1 part of c1 + 1 part of c1 is 2 parts of c1
              0 parts of c1 + 1 part of c2 is 1 part of c2
              
                if c is a colour component,
                 - more than 100% coverage is not possible.
                 - adding n parts of a component having c=50% is equivalent to adding n/2 parts of c=100%
                 - adding 1 part to a mix having 2 parts is the same as adding 1/5 part to a mix having 1 part                 
        """
        if type(cmyk) is CMYK:
            c1 = self.cmylist()
            c2 = cmyk.cmylist()
            if parts:
                total = self.density + parts*cmyk.density
                c, m, y = [(a*self.density + b*parts*cmyk.density)/total for a,b in zip(c1, c2)]
                density = (self.density + cmyk.density * parts) / total
                return CMYK(c,m,y,0,density)
            else:
                return cmyk
        else:
            raise ValueError("CMYK::mix(cmyk, parts) parameters have unexpected class")

    def cmylist(self):
        c = self.denormalise()
        return [c.cyan, c.magenta, c.yellow]
        
    def whiteness(self):
        """ Returns the amount of white pigment (uncovered area) in this colour
        """
        return 100 - max(self.cmylist())

    def multiply(self, ratio):
        """ Multiply self by a ratio
        """
        c = self.denormalise()
        return CMYK(c.cyan * ratio, c.magenta * ratio, c.yellow * ratio, 0, c.name)
    
    def divide(self, ratio):
        """ Divide self by a ratio
        """
        if ratio:
            return self.multiply(1.0/ratio)
        else:
            raise ValueError("CMYK::divide(ratio) attempted division by zero")    
        
    def ratio(self, target):
        """ Divide self by target, determining the minimum ratio of all components
        """        
        if type(target) is CMYK:
            source = self.cmylist()
            target = target.cmylist()
            return [a / b if b else 0 for a, b in zip(source, target)]
        else:
            raise ValueError("CMYK::ratio(target) parameters have unexpected class")

    def projection(self, c1, c2):
        ''' Vector c1 and c2 represent two palette colours, and we want to
            find the closest point to self on the line between c1 and c2.
            We also want to ensure that this point is not outside the bounds
            of the line.
        '''
        prj = Projection(self, c1, c2)
        
        return prj

    def interim(self, c1, c2, c3):
        ''' Given 3 palette colours c1,c2,c3, c0 is the current colour (self).
            Determine direction d0 = c1 -> c0, and d1 = c2 -> c3
            Find the closest points P0 and P1 on vectors d0 and d1
            where c1 -> c0 -> P1 and c2 -> P1 -> c3
        '''
        return Interim(self, c1, c2, c3)
        