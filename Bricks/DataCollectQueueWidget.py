from qt import *
import qttable
import logging
from BlissFramework import Icons
import os
import copy

class optionalDoubleValidator(QDoubleValidator):
    def validate(self,string,pos):
        if len(str(string)):
            return QDoubleValidator.validate(self,string,pos)
        return QDoubleValidator.validate(self,"0.0",pos)

class optionalIntValidator(QIntValidator):
    def validate(self,string,pos):
        if len(str(string)):
            return QIntValidator.validate(self,string,pos)
        return QIntValidator.validate(self,"0",pos)

class directoryValidator(QIntValidator):
    def setSpecificValidator(self,prop):
        self.proposalCode=prop[0]
        self.proposalNumber=prop[1]
    def validate(self,string,pos):
        try:
            prop_code=self.proposalCode
            prop_number=self.proposalNumber
        except AttributeError:
            valid=False
        else:
            dirs=str(string).split(os.path.sep)
            try:
                dirs.index("%s%s" % (self.proposalCode,self.proposalNumber))
            except ValueError:
                valid=False
            else:
                valid=True
        if valid:
            return QIntValidator.validate(self,"0",pos)
        return QIntValidator.validate(self,"a",pos)

class comboItem(qttable.QComboTableItem):
    MODES=["Software binned","Unbinned","Hardware binned"]
    def setQueueItemValue(self,value):
        try:
            value_index=self.MODES.index(value)
        except ValueError:
            pass
        else:
            self.setCurrentItem(value_index)
    def getQueueItemValue(self):
        return self.MODES[self.currentItem()]

class checkItem(qttable.QCheckTableItem):
    def setQueueItemValue(self,value):
        self.setChecked(value)
    def getQueueItemValue(self):
        return self.isChecked()

class editItem(qttable.QTableItem):
    def setQueueItemValue(self,value):
        self.setText(str(value))
    def getQueueItemValue(self):
        return str(self.text())
    def setContentFromEditor(self,w):
        qttable.QTableItem.setContentFromEditor(self,w)
        if self.myLineEdit is not None and self.myLineEdit.validator() is not None:
            if self.myLineEdit.hasAcceptableInput():
                self.myLineEdit.setPaletteBackgroundColor(QWidget.white)
    def createEditor(self):
        if not self.isEnabled():
            self.myLineEdit=None
            return None
        self.myLineEdit=qttable.QTableItem.createEditor(self)
        try:
            self.myLineEdit.setValidator(self.myValidator)
        except AttributeError:
            pass
        else:
            self.myLineEdit.setAlignment(self.myAlign)
        QObject.connect(self.myLineEdit,SIGNAL('textChanged ( const QString & )'),self.lineEditChanged)
        try:
            QObject.connect(self.myLineEdit,PYSIGNAL('inputValid'),self.processValidFun)
        except AttributeError:
            pass
        return self.myLineEdit
    def setValidator(self,validator):
        self.myAlign=QWidget.AlignRight
        self.myValidator=validator
    def lineEditChanged(self,text):
        valid=None
        if self.myLineEdit.validator() is not None:
            if self.myLineEdit.hasAcceptableInput():
                valid=True
                self.myLineEdit.setPaletteBackgroundColor(QWidget.yellow)
            else:
                valid=False
                self.myLineEdit.setPaletteBackgroundColor(QWidget.red)
        if valid is not None:
            self.myLineEdit.emit(PYSIGNAL("inputValid"),(self,valid,))
    def connectInputValid(self,process_valid_fun):
        self.processValidFun=process_valid_fun

class directoryItem(editItem):
    pass

class boolEditItem(editItem):
    def setQueueItemValue(self,value):
        if value[0]:
            self.setText(str(value[1]))
        else:
            self.setText("")
    def getQueueItemValue(self):
        text=str(self.text())
        if len(text):
            return (True,text)
        return (False,"")

class DataCollectQueueWidget(QWidget):
    DETECTOR_MODE_ITEMS = ( "software", "unbinned", "hardware" )

    PARAMETERS = {
        "prefix":(0, "Prefix", True, None, None),\
        "osc_start":(1, "Osc.start", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,)),\
        "osc_range":(2, "Osc.range", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,)),\
        "overlap":(3, "Overlap", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,)),\
        "exposure_time":(4, "Exp.time", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0)),\
        "number_passes":(5, "N.passes", None, [editItem,qttable.QTableItem.Always], (QIntValidator,1)),\
        "energy":(6, "Energy", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0)),\
        "transmission":(7, "Transmission", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0)),\
        "resolution":(8, "Resolution", None, [editItem,qttable.QTableItem.Always], (QDoubleValidator,0.0)),\
        "detector_mode":(9, "Binning", None, [comboItem,None], None),\
        "inverse_beam":(10, "Inverse beam", None, [boolEditItem,qttable.QTableItem.Always], (optionalIntValidator,1)),\
        "run_number":(11, "Run number", None, [editItem,qttable.QTableItem.Always], (QIntValidator,0)),\
        "first_image":(12, "1st image", None, [editItem,qttable.QTableItem.Always], (QIntValidator,0)),\
        "number_images":(13, "N.images", None, [editItem,qttable.QTableItem.Always], (QIntValidator,1)),\
        "comments":(14, "Comments", None, None, None),\
        "directory":(15, "Directory", None, [directoryItem,qttable.QTableItem.Always], [directoryValidator,None,None]),\
        "barcode":(16, "Barcode", True, None, None),\
        "location":(17, "Location", True, None, None)
    }
    #"inverse_beam":(10, "Inverse beam", None, (qttable.QCheckTableItem,"inverse")),\
    #    "prefix":(0, "Prefix",),\
    #    "dose_mode":(11, "Dose mode", None, (qttable.QCheckTableItem,"dose")),\
    #    "start_phi_curr_pos":(10, "Phi start", None, (checkItem,"from current")),\

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.lastSpecReady = False

        self.queueList = []
        self.table=qttable.QTable(0, 18, self)
        self.table.setLeftMargin(0)
        #self.table.setColumnMovingEnabled(True)
        #self.table.setRowMovingEnabled(True)
        self.connect(self.table,SIGNAL('contextMenuRequested ( int, int, const QPoint & )'),self.queueContextMenu)

        self.validDict = {}
        self.lastValid = True

        self.buttonsContainer=QHBox(self)
        HorizontalSpacer(self.buttonsContainer)
        self.collectButton=QToolButton(self.buttonsContainer)
        self.collectButton.setUsesTextLabel(True)
        self.collectButton.setTextPosition(QToolButton.BesideIcon)
        self.collectButton.setTextLabel("Collect queue")
        self.collectButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.collectButton.setEnabled(False)
        QObject.connect(self.collectButton,SIGNAL('clicked()'),self.collectQueue)

        det_mode_list=QStringList()
        DataCollectQueueWidget.PARAMETERS["detector_mode"][3][1] = det_mode_list

        for param_name in DataCollectQueueWidget.PARAMETERS:
            param=DataCollectQueueWidget.PARAMETERS[param_name]
            param_index=param[0]
            param_label=param[1]
            param_readonly=param[2]
            param_type=param[3]
            self.table.horizontalHeader().setLabel(param_index,param_label)        
            if param_readonly:
                self.table.setColumnReadOnly(param_index,True)

        self.table.setLeftMargin(4*self.table.leftMargin())

        QVBoxLayout(self,1,2)
        self.layout().addWidget(self.table)
        self.layout().addWidget(self.buttonsContainer)

    def setProposal(self,prop_code,prop_number):
        if prop_code is None:
            self.clearEntireQueue()
            validator=None
        else:
            validator=(prop_code,prop_number)
        DataCollectQueueWidget.PARAMETERS["directory"][4][2] = validator

    def setDetectorType(self,detector_type):
        if detector_type=='adsc':
            for s in DataCollectQueueWidget.DETECTOR_MODE_ITEMS:
                DataCollectQueueWidget.PARAMETERS["detector_mode"][3][1].append(s)
        else:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["detector_mode"][0],True)

    def disableDetectorMode(self):
        self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["detector_mode"][0],True)

    def contextMenuEvent(self,ev):
        count=len(self.queueList)
        if count>0:
            menu=QPopupMenu(self)
            label=QLabel('<nobr><b>Oscillation queue</b></nobr>',menu)
            label.setAlignment(Qt.AlignCenter)
            menu.insertItem(label)
            menu.insertSeparator()
            menu.insertItem("Clear entire queue",0)
            QObject.connect(menu,SIGNAL('activated(int)'),self.clearEntireQueue)
            menu.popup(QCursor.pos())

    def clearEntireQueue(self):
        self.queueList=[]
        self.table.setNumRows(0)
        self.validDict={}
        self.currentValid=True
        self.updateLength()

    def removeOscillation(self,row):
        redo_valid=False
        for i in range(self.table.numCols()):
            item=self.table.item(row,i)
            try:
                self.validDict.pop(item)
            except KeyError:
                pass
            else:
                redo_valid=True
        if redo_valid:
            current_valid=True
            for wid in self.validDict:
                if not self.validDict[wid]:
                    current_valid=False
            if current_valid!=self.lastValid:
                self.lastValid=current_valid
                self.collectButton.setEnabled(self.lastSpecReady and self.lastValid)

        self.table.removeRow(row)
        self.queueList.pop(row)
        self.updateLength()

    def queueContextMenu(self,row,col,point):
        #print "queueContextMenu",row,col,point
        if row==-1:
            return self.contextMenuEvent(None)

        menu=QPopupMenu(self)
        title=str(self.table.text(row,0))
        label=QLabel('<nobr><b>%s</b></nobr>' % title,menu)
        label.setAlignment(Qt.AlignCenter)
        menu.insertItem(label)
        menu.insertSeparator()
        menu.insertItem("Remove this oscillation",row)
        QObject.connect(menu,SIGNAL('activated(int)'),self.removeOscillation)
        menu.popup(QCursor.pos())

    def addParamDict(self,sample_info,collect_params,extra_parameters):
        #print "DataCollectQueueWidget.addParamDict",sample_info,collect_params,extra_parameters

        collect_params2=copy.deepcopy(collect_params)

        try:
            collect_params2["energy"]=extra_parameters["energy"]
        except KeyError:
            pass
        try:
            collect_params2["transmission"]=extra_parameters["transmission"]
        except KeyError:
            pass
        try:
            collect_params2["resolution"]=extra_parameters["resolution"]
        except KeyError:
            pass

        collect_params2["sample_info"]=sample_info

        self.queueList.append(collect_params2)

        row=self.table.numRows()
        self.table.insertRows(row)

        try:
            collect_params2['energy']
        except KeyError:
            try:
                collect_params2['energy']=extra_parameters["current_energy"]
            except KeyError:
                collect_params2['energy']=""
        try:
            collect_params2['transmission']
        except KeyError:
            try:
                collect_params2['transmission']=extra_parameters["current_transmission"]
            except KeyError:
                collect_params2['transmission']=""
        try:
            collect_params2['resolution']
        except KeyError:
            try:
                collect_params2['resolution']=extra_parameters["current_resolution"]
            except KeyError:
                collect_params2['resolution']=""

        for param_name in collect_params2:
            param_value=collect_params2[param_name]
            try:
                param_index=DataCollectQueueWidget.PARAMETERS[param_name][0]
            except KeyError:
                pass
            except:
                pass
            else:
                #print "addParamDict",param_index,param_name,param_value,self.table.isColumnReadOnly(param_index)
                param_type=DataCollectQueueWidget.PARAMETERS[param_name][3]
                if param_type is not None:
                    param_class=param_type[0]
                    try:
                        param_par=param_type[1]
                    except IndexError:
                        param_obj=param_class(self.table)
                    else:
                        param_obj=param_class(self.table,param_par)

                    param_validator=DataCollectQueueWidget.PARAMETERS[param_name][4]
                    if param_validator is not None:
                        class_validator=param_validator[0]
                        obj_validator=class_validator(None)
                        try:
                            param_class_validator=param_validator[1]
                        except IndexError:
                            pass
                        else:
                            if param_class_validator is not None:
                                obj_validator.setBottom(param_class_validator)
                        try:
                            param_class_validator2=param_validator[2]
                        except IndexError:
                            pass
                        else:
                            if param_class_validator2 is not None:
                                obj_validator.setSpecificValidator(param_class_validator2)
                        param_obj.setValidator(obj_validator)
                        param_obj.connectInputValid(self.isInputValid)

                    param_obj.setQueueItemValue(param_value)
                    if self.table.isColumnReadOnly(param_index):
                        param_obj.setEnabled(False)
                        if param_name=="transmission":
                            param_obj.setQueueItemValue(extra_parameters["fixed_transmission"])
                        elif param_name=="energy":
                            param_obj.setQueueItemValue(extra_parameters["fixed_energy"])
                    self.table.setItem(row,param_index,param_obj)
                else:
                    #try:
                    #    self.table.setText(row,param_index,str(param_value))
                    #except Exception,diag:
                    #    pass
                    self.table.setText(row,param_index,str(param_value))

        if collect_params2['energy']=="":
            collect_params2.pop('energy')
        if collect_params2['transmission']=="":
            collect_params2.pop('transmission')
        if collect_params2['resolution']=="":
            collect_params2.pop('resolution')

        if sample_info is not None:
            try:
                barcode=sample_info[1]["code"]
            except KeyError:
                pass
            else:
                param_index=DataCollectQueueWidget.PARAMETERS["barcode"][0]
                self.table.setText(row,param_index,barcode)

            try:
                basket=sample_info[1]["basket"]
            except KeyError:
                pass
            else:
                try:
                    vial=sample_info[1]["vial"]
                except KeyError:
                    pass
                else:
                    location="%d:%02d" % (basket,vial)
                    param_index=DataCollectQueueWidget.PARAMETERS["location"][0]
                    self.table.setText(row,param_index,location)

    def isInputValid(self,input_widget,valid):
        #print "IS INPUT VALID",input_widget,valid

        self.validDict[input_widget]=valid
        current_valid=True
        for wid in self.validDict:
            if not self.validDict[wid]:
                current_valid=False
        if current_valid!=self.lastValid:
            self.lastValid=current_valid
            self.collectButton.setEnabled(self.lastSpecReady and self.lastValid)

    def addParamList(self,selected_samples,collect_params,extra_parameters):
        #print "DataCollectQueueWidget.addParamList",selected_samples,collect_params

        try:
            current_energy=extra_parameters['current_energy']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["energy"][0],True)
        else:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["energy"][0],False)
        try:
            current_transmission=extra_parameters['current_transmission']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["transmission"][0],True)
            extra_parameters['fixed_transmission']=100
        else:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["transmission"][0],False)
        try:
            current_resolution=extra_parameters['current_resolution']
        except KeyError:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["resolution"][0],True)
        else:
            self.table.setColumnReadOnly(DataCollectQueueWidget.PARAMETERS["resolution"][0],False)

        if len(selected_samples):
            is_multiple=False
            if len(selected_samples)>1:
                is_multiple=True

            for sel_sample in selected_samples:
                for collect_param in collect_params:
                    if is_multiple:
                        #print sel_sample
                        #print collect_params
                        blsampleid=sel_sample[0]
                        sample_info=sel_sample[1]
                        if blsampleid is not None and blsampleid!="":
                            collect_param['prefix']="%s-%s" % (sel_sample[1]['protein_acronym'],sel_sample[1]['name'])
                            collect_param['directory']=os.path.join(collect_param['directory'],sel_sample[1]['protein_acronym'],sel_sample[1]['name'])
                        else:
                            collect_param['prefix']=sel_sample[1]['code']
                            collect_param['directory']=os.path.join(collect_param['directory'],sel_sample[1]['code'])

                    self.addParamDict(sel_sample,collect_param,extra_parameters)
        else:
            for collect_param in collect_params:
                self.addParamDict(None,collect_param,extra_parameters)

        self.updateLength()

    def updateLength(self):
        count=len(self.queueList)
        self.collectButton.setEnabled(self.lastSpecReady and count>0 and self.lastValid)
        self.emit(PYSIGNAL("queueLength"),(count,))

    def collectQueue(self):
        count=len(self.queueList)
        for row in range(count):
            for param_name in DataCollectQueueWidget.PARAMETERS:
                param=DataCollectQueueWidget.PARAMETERS[param_name]
                param_index=param[0]

                if not self.table.isColumnReadOnly(param_index):
                    param_type=DataCollectQueueWidget.PARAMETERS[param_name][3]
                    if param_type is not None:
                        text=self.table.item(row,param_index).getQueueItemValue()
                    else:
                        text=str(self.table.text(row,param_index))
                    self.queueList[row][param_name]=text

        self.emit(PYSIGNAL("collectQueue"),(self.queueList,))

    def setSpecReady(self,is_spec_ready):
        count=len(self.queueList)
        self.lastSpecReady=is_spec_ready
        self.collectButton.setEnabled(self.lastSpecReady and count>0 and self.lastValid)

    def setCollectQueueIcon(self,collect_icon):
        self.collectButton.setPixmap(Icons.load(collect_icon))

    def removeFirstOscillation(self):
        self.table.removeRow(0)
        self.queueList.pop(0)
        count=len(self.queueList)
        if count==0:
            self.validDict={}
            self.currentValid=True
        self.emit(PYSIGNAL("queueLength"),(count,))

class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
