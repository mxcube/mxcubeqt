from qt import *

from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons

__category__ = 'Synoptic'

class SynopticBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        #
        # add properties
        #
        self.addProperty('iconFile', 'file', 'Images (*.bmp *.gif *.jpg *.png *.xpm)')
        self.addProperty('hint', 'string', '')
        self.addProperty('showSynoptic', 'boolean', True)
        self.addProperty('showBorder', 'boolean', False)
        self.addProperty('showTitle', 'boolean', True)
        self.addProperty('alignment', 'combo', ('top', 'bottom', 'center'), 'top')
        self.addProperty('title', 'string', '')

        #
        # define BRICK signals/slots
        #
        self.defineSignal('synopticClicked', ()) #signal with no arguments

        #
        # GUI components
        #
        self.__topPanel = QFrame(self)
        self.containerBox = QVBox(self.__topPanel)
        self.__lblTitle = QLabel(self.__topPanel)
        self.__lblTitle.setAutoResize(True)
        self.__synoptic = QLabel(self.__topPanel)

        #
        # layout
        #
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        QVBoxLayout(self, 0, 0)
        self.layout().addWidget(self.__topPanel, 0, Qt.AlignTop | Qt.AlignHCenter)

        QVBoxLayout(self.__topPanel, 2, 2) #margin, spacing
        self.__topPanel.layout().addWidget(self.__lblTitle, 0, Qt.AlignTop | Qt.AlignHCenter)
        self.__topPanel.layout().addWidget(self.__synoptic, 0, Qt.AlignTop | Qt.AlignHCenter)
        self.__topPanel.layout().addWidget(self.containerBox, 0, Qt.AlignTop | Qt.AlignHCenter)
            

    def setTitle(self, title):
        self['title'] = str(title)


    def run(self):
        self.__synoptic.installEventFilter(self)


    def eventFilter(self, o, e):
        if o is not None and e is not None:
            if e.type() == QEvent.MouseButtonRelease:
                self.emit(PYSIGNAL('synopticClicked'), ())
        return False


    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'iconFile':
            img = QPixmap()
            if not img.load(str(newValue)):
                img = QPixmap(Icons.load('esrf_logo'))
            self.__synoptic.setPixmap(img)
        elif propertyName == 'showSynoptic':
            if newValue:
                self.__synoptic.show()
            else:
                self.__synoptic.hide()
            self.adjustSize()
            self.updateGeometry()
        elif propertyName == 'showBorder':
            if newValue:
                self.layout().setMargin(5)
                self.__topPanel.setFrameStyle(QFrame.GroupBoxPanel | QFrame.Raised)
                self.__topPanel.setMidLineWidth(0)
                self.__topPanel.setLineWidth(1)
            else:
                self.layout().setMargin(0)
                self.__topPanel.setFrameStyle(QFrame.NoFrame)
                self.__topPanel.setMidLineWidth(0)
                self.__topPanel.setLineWidth(0)
        elif propertyName == 'title':
            self.__lblTitle.setText(str(newValue))
        elif propertyName == 'showTitle':
            if newValue:
                self.__lblTitle.show()
            else:
                self.__lblTitle.hide()
            self.adjustSize()
            self.updateGeometry()
        elif propertyName == 'alignment':
            if newValue == 'top':
                self.layout().remove(self.__topPanel)
                self.layout().addWidget(self.__topPanel, 0, Qt.AlignTop | Qt.AlignHCenter)
            elif newValue == 'bottom':
                self.layout().remove(self.__topPanel)
                self.layout().addWidget(self.__topPanel, 0, Qt.AlignBottom | Qt.AlignHCenter)
            else:
                self.layout().remove(self.__topPanel)
                self.layout().addWidget(self.__topPanel, 0, Qt.AlignCenter)
        elif propertyName == 'hint':
            QToolTip.add(self, newValue)
