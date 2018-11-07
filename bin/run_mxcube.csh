#!/bin/csh -f

#export MXCUBE_GUI_FILE=/home/urbschaj/dev/projects/mxcube-master/ExampleFiles/Qt4_example_mxcube.gui

#python /home/urbschaj/dev/projects/mxcube-master/bin/mxcube \
#--hardwareRepository=/home/urbschaj/dev/projects/mxcube-master/ExampleFiles/HardwareObjects.xml \
#--hardwareObjectsDirs=/home/urbschaj/dev/projects/mxcube-master/HardwareObjects/sample_changer --pyqt4 $argv

python /home/urbschaj/dev/projects/mxcube-master/bin/mxcube \
--hardwareRepository=/home/urbschaj/dev/projects/mxcube-master/ExampleFiles/HardwareObjects.xml/desy_p11 \
--hardwareObjectsDirs=/home/urbschaj/dev/projects/mxcube-master/HardwareRepository/HardwareObjects/DESY/ \
--pyqt4 $argv
