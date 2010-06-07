from qt import *

_pleaseWaitDialog = None

def show(msg = "Please wait...", abortMsg = "abort", abortCallback = None):
    global _pleaseWaitDialog
    
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor), True)

    _pleaseWaitDialog = QWidget(None, '',  Qt.WStyle_Customize | Qt.WShowModal | Qt.WStyle_Splash | Qt.WDestructiveClose)
    pleaseWaitLabel = QLabel('<nobr><h1><b>%s</b></h1></nobr>' % msg, _pleaseWaitDialog)
    cmdAbort = QPushButton(abortMsg, _pleaseWaitDialog)
    _pleaseWaitDialog.setPaletteBackgroundColor(QColor(255, 255, 255))
    _pleaseWaitDialog.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    QVBoxLayout(_pleaseWaitDialog)
    _pleaseWaitDialog.layout().addWidget(pleaseWaitLabel)
    _pleaseWaitDialog.layout().addWidget(cmdAbort, Qt.AlignHCenter)

    if callable(abortCallback):
        QObject.connect(cmdAbort, SIGNAL('clicked()'), abortCallback)
        
    _pleaseWaitDialog.show()
    sw = QApplication.desktop().screen().width()
    sh = QApplication.desktop().screen().height()
    _pleaseWaitDialog.move((sw - _pleaseWaitDialog.width()) / 2, (sh - _pleaseWaitDialog.height()) / 2)
        

def hide():
    global _pleaseWaitDialog

    if _pleaseWaitDialog is not None and _pleaseWaitDialog.isShown():
        QApplication.restoreOverrideCursor()
        
        _pleaseWaitDialog.close(True)
        _pleaseWaitDialog = None
