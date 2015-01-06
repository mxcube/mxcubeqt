# MXCuBE Qt4 - preliminary study

This branch contains MXCuBE written in Qt4. It is a test study to explore the 
possibility to use Qt4 in further development. As it is not possible to use Qt3 
and Qt4 in the same application, new files, containing Qt4 code, have been 
created (prefix Qt4). This is done, because parts of MXCuBE are Qt 
independent (for example Hardware objects).

## This version includes

* GUI builder with possibility to save and load gui
* Hardware repository (tested with TINE control system)
* Test bricks
* Camera brick with mockup hardware object. Camera brick was tested with Lima 
and Prosilica camera. Qub is not used and image is converted with Qt4
* Test Hutch menu brick. If DiffractometerMockup hardware object is used 
then by clicking refresh graphics are initialized
* New GraphicsManager hardware object. It is extended version of ShapeHistory 
hardware object. It stores all graphic objects. As no Qub is used, graphical 
objects are crated as simple QtGui.QGraphicsItems. This version includes 
graphic objects to display beam shape, omega rotation axis, scale and centring 
points. These objects are not fully working, but first study profs the possibility 
to use them (color/size/shape change, dynamic selection e.c.)
* Ui files compatable with Qt4 (also with prefix Qt4)

## Running MXCuBE on Qt4

Once dependencies are satisfied, and the mxcube.gui is present, just run the mxcube
script:

    ./bin/mxcube --hardwareRepository=<directory or host:port>

As it was previously mentioned: it is not possible to run Qt3 and Qt4 in the same application. 
This version of MXCuBE contains a minimum set of files to run the software. There is a 
necessity to discuss, try or find alternative to the current dependencies: 
* PyMca
* Periodic table (could be used from PyMca or created from scratch) 
* Chooch for energy scans
* Graphs 
