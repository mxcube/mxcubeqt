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
#import email.Utils
from datetime import datetime
import smtplib

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework import Qt4_Icons
from BlissFramework import Qt4_BaseComponents
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Utils import Qt4_GUILogHandler
import BlissFramework

__category__ = 'General'

class CustomTreeWidget(QtGui.QTreeWidget):

    def __init__(self, parent, label, icon):
        QtGui.QTextEdit.__init__(self,parent)

        self.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                           QtGui.QSizePolicy.Expanding)
       
        self.tab_level = None  
        self.tab_label = label
        self.tab_icon = icon
        self.unread_messages = 0
        self.max_log_lines = None
      
        self.setColumnCount(4)
        self.setRootIsDecorated(False)
        self.setHeaderLabels(["Level", "Date", "Time", "Message"])

        self.contextMenuEvent = self.show_context_menu
        
    def add_log_line(self, record):
        #if self.tab_level:
        #    if self.tab_level = record.getLevel():
        #        return
        
        msg = record.getMessage().replace('\n',' ').strip()
        try: 
           info_str_list = QtCore.QStringList()
        except:
           info_str_list = []
        info_str_list.append(record.getLevelName())
        info_str_list.append(record.getDate())
        info_str_list.append(record.getTime())
        info_str_list.append(record.getMessage())
        new_item = QtGui.QTreeWidgetItem(info_str_list)
        self.addTopLevelItem(new_item)
        if self.topLevelItemCount() % 10 == 0:
            for col in range(4):
                new_item.setBackgroundColor(col, Qt4_widget_colors.LIGH_2_GRAY)
                 
        if self.max_log_lines and self.max_log_lines > 0:
            if self.topLevelItemCount() > self.max_log_lines:
                self.takeTopLevelItem(0) 
        self.scrollToBottom()

    def set_max_log_lines(self, max_log_lines):
        self.max_log_lines = max_log_lines

    def show_context_menu(self, context_menu_event):
        menu = QtGui.QMenu(self)
        menu.addAction("Clear", self.clear)
        menu.addAction("Copy", self.copy_log)
        menu.addAction("Save log", self.save_log)
        menu.popup(QtGui.QCursor.pos())

    def copy_log(self):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.clear(mode = clipboard.Clipboard)
        text = ""
        for item_index in range(self.topLevelItemCount()):
            for col in range(4):
                text += "%s%s" %(self.topLevelItem(item_index).text(col), chr(9))
            text += "\n"  
        clipboard.setText(text, mode = clipboard.Clipboard)

    def save_log(self):
        pass

class Submitfeedback(QtGui.QWidget):
    """Widget to submit a feedback email
    """

    def __init__(self, parent, label, email_addresses):
        QtGui.QWidget.__init__(self, parent)
        self.unread_messages = 0
        self.tab_label = label
        self.email_addresses = email_addresses
        self.from_email_address = None

        msg = ["Feel free to report any comment about this software;",
               " an email will be sent to the people concerned.",
               "Do not forget to put your name or email address if you require an answer."]
        label = QtGui.QLabel("<b>%s</b>" % "\n".join(msg), self)
        msg_label = QtGui.QLabel('Message:', self)

        self.submit_button = QtGui.QToolButton(self)
        #self.submit_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.submit_button.setText('Submit')
        self.submit_button.setUsesTextLabel(True)

        self.message_textedit = QtGui.QTextEdit(self)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(label)
        self.layout().addWidget(msg_label)
        self.layout().addWidget(self.message_textedit)
        self.layout().addWidget(self.submit_button)

        self.submit_button.clicked.connect(self.submit_message)
        self.message_textedit.setToolTip("Write here your comments or feedback")
        self.submit_button.setToolTip("Click here to send your feedback to the authors of this software")

    def clear(self):
        self.message_textedit.clear()

    def set_max_log_lines(self,lines):
        pass

    def submit_message(self):
        #msg_date = email.Utils.formatdate(localtime=True)
        msg_date = str(datetime.now())
        
        if self.from_email_address:
            fromaddr = self.from_email_address
        else: 
            try:
               user = os.environ['SMIS_BEAMLINE_NAME']
               fromaddr = user.replace(' ','-')
            except (KeyError,TypeError,ValueError,AttributeError):
               fromaddr = 'some-beamline'
            fromaddr += "@mxcube.com"

        try:
            smtp = smtplib.SMTP('smtp', smtplib.SMTP_PORT)
            toaddrs = self.email_addresses.replace(' ', ',')
            subj="[BEAMLINE FEEDBACK] %s" % os.getlogin()
            email_msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                fromaddr, 
                toaddrs,
                subj,
                msg_date,
                str(self.message_textedit.toPlainText()))

            logging.getLogger().debug("Sending feedback from %s to %s" % (fromaddr,toaddrs))
            error_dict = smtp.sendmail(fromaddr, toaddrs.split(','), email_msg)
        except smtplib.SMTPException as e:
            logging.getLogger().error("Could not send mail: %s" % str(e))
            smtp.quit()
        else:
            smtp.quit()
            if len(error_dict):
                logging.getLogger().error(str(error_dict))

            QtGui.QMessageBox.information(self, "Thank you!",
                "Your comments have been submitted.", QtGui.QMessageBox.Ok)

            self.message_textedit.clear()



###
### Views the log messages, either in a list or in separated tabs.
### In tab mode it is possible to send a feedback mail.
### The debug messages might me switched off (in either modes).
###
class Qt4_LogViewBrick(Qt4_BaseComponents.BlissWidget):
    LOGS = ("details", "info", "debug", "feedback")
    TITLES = {"info": "Information", 
              "feedback":"Submit feedback", 
              "details": "Errors and warnings", 
              "debug":"Debug"}
    TOOLTIPS = {"info": "Displays the progress of the requested operations",
                "feedback":"Submits a feedback email about this software",
                "details":"Detailed messages, including warnings and errors",
                "debug":"Debug messages; please disregard them"}
    ICONS = {"details" : "Caution"} 

    def __init__(self, *args):
        Qt4_BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('level', 'combo', ('NOT SET', 'INFO', 'WARNING', 'ERROR'), 'NOT SET')
        self.addProperty('showDebug', 'boolean', True)
        self.addProperty('appearance', 'combo', ('list', 'tabs'), 'tabs')
        self.addProperty('enableFeedback', 'boolean', True)
        self.addProperty('emailAddresses', 'string', '')
        self.addProperty('fromEmailAddress', 'string', '')
        self.addProperty('icons', 'string', 'Caution Inform Hammer Envelope')
        self.addProperty('maxLogLines', 'integer', -1)
        self.addProperty('autoSwitchTabs','boolean', False)
        self.addProperty('myTabLabel', 'string', '')

        self.defineSlot('clearLog',())
        self.defineSlot('tabSelected',())

        self.defineSignal('incUnreadMessages',())
        self.defineSignal('resetUnreadMessages',())

        self.filter_level = logging.NOTSET
        
        self.tab_widget = QtGui.QTabWidget(self)
        self.tab_widget.hide()

        for l in Qt4_LogViewBrick.LOGS:
            
            if l=="feedback":
                self.feedback_log = Submitfeedback(self, 
                     Qt4_LogViewBrick.TITLES["feedback"], self['emailAddresses'])
            else:
                tree_widget = CustomTreeWidget(self, Qt4_LogViewBrick.TITLES[l],
                      Qt4_LogViewBrick.ICONS.get(l))
                exec("self.%s_log = tree_widget" % l)
                
        for l in Qt4_LogViewBrick.LOGS[1:]:
            exec("self.%s_log.hide()" % l)

        self.tab_levels = {logging.NOTSET: self.info_log, 
                           logging.DEBUG: self.info_log, 
                           logging.INFO: self.info_log, 
                           logging.WARNING: self.info_log, 
                           logging.ERROR: self.info_log, 
                           logging.CRITICAL: self.info_log }

        self.setSizePolicy(QtGui.QSizePolicy.Minimum, 
                           QtGui.QSizePolicy.Expanding)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(self.info_log)
        self.layout().addWidget(self.tab_widget)
        # Register to GUI log handler
        Qt4_GUILogHandler.GUILogHandler().register(self)


    def run(self):
        # Register to GUI log handler
        self.tab_widget.currentChanged.connect(self.resetUnreadMessages)

    def clearLog(self):
        for l in Qt4_LogViewBrick.LOGS:
            exec("self.%s_log.clear()" % l)
            exec("self.%s_log.unread_messages=0" % l)
            exec("self.tab_widget.setTabLabel(self.%s_log,self.%s_log.tab_label)" % (l,l))

    def tabSelected(self,tab_name):
        if self["appearance"]=="list":
            if tab_name==self['myTabLabel']:
                self.emit(QtCore.SIGNAL("resetUnreadMessages"),(True,))


    def appendLogRecord(self, record):
        rec_level = record.getLevel()

        if rec_level == logging.DEBUG and not self['showDebug']:
            return
        else:
            if rec_level < self.filter_level:
                return

        tab = self.tab_levels[rec_level]
        level = None
        tab.add_log_line(record)

        if self["appearance"]=="tabs":
            if self.tab_widget.currentWidget() != tab:
                if self["autoSwitchTabs"]:
                    self.tab_widget.setCurrentWidget(tab)
                else:
                    tab.unread_messages = tab.unread_messages+1
                    tab_label="%s (%d)" % (tab.tab_label, tab.unread_messages)
                    self.tab_widget.setTabText(self.tab_widget.indexOf(tab), tab_label)
                    #self.tab_widget.setTabLabel(tab,tab_label)
        elif self["appearance"]=="list":
            self.emit(QtCore.SIGNAL("incUnreadMessages"),(1,True,))


    def resetUnreadMessages(self, tab_index):
        selected_tab = self.tab_widget.widget(tab_index)
        selected_tab.unread_messages = 0
        self.tab_widget.setTabText(tab_index, selected_tab.tab_label)

                          
    def customEvent(self, event):
        if self.isRunning():
            self.appendLogRecord(event.record)


    def blockSignals(self, block):
        # Redefine blockSignals, so signals are not blocked in Design mode
        pass
        
    def propertyChanged(self, property_name, old_value, new_value):
        if property_name == 'level':
            self.filter_level = logging.NOTSET

            if new_value == 'INFO':
                self.filter_level = logging.INFO
            elif new_value == 'WARNING':
                self.filter_level = logging.WARNING
            elif new_value == 'ERROR':
                self.filter_level = logging.ERROR

        elif property_name == 'showDebug':
            if self['appearance']=="tabs":
                if new_value:
                    if self.tab_widget.indexOf(self.debug_log)==-1:
                        self.tab_widget.insertTab(self.debug_log, 
                             self.debugLog.tab_label, 9)
                        self.tab_widget.setTabToolTip(self.debug_log, 
                             Qt4_LogViewBrick.TOOLTIPS["Debug"])
                else:
                    if self.tab_widget.indexOf(self.debug_log)!=-1:
                        self.tab_widget.removePage(self.debug_log)
        
        elif property_name == 'emailAddresses':
            self.feedback_log.email_addresses = new_value
        elif property_name == 'fromEmailAddress':
            self.feedback_log.from_email_address = new_value

        elif property_name == 'enableFeedback':
            if self['appearance'] == "tabs":
                if new_value:
                    if self.tab_widget.indexOf(self.feedback_log) == -1:
                        self.tab_widget.insertTab(2, self.feedback_log, 
                             self.feedback_log.tab_label)
                        self.tab_widget.setTabToolTip(
                             self.tab_widget.indexOf(self.feedback_log), 
                             Qt4_LogViewBrick.TOOLTIPS["feedback"])
                else:
                   if self.tab_widget.indexOf(self.feedback_log) != -1:
                        self.tab_widget.removePage(self.feedback_log)

        elif property_name == 'appearance':
            if new_value == "list":
                self.tab_levels = {logging.NOTSET: self.info_log, 
                                   logging.DEBUG: self.info_log, 
                                   logging.INFO: self.info_log, 
                                   logging.WARNING: self.info_log,
                                   logging.ERROR: self.info_log,
                                   logging.CRITICAL: self.info_log }
                self.info_log.show()
                self.tab_widget.hide()
            elif new_value == "tabs":
                self.tab_levels = {logging.NOTSET: self.details_log, 
                                   logging.DEBUG: self.debug_log,
                                   logging.INFO: self.info_log,
                                   logging.WARNING: self.details_log,
                                   logging.ERROR: self.details_log,
                                   logging.CRITICAL: self.details_log}
                
                for index, log_widget in enumerate(Qt4_LogViewBrick.LOGS):
                    if log_widget == "debug" and not self['showDebug']:
                        pass
                    elif log_widget == "feedback" and not self['enableFeedback']:
                        pass
                    else:
                        exec("self.tab_widget.addTab(self.%s_log,'%s')" % \
                             (log_widget, Qt4_LogViewBrick.TITLES[log_widget]))
                        exec("self.tab_widget.setTabToolTip(%d,'%s')" % \
                             (index, Qt4_LogViewBrick.TOOLTIPS[log_widget]))

                self.tab_widget.show()
                self.info_log.hide()

        elif property_name == 'icons':
            icons_list = new_value.split()
            for i in range(self.tab_widget.count()):
                try:
                    self.tab_widget.setTabIcon(i, Qt4_Icons.load_icon(icons_list[i]))
                except IndexError:
                    pass

            try:
                self.feedback_log.submit_button.setIcon(Qt4_Icons.load_icon(icons_list[-1]))
            except IndexError:
                pass

        elif property_name == 'maxLogLines':
            for l in Qt4_LogViewBrick.LOGS:
                exec("self.%s_log.set_max_log_lines(%d)" % (l, new_value))

        else:
            Qt4_BaseComponents.BlissWidget.propertyChanged(self, property_name, old_value, new_value)        
