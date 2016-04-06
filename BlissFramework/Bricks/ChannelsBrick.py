import qt
from BlissFramework.BaseComponents import BlissWidget
import logging

__category__ = "General"

class ChannelsBrick(BlissWidget):
    def __init__(self, parent, name):
        BlissWidget.__init__(self, parent, name)

        self.addProperty("xmlFile", "string", "")
        self.addProperty("uiFile", "string", "")
        self.addProperty("expert_channels", "string", "", hidden=True)
        self.__brick_properties = list(self.propertyBag.properties.keys())
        self.hwo = None
        self.expert_channels = []
        self.property_expert_channels = {}
        
    def propertyChanged(self, prop, oldValue, newValue):
        if prop == "xmlFile":
            if not self.isRunning():
              # we are changing xmlFile in design mode
              for propname in list(self.propertyBag.properties.keys()):
                if not propname in self.__brick_properties: 
                  self.delProperty(propname)

            self.hwo = self.getHardwareObject(newValue)
            if self.hwo is None:
              return       
 
            if not self.isRunning():
              for channel in self.hwo.getChannels():
                self.addProperty("%s expert only" % channel.name(), "boolean", False)
        elif prop == "uiFile":
            self.widget = self.createGUIFromUI(newValue)
            self.widget.show()
        elif prop == 'expert_channels':
            if self.isRunning():
              # it is time to set expert channels
              expert_channels = eval(self["expert_channels"])
              for channel_prop in list(expert_channels.keys()):
                expert = expert_channels[channel_prop]
                try:
                  self.getProperty(channel_prop).setValue(expert)
                except:
                  del expert_channels[channel_prop] 
                  continue
              self.getProperty("expert_channels").setValue(str(expert_channels))
        else:
            if prop.endswith("expert only"):
                self.property_expert_channels[prop] = newValue
                self.getProperty("expert_channels").setValue(str(self.property_expert_channels))
  
    def run(self):
        self.expert_channels = []
        # trigger evaluation of previously saved expert channels
        self["expert_channels"] = self["expert_channels"]

        # look for all checkboxes
        all_checkboxes = self.widget.queryList("QCheckBox")
        for checkbox in all_checkboxes:
          channel_name = str(checkbox.name())
          channel = self.hwo.getChannelObject(channel_name)
          def channelValueChanged(new_value, widget=checkbox):
            widget.setChecked(str(new_value)=='1')
          channelValueChanged(channel.getValue())

          def widgetValueChanged(widget=checkbox, channel=channel):
            if widget.isChecked():
              channel.setValue(1)
            else:
              channel.setValue(0)

          channel.connectSignal("update", channelValueChanged)
          qt.QObject.connect(checkbox, qt.SIGNAL("clicked()"), widgetValueChanged)
          try:
            if self["%s expert only" % channel_name] and checkbox.isEnabled():
              # if widget is expert, but not enabled since the beginning: ignore
              self.expert_channels.append(checkbox)
              checkbox.setEnabled(False)
          except:
            logging.getLogger().exception("%s: could not set expert property for channel %s", self.name(), channel_name)

    def setExpertMode(self, expert):
        for widget in self.expert_channels:
          widget.setEnabled(expert) 

