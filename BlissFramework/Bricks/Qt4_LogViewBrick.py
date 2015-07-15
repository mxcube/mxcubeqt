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

"""
Qt4_LogViewBrick

[Description]

The LogView brick displays log messages from the application.

[Properties]
----------------------------------------------------------------
|  Name   |   Type  | Description
----------------------------------------------------------------
|  level          | combo   | minimum level for a message to be added to the list
|  showDebug      | boolean | set whether debug messages are shown (default: False)
|  appearance     | combo   | "list" or " tabs"
|  enableFeedback | boolean | adds a new tab for mail feedback feature
|  emailAddresses | string  | list separated by spaces of email addresses for the feedback feature
|  icons          | string  | <icon for tab 1> <icon for tab 2> ... <icon for tab n> <feedback icon>
|  maxLogLines    | integer | max. log lines, negative value : infinite log
|  autoSwitchTabs | boolean | automatically switch to appropriate tab when a new message is logged
----------------------------------------------------------------

[Signals]

[Slots]

--------------------------------
| Name  | Arguments | Description 
--------------------------------
| clearLog |   |  removes all messages
--------------------------------

[HardwareObjects]
Any brick or Hardware Object can use the logging facility (from Python
standard library) in order to emit log messages :

===
import logging
logging.getLogger().info("A log message !")
===

Log messages are processed by the main logger and sent to several
handlers. The LogView brick is the GUI log handler.

The email feedback feature allows users to report any problem : an email
is sent to the recipients specified in the emailAddresses property.
"""
import logging
import os
import email.Utils
import smtplib

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework import Qt4_BaseComponents
from BlissFramework.Utils import Qt4_GUILogHandler
from BlissFramework import Qt4_Icons
import BlissFramework

__category__ = 'Qt4_General'

class LogView(QtGui.QTextEdit):
    COLORS = { logging.NOTSET: 'lightgrey', logging.DEBUG: 'darkgreen',
               logging.INFO: 'darkblue', logging.WARNING: 'orange',
               logging.ERROR: 'red', logging.CRITICAL: 'black'}

    LEVELS = { logging.NOTSET: 'NOTSET', logging.DEBUG: 'DEBUG',
               logging.INFO: 'INFO', logging.WARNING: 'WARNING',
               logging.ERROR: 'ERROR', logging.CRITICAL: 'CRITICAL'}

    def __init__(self,parent,label):
        QtGui.QTextEdit.__init__(self,parent)

        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        
        #self.setTextFormat(QTextEdit.PlainText)
        self.tabLabel=label
        self.unreadMessages=0
        
    def log(self,level,date,message):
        color=LogView.COLORS[level]
        self.append("[%s][%s] %s" % (LogView.LEVELS[level], date, message))
        #self.scrollToBottom()

###
### Widget to submit a feedback email
###
class SubmitFeedback(QtGui.QWidget):
    def __init__(self, parent, label, email_addresses):
        QtGui.QWidget.__init__(self, parent)
        self.unreadMessages=0
        self.tabLabel=label
        self.emailAddresses=email_addresses

        msg = ["Feel free to report any comment about this software;",
               " an email will be sent to the people concerned.",
               "Do not forget to put your name or email address if you require an answer."]
        label = QtGui.QLabel("<i>%s</i>" % "\n".join(msg), self)
      
        box1 = QtGui.QWidget(self)
        box1.setLayout(QtGui.QHBoxLayout()) 
        #box1 = QHBox(self)

        box2 = QtGui.QWidget(box1)
        box2.setLayout(QtGui.QVBoxLayout())
        QtGui.QLabel('Message:', box2)

        VerticalSpacer(box2)
        self.submitButton = QtGui.QToolButton(box2)
        self.submitButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)

        self.submitButton.setText('Submit')
        self.submitButton.setUsesTextLabel(True)
        self.submitButton.clicked.connect(self.submitMessage)

        self.message = QtGui.QTextEdit(box1)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(label)
        self.layout().addWidget(box1)

        self.message.setToolTip("Write here your comments or feedback")
        self.submitButton.setToolTip("Click here to send your feedback to the authors of this software")

    def clear(self):
        self.message.clear()

    def setMaxLogLines(self,lines):
        pass

    def submitMessage(self):
        msg_date = email.Utils.formatdate(localtime=True)
        
        try:
            user = os.environ['SMIS_BEAMLINE_NAME']
            fromaddr = user.replace(' ','-')
        except (KeyError,TypeError,ValueError,AttributeError):
            fromaddr = 'some-beamline'
        fromaddr += "@esrf.fr"

        try:
            smtp = smtplib.SMTP('smtp', smtplib.SMTP_PORT)
            toaddrs = self.emailAddresses.replace(' ', ',')
            subj="[BEAMLINE FEEDBACK] %s" % BlissFramework.loggingName
            email_msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                fromaddr, 
                toaddrs,
                subj,
                msg_date,
                str(self.message.text()))

            logging.getLogger().debug("Sending feedback from %s to %s" % (fromaddr,toaddrs))
            error_dict = smtp.sendmail(fromaddr, toaddrs.split(','), email_msg)
        except smtplib.SMTPException, e:
            logging.getLogger().error("Could not send mail: %s" % str(e))
            smtp.quit()
        else:
            smtp.quit()
            if len(error_dict):
                logging.getLogger().error(str(error_dict))

            info_dialog=QMessageBox("Thank you!","Your comments have been submitted.",\
                QMessageBox.Information,QMessageBox.Ok,QMessageBox.NoButton,\
                QMessageBox.NoButton,self)
            s=self.font().pointSize()
            f = info_dialog.font()
            f.setPointSize(s)
            info_dialog.setFont(f)
            info_dialog.updateGeometry()
            info_dialog.exec_loop()

            self.message.clear()



###
### Views the log messages, either in a list or in separated tabs.
### In tab mode it is possible to send a feedback mail.
### The debug messages might me switched off (in either modes).
###
class Qt4_LogViewBrick(Qt4_BaseComponents.BlissWidget):
    LOGS = ("Info", "Details", "Feedback","Debug")
    TITLES = {"Info":"Information messages", "Feedback":"Submit feedback", "Details":"Details", "Debug":"Debug"}
    TOOLTIPS = {"Info":"Displays the progress of the requested operations",\
        "Feedback":"Submits a feedback email about this software",\
        "Details":"Detailed messages, including warnings and errors",\
        "Debug":"Debug messages; please disregard them"}

    def __init__(self, *args):
        Qt4_BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('level', 'combo', ('NOT SET', 'INFO', 'WARNING', 'ERROR'), 'NOT SET')
        self.addProperty('showDebug', 'boolean', True)
        self.addProperty('appearance', 'combo', ('list', 'tabs'), 'list')
        self.addProperty('enableFeedback', 'boolean', True)
        self.addProperty('emailAddresses', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty('maxLogLines', 'integer', -1)
        self.addProperty('autoSwitchTabs','boolean', False)
        self.addProperty('myTabLabel', 'string', '')

        self.defineSlot('clearLog',())
        self.defineSlot('tabSelected',())

        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        self.color = {logging.NOTSET: 'lightgrey', 
                      logging.DEBUG: 'darkgreen', 
                      logging.INFO: 'darkblue', 
                      logging.WARNING: 'orange', 
                      logging.ERROR: 'red', 
                      logging.CRITICAL: 'black' }

        self.filterLevel = logging.NOTSET

        self.tabs = QtGui.QTabWidget(self)
        self.tabs.hide()

        for l in Qt4_LogViewBrick.LOGS:
            if l=="Feedback":
                self.FeedbackLog=SubmitFeedback(self,Qt4_LogViewBrick.TITLES["Feedback"],self['emailAddresses'])
            else:
                list_view = LogView(self, Qt4_LogViewBrick.TITLES[l])
                exec("self.%sLog = list_view" % l)
                
        for l in Qt4_LogViewBrick.LOGS[1:]:
            exec("self.%sLog.hide()" % l)

        self.tabLevels = { logging.NOTSET: self.InfoLog, logging.DEBUG: self.InfoLog, logging.INFO: self.InfoLog, logging.WARNING: self.InfoLog, logging.ERROR: self.InfoLog, logging.CRITICAL: self.InfoLog }

        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        self.setLayout(QtGui.QVBoxLayout())
        #QVBoxLayout(self)
        self.layout().addWidget(self.InfoLog)
              
        # Register to GUI log handler
        Qt4_GUILogHandler.GUILogHandler().register(self)


    def run(self):
        # Register to GUI log handler
        #Qt4_GUILogHandler.GUILogHandler().register(self)
        self.connect(self.tabs,QtCore.SIGNAL('currentChanged(QWidget *)'),self.resetUnreadMessages)


    def clearLog(self):
        for l in Qt4_LogViewBrick.LOGS:
            exec("self.%sLog.clear()" % l)
            exec("self.%sLog.unreadMessages=0" % l)
            exec("self.tabs.setTabLabel(self.%sLog,self.%sLog.tabLabel)" % (l,l))


    def tabSelected(self,tab_name):
        if self["appearance"]=="list":
            if tab_name==self['myTabLabel']:
                self.emit(QtCore.SIGNAL("resetUnreadMessages"),(True,))


    def appendLogRecord(self, record):
        recLevel = record.getLevel()

        if recLevel == logging.DEBUG and not self['showDebug']:
            return
        else:
            if recLevel < self.filterLevel:
                return

        tab=self.tabLevels[recLevel]
        msg=record.getMessage().replace('\n',' ').strip()

        level=None
        tab.log(recLevel,"%s %s" % (record.getDate(),record.getTime()),msg)

        if self["appearance"]=="tabs":
            if self.tabs.currentPage() != tab:
                if self["autoSwitchTabs"]:
                    self.tabs.showPage(tab)
                else:
                    tab.unreadMessages=tab.unreadMessages+1
                    tab_label="%s (%d)" % (tab.tabLabel,tab.unreadMessages)
                    self.tabs.setTabLabel(tab,tab_label)
        elif self["appearance"]=="list":
            self.emit(QtCore.SIGNAL("incUnreadMessages"),(1,True,))


    def resetUnreadMessages(self,tab):
        tab.unreadMessages=0
        self.tabs.setTabLabel(tab,tab.tabLabel)

                          
    def customEvent(self, event):
        if self.isRunning():
            self.appendLogRecord(event.record)


    def blockSignals(self, block):
        # Redefine blockSignals, so signals are not blocked in Design mode
        pass
        
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'level':
            self.filterLevel = logging.NOTSET

            if newValue == 'INFO':
                self.filterLevel = logging.INFO
            elif newValue == 'WARNING':
                self.filterLevel = logging.WARNING
            elif newValue == 'ERROR':
                self.filterLevel = logging.ERROR

        elif propertyName == 'showDebug':
            if self['appearance']=="tabs":
                if newValue:
                    if self.tabs.indexOf(self.DebugLog)==-1:
                        self.tabs.insertTab(self.DebugLog, self.DebugLog.tabLabel, 9)
                        self.tabs.setTabToolTip(self.DebugLog, Qt4_LogViewBrick.TOOLTIPS["Debug"])
                else:
                    if self.tabs.indexOf(self.DebugLog)!=-1:
                        self.tabs.removePage(self.DebugLog)
        
        elif propertyName == 'emailAddresses':
            self.FeedbackLog.emailAddresses=newValue

        elif propertyName == 'enableFeedback':
            if self['appearance']=="tabs":
                if newValue:
                    if self.tabs.indexOf(self.FeedbackLog)==-1:
                        self.tabs.insertTab(self.FeedbackLog, self.FeedbackLog.tabLabel, 2)
                        self.tabs.setTabToolTip(self.FeedbackLog, Qt4_LogViewBrick.TOOLTIPS["Feedback"])
                else:
                   if self.tabs.indexOf(self.FeedbackLog)!=-1:
                        self.tabs.removePage(self.FeedbackLog)

        elif propertyName == 'appearance':
            if oldValue=="list":
                self.layout().removeWidget(self.InfoLog)
            elif oldValue=="tabs":
                for l in Qt4_LogViewBrick.LOGS:
                    exec("self.tabs.removePage(self.%sLog)" % l)
                    exec("self.%sLog.reparent(self,0,QPoint(0,0),True)" % l)

                self.layout().removeWidget(self.tabs)

                for l in Qt4_LogViewBrick.LOGS[1:]:
                    exec("self.%sLog.hide()" % l)
                self.tabs.hide()
            elif oldValue is None:
                self.layout().removeWidget(self.InfoLog)

            if newValue=="list":
                self.tabLevels = { logging.NOTSET: self.InfoLog, logging.DEBUG: self.InfoLog, logging.INFO: self.InfoLog, logging.WARNING: self.InfoLog, logging.ERROR: self.InfoLog, logging.CRITICAL: self.InfoLog }
                self.layout().addWidget(self.InfoLog)
            elif newValue=="tabs":
                self.tabLevels = { logging.NOTSET: self.DetailsLog, logging.DEBUG: self.DebugLog, logging.INFO: self.InfoLog, logging.WARNING: self.DetailsLog, logging.ERROR: self.DetailsLog, logging.CRITICAL: self.DetailsLog }
                
                for l in Qt4_LogViewBrick.LOGS:
                    if l=="Debug" and not self['showDebug']:
                        pass
                    elif l=="Feedback" and not self['enableFeedback']:
                        pass
                    else:
                        exec("self.tabs.addTab(self.%sLog,'%s')" % (l, Qt4_LogViewBrick.TITLES[l]))
                        exec("self.tabs.setTabToolTip(self.%sLog,'%s')" % (l,Qt4_LogViewBrick.TOOLTIPS[l]))
                self.layout().addWidget(self.tabs)
                self.tabs.show()

        elif propertyName == 'icons':
            icons_list=newValue.split()

            for i in range(self.tabs.count()):
                try:
                    icon_name=icons_list[i]
                    pxmap=Qt4_Icons.load(icon_name)
                    icon_set=QIconSet(pxmap)
                    tab=self.tabs.page(i)
                    self.tabs.setTabIconSet(tab,icon_set)
                except IndexError:
                    pass

            try:
                self.FeedbackLog.submitButton.setIcon(QtGui.QIcon(Qt4_Icons.load(icons_list[-1])))
            except IndexError:
                pass

        elif propertyName == 'maxLogLines':
            print "maxLogLines - implement"
            #for l in Qt4_LogViewBrick.LOGS:
            #    exec("self.%sLog.setMaxLogLines(%d)" % (l,newValue))

        else:
            Qt4_BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        

        # Refresh log
        #for l in Qt4_LogViewBrick.LOGS:
        #    exec("self.%sLog.clear()" % l)
        #    exec("self.%sLog.unreadMessages=0" % l)
        #    exec("self.tabs.setTabLabel(self.%sLog,self.%sLog.tabLabel)" % (l,l))

        #Qt4_GUILogHandler.GUILogHandler().register(self)


###
### Auxiliary class for positioning
###
class VerticalSpacer(QtGui.QWidget):
    def __init__(self,*args):
        QtGui.QWidget.__init__(self,*args)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
