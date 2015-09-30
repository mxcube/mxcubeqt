from qt import *
import email.Utils
import smtplib
from BlissFramework import BaseComponents
from BlissFramework import Icons
import BlissFramework
import logging
import os
import xmlrpclib

__category__ = 'gui_utils'

###
### Widget to submit a feedback email
###
class FeedbackBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('emailAddresses', 'string', '')
        self.addProperty('icons', 'string', '')
        self.addProperty("jira_server", 'string', '')
        self.addProperty("jira_user", 'string', '')
        self.addProperty("jira_passwd", "string", "")
        self.addProperty("jira_project","string","")

        self.currentProposal=None

        self.defineSlot('setSession',())

        msg = ["Feel free to report any comment about this software;",
               " an email will be sent to the people concerned.",
               "Do not forget to put your name or email address if you require an answer."]
        label=QLabel("<i>%s</i>" % "\n".join(msg), self)

        box1=QWidget(self)
        QGridLayout(box1, 2, 2, 0, 2)

        email_label=QLabel("Your email:",box1)
        box1.layout().addWidget(email_label, 0, 0)
        self.sendersEmail=QLineEdit(box1)
        box1.layout().addWidget(self.sendersEmail,0,1)

        box2=QVBox(box1)
        message_label=QLabel('Message:',box2)
        message_label.setAlignment(Qt.AlignTop)
        self.submitButton=QToolButton(box2)
        self.submitButton.setTextLabel('Submit')
        self.submitButton.setUsesTextLabel(True)
        self.submitButton.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        QObject.connect(self.submitButton, SIGNAL('clicked()'), self.submitMessage)
        box1.layout().addWidget(box2, 1, 0)
        self.message=QTextEdit(box1)
        box1.layout().addWidget(self.message,1,1)

        QVBoxLayout(self)
        self.layout().addWidget(label)
        self.layout().addWidget(box1)

        box1.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

        QToolTip.add(self.message,"Write here your comments or feedback")
        QToolTip.add(self.submitButton,"Click here to send your feedback to the authors of this software")

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'emailAddresses':
            pass
        elif propertyName == 'icons':
            icons_list=newValue.split()
            try:
                self.submitButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)        

    def setSession(self,session_id,prop_code=None,prop_number=None):
        if prop_code is None or prop_number is None or prop_code=='' or prop_number=='':
            self.currentProposal=None
            self.sendersEmail.clear()
        else:
            self.currentProposal=(prop_code,prop_number)

    def submitMessage(self):
        msg_date = email.Utils.formatdate(localtime=True)
        
        try:
            frombl = os.environ['BEAMLINENAME'].lower()
        except (KeyError,TypeError,ValueError,AttributeError):
            frombl = 'unknown-beamline'

        try:
            local_user = os.environ['USER'].lower()
        except (KeyError,TypeError,ValueError,AttributeError):
            local_user = 'unknown_user'
        fromaddr = "%s@esrf.fr" % local_user

        try:
            smtp = smtplib.SMTP('smtp', smtplib.SMTP_PORT)
            toaddrs = self['emailAddresses'].replace(' ', ',')

            senders_email=str(self.sendersEmail.text())
            if len(senders_email):
                toaddrs+=","+senders_email

            if self.currentProposal is None:
                prop_str="unknown proposal"
            else:
                prop_str="%s-%s" % (self.currentProposal[0],self.currentProposal[1])

            subj="[BEAMLINE FEEDBACK] %s on %s (%s)" % (prop_str,frombl,BlissFramework.loggingName)
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

            if self["jira_server"]:
              jira_server = xmlrpclib.Server(self["jira_server"]+"/rpc/xmlrpc")
              auth = jira_server.jira1.login(self["jira_user"], self["jira_passwd"])
              jira_customfield = [{"customfieldId" : "customfield_10794",
                                   "values" : ["No"]},
                                   {"customfieldId" : "customfield_11290",
                                    "values" : ["No"]}]
              data = {"project": self["jira_project"],
                      "customFieldValues": jira_customfield, "type": 5,
                      "summary": subj,
                      "description": str(self.message.text())}
              jira_server.jira1.createIssue(auth, data)
            self.message.clear()
