#!/usr/bin/env bash

# Library versions
PYQT_VERSION=4.9.5
SIP_VERSION=4.14.1


curl -L -O http://sourceforge.net/projects/pyqt/files/sip/sip-$SIP_VERSION/sip-$SIP_VERSION.tar.gz
tar -xf sip-$SIP_VERSION.tar.gz
cd sip-$SIP_VERSION
python configure.py
make -j 2 --silent
sudo make install

cd ..
curl -L -O http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-$PYQT_VERSION/PyQt-x11-gpl-$PYQT_VERSION.tar.gz
tar -xf PyQt-x11-gpl-$PYQT_VERSION.tar.gz
cd PyQt-x11-gpl-$PYQT_VERSION
python configure.py --confirm-license
make -j 2 --silent
sudo make install
cd ..
