# -*- coding: utf-8 -*-

from qt import *
import logging
import HutchMenuBrick
import CommandMenuBrick
from BlissFramework import Icons


__category__ = 'SOLEIL'

###
### Sample centring brick
###
class SoleilHutchMenuBrick(HutchMenuBrick.HutchMenuBrick):

    def __init__(self, *args):
        HutchMenuBrick.HutchMenuBrick.__init__(self, *args)

        self.sampleCentreBox.hide()

        self.sampleCentreBox = QHBox(self)
        self.buttonsBox=QHBox(self.sampleCentreBox)
        self.buttonsBox.setSpacing(0)
        self.sampleCentreBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.buttonsBox.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        self.layout().addWidget(self.sampleCentreBox)

        self.buttonCentre=HutchMenuBrick.MenuButton(self.buttonsBox,"Centre")
        self.buttonCentre.setMinimumSize(QSize(50,40))
        self.connect(self.buttonCentre,PYSIGNAL('executeCommand'),self.centreSampleClicked)
        self.connect(self.buttonCentre,PYSIGNAL('cancelCommand'),self.cancelCentringClicked)

        self.buttonAccept = QToolButton(self.buttonsBox)
        self.buttonAccept.setUsesTextLabel(True)
        self.buttonAccept.setTextLabel("Save")
        self.buttonAccept.setMinimumSize(QSize(50,40))
        self.buttonAccept.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonAccept.setEnabled(False)
        QObject.connect(self.buttonAccept,SIGNAL('clicked()'),self.acceptClicked)
        self.standardColor=None

        self.buttonReject = QToolButton(self.buttonsBox)
        self.buttonReject.setUsesTextLabel(True)
        self.buttonReject.setTextLabel("Reject")
        self.buttonReject.setMinimumSize(QSize(50,40))
        self.buttonReject.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonReject.setEnabled(False)
        self.buttonReject.hide()
        QObject.connect(self.buttonReject,SIGNAL('clicked()'),self.rejectClicked)

        self.extraCommands=CommandMenuBrick.CommandMenuBrick(self.sampleCentreBox)
        self.extraCommands['showBorder']=False

        self.buttonSnapshot = QToolButton(self.sampleCentreBox)
        self.buttonSnapshot.setUsesTextLabel(True)
        self.buttonSnapshot.setTextLabel("Snapshot")
        self.buttonSnapshot.setMinimumSize(QSize(50,40))
        self.buttonSnapshot.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        QObject.connect(self.buttonSnapshot,SIGNAL('clicked()'),self.saveSnapshot)

        self.buttonBeamPosition = QToolButton(self.sampleCentreBox)
        self.buttonBeamPosition.setUsesTextLabel(True)
        self.buttonBeamPosition.setTextLabel("BeamPosition")
        self.buttonBeamPosition.setMinimumSize(QSize(50,40))
        self.buttonBeamPosition.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonBeamPosition.setPixmap(Icons.load("green_led"))
        QObject.connect(self.buttonBeamPosition, SIGNAL('clicked()'), self.beamPositionCheck)
        
        self.buttonApertureAlign = QToolButton(self.sampleCentreBox)
        self.buttonApertureAlign.setUsesTextLabel(True)
        self.buttonApertureAlign.setTextLabel("ApertureAlign")
        self.buttonApertureAlign.setMinimumSize(QSize(50,40))
        self.buttonApertureAlign.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonApertureAlign.setPixmap(Icons.load("Align"))
        QObject.connect(self.buttonApertureAlign, SIGNAL('clicked()'), self.apertureAlign)
        
    def beamPositionCheck(self):
        self.minidiff.beamPositionCheck()
        
    def apertureAlign(self):
        self.minidiff.apertureAlign()
        
