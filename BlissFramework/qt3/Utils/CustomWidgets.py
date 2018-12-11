#$Id: CustomWidgets.py,v 1.1 2004/09/14 12:23:44 guijarro Exp $
from qt import *
from BlissFramework import Icons
import collections

class QLineEditWithOkCancel(QHBox):
    def __init__(self, parent, text = ''):
        QHBox.__init__(self, parent)

        self.setSpacing(5)

        self.txtControl = QLineEdit(self)
        self.buttonBox = QHBox(self)
        self.cmdOK = QPushButton(self.buttonBox)
        size = self.txtControl.height() * 0.8
        buttonSize = QSize(size, size)
        self.cmdOK.setMaximumSize(buttonSize)
        self.cmdCancel = QPushButton(self.buttonBox)
        self.cmdCancel.setMaximumSize(buttonSize)
        self.cmdOK.setPixmap(Icons.load('button_ok_small')) #QPixmap(Icons.okXPM))
        self.cmdCancel.setPixmap(Icons.load('button_cancel_small')) #QPixmap(Icons.cancelXPM))
        self.connect(self.cmdOK, SIGNAL('clicked()'), self.cmdOKClicked)
        self.connect(self.cmdCancel, SIGNAL('clicked()'), self.cmdCancelClicked)
        self.connect(self.txtControl, SIGNAL('returnPressed()'), self.cmdOKClicked)
        self.connect(self.txtControl, SIGNAL('textChanged(const QString &)'), self.textChanged)
        self.setText(text)
      

    def textChanged(self, text):
        self.buttonBox.setEnabled(True)
        
        
    def text(self):
        return self.txtControl.text()


    def setText(self, text):
        self.cancelText = text
        self.txtControl.setText(text)
        self.buttonBox.setEnabled(False)


    def cmdOKClicked(self):
        self.cancelText = self.text()
        self.buttonBox.setEnabled(False)
        self.emit(PYSIGNAL('OKClicked'), ())


    def cmdCancelClicked(self):
        self.setText(self.cancelText)
        self.buttonBox.setEnabled(False)
        self.buttonBox.setFocus()


class DialogButtonsBar(QWidget):
    DEFAULT_MARGIN=6
    DEFAULT_SPACING=6
    def __init__(self, parent, button1="OK", button2="Cancel", button3=None, callback=None, margin=6, spacing=6):
        QWidget.__init__(self, parent)
        self.callback=callback
        spacer=QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        if button1 is not None:
            self.button1=QPushButton(button1,self)
        if button2 is not None:
            self.button2=QPushButton(button2,self)
        if button3 is not None:
            self.button3=QPushButton(button3,self)
        QHBoxLayout(self,margin,spacing)
        self.layout().addWidget(spacer)
        if button1 is not None:
            self.layout().addWidget(self.button1)
            QObject.connect(self.button1,SIGNAL('clicked()'),self.button1Clicked)
        if button2 is not None:
            self.layout().addWidget(self.button2)
            QObject.connect(self.button2,SIGNAL('clicked()'),self.button2Clicked)
        if button3 is not None:
            self.layout().addWidget(self.button3)
            QObject.connect(self.button3,SIGNAL('clicked()'),self.button3Clicked)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    def button1Clicked(self):
        if isinstance(self.callback, collections.Callable):
            self.callback(str(self.button1.text()))
    def button2Clicked(self):
        if isinstance(self.callback, collections.Callable):
            self.callback(str(self.button2.text()))
    def button3Clicked(self):
        if isinstance(self.callback, collections.Callable):
            self.callback(str(self.button3.text()))
