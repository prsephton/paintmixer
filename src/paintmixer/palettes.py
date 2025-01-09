'''
Created on 31 Jan 2022

@author: paul
'''
import grok
import math
import json

from paintmixer.colours import CMYK, ICMYK, MixInstruction
from persistent.list import PersistentList
from zope.interface import Interface
from zope import schema
from itertools import permutations
from functools import reduce


class IPaletteFields(Interface):
    '''  Palette Fields Marker
    '''
    # palette = schema.Object()
    # current = schema.Int()
    # grams = schema.Int()
    # mixes = schema.Text()
    
    
class IPalette(Interface):
    colours = schema.List(title=u'Palette Colours', unique=True, 
                          value_type=schema.Object(schema=ICMYK))

class Palette(grok.Model):
    grok.implements(IPalette, IPaletteFields)
    colours = []

    def __init__(self):
        self.colours = PersistentList([])

    def find(self, name):
        """ Find a colour by name """
        names = [c.name for c in self.colours]
        try:
            return names.index(name)
        except Exception:
            return -1

    def find_white(self):
        ''' return an index into the palette for the colour most likely to be white
        '''
        compare = list(enumerate([sum(c.cmylist()) for c in self.colours]))
        compare.sort(key=lambda x: x[1])
        return compare[0][0]

    def calibrate(self, cdata):
        ''' Calibrate the palette, altering the relative density of each colour.
            <cdata> contains calibration data for all palette colours other than white.
            White is treated as the reference colour.
            For each colour:
                Calibration presents shades of the colour by mixing white in the following ratios:
                   1:0, 1:0.2, 1:0.4, 1:0.6, 1:0.8, 1:1, 1:1.2, 1:1.4, 1:1.6, 1:1.8, 1:2
                The user mixes in white in a 1:1 ratio, and compares to the above scale.
                If the colour and white have equal pigment density, we expect the user to select 1:1
                If the user selects < 1:1, then white is denser than the colour, and vica verse
                
            We assume White as reference has a density of 1.
            
            The user chooses a ratio 1/0.6.  This means that we would need more of our colour vs. white.
            To calibrate this colour, we calculate it's density as (old_density * 1.667).  The next time 
            the scale is displayed (using the new density) the 1:1 point will correspond to the 
            correct mix.
            
            If the 1:0 point is selected, we assume that the user wants to reset the density to 1.0            
        '''
        white = self.find_white()
        reference = [5.0/(n+1) for n in range(10)]
        for i, c in enumerate(self.colours):
            if i == white:
                c.density = 1.0
                continue
            ofs = cdata.pop(0)
            if ofs:
                ratio = reference[ofs-1]
                c.density *= ratio
            else:
                c.density = 1.0
            print("Density of %s(%s) is %s" % (c.name, ofs, c.density))

    def pairs(self):
        return [(a, b) for idx, a in enumerate(self.colours) for b in self.colours[idx + 1:]]
        
    def triples(self):
        tlist = [(a, b, c) 
                 for i, a in enumerate(self.colours) 
                 for j, b in enumerate(self.colours[i + 1:])
                 for c in self.colours[i + j + 2:]]
        tlist = [list(permutations(e))[::2] for e in tlist]
        return reduce(lambda a, b: a + b, tlist, [])

    def add(self, cmyk):
        """ Add a colour to the current palette """
        self.colours.append(cmyk.denormalise().normalise())
        return len(self.colours)-1

    def remove(self, name):
        """ Remove a colour from the palette by name """
        n = self.find(name)
        self.colours.pop(n)

    def astext(self):
        """ Dump the palette to a JSON string """
        clist = [[c.cyan, c.magenta, c.yellow, c.black, c.name, c.to_mix.as_list() if c.to_mix else [], c.density] 
                 for c in self.colours]
        return json.dumps(clist)

    def fromtext(self, text):
        """ Read the palette from a JSON string """
        clist = json.loads(text)
        if clist:
            if len(clist[0]) == 7:
                self.colours = [CMYK(cyan, magenta, yellow, black, name, MixInstruction(*to_mix) if to_mix else None, density)
                                for [cyan, magenta, yellow, black, name, to_mix, density] in clist]
            elif len(clist[0]) == 6:
                self.colours = [CMYK(cyan, magenta, yellow, black, name, MixInstruction(*to_mix) if to_mix else None)
                                for [cyan, magenta, yellow, black, name, to_mix] in clist]
        return self
   
    def distance(self, target):
        sel = [c.cmylist() for c in self.colours] 
        t = target.cmylist()
        
        dx = [[i - j for i,j in zip(cmy, t)] for cmy in sel]
        sc = [sum([c*c, m*m, y*y])/3 for c,m,y in dx]
        ssx = [math.sqrt(sq) / 100 if sq else 0 for sq in sc]           # distance match
        
        return ssx
        
    def next_name(self):
        n = len([c.name for c in self.colours if c.name[:6]=='mixed.'])
        return 'mixed.{}'.format(n)

    def find_match(self, cmyk):
        '''  Return a list of raw mixing instructions to produce <cmyk>.
           A mixing instruction is a tuple (parts, colour)
        '''
        print("Interim Projections:")
        delta = 1.0;
        colourname = ""
        for _i in range(5):            
            closest_direct = sorted([cmyk.projection(c1, c2) for c1, c2 in self.pairs()])
            # for c in closest_direct:
            #     print(c)
            closest_direct = closest_direct[0]
#            print(closest_direct)
            
            closest = sorted([cmyk.interim(c1, c2, c3) for c1, c2, c3 in self.triples()])[0]
#            print(closest)
            
            tdelta = delta
            if not closest.Px or closest_direct.delta < closest.Px.delta:
                colourname = self.next_name()
                to_mix = closest_direct.mixing()
                c = closest_direct.P.as_cmyk(name=colourname, to_mix=to_mix, density=closest_direct.density)
                delta = closest_direct.delta                    
                self.add(c)
                if delta < 0.05 or abs(tdelta - delta) < 0.05:
                    print(c)
                    break
            else:
                name = self.next_name()
                c1 = closest.P1.as_cmyk(name=name, to_mix=closest.mixing(), density=closest.density)
                self.add(c1)
                colourname = self.next_name()
                c2 = closest.Px.P.as_cmyk(name=colourname, to_mix=closest.Px.mixing(name), density=closest.Px.density)
                self.add(c2)                                
                delta = closest.Px.delta
                if delta < 0.05 or abs(tdelta - delta) < 0.05:
                    break
        return colourname, delta

    def mixes(self, colourname, grams):
        instructions = []
        cnames = []
        while colourname:
            ofs = self.find(colourname)
            print("Colour find: ",colourname," at ",ofs)
            if ofs >= 0:
                c = self.colours[ofs]
                print(c.to_mix)
                
                if isinstance(c.to_mix, MixInstruction):
                    nparts = sum([parts for parts, _name in c.to_mix.parts])
                    grams_per_part = grams / nparts
                    for parts, name in c.to_mix.parts:
                        amount = parts * grams_per_part
                        instructions.append("    {:.2f} grams of {}".format(amount, name))
                        cnames.append((name, amount))
                    instructions.append("{}: {}".format(c.name, str(c.to_mix)))
            print(cnames)
            (colourname, grams) = cnames.pop(0) if cnames else ("", 0)
        instructions.reverse()            
        return instructions


class InstructionMgr(grok.ViewletManager):
    grok.context(IPaletteFields)
    grok.name('mix_instructions')


class MixInstructionViewlet(grok.Viewlet):
    grok.context(IPaletteFields)
    grok.viewletmanager(InstructionMgr)


class MixInstructionForm(grok.View):
    
    def update(self, palette, current=0, grams=10, delta=0, target=""):
        self.palette = self.context.fromtext(palette)
        self.current = int(current)
        self.grams = int(grams)
        self.delta = float(delta)
        colourname = self.context.colours[int(current)].name
        self.mixes = self.context.mixes(colourname, int(grams))
        self.target = target
        print("Mixes=", self.mixes)

    def render(self):
        tpl = grok.PageTemplate("""
            <div tal:replace="structure provider:mix_instructions"></div>
        """)
        return tpl.render(self)


class ProcessColour(grok.View):
    
    def update(self, palette, bn_calibrate=None, bn_add=None, bn_remove=None, bn_reset=None, bn_mix=None, 
               current=0, colourname='', cyan=None, magenta=None, yellow=None, black=None,
               mixes=None, grams=10, palette_name='Default', delta=0, target=""):
        
        if not mixes: mixes = ""        
        if bn_calibrate:
            self.redirect(self.url(self.context.__parent__, name='calibration', 
                                   data={'palette': palette, 'current': current,
                                         'mixes': mixes, 'grams': grams, 'palette_name': palette_name,
                                         'delta': delta, 'target': target}))
        elif bn_reset:
            self.redirect(self.url(self.context.__parent__, name='', data=dict(reset=True)))
        else:
            self.context.fromtext(palette)
            if bn_add:
                current = len(self.context.colours)
                self.context.add(CMYK(cyan, magenta, yellow, black, colourname))
            elif bn_remove:
                current = int(current)
                self.context.remove(colourname)
                if current >= len(self.context.colours):
                    current -= 1
            elif bn_mix:
                print("Palette: " + str([str(c) for c in self.context.colours]))
                cmyk = CMYK(cyan, magenta, yellow, black)
                colourname, delta = self.context.find_match(cmyk)
                current = len(self.context.colours) - 1
                cmyk.name = "CMYK"
                target = str(cmyk)
            
            if colourname and grams:
                mixes = self.context.mixes(colourname, int(grams))
                print("Mixes=", mixes)
                mixes = json.dumps(mixes)
            
            self.redirect(self.url(self.context.__parent__, name='index', 
                                   data={'palette': self.context.astext(), 'current': current,
                                         'mixes': mixes, 'grams': grams, 'palette_name': palette_name,
                                         'delta': delta, 'target': target}))

    def render(self):
        return self.context



class Calibrate(grok.View):
    
    def update(self, palette, bn_calibrate=None, 
               current=0, palette_name='Default', delta=0, target="",
               mixes=None, grams=10):
        if not mixes: mixes = ""   
        self.context.fromtext(palette)
        if bn_calibrate:
            cdata = [int(self.request.form["match_%i" % (i+1)])-1 for i in range(len(self.context.colours)-1)]
            self.context.calibrate(cdata)
        
        self.redirect(self.url(self.context.__parent__, name='index', 
                               data={'palette': self.context.astext(), 'current': current,
                                     'mixes': mixes, 'grams': grams, 'palette_name': palette_name,
                                     'delta': delta, 'target': target}))

    def render(self):
        return self.context

