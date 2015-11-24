#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import time
import stat
import sys
import cPickle
import logging

from PyQt4 import QtCore
from PyQt4 import QtGui

from HardwareRepository import HardwareRepository
from BlissFramework import Qt4_Configuration
from BlissFramework import Qt4_GUIBuilder
from BlissFramework.Utils import Qt4_GUIDisplay
from BlissFramework.Utils import PropertyBag
from BlissFramework.Qt4_BaseComponents import BlissWidget
import Qt4_Icons
import BlissFramework


LOAD_GUI_EVENT = QtCore.QEvent.MaxUser


class BlissSplashScreen(QtGui.QSplashScreen):
    def __init__(self, pixmap):
        QtGui.QSplashScreen.__init__(self, pixmap)

        self.guiName = ' '
        self.repaint()
        
    def mousePressEvent(self,e):
        e.accept()

    def setGUIName(self, name):
        self.guiName = str(name)
        if len(self.guiName) == 0:
            self.guiName = ' '
            
        self.repaint()


    def drawContents(self, painter):
        x0 = 10
        x1 = 218
        y0 = 109
        y1 = 109 + painter.fontMetrics().height()
        pxsize = 14
        painter.font().setPixelSize(pxsize)
    
        painter.setPen(QtGui.QPen(QtCore.Qt.white))

        painter.drawText(QtCore.QRect(QtCore.QPoint(x0, y0), QtCore.QPoint(x1, y1)), 
                                      QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, 'Loading')
        painter.font().setPixelSize(pxsize*2.5)
        y0 = y1
        y1 += 3 + painter.fontMetrics().height()
        painter.drawText(QtCore.QRect(QtCore.QPoint(x0, y0), QtCore.QPoint(x1, y1)), 
                                      QtCore.Qt.AlignCenter, self.guiName)
        painter.font().setPixelSize(pxsize)
        y0 = y1
        y1 += 3 + painter.fontMetrics().height()
        painter.drawText(QtCore.QRect(QtCore.QPoint(x0, y0), QtCore.QPoint(x1, y1)), 
                         QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom, 'Please wait...')


class GUISupervisor(QtGui.QWidget):
    def __init__(self, designMode = False, showMaximized=False, noBorder=False):
        QtGui.QWidget.__init__(self)

        self.launchInDesignMode = designMode
        self.hardwareRepository = HardwareRepository.HardwareRepository()
        self.showMaximized = showMaximized
        self.noBorder = noBorder
        self.windows = []
        #self.splashScreen = BlissSplashScreen(Qt4_Icons.load('splash'), QtCore.Qt.WA_DeleteOnClose)
        self.splashScreen = BlissSplashScreen(Qt4_Icons.load('splash'))
        self.splashScreen.show()
        self.timestamp = 0

    def loadGUI(self, GUIConfigFile):
        self.configuration = Qt4_Configuration.Configuration()
        self.GUIConfigFile = GUIConfigFile

        if self.GUIConfigFile:
            if hasattr(self, "splashScreen"):
                self.splashScreen.setGUIName(os.path.splitext(os.path.basename(GUIConfigFile))[0])
        
            if os.path.exists(GUIConfigFile):
                filestat = os.stat(GUIConfigFile)
                self.timestamp = filestat[stat.ST_MTIME]

                if filestat[stat.ST_SIZE] == 0:
                    # empty file
                    return self.newGUI()

                #
                # open existing file
                #
                try:
                    f = open(GUIConfigFile)
                except:
                    logging.getLogger().exception("Cannot open file %s", GUIConfigFile)
                    QtGui.QMessageBox.warning(self, "Error", "Could not open file %s !" % GUIConfigFile, QtGui.QMessageBox.Ok)
                else:
                    #
                    # find mnemonics to speed up loading
                    # (using the 'require' feature from Hardware Repository)
                    #
                    def getMnemonics(items_list):
                        mne_list = []

                        for item in items_list:
                            if "brick" in item:
                                try:
                                    props = cPickle.loads(item["properties"])
                                except:
                                    logging.getLogger().exception("could not load properties for %s", item["name"])
                                else:
                                    item["properties"]=props
                                    """
                                    try:
                                        mne_list.append(props["mnemonic"])
                                    except:
                                        pass
                                    """
                                    try:
                                      for prop in props:
                                        prop_value = prop.getValue()
                                        if type(prop_value)==type('') and prop_value.startswith("/"):
                                          mne_list.append(prop_value)
                                    except:
                                      logging.exception("could not build list of required hardware objects")

                                continue

                            mne_list += getMnemonics(item["children"])

                        return mne_list

                    raw_config = eval(f.read())
                    mnemonics = getMnemonics(raw_config)
                    self.hardwareRepository.require(mnemonics)
                    f.close()

                    try:
                        config = Qt4_Configuration.Configuration(raw_config)
                    except:
                        logging.getLogger().exception("Cannot read configuration from file %s", GUIConfigFile)
                        QtGui.QMessageBox.warning(self, "Error", "Could not read configuration\nfrom file %s" % GUIConfigFile, QtGui.QMessageBox.Ok)    
                    else:
                        self.configuration = config

                    if len(self.configuration.windows) == 0:
                        self.launchInDesignMode = True
                                        
                    if self.launchInDesignMode:
                        self.framework = Qt4_GUIBuilder.GUIBuilder()

                        QtGui.QApplication.setActiveWindow(self.framework)
                         
                        self.framework.filename = GUIConfigFile
                        self.framework.configuration = config
                        self.framework.setWindowTitle("GUI Builder - %s" % GUIConfigFile)
                        self.framework.gui_editor_window.set_configuration(config)
                        self.framework.gui_editor_window.draw_window_preview()  
                        self.framework.show()

                        return self.framework
                    else:
                        main_window = self.execute(self.configuration)
                        return main_window

        return self.newGUI()

            
    def newGUI(self):
        #
        # new GUI
        #
        self.timestamp = 0
        self.launchInDesignMode = True

        self.framework = Qt4_GUIBuilder.GUIBuilder()

        #tGui.QApplication.setMainWidget(self.framework)
        QtGui.QApplication.setActiveWindow(self.framework)

        self.framework.show()
            
        self.framework.new_clicked(self.GUIConfigFile)
        
        return self.framework
             

    def reloadGUI(self):
        if (QtGui.QMessageBox.question(self,
                                   "Reload GUI",
                                   "Are you sure you want to reload the GUI ?\nThis will stop the current application and restart it.",
                                   QtGui.QMessageBox.Yes,
                                   QtGui.QMessageBox.No,
                                   QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Yes):
            self.finalize()

            win0 = self.windows[0]
            for window in self.windows[1:]:
                window.close(True)
            self.windows=[]

            # for first window, delete all children one by one
            # (instead of deleting the window itself : indeed it's causing
            # a stop of the whole app. because of "last window closed" signal)
            for child in win0.children():
                if hasattr(child, "close"):
                    child.close(True)

            self.execute(self.configuration)

            # now let's destroy the window !
            win0.close(True)
            
        
    def execute(self, config):
        #
        # start in execution mode
        #
        self.windows = Qt4_GUIDisplay.display(config, noBorder=self.noBorder)
        main_window = None
        if len(self.windows) > 0:
            main_window = self.windows[0]
            main_window.configuration = config
            QtGui.QApplication.setActiveWindow(main_window)
            if self.noBorder:
                main_window.move(0, 0)
                w = QtGui.QApplication.desktop().width()
                h = QtGui.QApplicaitoj.desktop().height()
                main_window.resize(QtCore.QSize(w,h))
                
            #
            # make connections
            #        
            widgets_dict = dict([(callable(w.objectName) and str(w.objectName()) or None, w) for w in QtGui.QApplication.allWidgets()])

            def make_connections(items_list): 
                for item in items_list:
                    try:
                        sender = widgets_dict[item["name"]]
                    except KeyError:
                        logging.getLogger().error("Could not find receiver widget %s", item["name"])
                    else:
                        for connection in item["connections"]:
                            _receiver = connection["receiver"] or connection["receiverWindow"]
                            try:
                                receiver = widgets_dict[_receiver]
                            except KeyError:
                                logging.getLogger().error("Could not find receiver widget %s", _receiver)
                            else:
                                try:
                                    slot = getattr(receiver, connection["slot"])
                                except AttributeError:
                                    logging.getLogger().error("No slot '%s' in receiver %s", connection["slot"], _receiver)
                                else:
                                    sender.connect(sender, QtCore.SIGNAL(connection["signal"]), slot)
                    make_connections(item["children"])
                                        
            make_connections(config.windows_list)

            #
            # set run mode for every brick
            #
            BlissWidget.setRunMode(True)

            if self.showMaximized:
                main_window.showMaximized()
            else:
                main_window.show()

            for window in self.windows:
                """window._fontSizeMinusKey = QtGui.QShortcut(window)
                window._fontSizeMinusKey.setKey(QtCore.Qt.CTRL + QtCore.Qt.Key_Minus)
                window._fontSizePlusKey = QtGui.QShortcut(window)
                window._fontSizePlusKey.setKey(QtCore.Qt.CTRL + QtCore.Qt.Key_Plus)
                window._fontSizeAsteriskKey = QtGui.QShortcut(window)
                window._fontSizeAsteriskKey.setKey(QtCore.Qt.CTRL + QtCore.Qt.Key_Asterisk)
                window._whatsThisKey = QtGui.QShortcut(window)
                window._whatsThisKey.setKey(QtCore.Qt.Key_F1)
                window._reloadKey = QtGui.QShortcut(window)
                window._reloadKey.setKey(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_F5)

                window._splitterPositionAccel = QtGui.QShortcut(window)
                for key in [QtCore.Qt.Key_F9, QtCore.Qt.Key_F10, QtCore.Qt.Key_F11, QtCore.Qt.Key_F12] :
                    window._splitterPositionAccel.setKey(QtCore.Qt.SHIFT+key)
                    window._splitterPositionAccel.setKey(QtCore.Qt.CTRL+key)
                    window._splitterPositionAccel.setKey(key)

                QtCore.QObject.connect(window._splitterPositionAccel, QtCore.SIGNAL('activated()'),self.saveOrReloadSize)
                QtCore.QObject.connect(window._fontSizeMinusKey, QtCore.SIGNAL('activated()'), self.changeFontSize)
                QtCore.QObject.connect(window._whatsThisAccel, QtCore.SIGNAL('activated()'), BlissWidget.updateWhatsThis)
                QtCore.QObject.connect(window._reloadAccel, QtCore.SIGNAL('activated()'), self.reloadGUI)"""

                if window._show:
                    window.show()

        if BlissWidget._menuBar:
            BlissWidget._menuBar.set_exp_mode(False)
        
        return main_window
                
    def saveOrReloadSize(self,key) :
        if key & (QtCore.Qt.SHIFT|QtCore.Qt.CTRL) :
            key &= ~(QtCore.Qt.SHIFT|QtCore.Qt.CTRL)
            keyname = 'F%d' % ((key - qt.Qt.Key_F9) + 9)
            self.saveSize('_%d' % key)
            QtGui.QMessageBox.information(self,'Position and size',
                                          'This configuration is saved on key %s' % 
                                          keyname,
                                          QtGui.QMessageBox.Default)
        else:
            for display in self.windows:
                window = self.configuration.windows[str(display.name())]
                Qt4_GUIDisplay.restoreSizes(self.configuration,window,display,configurationSuffix = '_%d' % key,moveWindowFlag = False)
                
    def changeFontSize(self, mode):
        widgets_dict = dict([(callable(w.name) and w.name() or None, w) for w in qt.QApplication.allWidgets()])
        
        def setFontSize(item):
            if mode == 1:
                i = -1
            elif mode == 2:
                i = 1
            else:
                i = 0
                
            if self.configuration.isBrick(item):
                if i == 0:
                    item.brick['fontSize'] = 9
                else:
                    item.brick['fontSize']=int(item.brick['fontSize'])+i
            else:
                prop = item.properties.properties.get('fontSize', None)
                if prop is not None:
                    if i == 0:
                        prop.setValue(9)
                    else:
                        prop.setValue(prop.getValue()+i)
                    w = widgets_dict[item.name]
                    f = w.font()
                    f.setPointSize(prop.getValue())
                    w.setFont(f)

        [setFontSize(child) for child in sum([self.configuration.findAllChildren(window) for window in self.configuration.windows_list], [])]


    def finalize(self):
        BlissWidget.setRunMode(False) # call .stop() for each brick

        self.hardwareRepository.close()

        QtGui.QApplication.sendPostedEvents()
        QtGui.QApplication.processEvents()

        self.saveSize()
        
    def saveSize(self,configurationSuffix = '') :
        if not self.launchInDesignMode:
            # save windows positions
            for window in self.windows:
                window_cfg = self.configuration.windows[str(window.objectName())]

                window_cfg["properties"].getProperty("x%s" % configurationSuffix).setValue(window.x())
                window_cfg["properties"].getProperty("y%s" % configurationSuffix).setValue(window.y())
                window_cfg["properties"].getProperty("w%s" % configurationSuffix).setValue(window.width())
                window_cfg["properties"].getProperty("h%s" % configurationSuffix).setValue(window.height())

                splitters =  self.configuration.findAllChildrenWType("splitter", window_cfg)
                if len(splitters):
                    for sw in window.queryList("QSplitter"):
                        try:
                            splitter = splitters[sw.name()]
                            splitter["properties"].getProperty("sizes%s" % configurationSuffix).setValue(sw.sizes())
                        except KeyError:
                            continue
                        
            # save GUI file only if it is not more recent
            # (to prevent overwritting file if it has been modified in the meantime)
            if self.GUIConfigFile and os.path.exists(self.GUIConfigFile):
                ts = os.stat(self.GUIConfigFile)[stat.ST_MTIME]
                if ts <= self.timestamp:
                    if configurationSuffix == '':
                        logging.getLogger().debug("saving configuration file to keep windows pos. and sizes")
                    self.configuration.save(self.GUIConfigFile)


    def finishInit(self, GUIConfigFile):
        while True:
            try:
                self.hardwareRepository.connect()
            except:
                logging.getLogger().exception('Timeout while trying to connect to Hardware Repository server.')
                
                message = """Timeout while connecting to Hardware Repository server ;
                make sure the Hardware Repository Server is running on host %s.""" % str(self.hardwareRepository.serverAddress).split(':')[0]
                a = qt.QMessageBox.warning(None, 'Cannot connect to Hardware Repository', message, qt.QMessageBox.Retry, qt.QMessageBox.Cancel, qt.QMessageBox.NoButton)
                if a == qt.QMessageBox.Cancel:
                    logging.getLogger().warning('Gave up trying to connect to Hardware Repository server.')
                    break
            else:
                logging.getLogger().info('Connected to Hardware Repository server %s', self.hardwareRepository.serverAddress)
                break

        try:
            main_widget = None
            main_widget=self.loadGUI(GUIConfigFile)
            if main_widget:
                self.splashScreen.finish(main_widget)
            del self.splashScreen
        except:
            logging.getLogger().exception("exception while loading GUI file")
            QtGui.QApplication.exit()

    def customEvent(self, event):
        self.finishInit(event.data)
