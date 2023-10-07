from fanstatic import Library, Resource

library = Library('paintmixer', 'static')

style = Resource(library, 'style.css')
tooltips = Resource(library, 'tooltips.css')

htmx       = Resource(library, 'js/htmx.min.js')
jquery     = Resource(library, 'lib/jquery-1.11.1.min.js')
mixview    = Resource(library, 'js/mixview.js', depends=[jquery])