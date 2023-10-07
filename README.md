# PaintMixer

PaintMixer starts with a palette of known paints, and attempts to match a target paint colour using a reflective colour model.

## Best Effort

First, one must realise that this is a "best effort", since there are many types of paints, for example, oils, acrylics or water colours, and each of these behave differently when mixing.

Furthermore, Paintmixer converts between emissive RGB colours for display and CMYK reflective colours, and this conversion does not always perfectly describe the pigment quantities in a typical paint mixture.

It will sometimes be impossible to match a target colour from a given palette.  Typically, a basic palette contains red, blue and yellow with black and white.  From this palette it is impossible to reproduce pure primaries such as cyan or magenta.

## Features

 * Unlimited number of palettes
 * Calculates interim colours along a path to the target
 * Produces a mixing recipe for a desired quantity with amounts of constituent colours by weight.

## Notes

 * This project uses Python 2.7
 * The code uses the **grok** application server
 * Paintmixer is free for use under the GPL v3
