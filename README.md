# ArchiMusik
#### « an image file music player »

Version [__Prototype__ | ~~Alpha~~ | ~~Beta~~ | ~~Released~~]

###### what about played music from structural architecture elements ?

# Author
Jérôme Blanchi aka d.j.a.y

# Usage
```
usage: archimusik.py [-i INPUT_FILE]

Play the sound of the partition found in the image.
Basic sinusoïd, midi/osc/vdmx messages.

optional arguments:
  -h, --help            dont show this help message and exit
  -i, --image           input image file to play
  -v, --verbose         dont Enable debug output (default: off)
```

See the file [Issue.md](Issues.md) for known problem and task list and [LICENSE.md](LICENSE.md)
for information about copyright and usage terms.

Version [__Prototype__ | ~~Alpha~~ | ~~Beta~~ | ~~Released~~]

# Dependencies
* [OpenCV](http://opencv.org/), based on opencv 3.2

___Important___ : Only tested with OpenCV 3.2

```
pip3 install Wand
```
* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.

* [pyliblo](http://das.nasophon.de/pyliblo/), pyliblo is a Python wrapper for the liblo OSC library.
```
pip3 install pyliblo
```
