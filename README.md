# ArchiMusik
#### « an image file music player »

Version [__Prototype__ | ~~Alpha~~ | ~~Beta~~ | ~~Released~~]

###### what about played music from structural architecture elements ?

# Author
Jérôme Blanchi aka d.j.a.y

# Usage
```
PROTO ----- PROTO ----- PROTO ----- PROTO ----- PROTO
Your are viewing some not released work... good luck!
PROTO ----- PROTO ----- PROTO ----- PROTO ----- PROTO
```

Quick start:
```
$ /path/to/python3 archimusik.py -i ./test/rondrondrond.jpg
```

Long story:
```
usage: archimusik.py [-h] -i IMAGE [-m MODE] [-d DIRECTION] [-n] [-v]

What about played music from structural architecture elements ?
ArchMusik is an image music player for architecture elements.

Play the sound of the partition found in the image.
Basic sinusoïd, (todo) midi/osc/vdmx messages.

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        Path to the input image
  -m MODE, --mode MODE  Play mode : Head=1 (default) , Sequence=2
  -d DIRECTION, --direction DIRECTION
                        Mode direction : TtoB=1 (default) , BtoT=2 , RtoL=3 ,
                        LtoR=4
  -n, --normalize       Do NOT normalize the shapes when active
  -v, --verbose         Enable debug output (default: off)
```

See the file [Issue.md](Issues.md) for known problem and task list and [LICENSE.md](LICENSE.md)
for information about copyright and usage terms.

Version [__Prototype__ | ~~Alpha~~ | ~~Beta~~ | ~~Released~~]

# Dependencies
___Important___ : Only tested with OpenCV 3.2

* [OpenCV](http://opencv.org/), based on opencv 3.2
* Python 3 bindings for the computer vision library (Debian Package: python3-opencv)

## Python3 packages
* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.
* [Numpy](https://numpy.org/), scientific computing.
* [pyliblo](http://das.nasophon.de/pyliblo/), pyliblo is a Python wrapper for the liblo OSC library.

```
/path/to/python3 -m pip install numpy pyo pyliblo --user --upgrade
```
