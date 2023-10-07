import grok
import simplejson as json

from paintmixer import resource
from grok import IApplication
from palettes import Palette, CMYK, IPaletteFields
from zope import location


class Paintmixer(grok.Application, grok.Container):
    title = "Paint Mixer"
    palette = None
    grok.implements(IPaletteFields)
    
    def __init__(self):
        super(Paintmixer, self).__init__()
        self.palette = Palette()
        self.palette.add(CMYK(0,0,0,0,"white"))
        self.palette.add(CMYK(38,25,0,97,"black"))
        self.palette.add(CMYK(100,0,0,0,"cyan"))
        self.palette.add(CMYK(0,100,0,0,"magenta"))
        self.palette.add(CMYK(0,0,100,0,"yellow"))
#         self.palette.add(CMYK(0,87,83,17,"red"))
#         self.palette.add(CMYK(65,0,69,33,"green"))
#         self.palette.add(CMYK(89,42,0,50,"blue"))
#         self.palette.add(CMYK(0,12,89,2,"yellow"))
 

class PaintmixerTraverser(grok.Traverser):
    grok.context(Paintmixer)
    def traverse(self, name):
        if name == 'palette':
            return Palette()  # a default palette


class Index(grok.View):
    current = 0
    
    def update(self, palette=None, current=0, mixes=None, grams=10, palette_name='Default', 
               delta=0, target="", reset=False):
        self.palette = self.context.palette if palette is None else Palette().fromtext(palette)
        self.palette_name = palette_name
        self.current = int(current)
        self.grams = int(grams)
        self.reset = reset
        self.target = target
        self.delta = float(delta)
        if self.palette.colours:
            if (self.current < len(self.palette.colours)):
                self.colour = self.palette.colours[self.current]
            else:
                self.colour = self.palette.colours[0]
        self.mixes = json.loads(mixes) if mixes else None
        
        location.location.located(self.palette, self.context, 'palette')
        resource.style.need()
        resource.tooltips.need()
        resource.htmx.need()
        resource.jquery.need()
        resource.mixview.need()


class MastHead(grok.ViewletManager):
    grok.context(IApplication)

class Navigation(grok.ViewletManager):
    grok.context(IApplication)

class Content(grok.ViewletManager):
    grok.context(IApplication)

class Footer(grok.ViewletManager):
    grok.context(IApplication)

class PaletteMgr(grok.ViewletManager):
    grok.context(IApplication)


class MastHeadViewlet(grok.Viewlet):
    ''' Render layout masthead
    '''
    grok.context(IApplication)
    grok.viewletmanager(MastHead)

class NavigationViewlet(grok.Viewlet):
    ''' Render layout masthead
    '''
    grok.context(IApplication)
    grok.viewletmanager(Navigation)

class ContentViewlet(grok.Viewlet):
    ''' Render layout masthead
    '''
    grok.context(IApplication)
    grok.viewletmanager(Content)

class FooterViewlet(grok.Viewlet):
    ''' Render layout masthead
    '''
    grok.context(IApplication)
    grok.viewletmanager(Footer)

