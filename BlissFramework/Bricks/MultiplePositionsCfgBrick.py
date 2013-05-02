import logging
from qt import *
from BlissFramework.Bricks import MotorBrick
from BlissFramework.BaseComponents import BlissWidget

__category__ = 'Motor'

class ospDisplay(QHBox):
	def __init__(self, *args):
		QHBox.__init__(self, *args)
		
		self.radios = {}
		self.buttonGroup = QVButtonGroup("", self)
		self.vbox = QVBox(self)
				
	def setEquipment(self, equipment):			
		self.vbox.close(True)
		self.buttonGroup.close(True)
		self.radios = {}
		self.buttonGroup = QVButtonGroup("", self)
		self.vbox = QVBox(self)
		
		self.buttonGroup.setTitle(equipment.username) 
		for key in equipment.positionsIndex:
			self.radios[key] = QRadioButton(key, self.buttonGroup)

		for mot in equipment["motors"]:
			MotorBrick.MotorBrick(self.vbox)["mnemonic"] = mot.name()

		self.buttonGroup.show()
		self.vbox.show()
														
	def positionClicked(self):
		for name, radio in self.radios.items():
			if radio.isChecked():
				return name
	
class MultiplePositionsCfgBrick(BlissWidget):
	def __init__(self, *args):
		BlissWidget.__init__(self, *args)
		
		self.hwro = None
		self.defineSlot("setEquipment", ())
		
#		self.addProperty('mode', 'combo', ("absolute", "relative"), "absolute")
		self.addProperty('mnemonic', "string", "")
		
		QVBoxLayout(self)
		self.panelDisplay = ospDisplay(self)
		self.panel = QVBox(self)
		self.WSetPosition = QPushButton("Set New Position", self.panel)
		QObject.connect(self.WSetPosition, SIGNAL("clicked()"), \
										self.setPosition)

		self.layout().addWidget(self.panelDisplay)
		self.layout().addWidget(self.panel)		

	def propertyChanged(self, property, oldValue, newValue):
		if property == "mnemonic":
		  #if oldValue != newValue:
			self.setEquipment(newValue)

	def setEquipment(self, equipment):
		#if equipment != "":	
		self.getProperty("mnemonic").setValue(equipment)
		#self['mnemonic']=equipment
		
		self.hwro = self.getHardwareObject(equipment)
		
		if self.hwro is not None:
			self.disconnect(self.hwro, PYSIGNAL('equipmentReady'), self.equipmentReady)
			self.disconnect(self.hwro, PYSIGNAL('equipmentNotReady'), self.equipmentNotReady)
			self.connect(self.hwro, PYSIGNAL('equipmentReady'), self.equipmentReady)
			self.connect(self.hwro, PYSIGNAL('equipmentNotReady'), self.equipmentNotReady)
			
			self.panelDisplay.setEquipment(self.hwro)
			
			if self.hwro.isReady():
				self.equipmentReady()
				return
		
		self.equipmentNotReady()
				
	def equipmentReady(self):
		self.setEnabled(True)
		
	def equipmentNotReady(self):
		self.setEnabled(False)
		
	def setPosition(self):
		positionname = 	self.panelDisplay.positionClicked()
		if positionname is None:
			QMessageBox.warning(self, "Warning", "Select a position first")
			return

		if self.hwro.mode == "absolute":
			newValues = {}
			for mot in self.hwro["motors"]:
				newValues[mot.getMotorMnemonic()] = mot.getPosition()
				
			self.hwro.setNewPositions(positionname, newValues)
		else:
			for mot in self.hwro["motors"]:
				pos = mot.getDialPosition()
				mne = mot.getMotorMnemonic()
				val = self.hwro.positions[positionname][mne] - pos
				mot.setOffset(val)
			
