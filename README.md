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
  -s, --shapes          Do NOT care about shapes when active
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold value for adjusting image result ([5-250] -
                        default: 60)
  -n, --normalize       Do NOT normalize the shapes when active
  -f, --factorize       Do NOT factorize the areas when active
  -b, --largetohigh     Large areas produce hight frequencies sound
  -a, --audioconfig     Interactive audio setup - generate in the same time
                        the command line argument for -y/--pyoconfig
  -y PYOCONFIG, --pyoconfig PYOCONFIG
                        Set config for Pyo audio server (see -a/--audioconfig)
  -v, --verbose         Enable debug output (default: off)
```

See the file [Issue.md](Issues.md) for known problem and task list and [LICENSE.md](LICENSE.md)
for information about copyright and usage terms.

Version [__Prototype__ | ~~Alpha~~ | ~~Beta~~ | ~~Released~~]

# Dependencies
___Important___ : Only support OpenCV 3.x

## Gnu/Linux
* Python3
* Python3 pip (Debian package: python3-pip)
* [OpenCV](http://opencv.org/), based on opencv 3.x
* Python3 bindings for the computer vision library (Debian package: python3-opencv)

```
sudo apt-get install python3-pip python3-opencv
```

### Python3 packages
~~* [Cython], The Cython compiler for writing C extensions~~
~~* [setuptools], setuptools~~
* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.
* [Numpy](https://numpy.org/), scientific computing.

```
/path/to/python3 -m pip install numpy pyo --user --upgrade
```

## Mac OsX

* Python3 - www.python.org / install / mac
* Python3 pip

### Python3 packages

* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.
* [Numpy](https://numpy.org/), scientific computing.
* [OpenCV v3.x for Python](https://opencv.org/)  (3.4.8.29 .... check current version on https://pypi.org/ )

```
/path/to/python3 -m pip install numpy pyo opencv-python==3.4.8.29 --user --upgrade
```
