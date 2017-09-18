#!/usr/bin/env bash

#  DESCRIPTION
#  --------------
#  Generic startup script for any mxcube application using Qt4
#

#  ENVIRONMENT
#  -----------
#  The following environment variables are needed
#
#    INSTITUTE - ALBA, SOLEIL,...
#    MXCUBE_ROOT - directory where mxcube is installed (git clone destination)
#    MXCUBE_XML_PATH - directory for the HwObj xml files
#    MXCUBE_GUI_PATH - directory for the gui file(s)
#    MXCUBE_LOG_PATH - directory for storing the logs
#
#  You can create a .mxcube.rc file under $HOME's user folder using the
#  mxcube.rc template.
#

#  EXAMPLE of .mxcube.rc file
#  --------------------------
#  |#!/usr/bin/env bash
#  |
#  | export INSTITUTE=ALBA
#  | export MXCUBE_ROOT=/MXCuBE/mxcube
#  | export MXCUBE_XML_PATH=$MXCUBE_ROOT/../HardwareObjects.xml
#  | export MXCUBE_GUI_PATH=$MXCUBE_ROOT/../guis
#  | export MXCUBE_LOG_PATH=$MXCUBE_ROOT/../log/
#  |
#  | # include other local exports here.
#  |
#

#  RUNNING MXCUBE
#  -----------------
#  Setup the environment variables properly.
#
#  To run mxcube2 (or any other application <app_name>)
#     1) Copy the GUI file to $MXCUBE_GUI_PATH as <app_name>.gui
#     2) Execute <app_name>
#
#  If no file matching the <app_name>.gui is found, the example mxcube gui is started.
#
##########################################################################

# Define MXCuBE defaults
MXCUBE_BRICKS_PATH=$MXCUBE_ROOT/BlissFramework/Bricks # (This could be exported from python script)
MXCUBE_HWOBJS_PATH=$MXCUBE_ROOT/HardwareRepository/HardwareObjects # (This could be exported from python script)

GUI_FILE=$MXCUBE_GUI_PATH/$APP_NAME.yml
XML_PATH=$MXCUBE_XML_PATH
LOG_PREFIX=$MXCUBE_LOG_PATH/$APP_NAME-$USER

export PYTHONPATH=$PYTHONPATH:$MXCUBE_ROOT
export PYTHONPATH=$PYTHONPATH:$MXCUBE_BRICKS_PATH
export PYTHONPATH=$PYTHONPATH:$MXCUBE_HWOBJS_PATH

if [ ! -z "$INSTITUTE" ]; then
    export PYTHONPATH=$PYTHONPATH:$MXCUBE_BRICKS_PATH/$INSTITUTE
    export PYTHONPATH=$PYTHONPATH:$MXCUBE_HWOBJS_PATH/$INSTITUTE
fi

if [ -z "$USER" ]; then
    USER=UNKWOWN
fi

if [ ! -f $GUI_FILE ]; then
    echo "GUI file <$GUI_FILE> does not exists. Exiting!"
    exit -1
fi

echo "######################################################################"
echo " user:        $USER"
echo " institute:   $INSTITUTE"
echo " MXCUBE_ROOT: $MXCUBE_ROOT"
echo " gui file:    $GUI_FILE"
echo " log files:   $LOG_PREFIX (log/out/err)"
echo "######################################################################"

# Running the application
$MXCUBE_ROOT/bin/Qt4_startGUI --hardwareRepository=$XML_PATH \
			      --bricksDir=$MXCUBE_BRICKS_PATH \
			      --logFile=$LOG_PREFIX.log \
			      $GUI_FILE $* > $LOG_PREFIX.out 2> $LOG_PREFIX.err
