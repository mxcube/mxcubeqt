from qt import *
import os

class SpinBoxButtons(QWidget):
    def __init__(self, parent = None, name = None, fl = 0):
        QWidget.__init__(self, parent, name, fl)

        if not name:
            self.setName('SpinBoxButtons')


        v_layout = QVBoxLayout(self, 0, 0, "v_layout")
        self.up_button = QPushButton("u", self, "up_button")
        self.up_button.setMaximumHeight(20)
        self.up_button.setMaximumWidth(15)
        self.up_button.setPixmap(QPixmap(os.path.dirname(__file__) + \
                                             "/arrow_up.png"))
        self.down_button = QPushButton("d", self, "down_button")
        self.down_button.setMaximumHeight(20)
        self.down_button.setMaximumWidth(15)
        self.down_button.setPixmap(QPixmap(os.path.dirname(__file__) + \
                                             "/arrow_down.png"))

        v_layout.addWidget(self.up_button)
        v_layout.addWidget(self.down_button)
        

        QObject.connect(self.up_button, SIGNAL("clicked()"), 
                        self.up_clicked)

        QObject.connect(self.down_button, SIGNAL("clicked()"), 
                        self.down_clicked)


    def down_clicked(self):
        self.emit(PYSIGNAL("scroll_down"), (None,))


    def up_clicked(self):
        self.emit(PYSIGNAL("scroll_up"), (None,))
