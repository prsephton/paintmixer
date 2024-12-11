# PaintMixer

**PaintMixer** starts with a palette of known paints, and attempts to match a target paint colour using a reflective colour model.

## Best Effort

First, one must realise that this is a "best effort", since there are many types of paints, for example, oils, acrylics or water colours, and each of these behave differently when mixing.

Furthermore, Paintmixer converts between emissive RGB colours for display and CMYK reflective colours, and this conversion does not always perfectly describe the pigment quantities in a typical paint mixture.

It will sometimes be impossible to match a target colour from a given palette.  Typically, a basic palette contains red, blue and yellow with black and white.  From this palette it is impossible to reproduce pure primaries such as cyan or magenta.


## Running PaintMixer

There may already be an instance of PaintMixer running at [https://aptrackers.com/paintmixer](https://aptrackers.com/paintmixer).  If not, you can install it as follows.

Ensure you have Python 2.7 available, as this program uses it.   An easy way to ensure availability, is by using [pyenv](https://github.com/pyenv/pyenv).

We also need [pipenv](https://pipenv.pypa.io/en/latest/) for installation.  If you don't yet have pipenv, 

	pip install pipenv

Then, from the base folder of this project, 

	pipenv install

This installs [buildout](https://www.buildout.org/en/latest/) which we use for the rest of the installation, and sets up a virtual environment for the project.  After everything is done, type

	pipenv shell
	buildout bootstrap
	bin/buildout
	
There should be a lot of packages installed at this point.  When completed, run zpasswd to assign a system password to the app server:

	bin/zpasswd

Then start the application server on the default port 8080 with:

	bin/paster serve --reload parts/etc/deploy.ini

Point your browser at http://localhost:8080 and add an instance of the PaintMixer application to the app server.  You can then
follow the link you have just created to access the application.


## Features

 * Unlimited number of palettes
 * Calculates interim colours along a path to the target
 * Produces a mixing recipe for a desired quantity with amounts of constituent colours by weight.

## Notes

 * This project uses Python 2.7
 * The code uses the **grok** application server
 * Paintmixer is free for use under the GPL v3
