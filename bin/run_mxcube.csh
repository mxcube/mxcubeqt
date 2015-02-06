#!/bin/csh -f
setenv PYTHONPATH "/home/karpics/beamlinesw/release/lib/python2.7/site-packages:/home/karpics/software/library/linux/Lima/install"
setenv LD_LIBRARY_PATH "/home/karpics/beamlinesw/release/lib:/home/karpics/software/library/linux/Lima/install/Lima/lib"

limit coredumpsize unlimited

/home/karpics/mxcubeQt4/bin/mxcube --hardwareRepository=/home/karpics/mxcubeQt4/ExampleFiles/HardwareObjects.xml $argv

#/home/karpics/mxcubeQt4/bin/mxcube --hardwareRepository=/home/karpics/beamlinesw/trunk/beamline/simulation/app/mxCuBE2/HardwareObjects.xml --hardwareObjectsDirs=/home/karpics/beamlinesw/trunk/app/mxCuBE2/HardwareObjects $argv
