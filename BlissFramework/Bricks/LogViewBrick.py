"""
LogViewBrick

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

from BlissFramework import BaseComponents
from BlissFramework.Utils import GUILogHandler
from BlissFramework import Icons
import BlissFramework

from qt import *

__category__ = 'gui_utils'

class LogView(QTextEdit):
    COLORS = { logging.NOTSET: 'lightgrey', logging.DEBUG: 'darkgreen', logging.INFO: 'darkblue', logging.WARNING: 'orange', logging.ERROR: 'red', logging.CRITICAL: 'black' }

    def __init__(self,parent,label):
        QTextEdit.__init__(self,parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        self.setTextFormat(QTextEdit.LogText)
        self.tabLabel=label
        self.unreadMessages=0
        
    def log(self,level,date,message):
        color=LogView.COLORS[level]
        self.append("<font color=%s>%s %s" % (color,date,message))
        self.scrollToBottom()

###
### Widget to submit a feedback email
###
class SubmitFeedback(QWidget):
    def __init__(self, parent, label, email_addresses):
        QWidget.__init__(self, parent)
        self.unreadMessages=0
        self.tabLabel=label
        self.emailAddresses=email_addresses

        msg = ["Feel free to report any comment about this software;",
               " an email will be sent to the people concerned.",
               "Do not forget to put your name or email address if you require an answer."]
        label=QLabel("<i>%s</i>" % "\n".join(msg), self)
        box1=QHBox(self)

        box2=QVBox(box1)
        QLabel('Message:',box2)
        VerticalSpacer(box2)
        self.submitButton=QToolButton(box2)
        self.submitButton.setTextLabel('Submit')
        self.submitButton.setUsesTextLabel(True)
        QObject.connect(self.submitButton, SIGNAL('clicked()'), self.submitMessage)

        self.message=QTextEdit(box1)

        QVBoxLayout(self)
        self.layout().addWidget(label)
        self.layout().addWidget(box1)

        QToolTip.add(self.message,"Write here your comments or feedback")
        QToolTip.add(self.submitButton,"Click here to send your feedback to the authors of this software")

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
class LogViewBrick(BaseComponents.BlissWidget):
    LOGS = ("Info", "Details", "Feedback","Debug")
    TITLES = {"Info":"Information messages", "Feedback":"Submit feedback", "Details":"Details", "Debug":"Debug"}
    TOOLTIPS = {"Info":"Displays the progress of the requested operations",\
        "Feedback":"Submits a feedback email about this software",\
        "Details":"Detailed messages, including warnings and errors",\
        "Debug":"Debug messages; please disregard them"}

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

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

        self.color = { logging.NOTSET: 'lightgrey', logging.DEBUG: 'darkgreen', logging.INFO: 'darkblue', logging.WARNING: 'orange', logging.ERROR: 'red', logging.CRITICAL: 'black' }
        self.filterLevel = logging.NOTSET

        self.tabs=QTabWidget(self)
        self.tabs.hide()

        for l in LogViewBrick.LOGS:
            if l=="Feedback":
                self.FeedbackLog=SubmitFeedback(self,LogViewBrick.TITLES["Feedback"],self['emailAddresses'])
            else:
                list_view=LogView(self,LogViewBrick.TITLES[l])
                exec("self.%sLog = list_view" % l)
                
        for l in LogViewBrick.LOGS[1:]:
            exec("self.%sLog.hide()" % l)

        self.tabLevels = { logging.NOTSET: self.InfoLog, logging.DEBUG: self.InfoLog, logging.INFO: self.InfoLog, logging.WARNING: self.InfoLog, logging.ERROR: self.InfoLog, logging.CRITICAL: self.InfoLog }

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        QVBoxLayout(self)
        self.layout().addWidget(self.InfoLog)
              
        # Register to GUI log handler
        GUILogHandler.GUILogHandler().register(self)


    def run(self):
        # Register to GUI log handler
        #GUILogHandler.GUILogHandler().register(self)
        self.connect(self.tabs,SIGNAL('currentChanged(QWidget *)'),self.resetUnreadMessages)


    def clearLog(self):
        for l in LogViewBrick.LOGS:
            exec("self.%sLog.clear()" % l)
            exec("self.%sLog.unreadMessages=0" % l)
            exec("self.tabs.setTabLabel(self.%sLog,self.%sLog.tabLabel)" % (l,l))


    def tabSelected(self,tab_name):
        if self["appearance"]=="list":
            if tab_name==self['myTabLabel']:
                self.emit(PYSIGNAL("resetUnreadMessages"),(True,))


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
            self.emit(PYSIGNAL("incUnreadMessages"),(1,True,))


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
        #print "LogViewBrick.propertyChanged",propertyName,oldValue,newValue
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
                        self.tabs.setTabToolTip(self.DebugLog,LogViewBrick.TOOLTIPS["Debug"])
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
                        self.tabs.setTabToolTip(self.FeedbackLog,LogViewBrick.TOOLTIPS["Feedback"])
                else:
                   if self.tabs.indexOf(self.FeedbackLog)!=-1:
                        self.tabs.removePage(self.FeedbackLog)

        elif propertyName == 'appearance':
            if oldValue=="list":
                self.layout().remove(self.InfoLog)
            elif oldValue=="tabs":
                for l in LogViewBrick.LOGS:
                    exec("self.tabs.removePage(self.%sLog)" % l)
                    exec("self.%sLog.reparent(self,0,QPoint(0,0),True)" % l)

                self.layout().remove(self.tabs)

                for l in LogViewBrick.LOGS[1:]:
                    exec("self.%sLog.hide()" % l)
                self.tabs.hide()
            elif oldValue is None:
                self.layout().remove(self.InfoLog)

            if newValue=="list":
                self.tabLevels = { logging.NOTSET: self.InfoLog, logging.DEBUG: self.InfoLog, logging.INFO: self.InfoLog, logging.WARNING: self.InfoLog, logging.ERROR: self.InfoLog, logging.CRITICAL: self.InfoLog }
                self.layout().addWidget(self.InfoLog)
            elif newValue=="tabs":
                self.tabLevels = { logging.NOTSET: self.DetailsLog, logging.DEBUG: self.DebugLog, logging.INFO: self.InfoLog, logging.WARNING: self.DetailsLog, logging.ERROR: self.DetailsLog, logging.CRITICAL: self.DetailsLog }
                
                for l in LogViewBrick.LOGS:
                    if l=="Debug" and not self['showDebug']:
                        pass
                    elif l=="Feedback" and not self['enableFeedback']:
                        pass
                    else:
                        exec("self.tabs.addTab(self.%sLog,'%s')" % (l,LogViewBrick.TITLES[l]))
                        exec("self.tabs.setTabToolTip(self.%sLog,'%s')" % (l,LogViewBrick.TOOLTIPS[l]))
                self.layout().addWidget(self.tabs)
                self.tabs.show()

        elif propertyName == 'icons':
            icons_list=newValue.split()

            for i in range(self.tabs.count()):
                try:
                    icon_name=icons_list[i]
                    pxmap=Icons.load(icon_name)
                    icon_set=QIconSet(pxmap)
                    tab=self.tabs.page(i)
                    self.tabs.setTabIconSet(tab,icon_set)
                except IndexError:
                    pass

            try:
                self.FeedbackLog.submitButton.setPixmap(Icons.load(icons_list[-1]))
            except IndexError:
                pass

        elif propertyName == 'maxLogLines':
            for l in LogViewBrick.LOGS:
                exec("self.%sLog.setMaxLogLines(%d)" % (l,newValue))

        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        

        # Refresh log
        #for l in LogViewBrick.LOGS:
        #    exec("self.%sLog.clear()" % l)
        #    exec("self.%sLog.unreadMessages=0" % l)
        #    exec("self.tabs.setTabLabel(self.%sLog,self.%sLog.tabLabel)" % (l,l))

        #GUILogHandler.GUILogHandler().register(self)


###
### Auxiliary class for positioning
###
class VerticalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
