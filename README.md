# PaintMixer

**PaintMixer** starts with a palette of known paints, and attempts to match a target paint colour using a reflective colour model.

## Best Effort

First, one must realise that this is a "best effort", since there are many types of paints, for example, oils, acrylics or water colours, and each of these behave differently when mixing.

Furthermore, Paintmixer converts between emissive RGB colours for display and CMYK reflective colours, and this conversion does not always perfectly describe the pigment quantities in a typical paint mixture.

It will sometimes be impossible to match a target colour from a given palette.  Typically, a basic palette contains red, blue and yellow with black and white.  From this palette it is impossible to reproduce pure primaries such as cyan or magenta.


## Running PaintMixer

This project is now based on the docker container at https://hub.docker.com/r/prsephton/grokserver.  Therefore, to run the server, you will need
docker installed.

After installing docker, clone the repo, and from the base folder, type "make run".   You will be prompted for a super user name and password.

The application server will be available by default on [localhost http port 8080](http://localhost:8080).

First install the application with a chosen name (eg. "pm").  Then navigate to the installed app by clicking the link.


## Features

 * Unlimited number of palettes
 * Calculates interim colours along a path to the target
 * Produces a mixing recipe for a desired quantity with amounts of constituent colours by weight.

## Notes

 * This project now uses Python 3.13
 * The code uses the **grok** application server
 * Paintmixer is free for use under the GPL v3
