# MXCuBE web application - preliminary study

This branch contains an embryo MXCuBE web server, embedding
a MXCuBE application. The code was first demonstrated at the
3rd MXCuBE meeting in April, 2013. It has been updated on
the 7th October 2014 after the MXCuBE 3 study meeting at
ALBA.

## Installing

First you need to make sure requirements are satisfied.
The easiest way is to use the "requirements.txt" file with
[pip](https://pip.readthedocs.org/en/latest/):

    pip install -r requirements.txt

If your Linux distribution doesn't allow you to have those
dependencies installed, use [pythonbrew](https://github.com/utahta/pythonbrew) to make your own
Python environment. Follow instructions on this [page](https://pypi.python.org/pypi/pythonbrew/),
then install Python 2.7.7 (for example):

    pythonbrew install 2.7.7
    
Also install pip for this Python 2.7.7 install:
 
    pythonbrew use 2.7.7
    
    curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    python get-pip.py
    

Once Python environment is ready, let's clone the repository:
    
    capek:~/local % git clone git://github.com/mxcube/mxcube -b web ./mxcube-web
    Cloning into ./mxcube-web...
    remote: Counting objects: 8698, done.
    remote: Compressing objects: 100% (50/50), done.
    remote: Total 8698 (delta 15), reused 0 (delta 0)
    Receiving objects: 100% (8698/8698), 4.60 MiB | 1.64 MiB/s, done.
    Resolving deltas: 100% (5822/5822), done.
    
And initialize the HardwareRepository submodule:
    
    capek:~/local % cd mxcube-web/
    capek:~/local/mxcube-web % git submodule init
    Submodule 'HardwareRepository' (git://github.com/mxcube/HardwareRepository) registered for path 'HardwareRepository'
    capek:~/local/mxcube-web % git submodule update
    Cloning into HardwareRepository...
    remote: Counting objects: 1085, done.
    remote: Total 1085 (delta 0), reused 0 (delta 0)
    Receiving objects: 100% (1085/1085), 238.94 KiB | 242 KiB/s, done.
    Resolving deltas: 100% (631/631), done.
    Submodule path 'HardwareRepository': checked out '68ccb739a9817451a84a402f7c91c8882285e64c'
    capek:~/local/mxcube-web %

And you're done !

## How to run it

*disclaimer: code will only work with Firefox >= 19 and Chrome. Safari is not tested. IE is **not supported.***

Once branch is checked out and additional dependencies are satisfied (see above), you can
immediately start the MXCuBE server using some defaults XML files and mockup objects that
are shipped with the code:

    ./bin/mxcube-server ExampleFiles/HardwareObjects.xml
    
Then, go to the [http://localhost:8080](http://localhost:8080) URL within your web browser.

