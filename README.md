# ArchiMusik
#### « an image to music transcoder »

Version [~~Prototype~~ | __Alpha__ | ~~Beta~~ | ~~Released~~]

##WHAT THE HECK?
#Generative Synthesis
#In playhead mode, the audio synthesis is generated during the travel of the play head. The audio synthesis is based on the shape area.
#In sequential mode, play each shape sequencialy. The generation of the audio synthesis is based on the shape area.
#MIDI control
#In playhead mode, the MIDI control are sent during the travelof the play head. The MIDI note is based on the shape area.
#In sequential mode, play each shape sequencialy. The MIDI note is based on the shape area.


###### what about played music from structural architecture elements ?

# Author
Jérôme Blanchi aka d.j.a.y

# Usage
```
ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA
Your are viewing some not released work... good luck!
ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA
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

Version [~~Prototype~~ | __Alpha__ | ~~Beta~~ | ~~Released~~]

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
