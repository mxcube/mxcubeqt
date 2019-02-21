#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

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
import os
import sys
import logging

# import email.Utils
from datetime import datetime
import smtplib

from gui.utils import Icons, Colors, GUILogHandler, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Log"


class CustomTreeWidget(QtImport.QTreeWidget):
    def __init__(self, parent, tab_label):
        QtImport.QTreeWidget.__init__(self, parent)

        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Expanding)
        self.tab_label = tab_label
        self.unread_messages = 0
        self.max_log_lines = None

        self.setColumnCount(4)
        self.setRootIsDecorated(False)
        self.setHeaderLabels(["Level", "Date", "Time", "Message"])

        self.contextMenuEvent = self.show_context_menu
        self.clipboard = QtImport.QApplication.clipboard()

    def add_log_line(self, record):
        msg = record.getMessage().replace("\n", " ").strip()
        info_str_list = []

        info_str_list.append(record.getLevelName())
        info_str_list.append(record.getDate())
        info_str_list.append(record.getTime())
        info_str_list.append(msg)
        new_item = QtImport.QTreeWidgetItem(info_str_list)
        self.addTopLevelItem(new_item)
        if self.topLevelItemCount() % 10 == 0:
            for col in range(4):
                new_item.setBackground(col, QtImport.QBrush(Colors.LIGHT_2_GRAY))

        if self.max_log_lines and self.max_log_lines > 0:
            if self.topLevelItemCount() > self.max_log_lines:
                self.takeTopLevelItem(0)
        self.scrollToBottom()

    def set_max_log_lines(self, max_log_lines):
        self.max_log_lines = max_log_lines

    def show_context_menu(self, context_menu_event):
        menu = QtImport.QMenu(self)
        menu.addAction("Clear", self.clear)
        menu.addAction("Copy", self.copy_log)
        menu.addAction("Save log", self.save_log)
        menu.popup(QtImport.QCursor.pos())

    def copy_log(self):
        self.clipboard.clear(mode=self.clipboard.Clipboard)
        text = ""
        for item_index in range(self.topLevelItemCount()):
            for col in range(4):
                text += "%s%s" % (self.topLevelItem(item_index).text(col), chr(9))
            text += "\n"
        self.clipboard.setText(text, mode=self.clipboard.Clipboard)

    def save_log(self):
        self.copy_log()
        filename = str(
            QtImport.QFileDialog.getSaveFileName(
                self, "Choose a filename to save under", "/tmp"
            )
        )
        if len(filename) > 0:
            log_file = open(filename, "w")
            log_file.write(self.clipboard.text())
            log_file.close()


class Submitfeedback(QtImport.QWidget):
    """Widget to submit a feedback email
    """

    def __init__(self, parent, email_addresses, tab_label):
        QtImport.QWidget.__init__(self, parent)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------
        self.tab_label = tab_label
        self.unread_messages = 0
        self.email_addresses = email_addresses
        self.from_email_address = None

        msg = [
            "Feel free to report any comment about this software;",
            " an email will be sent to the people concerned.",
            "Do not forget to put your name or email address if you require an answer.",
        ]
        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        __label = QtImport.QLabel("<b>%s</b>" % "\n".join(msg), self)
        __msg_label = QtImport.QLabel("Message:", self)

        self.submit_button = QtImport.QToolButton(self)
        self.message_textedit = QtImport.QTextEdit(self)

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(__label)
        _main_vlayout.addWidget(__msg_label)
        _main_vlayout.addWidget(self.message_textedit)
        _main_vlayout.addWidget(self.submit_button)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.submit_button.clicked.connect(self.submit_message)

        # Other ---------------------------------------------------------------
        self.message_textedit.setToolTip("Write here your comments or feedback")
        self.submit_button.setText("Submit")

        # if hasattr(self.submit_button, "setUsesTextLabel"):
        #    self.submit_button.setUsesTextLabel(True)
        # elif hasattr(self.submit_button, "setToolButtonStyle"):
        #    self.submit_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.submit_button.setToolButtonStyle(True)
        self.submit_button.setIcon(Icons.load_icon("Envelope"))
        self.submit_button.setToolTip(
            "Click here to send your feedback " + "to the authors of this software"
        )

    def clear(self):
        """Clears log"""
        self.message_textedit.clear()

    def submit_message(self):
        """Submits email"""
        msg_date = str(datetime.now())

        if self.from_email_address:
            from_addr = self.from_email_address
        else:
            try:
                user = os.environ["SMIS_BEAMLINE_NAME"]
                from_addr = user.replace(" ", "-")
            except (KeyError, TypeError, ValueError, AttributeError):
                from_addr = "some-beamline"
            from_addr += "@mxcube.com"

        try:
            smtp = smtplib.SMTP("smtp", smtplib.SMTP_PORT)
            to_addrs = self.email_addresses.replace(" ", ",")
            subj = "[BEAMLINE FEEDBACK] %s" % os.getlogin()
            email_msg = (
                "From: %s\r\n" % from_addr
                + "To: %s\r\n" % from_addr
                + "Subject: %s\r\n" % subj
                + "Date: %s\r\n\r\n" % msg_date
                + str(self.message_textedit.toPlainText())
            )
            logging.getLogger("HWR").debug(
                "Sending feedback from " + "%s to %s" % (from_addr, to_addrs)
            )
            error_dict = smtp.sendmail(from_addr, to_addrs.split(","), email_msg)
        except smtplib.SMTPException as e:
            logging.getLogger().error("Could not send mail: %s" % str(e))
            smtp.quit()
        else:
            smtp.quit()
            if len(error_dict):
                logging.getLogger().error(str(error_dict))

            QtImport.QMessageBox.information(
                self, "Thank you!", "Your comments have been submitted.", QtImport.QMessageBox.Ok
            )
            self.message_textedit.clear()


class LogViewBrick(BaseWidget):
    """Views the log messages, either in a list or in separated tabs.
       In tab mode it is possible to send a feedback mail.
       The debug messages might me switched off (in either modes).
    """

    TOOLTIPS = {
        "info": "Displays the progress of the requested operations",
        "feedback": "Submits a feedback email about this software",
        "details": "Detailed messages, including warnings and errors",
        "debug": "Debug messages; please disregard them",
    }

    incUnreadMessagesSignal = QtImport.pyqtSignal(int, bool)
    resetUnreadMessagesSignal = QtImport.pyqtSignal(bool)

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property(
            "level", "combo", ("NOT SET", "INFO", "WARNING", "ERROR"), "NOT SET"
        )
        self.add_property("showDebug", "boolean", True)
        self.add_property("appearance", "combo", ("list", "tabs"), "tabs")
        self.add_property("enableFeedback", "boolean", True)
        self.add_property("emailAddresses", "string", "")
        self.add_property("fromEmailAddress", "string", "")
        self.add_property("maxLogLines", "integer", -1)
        self.add_property("autoSwitchTabs", "boolean", False)
        self.add_property("myTabLabel", "string", "")

        # Signals -------------------------------------------------------------
        self.define_signal("incUnreadMessagesSignal", ())
        self.define_signal("resetUnreadMessagesSignal", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("clearLog", ())
        self.define_slot("tabSelected", ())

        # Graphic elements ----------------------------------------------------
        self.tab_widget = QtImport.QTabWidget(self)

        self.details_log = CustomTreeWidget(self.tab_widget, "Errors and warnings")
        self.info_log = CustomTreeWidget(self.tab_widget, "Information")
        self.debug_log = CustomTreeWidget(self.tab_widget, "Debug")
        self.feedback_log = Submitfeedback(
            self.tab_widget, self["emailAddresses"], "Submit feedback"
        )

        self.tab_widget.addTab(
            self.details_log, Icons.load_icon("Caution"), "Errors and warnings"
        )
        self.tab_widget.addTab(self.info_log, Icons.load_icon("Inform"), "Information")
        self.tab_widget.addTab(self.debug_log, Icons.load_icon("Hammer"), "Debug")
        self.tab_widget.addTab(
            self.feedback_log, Icons.load_icon("Envelope"), "Submit feedback"
        )

        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.tab_widget)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(QtImport.QSizePolicy.Minimum, QtImport.QSizePolicy.Expanding)

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        self.tab_levels = {
            logging.NOTSET: self.info_log,
            logging.DEBUG: self.info_log,
            logging.INFO: self.info_log,
            logging.WARNING: self.info_log,
            logging.ERROR: self.info_log,
            logging.CRITICAL: self.info_log,
        }

        self.filter_level = logging.NOTSET
        # Register to GUI log handler
        GUILogHandler.GUILogHandler().register(self)

    def run(self):
        # Register to GUI log handler
        self.tab_widget.currentChanged.connect(self.resetUnreadMessages)

    def clearLog(self):
        self.details_log.clear()
        self.info_log.clear()
        self.debug_log.clear()

        self.details_log.unread_messages = 0
        self.info_log.unread_messages = 0
        self.debug_log.unread_messages = 0

    def tabSelected(self, tab_name):
        if self["appearance"] == "list":
            if tab_name == self["myTabLabel"]:
                self.resetUnreadMessagesSignal.emit(True)

    def append_log_record(self, record):
        rec_level = record.getLevel()

        if rec_level == logging.DEBUG and not self["showDebug"]:
            return
        else:
            if rec_level < self.filter_level:
                return

        tab = self.tab_levels[rec_level]
        level = None
        tab.add_log_line(record)

        if self["appearance"] == "tabs":
            if self.tab_widget.currentWidget() != tab:
                if self["autoSwitchTabs"]:
                    self.tab_widget.setCurrentWidget(tab)
                else:
                    tab.unread_messages += 1
                    tab_label = "%s (%d)" % (tab.tab_label, tab.unread_messages)
                    self.tab_widget.setTabText(self.tab_widget.indexOf(tab), tab_label)
        elif self["appearance"] == "list":
            self.incUnreadMessagesSignal.emit(1, True)

    def resetUnreadMessages(self, tab_index):
        selected_tab = self.tab_widget.widget(tab_index)
        selected_tab.unread_messages = 0
        self.tab_widget.setTabText(tab_index, selected_tab.tab_label)

    def customEvent(self, event):
        if self.is_running():
            self.append_log_record(event.record)

    def blockSignals(self, block):
        pass

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "level":
            self.filter_level = logging.NOTSET

            if new_value == "INFO":
                self.filter_level = logging.INFO
            elif new_value == "WARNING":
                self.filter_level = logging.WARNING
            elif new_value == "ERROR":
                self.filter_level = logging.ERROR

        elif property_name == "showDebug":
            if self["appearance"] == "tabs":
                if not new_value:
                    self.tab_widget.removeTab(self.tab_widget.indexOf(self.debug_log))

        elif property_name == "emailAddresses":
            self.feedback_log.email_addresses = new_value
        elif property_name == "fromEmailAddress":
            self.feedback_log.from_email_address = new_value

        elif property_name == "enableFeedback":
            if self["appearance"] == "tabs":
                if not new_value:
                    self.tab_widget.removeTab(
                        self.tab_widget.indexOf(self.feedback_log)
                    )

        elif property_name == "appearance":
            if new_value == "list":
                self.tab_levels = {
                    logging.NOTSET: self.info_log,
                    logging.DEBUG: self.info_log,
                    logging.INFO: self.info_log,
                    logging.WARNING: self.info_log,
                    logging.ERROR: self.info_log,
                    logging.CRITICAL: self.info_log,
                }

                self.tab_widget.removeTab(self.tab_widget.indexOf(self.details_log))
                self.tab_widget.removeTab(self.tab_widget.indexOf(self.debug_log))

            elif new_value == "tabs":
                self.tab_levels = {
                    logging.NOTSET: self.details_log,
                    logging.DEBUG: self.debug_log,
                    logging.INFO: self.info_log,
                    logging.WARNING: self.details_log,
                    logging.ERROR: self.details_log,
                    logging.CRITICAL: self.details_log,
                }

        elif property_name == "maxLogLines":
            self.details_log.set_max_log_lines(new_value)
            self.info_log.set_max_log_lines(new_value)
            self.debug_log.set_max_log_lines(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
