import webbrowser
import logging
import types

from qt import *

from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons

 __category__ = 'gui_utils'

class ToolButton(QToolButton):
    def __init__(self, parent, icon, text=None, callback=None, tooltip=None):
        QToolButton.__init__(self, parent)

        self.setIconSet(QIconSet(Icons.load(icon)))

        if type(text) != types.StringType:
            tooltip = callback
            callback = text
        else:
            self.setTextLabel(text)
            self.setTextPosition(QToolButton.BelowIcon)
            self.setUsesTextLabel(True)

        if callback is not None:
            QObject.connect(self, SIGNAL("clicked()"), callback)

        if tooltip is not None:
            QToolTip.add(self, tooltip)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        

class HelpBrick(BlissWidget):
    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        self.addProperty("help_url", "string", "http://intranet")
        self.addProperty("browser", "combo", ("default", "mozilla", "netscape"), "default")

        self.cmdShowHelp = ToolButton(self, "rescue", "Help !", self.cmdShowHelpClicked, "Open help web page")

        QVBoxLayout(self)
        self.layout().addWidget(self.cmdShowHelp)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)


    def cmdShowHelpClicked(self):
        if self["browser"] != "default":
           browser = webbrowser.get(self["browser"])
        else:
           browser = webbrowser

        try:
            webbrowser.open(self["help_url"])
        except:
            logging.getLogger().exception("%s: could not open web browser", self.name())

    
    
