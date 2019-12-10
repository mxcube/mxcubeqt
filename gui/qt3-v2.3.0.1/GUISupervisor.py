import logging
import os
import stat
import sys
import cPickle
import time

import qt

from HardwareRepository import HardwareRepository
from BlissFramework import Configuration
from BlissFramework import GUIBuilder
from BlissFramework.Utils import GUIDisplay
from BlissFramework.Utils import PropertyBag
from BlissFramework.BaseComponents import BlissWidget
import Icons
import BlissFramework


LOAD_GUI_EVENT = qt.QEvent.MaxUser


class BlissSplashScreen(qt.QSplashScreen):
    def __init__(self, *args, **kwargs):
        qt.QSplashScreen.__init__(self, *args)

        self.guiName = " "
        self.repaint()

    def mousePressEvent(self, e):
        e.accept()

    def setGUIName(self, name):
        self.guiName = str(name)
        if len(self.guiName) == 0:
            self.guiName = " "

        self.repaint()

    def drawContents(self, painter):
        x0 = 10
        x1 = 218
        y0 = 109
        y1 = 109 + painter.fontMetrics().height()
        pxsize = 14
        painter.font().setPixelSize(pxsize)

        painter.setPen(qt.QPen(qt.Qt.white))

        painter.drawText(
            qt.QRect(qt.QPoint(x0, y0), qt.QPoint(x1, y1)),
            qt.Qt.AlignLeft | qt.Qt.AlignTop,
            "Loading",
        )
        painter.font().setPixelSize(pxsize * 2.5)
        y0 = y1
        y1 += 3 + painter.fontMetrics().height()
        painter.drawText(
            qt.QRect(qt.QPoint(x0, y0), qt.QPoint(x1, y1)),
            qt.Qt.AlignCenter,
            self.guiName,
        )
        painter.font().setPixelSize(pxsize)
        y0 = y1
        y1 += 3 + painter.fontMetrics().height()
        painter.drawText(
            qt.QRect(qt.QPoint(x0, y0), qt.QPoint(x1, y1)),
            qt.Qt.AlignLeft | qt.Qt.AlignBottom,
            "Please wait...",
        )


class GUISupervisor(qt.QWidget):
    def __init__(self, designMode=False, showMaximized=False, noBorder=False):
        qt.QWidget.__init__(self)

        self.launchInDesignMode = designMode
        self.hardwareRepository = HardwareRepository.getHardwareRepository()
        self.showMaximized = showMaximized
        self.noBorder = noBorder
        self.windows = []
        self.splashScreen = BlissSplashScreen(
            Icons.load("splash"), qt.Qt.WDestructiveClose
        )
        self.splashScreen.show()
        self.timestamp = 0

    def loadGUI(self, GUIConfigFile):
        self.configuration = Configuration.Configuration()
        self.GUIConfigFile = GUIConfigFile

        if self.GUIConfigFile:
            if hasattr(self, "splashScreen"):
                self.splashScreen.setGUIName(
                    os.path.splitext(os.path.basename(GUIConfigFile))[0]
                )

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
                except BaseException:
                    logging.getLogger().exception("Cannot open file %s", GUIConfigFile)
                    qt.QMessageBox.warning(
                        self,
                        "Error",
                        "Could not open file %s !" % GUIConfigFile,
                        qt.QMessageBox.Ok,
                    )
                else:
                    #
                    # find mnemonics to speed up loading
                    # (using the 'require' feature from Hardware Repository)
                    #
                    def getMnemonics(items_list):
                        mne_list = []

                        for item in items_list:
                            if "brick" in item:
                                # print item["name"]
                                try:
                                    props = cPickle.loads(item["properties"])
                                except BaseException:
                                    logging.getLogger().exception(
                                        "could not load properties for %s", item["name"]
                                    )
                                else:
                                    item["properties"] = props
                                    """
                                    try:
                                        mne_list.append(props["mnemonic"])
                                    except:
                                        pass
                                    """
                                    try:
                                        for prop in props:
                                            prop_value = prop.getValue()
                                            if isinstance(
                                                prop_value, type("")
                                            ) and prop_value.startswith("/"):
                                                mne_list.append(prop_value)
                                    except BaseException:
                                        logging.exception(
                                            "could not build list of required hardware objects"
                                        )

                                continue

                            mne_list += getMnemonics(item["children"])

                        return mne_list

                    try:
                        raw_config = eval(f.read())

                        mnemonics = getMnemonics(raw_config)

                        # print mnemonics
                        self.hardwareRepository.require(mnemonics)
                    finally:
                        f.close()

                    try:
                        config = Configuration.Configuration(raw_config)
                    except BaseException:
                        logging.getLogger().exception(
                            "Cannot read configuration from file %s", GUIConfigFile
                        )
                        qt.QMessageBox.warning(
                            self,
                            "Error",
                            "Could not read configuration\nfrom file %s"
                            % GUIConfigFile,
                            qt.QMessageBox.Ok,
                        )
                    else:
                        self.configuration = config

                    if len(self.configuration.windows) == 0:
                        self.launchInDesignMode = True

                    if self.launchInDesignMode:
                        self.framework = GUIBuilder.GUIBuilder()

                        qt.qApp.setMainWidget(self.framework)

                        self.framework.filename = GUIConfigFile
                        self.framework.configuration = config
                        self.framework.setCaption("GUI Builder - %s" % GUIConfigFile)
                        self.framework.guiEditorWindow.setConfiguration(config)

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

        self.framework = GUIBuilder.GUIBuilder()

        qt.qApp.setMainWidget(self.framework)

        self.framework.show()

        self.framework.newClicked(self.GUIConfigFile)

        return self.framework

    def reloadGUI(self):
        if (
            qt.QMessageBox.question(
                self,
                "Reload GUI",
                "Are you sure you want to reload the GUI ?\nThis will stop the current application and restart it.",
                qt.QMessageBox.Yes,
                qt.QMessageBox.No,
                qt.QMessageBox.Cancel,
            )
            == qt.QMessageBox.Yes
        ):
            self.finalize()

            win0 = self.windows[0]
            for window in self.windows[1:]:
                window.close(True)
            self.windows = []

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
        self.windows = GUIDisplay.display(config, noBorder=self.noBorder)

        main_window = None
        if len(self.windows) > 0:
            main_window = self.windows[0]
            main_window.configuration = config
            qt.qApp.setMainWidget(main_window)

            if self.noBorder:
                main_window.move(0, 0)
                w = qt.qApp.desktop().width()
                h = qt.qApp.desktop().height()
                main_window.resize(qt.QSize(w, h))

            #
            # make connections
            #
            widgets_dict = dict(
                [
                    (callable(w.name) and w.name() or None, w)
                    for w in qt.QApplication.allWidgets()
                ]
            )

            def make_connections(items_list):
                for item in items_list:
                    try:
                        sender = widgets_dict[item["name"]]
                    except KeyError:
                        logging.getLogger().error(
                            "Could not find receiver widget %s", item["name"]
                        )
                    else:
                        for connection in item["connections"]:
                            _receiver = (
                                connection["receiver"] or connection["receiverWindow"]
                            )
                            try:
                                receiver = widgets_dict[_receiver]
                            except KeyError:
                                logging.getLogger().error(
                                    "Could not find receiver widget %s", _receiver
                                )
                            else:
                                try:
                                    slot = getattr(receiver, connection["slot"])
                                except AttributeError:
                                    logging.getLogger().error(
                                        "No slot '%s' in receiver %s",
                                        connection["slot"],
                                        _receiver,
                                    )
                                else:
                                    # print "connecting %s to slot %s on signal %s" % (sender, slot, connection["signal"])
                                    sender.connect(
                                        sender, qt.PYSIGNAL(connection["signal"]), slot
                                    )
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
                window._fontSizeAccel = qt.QAccel(window)
                window._fontSizeAccel.insertItem(qt.Qt.CTRL + qt.Qt.Key_Minus, 1)
                window._fontSizeAccel.insertItem(qt.Qt.CTRL + qt.Qt.Key_Plus, 2)
                window._fontSizeAccel.insertItem(qt.Qt.CTRL + qt.Qt.Key_Asterisk, 0)
                window._whatsThisAccel = qt.QAccel(window)
                window._whatsThisAccel.insertItem(qt.Qt.Key_F1)
                window._reloadAccel = qt.QAccel(window)
                window._reloadAccel.insertItem(qt.Qt.CTRL + qt.Qt.SHIFT + qt.Qt.Key_F5)

                window._splitterPositionAccel = qt.QAccel(window)
                for key in [qt.Qt.Key_F9, qt.Qt.Key_F10, qt.Qt.Key_F11, qt.Qt.Key_F12]:
                    window._splitterPositionAccel.insertItem(
                        qt.Qt.SHIFT + key, qt.Qt.SHIFT + key
                    )
                    window._splitterPositionAccel.insertItem(
                        qt.Qt.CTRL + key, qt.Qt.CTRL + key
                    )
                    window._splitterPositionAccel.insertItem(key, key)

                qt.QObject.connect(
                    window._splitterPositionAccel,
                    qt.SIGNAL("activated(int)"),
                    self.saveOrReloadSize,
                )
                qt.QObject.connect(
                    window._fontSizeAccel,
                    qt.SIGNAL("activated(int)"),
                    self.changeFontSize,
                )
                qt.QObject.connect(
                    window._whatsThisAccel,
                    qt.SIGNAL("activated(int)"),
                    BlissWidget.updateWhatsThis,
                )
                qt.QObject.connect(
                    window._reloadAccel, qt.SIGNAL("activated(int)"), self.reloadGUI
                )

                if window._show:
                    window.show()

        if BlissWidget._menuBar:
            BlissWidget._menuBar.setExpertMode(False)

        return main_window

    def saveOrReloadSize(self, key):
        if key & (qt.Qt.SHIFT | qt.Qt.CTRL):
            key &= ~(qt.Qt.SHIFT | qt.Qt.CTRL)
            keyname = "F%d" % ((key - qt.Qt.Key_F9) + 9)
            self.saveSize("_%d" % key)
            qt.QMessageBox.information(
                self,
                "Position and size",
                "This configuration is saved on key %s" % keyname,
                qt.QMessageBox.Default,
            )
        else:
            for display in self.windows:
                window = self.configuration.windows[str(display.name())]
                GUIDisplay.restoreSizes(
                    self.configuration,
                    window,
                    display,
                    configurationSuffix="_%d" % key,
                    moveWindowFlag=False,
                )

    def changeFontSize(self, mode):
        widgets_dict = dict(
            [
                (callable(w.name) and w.name() or None, w)
                for w in qt.QApplication.allWidgets()
            ]
        )

        def setFontSize(item):
            if mode == 1:
                i = -1
            elif mode == 2:
                i = 1
            else:
                i = 0

            if self.configuration.isBrick(item):
                if i == 0:
                    item.brick["fontSize"] = 11
                else:
                    item.brick["fontSize"] = int(item.brick["fontSize"]) + i
            else:
                prop = item.properties.properties.get("fontSize", None)
                if prop is not None:
                    if i == 0:
                        prop.setValue(11)
                    else:
                        prop.setValue(prop.getValue() + i)
                    w = widgets_dict[item.name]
                    f = w.font()
                    f.setPointSize(prop.getValue())
                    w.setFont(f)

        [
            setFontSize(child)
            for child in sum(
                [
                    self.configuration.findAllChildren(window)
                    for window in self.configuration.windows_list
                ],
                [],
            )
        ]

    def finalize(self):
        BlissWidget.setRunMode(False)  # call .stop() for each brick

        self.hardwareRepository.close()

        qt.qApp.sendPostedEvents()
        qt.qApp.processEvents()

        self.saveSize()

    def saveSize(self, configurationSuffix=""):
        if not self.launchInDesignMode:
            # save windows positions
            for window in self.windows:
                window_cfg = self.configuration.windows[str(window.name())]

                window_cfg["properties"].getProperty(
                    "x%s" % configurationSuffix
                ).setValue(window.x())
                window_cfg["properties"].getProperty(
                    "y%s" % configurationSuffix
                ).setValue(window.y())
                window_cfg["properties"].getProperty(
                    "w%s" % configurationSuffix
                ).setValue(window.width())
                window_cfg["properties"].getProperty(
                    "h%s" % configurationSuffix
                ).setValue(window.height())

                splitters = self.configuration.findAllChildrenWType(
                    "splitter", window_cfg
                )
                if len(splitters):
                    for sw in window.queryList("QSplitter"):
                        try:
                            splitter = splitters[sw.name()]
                            splitter["properties"].getProperty(
                                "sizes%s" % configurationSuffix
                            ).setValue(sw.sizes())
                        except KeyError:
                            continue

            # save GUI file only if it is not more recent
            # (to prevent overwritting file if it has been modified in the meantime)
            if self.GUIConfigFile and os.path.exists(self.GUIConfigFile):
                ts = os.stat(self.GUIConfigFile)[stat.ST_MTIME]
                if ts <= self.timestamp:
                    if configurationSuffix == "":
                        logging.getLogger().debug(
                            "saving configuration file to keep windows pos. and sizes"
                        )
                    self.configuration.save(self.GUIConfigFile)

    def finishInit(self, GUIConfigFile):
        while True:
            try:
                self.hardwareRepository.connect()
            except BaseException:
                logging.getLogger().exception(
                    "Timeout while trying to connect to Hardware Repository server."
                )

                message = (
                    """Timeout while connecting to Hardware Repository server ;
                make sure the Hardware Repository Server is running on host %s."""
                    % str(self.hardwareRepository.serverAddress).split(":")[0]
                )
                a = qt.QMessageBox.warning(
                    None,
                    "Cannot connect to Hardware Repository",
                    message,
                    qt.QMessageBox.Retry,
                    qt.QMessageBox.Cancel,
                    qt.QMessageBox.NoButton,
                )
                if a == qt.QMessageBox.Cancel:
                    logging.getLogger().warning(
                        "Gave up trying to connect to Hardware Repository server."
                    )
                    break
            else:
                logging.getLogger().info(
                    "Connected to Hardware Repository server %s",
                    self.hardwareRepository.serverAddress,
                )
                break

        try:
            main_widget = None

            try:
                main_widget = self.loadGUI(GUIConfigFile)
            finally:
                if main_widget:
                    self.splashScreen.finish(main_widget)
                del self.splashScreen
        except BaseException:
            logging.getLogger().exception("exception while loading GUI file")
            qt.qApp.exit()

    def customEvent(self, event):
        self.finishInit(event.data())
