'''
Created on 31 Jan 2022

@author: paul
'''
import grok
import math
import simplejson as json

from colours import CMYK, ICMYK, MixInstruction
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
        clist = [[c.cyan, c.magenta, c.yellow, c.black, c.name, c.to_mix.as_list() if c.to_mix else []] 
                 for c in self.colours]
        return json.dumps(clist)
    
    def fromtext(self, text):
        """ Read the palette from a JSON string """
        clist = json.loads(text)
        self.colours = [CMYK(cyan, magenta, yellow, black, name, MixInstruction(*to_mix) if to_mix else None)
                        for [cyan, magenta, yellow, black, name, to_mix] in clist]
        return self

    # def mix(self, mixes):
    #     current = self.colours[self.find('white')]
    #     cparts = 0
    #     for parts, cname in mixes:
    #         c = self.colours[self.find(cname)]
    #         current = current.mix(c, cparts, parts)
    #         cparts += parts
    #     return current
    #
    # def gradients(self, target):
    #     sel = [c.cmylist() for c in self.colours] 
    #     t = target.cmylist()
    #
    #     mx = [(m-c, y-m) for c,m,y in sel]   # gradients
    #     mz = (t[1]-t[0], t[2]-t[1])       # target gradients
    #
    #     mzx = [[x - y for x, y in zip(xsel, mz)] for xsel in mx]
    #     ssq = [sum([mc*mc, ym*ym])/2 for mc, ym in mzx]
    #     grad = [math.sqrt(sq)/100 if sq>0 else 0 for sq in ssq]             # gradient match
    #
    #     return grad
    
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
                c = closest_direct.P.as_cmyk(name=colourname, to_mix=closest_direct.mixing())
                delta = closest_direct.delta                    
                self.add(c)
                if delta < 0.05 or abs(tdelta - delta) < 0.05:
                    print(c)
                    break
            else:
                name = self.next_name()
                c1 = closest.P1.as_cmyk(name=name, to_mix=closest.mixing())
                self.add(c1)
                colourname = self.next_name()
                c2 = closest.Px.P.as_cmyk(name=colourname, to_mix=closest.Px.mixing(name))
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
    
    def update(self, palette, bn_add=None, bn_remove=None, bn_reset=None, bn_mix=None, 
               current=0, colourname='', cyan=None, magenta=None, yellow=None, black=None,
               mixes=None, grams=10, palette_name='Default', delta=0, target=""):
        
        if not mixes: mixes = ""        
        if bn_reset:
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
