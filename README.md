# PaintMixer

**PaintMixer** starts with a palette of known paints, and attempts to match a target paint colour using a reflective colour model.

## Best Effort

First, one must realise that this is a "best effort", since there are many types of paints, for example, oils, 
acrylics or water colours, and each of these behave differently when mixing.

Furthermore, Paintmixer converts between emissive RGB colours for display and CMYK reflective colours, and this 
conversion does not always perfectly describe the pigment quantities in a typical paint mixture.

It will sometimes be impossible to match a target colour from a given palette.  Typically, a basic palette contains red, blue 
and yellow with black and white.  From such palettes it is impossible to reproduce pure primaries such as cyan or magenta.


## Running PaintMixer

This project is now based on the docker container at https://hub.docker.com/r/prsephton/grokserver.  Therefore, to run 
the server, you will need docker installed.

After installing docker, clone the repo, and from the base folder, type "make run".   You will be prompted for a super user 
name and password on the first run.

The application server will be available by default on [localhost http port 8080](http://localhost:8080).

First install the application (PaintMixer) with a chosen name (eg. "pm").  Then navigate to the installed app by clicking the link.

## How to use it

The first time you access the program, you are presented with a default CMYK palette.  In the real world, such a palette is only 
found in a colour lazer or inkjet printer, and rarely in paints.

More commonly, one will have a set of paints, the basic palette being blue, yellow, red, while and black.  From this core set, it
is well known that one might mix these to produce a variety of colours and shades.  Even though the variety is not exhaustive (there
are certainly some that are not achievable) there are a great many combinations.

The problem faced when mixing paints, and what this program tries to solve, is that most mixing of paints is based upon 
experience, intuition, trial and error, and imperfect prior knowledge can lead to much material wastage and cost.  What 
if one could instead generate a set of mixing instructions which, given a known palette, will produce a colour or shade 
close to your desired target?

### Mixing paints; palettes

The first step is to tell the program about your palette.  Thare are a variety of pigments available, and all purchased paints
differ in concentration (weight per volume of paint), the choice of pigments used, attributes such as "shininess" or transparency,
the type of paint (eg. oils or acrylic) and so forth.  However, assuming your paints are of the same type and sourced from the same 
manufacturer, the chances are that you will be able to mix them to produce different colours, shades, tints, and so on.

Purchased paints might have a name like "Cerulean blue", "Brick Red" or "Primrose Yellow".  These are named colours which have a 
well known corresponding CMYK value.   Some paints though have weird names or 

A reasonable way of determining the actual colour of a given paint, is to paint a sample on a white sheet of paper, and after it is dry, take a 
photograph with your phone.  Depending on lighting conditions, you should be able to use Google to match the colour.  You can ask Google what
the RGB or CMYK values (or even the name) are of the paint.

Another approach is to match the painted sample against a standard such as Pantone.  

Once you have the CMYK (preferred) or RGB values for your paint, add it to the current palette by 
	* for RGB, clicking the "Colour" box and entering the colour information or
	* for CMYK, enter the values directly in the boxes provided

After the colour information is entered, give the colour a name, and click "Add" to add it to the palette.

For extraneous colours, simply select each in the palette view and click "Remove" to remove it.

Once all of the colours in yourr palette are present, overwrite the palette name and click the "Save" button, which will then
make your palette available in the palette dropdown.

### Calibration

You may be surprised to learn that all paints are not of equal strength.  Even by weight.  For example, it is well known that 
mixing yellow and blue will produce a green pigment.  However, to produce a green colour exactly between blue and yellow on 
the spectrum, you will need to add a lot more yellow than one might expect.

Likewise, red is generally a much stronger pigment than the others, and a little red goes a very long way.

There is no universal guideline that will tell us exactly how much of one colour to mix with another to achieve a desired
affect.  It depends completely on the type of paint and manufacturer.  That is why it is a very hard thing to learn to do 
under ordinary circumstance.

Our paintmixer program provides a process whereby one may determine the relative strengths of each pigment, so that it knows
with reasonable preciseness how much paint to add to another to achieve a target colour.  It does this by comparing the 
strength of each pigment to a common known pigment (white).

The calibration process asks you to mix equal weights of white to each of the other colour pigments (not black).  For example,
0.1g white and 0.1g Azure Blue, and paint the mixture on a sheet of white paper.  The program then presents you with a list of
shades which, assuming equal pigment strength, would place the painted shade in the middle of the list.  You then select the
closest matching shade from the list, and the program uses this information to adjust the relative strengths of the pigments 
for your palette.

### Mixing instructions

With a defined palette selected, the program allows the selection of a target colour (RGB or CMYK) and will then use your palette 
to produce a set of mixing instructions (the "Mix" button).  The initial target weight is 10g of paint, but you can enter
 a different value, and the program will output an adjusted set of instructions.

Note that the program uses weight and not volume to measure portions, as the density of your pigments may change as the paints 
evaporate.

#### An example.

Given the default CMYK palette, type the value 10 (10%) into the "Cyan" box, and hit "Mix".

The program produces the following mixing instructions:

```

		Mixing Instructions for target: CMYK(10,0,0,0)
			( 100.00% matching accuracy achieved )

		mixed.0: 9.00 parts of (white) to 1.00 parts of (cyan)
    			1.00 grams of cyan
    			9.00 grams of white

```

Mixed Colours in the palette are named "Mixed.n" where *n* is a number indicating the target colour.

Now add a value of 10% Magenta, and hit "Mix" again.  This time, the program produces a new set of mixing instructions.

```

		Mixing Instructions for target: CMYK(10,10,0,0)
			( 100.00% matching accuracy achieved )
		
		mixed.1: 2.00 parts of (cyan) to 2.00 parts of (magenta)		
		    1.00 grams of magenta
		    1.00 grams of cyan
		
		mixed.2: 4.00 parts of (white) to 1.00 parts of (mixed.1)		
		    2.00 grams of mixed.1
		    8.00 grams of white

```

The program is saying to first mix 1 gram of cyan and 1 gram of magenta.  Then mix those 2 grams with anothert 8 grams of white
to produce 10 grams of final mixture, with 80% white, 10% cyan and 10% magenta.  

In the reflective colour model, this means that 
90% of incoming white light cyan wavelength will be reflected (80% white includes all colours including cyan + 10% cyan = 90%), and 
the same for the magenta wavelength.  There is also an 80% reflection for all colours in the spectrum.  

The resulting colur will be a lavender blue (R: 229, G: 229, B: 255 or #e5e5ff).

Remember that this assumes equal pigment strengths, and that cyan and magenta pigments are the perfect primaries.  Nevertheless, it 
should be plain that the program is producing the appropriate instructions, given these rather idealistic conditions.  Things 
become a lot more messy in the real world.

## Features

 * Unlimited number of palettes.
 * Palettes are stored using your browser's local store.  No permanent information is stored by the server.
 * Calculates interim colours along a path to the target.
 * Produces a mixing recipe for a desired quantity with amounts of constituent colours by weight.
 * Calibration of your palette pigments via a well described and simple to use procedure will vastly improve results.

## Notes

 * This project now uses Python 3.13.
 * The code uses the **grok** application server.
 * Paintmixer is free for use under the GPL v3.
