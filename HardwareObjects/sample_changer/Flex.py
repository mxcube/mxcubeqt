from .GenericSampleChanger import *

import xml.sax
from xml.sax import SAXParseException
from xml.sax.handler import ContentHandler
import os
from HardwareRepository.Command.Exporter import exporter_clients

class Pin(Sample):        
    def __init__(self,basket,basket_no,sample_no, sBarcode, sState):
        super(Pin, self).__init__(basket, Pin.getSampleAddress(basket_no,sample_no), True)
        self._setHolderLength(27.0)
        self.Barcode=sBarcode
        self.state=sState
        self.PuckPos=basket_no
        self.SamplePos=sample_no
        #print "Pin",basket_no,sample_no, self.getContainer().getIndex()

    def getBasketNo(self):
        return self.getContainer().getIndex()+1

    def getVialNo(self):
        return self.getIndex()+1

    def getCoords(self):
		return (self.PuckPos, self.SamplePos)

    def getID(self):
		return self.Barcode
		
    @staticmethod
    def getSampleAddress(basket_number, sample_number):
		#print "getSampleAddress", str(basket_number) + ":" + "%02d" % (sample_number)
		return str(basket_number) + ":" + "%02d" % (sample_number)

class Basket(Container):
    __TYPE__ = "Puck"    
    __maxSamples__=0   
    def __init__(self,container,number):
        super(Basket, self).__init__(self.__TYPE__,container,Basket.getBasketAddress(number),True)
        self.Position=number
        for i in range(self.__maxSamples__):
            slot = Pin(self,number,i+1,"","")
            self._addComponent(slot)
    def getID(self):
		return self.Position
                            
    def addSample(self,sample):
        if len(self.getComponents())<= self.__maxSamples__:
            self._addComponent(sample)
        else:
			raise BaseException("Ak Error max sample "+str(len(self.getComponents())))
                            
    @staticmethod
    def getBasketAddress(basket_number):
        return str(basket_number)

    def clearInfo(self):
        self.getContainer()._reset_basket_info(self.getIndex()+1)
        self.getContainer()._triggerInfoChangedEvent()
            

class NoneBasket(Basket):
    __TYPE__ = "Puck"
    __STYPE__ = "None"
    __maxSamples__=0   
    def __init__(self,container,number):
        super(NoneBasket, self).__init__(container, number)

class MiniSpineBasket(Basket):
    __TYPE__ = "Puck"
    __STYPE__ = "MiniSpine"
    __maxSamples__=36   
    def __init__(self,container,number):
        super(MiniSpineBasket, self).__init__(container, number)
            
class UniPuckBasket(Basket):
    __TYPE__ = "Puck"
    __STYPE__ = "UniPuck"
    __maxSamples__=16   
    def __init__(self,container,number):
        super(UniPuckBasket, self).__init__(container, number)
            
class SpinePlusBasket(Basket):
    __TYPE__ = "Puck"
    __STYPE__ = "SpinePlus"
    __maxSamples__=15   
    def __init__(self,container,number):
        super(SpinePlusBasket, self).__init__(container, number)
            
class SC3Basket(Basket):
    __TYPE__ = "Puck"
    __STYPE__ = "SC3"
    __maxSamples__=10   
    def __init__(self,container,number):
        super(SC3Basket, self).__init__(container, number)
            
            
class XMLDataMatrixReadingHandler(ContentHandler):
    def __init__(self,maxBasketIdx):
        ContentHandler.__init__(self)
        self.dataMatrixList = []
        self.basketDataMatrixList = [('',4)] *maxBasketIdx
        self.dataMatrix = ''
        self.basketLocation = -1
        self.sampleLocation = -1
        self.flag = 0
        self.holder_length=222.0

    def startElement(self, name, attrs):
        self.addBasketLocation = name == "BasketLocation"
        self.addSampleLocation = name == "Location"
        self.addDataMatrix = name == "DataMatrix"
        self.addFlag = name in ("SampleFlag","BasketFlag")
        self.addHolderLength = name == "HolderLength"        

    def characters(self, content):
        if self.addDataMatrix:          self.dataMatrix = str(content)
        elif self.addBasketLocation:    self.basketLocation = int(content)
        elif self.addSampleLocation:    self.sampleLocation = int(content)
        elif self.addFlag:              self.flag = int(content)
        elif self.addHolderLength:      self.holder_length =  float(content)

    def endElement(self, name):
        if name == "Sample":
            self.dataMatrixList.append((self.dataMatrix,self.basketLocation,self.sampleLocation,self.flag,self.holder_length))
            self.dataMatrix = ''
            self.basketLocation = -1
            self.sampleLocation = -1
            self.flag = 0
            self.holder_length=223.0
        elif name == "Basket":
            if len(self.dataMatrix) > 0:
                self.basketDataMatrixList[self.sampleLocation-1]=(self.dataMatrix,self.flag)
            self.dataMatrix = ''
            self.basketLocation = -1
            self.sampleLocation = -1
            self.flag = 0
            self.holder_length=22.0
        elif name == "BasketLocation":              self.addBasketLocation = None
        elif name == "Location":                    self.addSampleLocation = None
        elif name == "DataMatrix":                  self.addDataMatrix = None        
        elif name in ("SampleFlag","BasketFlag"):   self.addFlag = None
        elif name == "HolderLength":                self.addHolderLength = None
            
    
class Flex(SampleChanger):
    __TYPE__ = "FLEX"
    __maxBasketIdx__ = 24
    SAMPLE_ALREADY_MOUNTED = '-231'
    
    state_converter = { "ALARM": SampleChangerState.Alarm,
                            "FAULT": SampleChangerState.Fault,
                            "MOVING": SampleChangerState.Moving,
                            "STANDBY": SampleChangerState.Ready,
                            "READY": SampleChangerState.Ready,
                            "RUNNING": SampleChangerState.Moving,
                            "LOADING": SampleChangerState.Charging,
                            "LOADING": SampleChangerState.Charging,
                            "INITIALIZING": SampleChangerState.Initializing }


    """
    Concrete implementation of FLEX Sample Changer
    """    
    def __init__(self, *args, **kwargs):
        super(Flex, self).__init__(self.__TYPE__,True, *args, **kwargs)
	basket = SpinePlusBasket(self,1)
	self._addComponent(basket)
	basket = UniPuckBasket(self,2)
	self._addComponent(basket)
	basket = MiniSpineBasket(self,3)
	self._addComponent(basket)
        for i in range(self.__maxBasketIdx__ - 2):
            basket = SC3Basket(self,i+4)
            self._addComponent(basket)
	    
    def init(self):

        self.exporterClient=""
        self._setTimerUpdateInterval(10)
        self.onGoingTasks=[]  
        self.currentTaskId=""    
        self.startStamp=""    
        self.endStamp=""    
        self.exporterAttributes=["LastTaskException","LastTaskInfo", "PresentPucks", "State","MountedSamplePosition", "PresentSamples", "Status", "LIST", "PLST"]
        self.holder_length = self.getProperty("holderLength")
        self.tangoDevice = self.getProperty("tangoDevice") # set using flex-mockup.xml
        self.exporterDevice = self.getProperty("exporterDevice") # set using flex-mockup.xml
        self.comMode = self.getProperty("comMode") # set using flex-mockup.xml
	print "AK comMode", self.comMode
        self.__maxBasketIdx__ = self.getProperty("maxPucks") # set using flex-mockup.xml
        if self.comMode is None: self.comMode="exporter"
        if self.tangoDevice is None: self.tangoDevice="tango://CRG14-MADCAD.esrf.fr:18001/embl/flex/1#dbase=no"
        if self.exporterDevice is None: self.exporterDevice="wbm14staubli.esrf.fr:9001"
	print "Flex self.__maxBasketIdx__ ", self.__maxBasketIdx__ 
	print "Flex exporterDevice", self.exporterDevice
	if self.comMode=="tango": self.initTango()
	else: 
		try:
			self.initExporter()
		except:
			pass
	self.initWithPresentSamples()  
#######AK
    	self.currentSampleLocation=None
#######

	SampleChanger.init(self) 

    def initTango(self):      
	# Tango methods
        for command_name in ("scanSamples", "loadSample", "unloadSample", "getSampleIsLoaded", "getPresentPucks"):
		self.addCommand({ "type": "tango", "name": command_name, "tangoname": self.tangoDevice }, command_name)

	# Tango attributes
      	for channel_name in ("SampleIsLoaded","PresentPucks"):
         	self.addChannel({"type":"tango", "name": channel_name, "tangoname": self.tangoDevice }, channel_name)
        	#setattr(self, channel_name, self.getChannelObject(channel_name))  

          

    def initExporter(self):
		try:
			self.channel_type="exporter"		
			self.exporter_address=self.exporterDevice	      
			for channel_name in self.exporterAttributes:
				exporterChannel=self.addChannel({"type": "exporter", "name":channel_name}, channel_name)
				
			for command_name in ("scanSamples", "loadSample", "unloadSample", "getPresentPucks", "parkRobot", "initRobot","scanSamples","reloadPucks"):
				self.addCommand({ "type": "exporter", "name": command_name }, command_name)
			
			self.setExporterClient()
			self.exporterClient.register('State', self.stateCallbak)
			self.exporterClient.register('Status', self.statusCallbak)
			self.exporterClient.register('LastTaskInfo', self.lastTaskInfoCallBack)
			self.exporterClient.register('PresentSamples', self.updateInfoCallBack)
		except:
			pass
        
    def setExporterClient(self):       
		address, port = self.exporter_address.split(":")
		port =int(port)
		self.exporterClient=exporter_clients[(address, port)]
		return self.exporterClient
#---------------------------Exporter CallBacks --------------------------------
    def stateCallbak(self,value):
		formerState=self.state
		self.state=value
		self._triggerStateChangedEvent(formerState)

		
    def statusCallbak(self,value):
		self.status=value
		print "statusCallbak", value
		self._triggerStatusChangedEvent()

    def lastTaskInfoCallBack(self, lastTaskInfo):    
		#print "AK Flex lastTaskInfoCallBack", lastTaskInfo
		#remove the TaskId lastTaskInfo[7], from the onGoingTasks List
		try:
			self.onGoingTasks.remove(lastTaskInfo[7])
		except: pass

		# if there is an error trigger the EcxeptionEvent
		if len(lastTaskInfo)>6 and lastTaskInfo[6]<>'1': #On a une erreur
			print "AK triggerExceptionEvent", lastTaskInfo[5]
			self._triggerExceptionEvent(lastTaskInfo[5])
		

		
    def updateInfoCallBack(self, sampleList):  
        print "AK Flex updateInfoCallBack", sampleList
        self.setWithPresentSamples(sampleList)
        self._triggerInfoChangedEvent()
		
#-------------------------------------------------------------------------------
    def getSampleByCoords(self, location):       
		for s in self.getSampleList():
			if (s.getCoords()==location):
				return s        
		return None

    def get_holder_length(self):
        return self.holder_length  
           
    def getSampleProperties(self):
        return (Pin.__HOLDER_LENGTH_PROPERTY__,)
            
        
    def isSampleLoaded(self):
	return self.getChannelObject("SampleIsLoaded").getValue()
        
    def getBasketList(self):
	return self.getComponents()

    def readFlexAtttribut(self, Attribut):
		return self.getChannelObject(Attribut).getValue()
        
    def getLastTaskInfo(self):
		#LastTaskInfo: ['defreezing gripper', '0', '2015-08-19 10:32:21.498', '2015-08-19 10:32:23.501', 'true', 'null', '1']
		return self.getChannelObject("LastTaskInfo").getValue()
        
    def getLastTaskStamps(self):
		return (self.getLastTaskInfo()[2],self.getLastTaskInfo()[3])
        
    def getPresentPucks(self):
		return self.getChannelObject("PresentPucks").getValue()
        
    def getFlexState(self):
		return self.getChannelObject("State").getValue()
	
    def getStatus(self):
		return self.getChannelObject("Status").getValue()
        
    def addBasket(self, id, stype):
		#print "self.addBasket(" +str(id)+", "+type+")"
		type=stype.lower()
		if (type=="unipuck"):
			basket=UniPuckBasket(self,id)
		elif (type=="minispine"):
			basket=MiniSpineBasket(self,id)
		elif (type=="sc3_puck"):
			basket=SC3Basket(self,id)
		elif (type=="spineplus"):
			basket=SpinePlusBasket(self,id)
		else:
			basket=NoneBasket(self,id)
		self._addComponent(basket)
		return basket
###################        
    def initWithPresentSamples(self):
		sampleList = self.getChannelObject("PresentSamples").getValue()
		#print "AK ",sampleList
		self.setWithPresentSamples(sampleList)
	
	
    def setWithPresentSamples(self, sampleList):
		self._clearComponents()
		plist = sampleList.split(":")
		curPpos=""
		for p in plist:
			if p=="":
				break
			(pPos, pType,pBarCode,sPos,sBarcode,sState) = p.split(",")
			if pPos<>curPpos:
				curP=self.addBasket(int(pPos), pType.lower())
				curP._clearComponents()
				curPpos=pPos
			fPin=Pin(curP,int(pPos),int(sPos), sBarcode, sState)
			if sState=="on_gonio":
				fPin.loaded=True
			curP.addSample(fPin)
		return len(self.getComponents())
#---------------------------------------------------------------------------------------------
    def reloadPucks(self, puckList):
		pl=[]
		for p in puckList:
			if p is not None:pl.append(p)		
		self._AKexecuteServerTask(self._doReloadPucks, pl)
			
    def reloadPuck(self, puckNumber):
		self.reloadPucks([puckNumber])

    def scanSamples(self, keepBarCodes):
		self._AKexecuteServerTask(self._doScanSamples, keepBarCodes)

    def clearInfo(self):
		self.scanSamples(True)

    def parkRobot(self):
		self._AKexecuteServerTask(self._doParkRobot)

    def initRobot(self):
		self._AKexecuteServerTask(self._doInitRobot)

    def load_sample(self, holder_length, sample_location, wait):
	sl=(str(sample_location[0]), str(sample_location[1]))
	try:
		taskId=self._AKexecuteServerTask(self._doLoad,holder_length, sl)
		if wait:
			self.waitEndOfTask(taskId)
	except Exception as e:
		msg= "Flex load_sample "+ str(e.args)
		raise e
        return
	sample=self.getComponentByAddress(Pin.getSampleAddress(int(basketId), int(sampleId)))
	sample.loaded=True

    def unload_sample(self, holder_length, sample_location, wait):
	print str(self)+" Flex unload_sample:sample_location"+str(sample_location)
	sl=(str(sample_location[0]), str(sample_location[1]))
	try:
		taskId=self._AKexecuteServerTask(self._doUnload,holder_length, sl)
		if wait:
			self.waitEndOfTask(taskId)
	except Exception as e:
		msg= "Flex unload_sample "+ str(e.args)
		raise e
        return
	sample=self.getComponentByAddress(Pin.getSampleAddress(int(basketId), int(sampleId)))
	sample.loaded=False


#########################           TASKS           #########################
    def _doLoad(self,holder_length, sample_location):
		(sampleId, basketId)=sample_location
		taskId=self.getCommandObject("loadSample")(sampleId , basketId)
		return taskId
				

    def _doUnload(self,holder_length, sample_location):
		(sampleId, basketId)=sample_location
		taskId = self.getCommandObject("unloadSample")(sampleId, basketId)
		return taskId

    def _doParkRobot(self):
		return self.getCommandObject("parkRobot")()

    def _doInitRobot(self):
		return self.getCommandObject("initRobot")()

    def _doScanSamples(self, keepBarcodes):
		return self.getCommandObject("scanSamples")(keepBarcodes)
				
    def _doReloadPucks(self, puckList):
		return self.getCommandObject("reloadPucks")(puckList)
				
#-----------------------------------------------------------------------------------------------
    def _doAbort(self):
		#print "Flex _doAbort" 
		self._abort()            
            

    def updateInfo(self):    
        return


    def _doUpdateInfo(self):    # Not used anymore since events
        #print "Flex _doUpdateInfo"
        startStamp, endStamp = self.getLastTaskStamps()
        if self.startStamp<>startStamp or self.endStamp<>endStamp:
				self.initWithPresentSamples()
				self.startStamp=startStamp
				self.endStamp=endStamp
        else:
			self._resetDirty() # Do not trigger _triggerInfoChangedEvent. Nothing has changed

    def _doChangeMode(self,mode):
        print "Flex _doChangeMode" 
        if mode==SampleChangerMode.Charging:
            self._executeServerTask(self._set_sample_charge, True)                    
        elif mode==SampleChangerMode.Normal:
            self._executeServerTask(self._set_sample_charge, False)
    
    def _doScan(self,component, recursive):
        #print "Flex _doScan" 
        selected_basket = self.getSelectedComponent()
        if isinstance(component, Sample):            
            if (selected_basket is None) or (selected_basket != component.getContainer()):
                self._doSelect(component)            
            self._executeServerTask(self._scan_samples, [component.getIndex()+1,])
            
        elif isinstance(component, Container) and ( component.getType() == Basket.__TYPE__):
            if recursive:
                self._executeServerTask(self._scan_basket, (component.getIndex()+1))                
            else:
                if (selected_basket is None) or (selected_basket != component):
                    self._doSelect(component)            
                self._executeServerTask(self._scan_samples, (0,))                
        elif isinstance(component, Container) and ( component.getType() == Flex.__TYPE__):
            for basket in self.getComponents():
                self._doScan(basket, True)
    
    def _doSelect(self,component):
		print "Flex _doSelect" 
		if isinstance(component, Sample):
			selected_basket = self.getSelectedComponent()
			if (selected_basket is None) or (selected_basket != component.getContainer()):
				self._executeServerTask(self._select_basket , component.getBasketNo())
			self._executeServerTask(self._select_sample, component.getIndex()+1)
		elif isinstance(component, Container) and ( component.getType() == Basket.__TYPE__):
			self._executeServerTask(self._select_basket, component.getIndex()+1)
			
 
    def _doReset(self):
		#print "Flex _doReset" 
		self._executeServerTask(self._reset)

    def clearBasketInfo(self, basket):
		#print "Flex clearBasketInfo" 
		self._reset_basket_info(basket)


        
#########################           PRIVATE           #########################        
    def _AKexecuteServerTask(self, method, *args):
		if self.exporterClient=="":
			try	:
				self.initExporter()
			except:
				raise 
				
		task_id = method(*args)
		self.currentTaskId=str(task_id)
		# Add the task in the ongoing tasks list
		# it will be removed by the lastTaskInfo callBack function at the end of the task
		self.onGoingTasks.append(self.currentTaskId)
		return self.currentTaskId
		
    def waitEndOfTask(self,tId):	
		while tId in self.onGoingTasks:
			time.sleep(1)
		
#-------------------------------------------------------------------------------
    def _executeServerTask(self, method, *args):
		
		#print "Flex _executeServerTask" 
		self._waitDeviceReady(3.0)
		task_id = method(*args)
		ret=None
		if task_id is None: #Reset
			while self._isDeviceBusy():
				gevent.sleep(0.1)
		else:
			while str(self._is_task_running(task_id)).lower() == 'true': 
				gevent.sleep(0.1)            
			try:
				print "------------------"
				ret = self._check_task_result(task_id)                
			except Exception,err:
				raise 
		return ret

    def _updateState(self):
		#print "Flex _updateState" 
		try:
		  state = self._readState()
		except:
		  state = SampleChangerState.Unknown
		if state == SampleChangerState.Moving and self._isDeviceBusy(self.getState()):
			return          
		self._setState(state)
       

################################# TESTS ############################################
    def testEvent(self):
		name="grippertemperatureValue"
		self.exporterClient.register('grippertemperatureValue', self.akCallbak)
		
    def akCallbak(self,value):
		print "AK grippertemperatureValue callback ", value
		

    def testchannel(self, name):
		print "Flex.test Attribut.. "+name+":", self.getChannelObject(name).getValue()

    def testCommand(self):
		name="reloadPucks"
		print "Flex.test command.. "+name+":", self.getCommandObject(name)()
                            
    def testexporter(self):
		exporterAttributes=["LastTaskException","LastTaskInfo", "PresentPucks", "State","Status","MountedSamplePosition", "PresentSamples"]
		for channel_name in exporterAttributes:
			self.addChannel({"type": "exporter", "name":channel_name}, channel_name)
            
		for channel_name in exporterAttributes:
			print channel_name+":", self.getChannelObject(channel_name).getValue()

#------------------------------------------------------------------------------------------------
import sys
def main():
	for arg in sys.argv:
	    print arg

if __name__ == "__main__": 
	sc=Flex()
	sc.init()
	if len(sys.argv)>1:
		if sys.argv[1]=='l':
			sc.AsyncLoadsample(sys.argv[2],sys.argv[3])
		elif sys.argv[1]=='u':
			sc.AsyncUnloadsample(sys.argv[2],sys.argv[3])
		elif sys.argv[1]=='t':
			sc.testexporter()
	else:
		#sc.testexporter()
		#sc.testchannel("PresentSamples")
		#print sc.exporterClient.getMethodList()
		#print sc.exporterClient.getPropertyList()
		for p in sc.getComponents():
			print p.getID()
		print sc.getComponentById("1")
		print sc.getComponentById("1")




        

