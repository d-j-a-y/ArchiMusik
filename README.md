# ArchiMusik
#### « an image to music transcoder »
###### what about played music from structural architecture elements ?

Version [~~Prototype~~ | __Alpha__ | ~~Beta~~ | ~~Released~~]

# Author
Jérôme Blanchi aka d.j.a.y

Thanks to Vloop for some coding rendez-vous!

# About
See the file [Issue.md](Issues.md) for known problems and task list and [LICENSE.md](LICENSE.md)
for information about copyright and usage terms.
## WHAT THE HECK?
### Generative Synthesis
* In play head mode, the audio synthesis is generated during the travel of the play head. The audio synthesis is based on the shape.
* In sequential mode, play each shape sequencially. The generation of the audio synthesis is based on the shape.
### MIDI control
* In play head mode, the MIDI control are sent during the travel of the play head. The MIDI note is based on the shape.
* In sequential mode, play each shape sequencially. The MIDI note is shape based.

# Usage
```
                        ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA
                        Your are viewing some not released work... good luck!
                        ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA
```

## Quick start:
Download the latest [release](https://github.com/d-j-a-y/ArchiMusik/releases), extract and launch!
```
$ /path/to/python3 archimusik.py -i ./test/rondrondrond.jpg
```

There is more infos and dependencies in __Installation__ section.
## Long story:
```
usage: archimusik.py [-h] -i IMAGE [-m MODE] [-d DIRECTION] [-s]
                     [-t THRESHOLD] [-n] [-f] [-b] [-a] [-y PYOCONFIG] [-v]

What about played music from structural architecture elements ? ArchMusik is
an image music player for architecture elements. It transcode to sound the
partition found in the image using basic sound synthesis or by sending MIDI
messages.

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
  -b, --largetohigh     Large areas produce high frequencies sound
  -a, --audioconfig     Interactive audio/midi setup, try that if mute ;-) -
                        (generate also the argument for passing to
                        -y/--pyoconfig)
  -y PYOCONFIG, --pyoconfig PYOCONFIG
                        Set config for Pyo audio server (see -a/--audioconfig)
  -v, --verbose         Enable debug output (default: off)

```

Version [~~Prototype~~ | __Alpha__ | ~~Beta~~ | ~~Released~~]

# Installation
ArchiMusik -actually- is a standalone Python script.
But, need some extra dependencies (a few bunch of hundreds of megao!)

* [Follow the release](https://github.com/d-j-a-y/ArchiMusik/releases) to install the latest or specific version of ArchiMusik.
* Clone the git - https://github.com/d-j-a-y/ArchiMusik.git - or
* download the [master](https://github.com/d-j-a-y/ArchiMusik/archive/master.zip) for fresh meat.

## Dependencies
___Important___ : Only support OpenCV 3.4 series

### Gnu/Linux
* Python3
* Python3 pip (Debian package: python3-pip)
* [OpenCV](http://opencv.org/), based on opencv 3.4 ! (Debian package: buster is only 3.2! __fixme__)

```
sudo apt-get install python3-pip
```

#### Python3 packages
* [Numpy](https://numpy.org/), scientific computing.
* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.
* [OpenCV](http://opencv.org/)

```
/path/to/python3 -m pip install numpy pyo opencv-python>=3.4.0,<4.0.0 --user --upgrade
```

### Mac OsX -draft-

* Python3 - [python.org](https://www.python.org) -> install -> mac
* Python3 / pip

#### Python3 packages

* [Numpy](https://numpy.org/), scientific computing.
* [OpenCV v3.x for Python](https://opencv.org/)  (3.4.8.29 .... check current version on https://pypi.org/ )
* [Pyo](http://ajaxsoundstudio.com/pyodoc), audio server.

```
/path/to/python3 -m pip install numpy pyo opencv-python>=3.4.0,<4.0.0 --user --upgrade
```

### Others -todo-
