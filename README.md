# KeebGen
A python library that gives the poeple who use keyboards the most the power to design their own

### Authors
- Darren Harton
- Quentin Torgerson

## Package Summary
The KeebGen package is intended as a way for programmers to easily generate
their own custom keyboards. This project was inspired by the Dactyl project,
but is intended to be a genaric library of building blocks that can be used to
quickly and easily design any type of keyboard.

KeebGen provides users with common keyboard primatives that allow a user to
model an entire keyboard without having to worry about the minutia of a design.
A Cherry MX switch is a standard part, so users should not have to re-draw a
socket for it every time they want to design a new keyboard. Instead, they can
just add a CherryMXSocket() to the model and move it to its place.

KeebGen uses the [SolidPython](https://github.com/SolidCode/SolidPython) package to generate openscad files. [OpenSCAD](https://www.openscad.org/) is a
free software that generates 3D models from code. OpenSCAD is a powerful tool
for making parametric 3D models, but it can be difficult for a python
programmer to get used to its syntax. The SolidPython package bridges the gap,
and is the basis of KeebGen modeling.


## Quick Start
You can start making your own keyboards quickly using the primatives that
already exist in the class
```python
import keebgen
with file load config something something
modify config, change num rows or something
keeb = keebgen.DactylManuform(config)
keeb.to_file(outfile)
```
show screenshot of the model that is generated from the example code to get
people hooked on how amazing it is

point to file so they can see latest list of built in keyboard designs

Users can also generate their own keyboards from scratch using included primatives
```python
import keebgen
not sure yet
some trivial example for a flat keyboard
maybe show a minimal custom Keyboard class?
maybe just make something small like a numpad/macropad or 4 arrow keys out of Key primatives
```
show the cool example 3D model here

users can add their own specializations to current primative types
```python
example of making simple custom socket or keycap or something
```
show model here

convert *.scad file to .stl in ther terminal
```openscad <file.scad> -o <dest_file.stl>```
This is also possible in the OpenSCAD viewer window. Render the file with F6, then file->export->stl

When customizing a keyboard, it can be helpful to have the OpenSCAD model open
to see updates immediately automatically re-run python script on save. have
OpenSCAD open

to automatically run script whenever directory changes:
`while true; do inotifywait -e modify <path_to_directory> && python3 <script to run>; done`
`while true; do inotifywait -e modify keebgen && python3 examples.py; done`

talk about printing smallest building block as you go. If you don't know
printer parameters you need for a good socket, start by printing a socket only
and testing. As this works, add more sockets and test if the layout is good.
Once this owrks, add a full shell and then print a final version. Wastes less
time and filament on each design iteration,


## Contributing
We welcome contributions. This can be things such as code improvements, new
primatives, or entirely new keyboard designs to be added to the default
library.

quick explanation of current class hierarchy. what each type of object is

explain the importance of anchors. needed to track geometry transformations and
allow stuff to be parametric. Using the standard anchor points for a primative
allow it to be inserted into existing keyboard design with a simple config
change.

some guidelines of adding new primatives.
all of the base class functions implemented
anchor scheme matches the general scheme of the primative type

Ideally, keyboard models are parametric when appropriate, at a minimum
allowing users to customize keycap and switch type with a config file

### Contributors
- someone
