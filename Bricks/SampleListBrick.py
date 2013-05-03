from BlissFramework import BaseComponents
import logging
from qt import *
import sys
from BlissFramework import Icons

__category__ = 'mxCuBE'

SAMPLELIST_GUI_EVENT = QEvent.User
class SampleListGUIEvent(QCustomEvent):
    def __init__(self, method, arguments):
        QCustomEvent.__init__(self, SAMPLELIST_GUI_EVENT)
        self.method = method
        self.arguments = arguments


class SampleListBrick(BaseComponents.BlissWidget):
    GROUPING = ("no grouping", "sample changer location", "protein acronym")
    FILTER_MSG = "Show only the samples inside the sample changer"

    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.activeThread=None

        self.sampleChanger=None
        self.dbServer=None
        self.sessionId=None
        self.proposal=None
        self.__refs={}
        self.loadedSampleDataMatrix=None
        self.loadedSampleLocation=None
        self.samplesInfo=[]
        self.sampleItem={}
        self.oscillationInfo={}
        self.oscillationItem={}
        self.dnaInfo={}
        self.dnaItem={}
        self.sample2Dna={}
        self.latestBarcodes=[]
        self.itemSingleSelected=None
        self.collectObj = None

        self.widthHint=None
        self.isCollecting=None

        self.unknownSampleItem=None

        self.contentsBox=QVGroupBox("Available samples",self)
        self.contentsBox.setInsideMargin(4)
        self.contentsBox.setInsideSpacing(2)

        self.sampleList=QListView(self.contentsBox)
        self.sampleList.setShowSortIndicator(True)
        self.sampleList.setAllColumnsShowFocus(True)
        self.sampleList.setSelectionMode(QListView.NoSelection)
        self.sampleList.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

        self.sampleList.addColumn("Name")
        self.sampleList.addColumn("Acronym")
        self.sampleList.addColumn("Barcode")
        self.sampleList.addColumn("Location")
        self.sampleList.addColumn("Space group")
        self.sampleList.addColumn("a   b   c   %s   %s   %s" % (u'\u03B1',u'\u03B2',u'\u03B3'))
        self.sampleList.addColumn("Min.res.")
        self.sampleList.addColumn("Basket")
        self.sampleList.setColumnAlignment(0,Qt.AlignLeft)
        self.sampleList.setColumnAlignment(1,Qt.AlignLeft)
        self.sampleList.setColumnAlignment(2,Qt.AlignLeft)
        self.sampleList.setColumnAlignment(3,Qt.AlignRight)
        self.sampleList.setColumnAlignment(4,Qt.AlignRight)
        self.sampleList.setColumnAlignment(5,Qt.AlignRight)
        self.sampleList.setColumnAlignment(6,Qt.AlignRight)
        self.sampleList.setColumnAlignment(7,Qt.AlignLeft)
        self.sampleList.setSorting(3)
        self.sampleList.setRootIsDecorated(True)

        self.connect(self.sampleList,SIGNAL('clicked(QListViewItem *)'),self.itemClicked)
        self.connect(self.sampleList,SIGNAL('contextMenuRequested ( QListViewItem *, const QPoint &, int)'),self.listContextMenu)
        self.connect(self.sampleList,SIGNAL('itemRenamed ( QListViewItem *, int, const QString &)'),self.resolutionItemRenamed)

        box2=QHBox(self.contentsBox)
        self.insideSCFilter=QCheckBox(SampleListBrick.FILTER_MSG,box2)
        self.insideSCFilter.setChecked(True)
        self.connect(self.insideSCFilter,SIGNAL('toggled(bool)'),self.filterList)

        HorizontalSpacer(box2)
        QLabel("Group by:",box2)
        self.groupSamples=QComboBox(box2)
        for grouping in SampleListBrick.GROUPING:
            self.groupSamples.insertItem(grouping)
        self.connect(self.groupSamples,SIGNAL('activated(const QString &)'),self.changeGrouping)

        self.refreshButton=QToolButton(box2)
        self.refreshButton.setTextLabel("Refresh")
        self.refreshButton.setUsesTextLabel(True)
        self.refreshButton.setTextPosition(QToolButton.BesideIcon)
        self.refreshButton.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        QObject.connect(self.refreshButton,SIGNAL("clicked()"),self.refreshList)

        self.addProperty('sampleChanger','string','')
        self.addProperty('dbServer','string','')
        self.addProperty('allowMultipleSelection','boolean',True)
        self.addProperty('icons','string','')
        self.addProperty('dataCollect','string')

        self.defineSlot('setSession',())
        self.defineSlot('setEnabled',())
        self.defineSlot('setCollecting',())
        self.defineSlot('updateList',())
        self.defineSlot('enqueueOscillation',())
        self.defineSlot('updateOscillation',())
        self.defineSlot('enqueueDNAStep',())
        self.defineSlot('updateDNAStep',())
        self.defineSlot('gotoOscillation',())

        self.defineSignal('sampleSelected',())
        self.defineSignal('oscillationSelected',())
        self.defineSignal('sampleClicked',())
        self.defineSignal('oscillationClicked',())
        self.defineSignal('dnaStepSelected',())
        self.defineSignal('sampleLoaded',())

        QVBoxLayout(self)
        self.layout().addWidget(self.contentsBox)

    def customEvent(self, event):
        logging.getLogger().debug("SampleListBrick: custom event (%s)" % str(event))

        if self.isRunning():
            if event.type() == SAMPLELIST_GUI_EVENT:
                try:
                    method=event.method
                    arguments=event.arguments
                except Exception,diag:
                    logging.getLogger().exception("SampleListBrick: problem in event! (%s)" % str(diag))
                except:
                    logging.getLogger().exception("SampleListBrick: problem in event!")
                else:
                    logging.getLogger().debug("SampleListBrick: custom event method is %s" % method)
                    if callable(method):
                        try:
                            method.im_func(*arguments)
                        except Exception,diag:
                            logging.getLogger().exception("SampleListBrick: uncaught exception! (%s)" % str(diag))
                        except:
                            logging.getLogger().exception("SampleListBrick: uncaught exception!")
                        else:
                            logging.getLogger().debug("SampleListBrick: custom event finished")
                    else:
                        logging.getLogger().warning('SampleListBrick: uncallable custom event!')

            self.activeThread.wait()
            self.activeThread=None

    def resolutionItemRenamed(self,item,col,res_str):
        res_str=str(res_str)
        if res_str!="":
            try:
                res=float(res_str)
            except:
                logging.getLogger().warning('Invalid resolution!')
                item.setText(6,"")
            else:
                if res<0.0:
                    logging.getLogger().warning('Invalid resolution!')
                    item.setText(6,"")

    def run(self):
        if self.widthHint is None:
            self.widthHint=self.sampleList.columnWidth(0)

    def setCollecting(self,enabled_state):
        self.isCollecting=not enabled_state

    def buildColumns(self,mode):
        if self.widthHint is None:
            self.widthHint=self.sampleList.columnWidth(0)
        if mode=="no grouping":
            self.sampleList.setColumnText(0, "Name")
            self.sampleList.setColumnWidth(1,self.widthHint)
            self.sampleList.setColumnWidth(7,self.widthHint)
        elif mode=="sample changer location":
            self.sampleList.setColumnText(0, "Basket / Name")
            self.sampleList.setColumnWidth(7,0)
        elif mode=="protein acronym":
            self.sampleList.setColumnText(0, "Acronym / Name")
            self.sampleList.setColumnWidth(1,0)

    def refreshList(self,oscillations2enqueue=[]):
        try:
          self.sampleChanger.updateDataMatrices()
        except:
          pass
        self.updateList(self.latestBarcodes,oscillations2enqueue)

    def changeGrouping(self,grouping):
        self.buildList(str(grouping))

    def clearList(self):
        for location in self.__refs:
            popup_menu=self.__refs[location]
            QObject.disconnect(popup_menu[0],SIGNAL('activated(int)'),popup_menu[1])
        self.__refs={}
        self.sampleList.clear()
        self.unknownSampleItem=None
        self.itemSingleSelected=None
        self.insideSCFilter.setText(SampleListBrick.FILTER_MSG)
        self.emit(PYSIGNAL("sampleSelected"),([],))
        self.emit(PYSIGNAL("oscillationSelected"), (None,))

    def filterList(self,show_only_inside):
        item=self.sampleList.firstChild()
        showing=0
        hidden=0
        child_showing=0
        sel_changed=False

        while item is not None:
            if isinstance(item,genericSampleItem):
                if show_only_inside:
                    if self.sampleChanger.sampleInSampleChanger(item):
                        item.setVisible(True)
                        showing+=1
                    else:
                        item.setVisible(False)
                        if item.isSelected():
                            sel_changed=True
                            item.setSelected(False)
                        hidden+=1
                else:
                    item.setVisible(True)
                    showing+=1
            elif isinstance(item,unknownSampleItem):
                item.setVisible(not show_only_inside)
                if show_only_inside:
                    hidden+=1
                else:
                    showing+=1
            elif isinstance(item,basketItem) or isinstance(item,proteinItem):
                child_showing=0
                child=item.firstChild()
                while child is not None:
                    if show_only_inside:
                        if child.isInSampleChanger():
                            child.setVisible(True)
                            showing+=1
                            child_showing+=1
                        else:
                            child.setVisible(False)
                            if item.isSelected():
                                sel_changed=True
                                item.setSelected(False)
                            hidden+=1
                    else:
                        item.setVisible(True)
                        showing+=1
                        child_showing+=1

                    child=child.nextSibling()
                if child_showing>0:
                    item.setVisible(True)
                else:
                    item.setVisible(False)

            item=item.nextSibling()

        if showing==0 and hidden==0:
            self.insideSCFilter.setText(SampleListBrick.FILTER_MSG)
        else:
            txt="%d sample" % showing
            if showing>1 or showing==0:
                txt+='s'
            if hidden>0:
                txt+=", %d hidden" % hidden
            self.insideSCFilter.setText("%s (%s)" % (SampleListBrick.FILTER_MSG,txt))

        if sel_changed:
            self.sampleSelectionChanged(self.getSelectedItems())

    def setSession(self,session_id,prop_code=None,prop_number=None,prop_id=None):
        self.sessionId=session_id
        self.clearList()
        self.samplesInfo=[]
        self.sampleItem={}
        self.oscillationInfo={}
        self.oscillationItem={}
        self.dnaInfo={}
        self.dnaItem={}
        self.sample2Dna={}

        if session_id is not None and session_id!="":
            self.proposal=(prop_code,prop_number,prop_id)

            session_collections=[]
            if self.collectObj is not None:
                session_collections=self.collectObj.getOscillations(session_id)
                if session_collections is None:
                    session_collections=[]

            self.refreshList(session_collections)

        else:
            self.proposal=None
            self.refreshList()

    def getSelectedItems(self):
        item_iterator=QListViewItemIterator(self.sampleList)
        selected_items=[]
        while item_iterator.current():
            if item_iterator.current().isSelected():
                selected_items.append(item_iterator.current())
            item_iterator+=+1
        return selected_items

    def enqueueOscillation(self,owner,blsampleid,barcode,location,collect_dict,oscillation_id,history_db=False,history_sc=False):
        blsampleid_item=None
        osc_item=None
        refilter=False

        if blsampleid is None and location is None and not history_db:
            if self.unknownSampleItem is None:
                self.unknownSampleItem=unknownSampleItem(self.sampleList)
                refilter=True

            try:
                osc_list=self.oscillationInfo[None]
            except KeyError:
                self.oscillationInfo[None]=[(oscillation_id,collect_dict)]
            else:
                self.oscillationInfo[None].append((oscillation_id,collect_dict))

            run_number=collect_dict['fileinfo']['run_number']
            osc_item=oscillationItem(self.unknownSampleItem,run_number,oscillation_id)
            try:
                osc_code=bool(collect_dict["collection_code"])
            except KeyError:
                osc_item.setFinished(None)
            else:
                osc_item.setFinished(osc_code)

            self.oscillationItem[oscillation_id]=[osc_item]
        else:
            if blsampleid is not None and not history_sc:
                try:
                    blsampleid_item=self.sampleItem[blsampleid]
                except KeyError:
                    pass
                else:
                    try:
                        osc_list=self.oscillationInfo[blsampleid]
                    except KeyError:
                        self.oscillationInfo[blsampleid]=[(oscillation_id,collect_dict)]
                    else:
                        self.oscillationInfo[blsampleid].append((oscillation_id,collect_dict))

                    run_number=collect_dict['fileinfo']['run_number']
                    osc_item=oscillationItem(blsampleid_item,run_number,oscillation_id)
                    try:
                        osc_code=bool(collect_dict["collection_code"])
                    except KeyError:
                        osc_item.setFinished(None)
                    else:
                        osc_item.setFinished(osc_code)
                    try:
                        osc_item_list=self.oscillationItem[oscillation_id]
                    except KeyError:
                        self.oscillationItem[oscillation_id]=[osc_item]
                    else:
                        osc_item_list.append(osc_item)

            if location is not None and not history_db:
                try:
                    barcode_item=self.sampleItem[location]
                except KeyError:
                    pass
                else:
                    if blsampleid_item is not barcode_item:
                        try:
                            osc_list=self.oscillationInfo[location]
                        except KeyError:
                            self.oscillationInfo[location]=[(oscillation_id,collect_dict)]
                        else:
                            self.oscillationInfo[location].append((oscillation_id,collect_dict))

                        run_number=collect_dict['fileinfo']['run_number']
                        osc_item=oscillationItem(barcode_item,run_number,oscillation_id)
                        try:
                            osc_code=bool(collect_dict["collection_code"])
                        except KeyError:
                            osc_item.setFinished(None)
                        else:
                            osc_item.setFinished(osc_code)
                        try:
                            osc_item_list=self.oscillationItem[oscillation_id]
                        except KeyError:
                            self.oscillationItem[oscillation_id]=[osc_item]
                        else:
                            osc_item_list.append(osc_item)

        if osc_item is not None and not history_db and not history_sc:
            self.sampleList.ensureItemVisible(osc_item)
            self.emit(PYSIGNAL("oscillationSelected"), (oscillation_id,))
            self.emit(PYSIGNAL("oscillationClicked"), ())

        if refilter and not history_sc and not history_db:
            self.filterList(self.insideSCFilter.isChecked())

    def enqueueDNAStep(self,step_id,step_name,step_desc,blsampleid,barcode,location):
        print "SampleListBrick.enqueueuDNAStep",step_id,blsampleid,barcode,location,step_name,step_desc

        blsampleid_item=None
        dna_item=None
        refilter=False

        self.dnaInfo[step_id]=[step_name,step_desc,None,None,None]

        class_name="%sItem" % step_name

        if blsampleid is None and location is None:
            if self.unknownSampleItem is None:
                self.unknownSampleItem=unknownSampleItem(self.sampleList)
                refilter=True
            exec("dna_item=%s(self.unknownSampleItem,step_desc,step_id)" % class_name)
            try:
                dna_steps=self.sample2Dna[None]
            except:
                dna_steps=[step_id]
            else:
                dna_steps.append(step_id)
            self.sample2Dna[None]=dna_steps
        else:
            if blsampleid is not None:
                try:
                    blsampleid_item=self.sampleItem[blsampleid]
                except KeyError:
                    pass
                else:
                    exec("dna_item=%s(blsampleid_item,step_desc,step_id)" % class_name)
                    try:
                        dna_steps=self.sample2Dna[blsampleid]
                    except:
                        dna_steps=[step_id]
                    else:
                        dna_steps.append(step_id)
                    self.sample2Dna[blsampleid]=dna_steps

            if location is not None:
                try:
                    barcode_item=self.sampleItem[location]
                except KeyError:
                    pass
                else:
                    exec("dna_item=%s(barcode_item,step_desc,step_id)" % class_name)
                    try:
                        dna_steps=self.sample2Dna[location]
                    except:
                        dna_steps=[step_id]
                    else:
                        dna_steps.append(step_id)
                    self.sample2Dna[location]=dna_steps

        if dna_item is not None:
            self.dnaItem[step_id]=dna_item
            dna_item.setFinished(None)
            self.sampleList.ensureItemVisible(dna_item)
            logging.getLogger().debug("SampleListBrick: enqueueDNAStep, dnaInfo %r" % (self.dnaInfo[step_id]))

            self.emit(PYSIGNAL("dnaStepSelected"), (step_name,step_desc,self.dnaInfo[step_id][2],self.dnaInfo[step_id][3],self.dnaInfo[step_id][4]))
        else:
            logging.getLogger().debug("SampleListBrick: enqueueDNAStep dna_item is None!" )

        if refilter:
            self.filterList(self.insideSCFilter.isChecked())

    def updateDNAStep(self,step_id,step_status,step_message,step_results):
        logging.getLogger().debug("SampleListBrick.updateDNAStep ,step_id %r,step_status %r,step_message %r,step_results %r" % (step_id,step_status,step_message,step_results))
        self.dnaInfo[step_id][2]=step_status
        self.dnaInfo[step_id][3]=step_message
        self.dnaInfo[step_id][4]=step_results
        dna_item=self.dnaItem[step_id]
        dna_item.setFinished(step_status is True)
        self.sampleList.repaintContents()

        if self.sampleList.currentItem() is dna_item:
            self.emit(PYSIGNAL("dnaStepSelected"), (self.dnaInfo[step_id][0],self.dnaInfo[step_id][1],self.dnaInfo[step_id][2],self.dnaInfo[step_id][3],self.dnaInfo[step_id][4]))
        else:
            logging.getLogger().debug("DNARunBrick:updateDNAStep: current sample is not dna_item ???" )
            # add following line to see what happens
            self.emit(PYSIGNAL("dnaStepSelected"), (self.dnaInfo[step_id][0],self.dnaInfo[step_id][1],self.dnaInfo[step_id][2],self.dnaInfo[step_id][3],self.dnaInfo[step_id][4]))
            
    def updateOscillation(self,owner,state,message,col_id,oscillation_id):
        try:
            osc_list=self.oscillationItem[oscillation_id]
        except KeyError,diag:
            logging.getLogger().warning("SampleListBrick: unknown oscillation %s (%s)" % (oscillation_id,str(diag)))
        else:
            for osc_item in osc_list:
                osc_item.setFinished(state is True)

            self.sampleList.repaintContents()

    def gotoOscillation(self,oscillation_id):
        logging.getLogger().debug("SampleListBrick: gotoOscillation %s" % (oscillation_id))
        try:
            osc_list=self.oscillationItem[oscillation_id]
        except KeyError,diag:
            logging.getLogger().warning("SampleListBrick: unknown oscillation %s (%s)" % (oscillation_id,str(diag)))
        else:
            try:
                osc_item=osc_list[-1]
            except:
                pass
            else:
                self.sampleList.setCurrentItem(osc_item)
                self.sampleList.ensureItemVisible(osc_item)
                self.emit(PYSIGNAL("oscillationSelected"), (oscillation_id,))
                self.emit(PYSIGNAL("oscillationClicked"), ())
                logging.getLogger().debug("SampleListBrick: gotoOscillation, successfully set to %r" % (osc_item))

    def connectContextMenu(self,menu,list_item,matrix,location,holderlength,blsampleid):
        try:
            prev_menu=self.__refs[location]
        except KeyError:
            pass
        else:
            QObject.disconnect(prev_menu[0],SIGNAL('activated(int)'),prev_menu[1])

        menu.insertItem("Mount",0)
        menu.insertItem("Unmount",1)
        menu.insertItem("Remove oscillations",2)

        can_unload=False
        can_load=False
        if self.sampleChangerOk():
            sc_can_load=self.sampleChanger.canLoadSample(matrix,location,holderlength)
            if sc_can_load[0]:
                can_unload=sc_can_load[1]
                can_load=not can_unload
        menu.setItemEnabled(0,can_load)
        menu.setItemEnabled(1,can_unload)

        if list_item.childCount()==0:
            menu.setItemEnabled(2,False)
        action_fun=lambda i:SampleListBrick.contextMenuAction.im_func(self,i,list_item,matrix,location,holderlength)
        QObject.connect(menu,SIGNAL('activated(int)'),action_fun)
        self.__refs[location]=(menu,action_fun)

    def listContextMenu(self,item,point,column):
        if self.isCollecting:
            return

        if item!=None and column!=-1:
            if isinstance(item,genericSampleItem):
                try:
                    sample_info=self.samplesInfo[int(str(item.text(9)))]
                except:
                    logging.getLogger().exception("SampleListBrick: unknown sample")
                    return
 
                title=None
                try:
                    sample_acronym=sample_info['acronym']
                except KeyError:
                    pass
                else:
                    try:
                        sample_name=sample_info['name']
                    except KeyError:
                        pass
                    else:
                        title="%s-%s" % (sample_acronym,sample_name)

                if item.isInSampleChanger():
                    try:
                        sample_code=sample_info['barcode']
                    except KeyError:
                        sample_code=None
                    try:
                        blsampleid=int(str(sample_info['blsampleid']))
                    except (KeyError,ValueError):
                        blsampleid=None
                    try:
                        holderlength=sample_info['holderlength']
                    except KeyError:
                        holderlength=None
                    try:
                        sample_location=(sample_info['basket'],sample_info['vial'])
                    except KeyError:
                        sample_location=None

                    menu=QPopupMenu(self)
                    if title is None:
                        title=sample_code or "Unknown code"
                    label=QLabel('<nobr><b>%s</b></nobr>' % title, menu)
                    label.setAlignment(Qt.AlignCenter)
                    menu.insertItem(label)
                    menu.insertSeparator()
                    self.connectContextMenu(menu,item,sample_code,sample_location,holderlength,blsampleid)
                    menu.popup(QCursor.pos())
                else:
                    menu=QPopupMenu(self)
                    try:
                        blsampleid=int(str(sample_info['blsampleid']))
                    except (KeyError,ValueError):
                        blsampleid=None
                    if title is None:
                        title="Unknown name"
                    label=QLabel('<nobr><b>%s</b></nobr>' % title, menu)
                    label.setAlignment(Qt.AlignCenter)
                    menu.insertItem(label)
                    menu.insertSeparator()
                    self.connectContextMenu(menu,item,None,None,None,blsampleid)
                    menu.popup(QCursor.pos())

            elif isinstance(item,oscillationItem):
                try:
                    osc_id=int(str(item.text(9)))
                except Exception,diag:
                    logging.getLogger().exception("SampleListBrick: unknown oscillation")
                    return
                menu=QPopupMenu(self)
                label=QLabel('<nobr><b>%s</b></nobr>' % str(item.text(0)) , menu)
                label.setAlignment(Qt.AlignCenter)
                menu.insertItem(label)
                menu.insertSeparator()
                menu.insertItem("Remove this oscillation",osc_id)
                QObject.connect(menu,SIGNAL('activated(int)'),self.removeOscillation)
                menu.popup(QCursor.pos())

            elif isinstance(item,unknownSampleItem):
                menu=QPopupMenu(self)
                title="Unknown sample"
                blsampleid=None
                label=QLabel('<nobr><b>%s</b></nobr>' % title, menu)
                label.setAlignment(Qt.AlignCenter)
                menu.insertItem(label)
                menu.insertSeparator()
                self.connectContextMenu(menu,item,None,None,None,blsampleid)
                menu.popup(QCursor.pos())
        else:
            return # until further notice...
            if len(self.oscillationInfo)==0:
                return

            menu=QPopupMenu(self)
            label=QLabel('<nobr><b>Sample list</b></nobr>', menu)
            label.setAlignment(Qt.AlignCenter)
            menu.insertItem(label)
            menu.insertSeparator()
            menu.insertItem("Remove failed oscillations",0)
            menu.insertItem("Remove all oscillations",1)
            QObject.connect(menu,SIGNAL('activated(int)'),self.removeOscillations)
            menu.popup(QCursor.pos())

    def removeOscillation(self,i):
        to_pop=[]
        for sample_id in self.oscillationInfo:
            osc_list=self.oscillationInfo[sample_id]
            new_osc_list=[]
            for osc_id,col_dict in osc_list:
                if i==osc_id:
                    pass
                else:
                    new_osc_list.append((osc_id,col_dict))
            if len(new_osc_list)==0:
                to_pop.append(sample_id)
            else:
                self.oscillationInfo[sample_id]=new_osc_list

        for pop in to_pop:
            self.oscillationInfo.pop(pop)
        self.oscillationItem.pop(i)

        try:
            orphans=len(self.oscillationInfo[None])
        except KeyError:
            orphans=0
        if orphans==0 and self.unknownSampleItem is not None:
            self.sampleList.takeItem(self.unknownSampleItem)
            self.unknownSampleItem=None
        self.buildList(str(self.groupSamples.currentText()))
        self.emit(PYSIGNAL("oscillationSelected"), (None,))

    def sampleLoadSuccess(self,already_loaded):
        pass

    def contextMenuAction(self,i,list_item,matrix_code,sample_location,holder_length):
        refilter=False
        if i==0:
            if sample_location is not None:
                matrix_code=None
            self.sampleChanger.loadSample(holder_length,matrix_code,sample_location,self.sampleLoadSuccess)
        elif i==1:
            if sample_location is not None:
                matrix_code=None
            self.sampleChanger.unloadSample(holder_length,matrix_code,sample_location)
        elif i==2:
            if isinstance(list_item,unknownSampleItem):
                for osc_id,coll_dict in self.oscillationInfo[None]:
                    for osc_item in self.oscillationItem[osc_id]:
                        if osc_item is list_item:
                            self.oscillationItem[osc_id].remove(osc_item)
                        pass
                    if len(self.oscillationItem[osc_id])==0:
                        self.oscillationItem.pop(osc_id)
                self.oscillationInfo.pop(None)
                self.sampleList.takeItem(self.unknownSampleItem)
                self.unknownSampleItem=None
                refilter=True
            else:
                to_remove=[]
                child=list_item.firstChild()
                while child is not None:
                    osc_id=int(str(child.text(9)))
                    to_remove.append(osc_id)
                    child=child.nextSibling()

                to_pop=[]
                for sample_id in self.oscillationInfo:
                    osc_list=self.oscillationInfo[sample_id]
                    new_osc_list=[]
                    for osc_id,col_dict in osc_list:
                        try:
                            to_remove.index(osc_id)
                        except ValueError:
                            new_osc_list.append((osc_id,col_dict))
                    if len(new_osc_list)==0:
                        to_pop.append(sample_id)
                    else:
                        self.oscillationInfo[sample_id]=new_osc_list
                for pop in to_pop:
                    self.oscillationInfo.pop(pop)
                for osc_id in to_remove:
                    self.oscillationItem.pop(osc_id)

            self.buildList(str(self.groupSamples.currentText()))
            self.emit(PYSIGNAL("oscillationSelected"), (None,))

        if refilter:
            self.filterList(self.insideSCFilter.isChecked())

    def sampleChangerOk(self):
        return (self.sampleChanger is not None)

    def updateList(self,barcodes,oscillations2enqueue=[]):
        self.latestBarcodes=barcodes or []

        if barcodes is not None:
            self.contentsBox.setEnabled(False)

            sc_locations_dict={}
            barcodes_checked=[]
            for sample in barcodes:
                try:
                    code=sample[0]
                    basket=sample[1]
                    vial=sample[2]
                    basket_code=sample[3]
                except (IndexError,TypeError),diag:
                    logging.getLogger().warning("SampleListBrick: error in barcode information (%s)" % str(diag))
                else:
                    if code is None or basket is None or vial is None:
                        logging.getLogger().warning("SampleListBrick: missing barcode information (%s)" % str(sample))
                    else:
                        try:
                            code=str(code)
                            basket=int(basket)
                            vial=int(vial)
                            basket_code=str(basket_code)
                        except (TypeError,ValueError),diag:
                            logging.getLogger().warning("SampleListBrick: error in barcode information (%s)" % str(diag))
                        else:
                            sc_locations_dict[(basket,vial)]=(code,basket_code)
                            barcodes_checked.append((code,basket,vial,basket_code))

            prev_sel_samples=self.updateListSampleChanger(sc_locations_dict,oscillations2enqueue=oscillations2enqueue)
            if self.proposal is not None and self.sessionId is not None and self.dbServer is not None:
                if self.activeThread is None:
                    self.activeThread=ListThread(self,self.dbServer,self.proposal[2],self.sessionId,barcodes_checked,sc_locations_dict,prev_sel_samples,oscillations2enqueue)
                    self.activeThread.start()
            else:
                self.contentsBox.setEnabled(True)

    def updateListDatabase(self,db_samples,sc_locations,prev_sel_samples,oscillations2enqueue=[]):
        basket_barcodes=[None, "", "", "", "", ""]
        for location in sc_locations:
            bar_code,basket_code=sc_locations[location]
            basket=location[0]
            vial=location[1]
            basket_barcodes[basket]=basket_code

        self.samplesInfo=[]
        for sample in db_samples:
            #blsample=sample['BLSample']
            #container=sample['Container']
            try:
                blsampleid=int(sample['sampleId'])
            except (KeyError,ValueError,TypeError):
                bar_code=str(sample['code'])

                try:
                    basket=int(sample['containerSampleChangerLocation'])
                    if 'sampleLocation' in sample:
                        vial=int(sample['sampleLocation'])
                    else:
                        vial=int(sample['location'])
                except (ValueError,TypeError,KeyError,IndexError):
                    pass
                else:
                    sample_dict={
                        "basket":basket,\
                        "vial":vial,\
                        "barcode":bar_code,\
                        "basket_barcode":basket_barcodes[basket]\
                    }
                    self.samplesInfo.append(sample_dict)
            else:
                sample_name=sample.get('sampleName')
                if sample_name is None:
                    sample_name=""
                bar_code=sample.get('code')

                try:
                    holder_length=float(sample.get('holderLength'))
                except (TypeError,ValueError):
                    holder_length=None

                #crystal=sample['Crystal']
                crystal_space_group=sample.get('crystalSpaceGroup')
                crystal_cell_a=sample.get('cellA')
                try:
                    crystal_cell_a=str(float(crystal_cell_a))
                except (TypeError,ValueError):
                    crystal_cell_a="?"
                crystal_cell_b=sample.get('cellB')
                try:
                    crystal_cell_b=str(float(crystal_cell_b))
                except (TypeError,ValueError):
                    crystal_cell_b="?"
                crystal_cell_c=sample.get('cellC')
                try:
                    crystal_cell_c=str(float(crystal_cell_c))
                except (TypeError,ValueError):
                    crystal_cell_c="?"
                crystal_cell_alpha=sample.get('cellAlpha')
                try:
                    crystal_cell_alpha=str(float(crystal_cell_alpha))
                except (TypeError,ValueError):
                    crystal_cell_alpha="?"
                crystal_cell_beta=sample.get('cellBeta')
                try:
                    crystal_cell_beta=str(float(crystal_cell_beta))
                except (TypeError,ValueError):
                    crystal_cell_beta="?"
                crystal_cell_gamma=sample.get('cellGamma')
                try:
                    crystal_cell_gamma=str(float(crystal_cell_gamma))
                except (TypeError,ValueError):
                    crystal_cell_gamma="?"
                crystal_cell="%s %s %s %s %s %s" %\
                    (crystal_cell_a,crystal_cell_b,crystal_cell_c,\
                    crystal_cell_alpha,crystal_cell_beta,crystal_cell_gamma)

                #protein=sample['Protein']
                protein_acronym=sample.get('proteinAcronym')
                if protein_acronym is None:
                    protein_acronym=""

                #diffractionplan=sample['DiffractionPlan_BLSample']
                #diffractionplan=sample['DiffractionPlan_CrystalType']
                minimal_resolution=sample.get('minimalResolution')
                try:
                    minimal_resolution=str(float(minimal_resolution))
                except (TypeError,ValueError):
                    minimal_resolution=None

                try:
                    basket=int(sample['containerSampleChangerLocation'])
                    vial=int(sample['sampleLocation'])
                except (ValueError,TypeError,KeyError):
                    basket=None
                    vial=None
                    basket_barcode=None
                else:
                    basket_barcode=basket_barcodes[basket]

                sample_dict={
                    "acronym":protein_acronym,\
                    "name":sample_name,\
                    "spacegroup":crystal_space_group,\
                    "cell":crystal_cell,\
                    "blsampleid":blsampleid\
                }
                if minimal_resolution is not None:
                    sample_dict["minimal_resolution"]=minimal_resolution

                if basket is not None and vial is not None:
                    sample_dict["basket"]=basket
                    sample_dict["vial"]=vial
                    sample_dict["basket_barcode"]=basket_barcode
                if bar_code is not None and bar_code!="":
                    sample_dict["barcode"]=bar_code
                if holder_length is not None:
                    sample_dict["holderlength"]=holder_length

                self.samplesInfo.append(sample_dict)

        prev_sel_samples=self.buildList(str(self.groupSamples.currentText()),prev_sel_samples)

        for collect_id in oscillations2enqueue:
            collect_info=self.collectObj.getOscillation(collect_id)
            blsampleid=collect_info[0]
            sample_barcode=collect_info[1]
            sample_location=collect_info[2]
            collect_dict=collect_info[3]
            self.enqueueOscillation(None,blsampleid,sample_barcode,sample_location,collect_dict,collect_id,history_db=True)

        self.contentsBox.setEnabled(True)

        return prev_sel_samples

    def updateListSampleChanger(self,sc_locations,msg=None,oscillations2enqueue=[]):
        self.samplesInfo=[]
        for location in sc_locations:
            bar_code,basket_code=sc_locations[location]
            basket=location[0]
            vial=location[1]

            sample_dict={
                "basket":basket,\
                "vial":vial,\
                "barcode":bar_code,\
                "basket_barcode":basket_code\
            }
            self.samplesInfo.append(sample_dict)

        prev_sel_samples=self.buildList(str(self.groupSamples.currentText()))

        for collect_id in oscillations2enqueue:
            collect_info=self.collectObj.getOscillation(collect_id)
            blsampleid=collect_info[0]
            sample_barcode=collect_info[1]
            sample_location=collect_info[2]
            collect_dict=collect_info[3]
            self.enqueueOscillation(None,blsampleid,sample_barcode,sample_location,collect_dict,collect_id,history_sc=True)

        if msg is not None:
            logging.getLogger().warning(msg)
            self.contentsBox.setEnabled(True)

        return prev_sel_samples

    def buildList(self,grouping,prev_sel_samples=[]):
        if self.sampleChangerOk():
            self.loadedSampleChanged(self.sampleChanger.getLoadedSample(),build=False)

        sel_items=self.getSelectedItems()
        sel_samples=[]
        for sel_item in sel_items:
            for sample_item_key in self.sampleItem:
                try:
                    sel_items.index(self.sampleItem[sample_item_key])
                except:
                    pass
                else:
                    try:
                        sel_samples.index(sample_item_key)
                    except:
                        sel_samples.append(sample_item_key)

        self.clearList()
        self.buildColumns(grouping)
        baskets={}
        proteins={}
        self.sampleItem={}
        self.oscillationItem={}
        self.dnaItem={}

        i=0
        for sample in self.samplesInfo:
            try:
                blsampleid=sample["blsampleid"]
            except KeyError:
                in_db=False
            else:
                in_db=True
            basket_barcode=""
            try:
                sample["basket"]
            except KeyError:
                in_sc=False
            else:
                in_sc=True
                basket=sample['basket']
                vial=sample['vial']
                basket_barcode=sample['basket_barcode']
            try:
                barcode=sample['barcode']
            except KeyError:
                barcode=None
            try:
                min_res=sample["minimal_resolution"]
            except KeyError:
                min_res=None

            if grouping=="no grouping":
                if in_db:
                    loc_str=None
                    if in_sc:
                        loc_str="%d:%02d" % (basket,vial)
    
                    item=sampleItem(self.sampleList,\
                        sample["name"],\
                        sample["acronym"],\
                        barcode,\
                        loc_str,\
                        sample["spacegroup"],\
                        sample["cell"],\
                        min_res,\
                        basket_barcode,\
                        i)

                    self.sampleItem[blsampleid]=item
                    if in_sc:
                        self.sampleItem[(basket,vial)]=item
                        if self.loadedSampleLocation==(basket,vial):
                            item.setMounted(True)
                            self.sampleSelectionChanged([item])
                else:
                    loc_str="%d:%02d" % (basket,vial)
                    item=vialItem(self.sampleList,barcode,loc_str,basket_barcode,i)
                    self.sampleItem[(basket,vial)]=item
                    if self.loadedSampleLocation==(basket,vial):
                        item.setMounted(True)
                        self.sampleSelectionChanged([item])
            elif grouping=="sample changer location":
                if in_sc:
                    try:
                        basket_item=baskets[basket]
                    except KeyError:
                        basket_item=basketItem(self.sampleList,\
                            basket_barcode,basket)
                        baskets[basket]=basket_item

                if in_db:
                    loc_str=None
                    if in_sc:
                        loc_str="%02d" % vial

                    if in_sc:
                        parent=basket_item
                    else:
                        parent=self.sampleList

                    item=sampleItem(parent,\
                        sample["name"],\
                        sample["acronym"],\
                        barcode,\
                        loc_str,\
                        sample["spacegroup"],\
                        sample["cell"],\
                        min_res,\
                        basket_barcode,\
                        i)

                    self.sampleItem[blsampleid]=item

                    if in_sc:
                        self.sampleItem[(basket,vial)]=item
                        if self.loadedSampleLocation==(basket,vial):
                            item.setMounted(True)
                            self.sampleSelectionChanged([item])
                else:
                    loc_str="%02d" % vial
                    item=vialItem(basket_item,barcode,loc_str,basket_barcode,i)
                    self.sampleItem[(basket,vial)]=item
                    if self.loadedSampleLocation==(basket,vial):
                        item.setMounted(True)
                        self.sampleSelectionChanged([item])
            elif grouping=="protein acronym":
                if in_db:
                    protein_acronym=sample["acronym"]

                    try:
                        protein_item=proteins[protein_acronym]
                    except KeyError:
                        protein_item=proteinItem(self.sampleList,protein_acronym)
                        proteins[protein_acronym]=protein_item

                    loc_str=None
                    if in_sc:
                        loc_str="%d:%02d" % (basket,vial)
                    item=sampleItem(protein_item,\
                        sample["name"],\
                        sample["acronym"],\
                        barcode,\
                        loc_str,\
                        sample["spacegroup"],\
                        sample["cell"],\
                        min_res,\
                        basket_barcode,\
                        i)

                    self.sampleItem[blsampleid]=item
                    if in_sc:
                        self.sampleItem[(basket,vial)]=item
                        if self.loadedSampleLocation==(basket,vial):
                            item.setMounted(True)
                            self.sampleSelectionChanged([item])
                else:
                    loc_str="%d:%02d" % (basket,vial)
                    item=vialItem(self.sampleList,barcode,loc_str,basket_barcode,i)
                    self.sampleItem[(basket,vial)]=item
                    if self.loadedSampleLocation==(basket,vial):
                        item.setMounted(True)
                        self.sampleSelectionChanged([item])

            if in_db:
                blsampleid=sample["blsampleid"]
                try:
                    oscillations=self.oscillationInfo[blsampleid]
                except KeyError:
                    pass
                else:
                    for osc_id,osc_dict in oscillations:
                        run_number=osc_dict["fileinfo"]["run_number"]
                        osc_item=oscillationItem(item,run_number,osc_id)
                        
                        try:
                            osc_item_list=self.oscillationItem[osc_id]
                        except KeyError:
                            self.oscillationItem[osc_id]=[osc_item]
                        else:
                            osc_item_list.append(osc_item)
                        try:
                            osc_code=bool(osc_dict["collection_code"])
                        except KeyError:
                            osc_item.setFinished(None)
                        else:
                            osc_item.setFinished(osc_code)

                try:
                    dna_steps=self.sample2Dna[blsampleid]
                except:
                    dna_steps=None
                if dna_steps is not None:
                    for dna_step_id in dna_steps:
                        class_name="%sItem" % self.dnaInfo[dna_step_id][0]
                        exec("dna_item=%s(item,self.dnaInfo[dna_step_id][1],dna_step_id)" % class_name)
                        self.dnaItem[dna_step_id]=dna_item
                        dna_item.setFinished(self.dnaInfo[dna_step_id][2])

            elif in_sc:
                try:
                    oscillations=self.oscillationInfo[(basket,vial)]
                except KeyError:
                    pass
                else:
                    for osc_id,osc_dict in oscillations:
                        run_number=osc_dict["fileinfo"]["run_number"]
                        osc_item=oscillationItem(item,run_number,osc_id)
                        try:
                            osc_item_list=self.oscillationItem[osc_id]
                        except KeyError:
                            self.oscillationItem[osc_id]=[osc_item]
                        else:
                            osc_item_list.append(osc_item)
                        try:
                            osc_code=bool(osc_dict["collection_code"])
                        except KeyError:
                            osc_item.setFinished(None)
                        else:
                            osc_item.setFinished(osc_code)

                try:
                    dna_steps=self.sample2Dna[(basket,vial)]
                except:
                    dna_steps=None
                if dna_steps is not None:
                    for dna_step_id in dna_steps:
                        class_name="%sItem" % self.dnaInfo[dna_step_id][0]
                        exec("dna_item=%s(item,self.dnaInfo[dna_step_id][1],dna_step_id)" % class_name)
                        self.dnaItem[dna_step_id]=dna_item
                        dna_item.setFinished(self.dnaInfo[dna_step_id][2])

            i+=1

        try:
            oscillations=self.oscillationInfo[None]
        except KeyError:
            pass
        else:
            if self.unknownSampleItem is None:
                self.unknownSampleItem=unknownSampleItem(self.sampleList)

            for osc_id,osc_dict in oscillations:
                run_number=osc_dict["fileinfo"]["run_number"]
                osc_item=oscillationItem(self.unknownSampleItem,run_number,osc_id)
                try:
                    osc_item_list=self.oscillationItem[osc_id]
                except KeyError:
                    self.oscillationItem[osc_id]=[osc_item]
                else:
                    osc_item_list.append(osc_item)
                try:
                    osc_code=bool(osc_dict["collection_code"])
                except KeyError:
                    osc_item.setFinished(None)
                else:
                    osc_item.setFinished(osc_code)

            self.unknownSampleItem.setOpen(True)

        try:
            dna_steps=self.sample2Dna[None]
        except:
            dna_steps=None
        if dna_steps is not None:
            if self.unknownSampleItem is None:
                self.unknownSampleItem=unknownSampleItem(self.sampleList)

            for dna_step_id in dna_steps:
                class_name="%sItem" % self.dnaInfo[dna_step_id][0]
                exec("dna_item=%s(self.unknownSampleItem,self.dnaInfo[dna_step_id][1],dna_step_id)" % class_name)
                self.dnaItem[dna_step_id]=dna_item
                dna_item.setFinished(self.dnaInfo[dna_step_id][2])

        for sel_sample in sel_samples:
            try:
                item2select=self.sampleItem[sel_sample]
            except:
                pass
            else:
                self.sampleList.setSelected(item2select,True)
        for sel_sample in prev_sel_samples:
            try:
                item2select=self.sampleItem[sel_sample]
            except:
                pass
            else:
                self.sampleList.setSelected(item2select,True)

        self.sampleList.sort()
        self.filterList(self.insideSCFilter.isChecked())

        return sel_samples
    
    def sampleSelectionChanged(self,selected_items):
        if len(selected_items)==0:
            self.emit(PYSIGNAL("sampleSelected"),([],))
        else:
            list_dicts=[]
            for item in selected_items:
                if isinstance(item,genericSampleItem):
                    temp_dict={}

                    try:
                        sample_info=self.samplesInfo[int(str(item.text(9)))]
                    except:
                        logging.getLogger().exception("SampleListBrick: unknown sample")
                    else:
                        try:
                            temp_dict['protein_acronym']=sample_info['acronym']
                        except KeyError:
                            pass
                        try:
                            temp_dict['name']=sample_info['name']
                        except KeyError:
                            pass
                        try:
                            temp_dict['cell']=sample_info['cell']
                        except KeyError:
                            pass
                        try:
                            temp_dict['crystal_space_group']=sample_info['spacegroup']
                        except KeyError:
                            pass
                        try:
                            temp_dict['minimal_resolution']=sample_info['minimal_resolution']
                        except KeyError:
                            pass
                        try:
                            temp_dict['code']=sample_info['barcode']
                        except KeyError:
                            pass
                        try:
                            temp_dict['basket']=sample_info['basket']
                        except KeyError:
                            pass
                        try:
                            temp_dict['vial']=sample_info['vial']
                        except KeyError:
                            pass
                        try:
                            temp_dict['holder_length']=sample_info['holderlength']
                        except KeyError:
                            pass
                        try:
                            blsampleid=sample_info['blsampleid']
                        except KeyError:
                            blsampleid=""
                        temp_dict['id']=blsampleid

                        list_dicts.append((blsampleid,temp_dict))
    
                self.emit(PYSIGNAL("sampleSelected"), (list_dicts,))

    def itemClicked(self,item):
        #print "ITEMCLICKED",item

        oscillation_id=None
        sample_clicked=False
        dna_step_id=None
        
        if isinstance(item,sampleItem) or isinstance(item,vialItem):
            if not self.isCollecting:
                sel_items=self.getSelectedItems()
                if len(sel_items)>1:
                    for item in sel_items:
                        if not item.isInSampleChanger():
                            item.setSelected(False)
                sample_clicked=True

        elif isinstance(item,oscillationItem):
            oscillation_id=int(str(item.text(9)))

        elif isinstance(item,genericDNAItem):
            dna_step_id=int(str(item.text(9)))

        if oscillation_id is not None:
            self.emit(PYSIGNAL("oscillationSelected"), (oscillation_id,))
            self.emit(PYSIGNAL("oscillationClicked"), ())
        elif dna_step_id is not None:
            parent_sample=item.parent()
            if isinstance(parent_sample,sampleItem) or isinstance(parent_sample,vialItem):
                self.sampleList.clearSelection()
                parent_sample.activate()
                parent_sample.setSelected(True)
                self.sampleList.repaintContents()
                self.itemClicked(parent_sample)

            try:
                step_info=self.dnaInfo[dna_step_id]
            except:
                pass
            else:
                t=tuple(step_info)
                self.emit(PYSIGNAL("dnaStepSelected"), t )

        elif sample_clicked:
            self.sampleSelectionChanged(self.getSelectedItems())
            self.emit(PYSIGNAL("sampleClicked"), ())

    def propertyChanged(self,propertyName,oldValue,newValue):
        if propertyName=="sampleChanger":
            self.clearList()
            if self.sampleChanger is not None:
                self.disconnect(self.sampleChanger, PYSIGNAL("loadedSampleChanged"), self.loadedSampleChanged)
            self.sampleChanger=self.getHardwareObject(newValue)
            if self.sampleChanger is not None:
                self.connect(self.sampleChanger, PYSIGNAL("loadedSampleChanged"), self.loadedSampleChanged)
                self.loadedSampleChanged(self.sampleChanger.getLoadedSample())
        elif propertyName=="dbServer":
            self.clearList()
            self.dbServer=self.getHardwareObject(newValue)
        elif propertyName=='allowMultipleSelection':
            self.sampleList._allowMultipleSelection=newValue
        elif propertyName=="icons":
            icons_list=newValue.split()

            try:
                self.refreshButton.setPixmap(Icons.load(icons_list[0]))
            except IndexError:
                pass
        elif propertyName == 'dataCollect':
            self.collectObj=self.getHardwareObject(newValue)
        else:
            BaseComponents.BlissWidget.propertyChanged(self,propertyName,oldValue,newValue)

    def loadedSampleChanged(self,loaded_sample_dict,build=True):
        print "SampleListBrick.loadedSampleChanged",self,loaded_sample_dict,build

        try:
            loaded=loaded_sample_dict["loaded"]
        except:
            loaded=False
        if loaded:
            try:
                barcode=loaded_sample_dict["barcode"]
            except:
                barcode=None

            try:
                basket=int(loaded_sample_dict["basket"])
                vial=int(loaded_sample_dict["vial"])
            except:
                basket=None
                vial=None
                location=None
            else:
                location=(basket,vial)
        else:
            barcode=None
            location=None

        self.loadedSampleDataMatrix=barcode
        self.loadedSampleLocation=location

        loaded_sample_dict=None
        if location is not None:
            for sample_dict in self.samplesInfo:
                try:
                    stored_basket=int(sample_dict["basket"])
                    stored_vial=int(sample_dict["vial"])
                except:
                    stored_location=None
                else:
                    stored_location=(stored_basket,stored_vial)

                if location==stored_location:
                    try:
                        stored_blsampleid=sample_dict["blsampleid"]
                    except:
                        stored_blsampleid=None

                    if stored_blsampleid is not None and self.sampleChangerOk():
                        self.sampleChanger.extendLoadedSample({"blsampleid":stored_blsampleid})

                    loaded_sample_dict={"code":barcode, "basket":basket, "vial":vial}
                    try:
                        loaded_sample_dict['protein_acronym']=sample_dict['acronym']
                    except KeyError:
                        pass
                    try:
                        loaded_sample_dict['name']=sample_dict['name']
                    except KeyError:
                        pass
                    try:
                        loaded_sample_dict['crystal_space_group']=sample_dict['spacegroup']
                    except KeyError:
                        pass
                    try:
                        loaded_sample_dict['cell']=sample_dict['cell']
                    except KeyError:
                        pass
                    try:
                        loaded_sample_dict['minimal_resolution']=sample_dict['minimal_resolution']
                    except KeyError:
                        pass
                    try:
                        loaded_sample_dict['holder_length']=sample_dict['holderlength']
                    except KeyError:
                        pass
                    try:
                        blsampleid=sample_dict['blsampleid']
                    except KeyError:
                        blsampleid=""
                    loaded_sample_dict['id']=blsampleid

        if loaded_sample_dict is not None:
            self.emit(PYSIGNAL("sampleLoaded"), ([(blsampleid,loaded_sample_dict)],))
        else:
            self.emit(PYSIGNAL("sampleLoaded"), ([],))

        if build:
            self.buildList(str(self.groupSamples.currentText()))


class genericItem(QListViewItem):
    def __init__(self,parent,*args):
        QListViewItem.__init__(self,parent)
        self.myColor=None
        self.myColorGroup={}
        i=0
        for a in args:
            if a is not None:
                QListViewItem.setText(self,i,str(a))
            i+=1
        if isinstance(parent,QListViewItem):
            parent.setOpen(True)
        self.setSelectable(False)
    def setItalic(self,state):
        self.isItalic=state
    def setBold(self,state):
        self.isBold=state
    def setMyColor(self,color):
        self.myColor=color
    def allowMultipeSiblingSelection(self):
        return False
    def paintCell(self,painter,colors,column,width,align):
        if self.myColor is not None:
            try:
                colors=self.myColorGroup[self.myColor]
            except KeyError:
                colors=QColorGroup(colors)
                colors.setColor(QColorGroup.Text,self.myColor)
                colors.setColor(QColorGroup.HighlightedText,self.myColor)
                self.myColorGroup[self.myColor]=colors
            font=painter.font()
            try:
                is_bold=self.isBold
            except AttributeError:
                pass
            else:
                font.setBold(is_bold)
            painter.setFont(font)
        else:
            try:
                if self.isItalic:
                    try:
                        colors=self.grayColorGroup
                    except AttributeError:
                        colors=QColorGroup(colors)
                        colors.setColor(QColorGroup.Text,QWidget.darkGray)
                        self.grayColorGroup=colors
                    font=painter.font()
                    font.setItalic(True)
                    painter.setFont(font)
            except AttributeError:
                pass
        QListViewItem.paintCell(self,painter,colors,column,width,align)
    def compare(self,i,col,asc):
        if isinstance(self,unknownSampleItem):
            comp=1
            if not asc:
                comp*=-1
            return comp
        if isinstance(i,unknownSampleItem):
            comp=-1
            if not asc:
                comp*=-1
            return comp
        return QListViewItem.compare(self,i,col,asc)
    def getSelectedItems(self):
        list_view=self.listView()
        item_iterator=QListViewItemIterator(list_view)
        selected_items=[]
        while item_iterator.current():
            if item_iterator.current().isSelected():
                selected_items.append(item_iterator.current())
            item_iterator+=+1
        return selected_items
    def activate(self):
        list_view=self.listView()
        list_view.clearSelection()
        list_view.setSelectionMode(QListView.NoSelection)

class basketItem(genericItem):
    def __init__(self,parent,barcode,position):
        desc="basket"
        if barcode is not None:
            desc="basket %s" % barcode
        genericItem.__init__(self,parent,desc,None,None,position)
        self.setItalic(True)

class proteinItem(genericItem):
    def __init__(self,parent,acronym):
        desc="protein %s" % acronym
        genericItem.__init__(self,parent,desc)
        self.setItalic(True)

class unknownSampleItem(genericItem):
    def __init__(self,parent):
        genericItem.__init__(self,parent,"unknown sample")
        self.setItalic(True)

class genericSampleItem(genericItem):
    def __init__(self,parent,*args):
        genericItem.__init__(self,parent,*args)
        self.barcode=None
        self.locationStr=None
        self.setSelectable(True)
    def setMounted(self,mounted):
        if mounted:
            self.setBold(True)
            self.setMyColor(QWidget.green)
        else:
            self.setBold(False)
            self.setMyColor(None)
    def isInSampleChanger(self):
        return False
    def getBarcode(self):
        return self.barcode
    def activate(self):
        list_view=self.listView()
        if not self.isInSampleChanger() or not list_view._allowMultipleSelection:
            sel_mode=QListView.Single
            list_view.clearSelection()
        else:
            sel_mode=QListView.Extended
        if sel_mode!=list_view.selectionMode():
            list_view.setSelectionMode(sel_mode)
        self.setSelectable(True)

class vialItem(genericSampleItem):
    def __init__(self,parent,barcode,location_str,basket_barcode,index):
        genericSampleItem.__init__(self,parent,None,None,barcode,location_str,None,None,None,basket_barcode,None,index)
        if barcode=="":
            barcode=None
        self.barcode=barcode
        self.locationStr=location_str
    def isInSampleChanger(self):
        return True

class sampleItem(genericSampleItem):
    def __init__(self,parent,name,acronym,barcode,location_str,spacegroup,cell,min_res,basket_barcode,index):
        genericSampleItem.__init__(self,parent,name,acronym,barcode,location_str,spacegroup,cell,min_res,basket_barcode,None,index)
        self.locationStr=location_str
        if barcode=="":
            barcode=None
        self.barcode=barcode
        self.setRenameEnabled(6,True)
    def isInSampleChanger(self):
        #return self.locationStr is not None and len(self.locationStr)
        return self.locationStr is not None and self.locationStr

class oscillationItem(genericItem):
    def __init__(self,parent,run_number,index):
        desc="run number %d" % int(str(run_number))
        genericItem.__init__(self,parent,desc,None,None,None,None,None,None,None,None,index)
        self.oscillationOrder=index
    def compare(self,i,col,asc):
        try:
            comp=0
            if self.oscillationOrder>i.oscillationOrder:
                comp=1
            elif self.oscillationOrder<i.oscillationOrder:
                comp=-1
            if not asc:
                comp*=-1
        except:
            comp=QListViewItem.compare(self,i,col,asc)        
        return comp
    def setFinished(self,state):
        if state is None:
            self.setMyColor(QWidget.darkYellow)
        elif state is True:
            self.setMyColor(QWidget.darkGreen)
        else:
            self.setMyColor(QWidget.darkRed)

class genericDNAItem(genericItem):
    DESCRIPTIONS = {\
            "referenceImages": "ref.images",\
            "indexReference": "indexing",\
            "calculateStrategy": "strategy",\
            "screening": "screening",\
            "collectIntegrate": "collect"\
        }

    def __init__(self,parent,desc,index):
        try:
            description=genericDNAItem.DESCRIPTIONS[desc]
        except:
            description=desc
        genericItem.__init__(self,parent,description,None,None,None,None,None,None,None,None,index)
        self.stepOrder=index
    def compare(self,i,col,asc):
        try:
            comp=0
            if self.stepOrder>i.stepOrder:
                comp=1
            elif self.stepOrder<i.stepOrder:
                comp=-1
            if not asc:
                comp*=-1
        except:
            comp=QListViewItem.compare(self,i,col,asc)        
        return comp
    def setFinished(self,state):
        if state is None:
            self.setMyColor(QWidget.darkYellow)
        elif state is True:
            self.setMyColor(QWidget.darkGreen)
        else:
            self.setMyColor(QWidget.darkRed)

class referenceImagesItem(genericDNAItem):
    pass

class indexReferenceItem(genericDNAItem):
    pass

class calculateStrategyItem(genericDNAItem):
    pass

class collectIntegrateItem(genericDNAItem):
    pass

class screeningItem(genericDNAItem):
    pass

###
### Auxiliary class for positioning
###
class HorizontalSpacer(QWidget):
    def __init__(self,*args):
        QWidget.__init__(self,*args)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)

### Thread to perform the list actions in the background:
### get samples from the ISPyB server
class ListThread(QThread):
    def __init__(self,brick,db_server,proposal_id,session_id,barcodes,sc_locations,prev_sel_samples,oscillations2enqueue):
        QThread.__init__(self)
        self.Brick=brick
        self.dbServer=db_server
        self.proposalId=proposal_id
        self.sessionId=session_id
        self.sampleBarcodes=barcodes
        self.scLocations=sc_locations
        self.prevSelSamples=prev_sel_samples
        self.oscillations2enqueue=oscillations2enqueue

    def run(self):
        samples_in_session=self.dbServer.getSessionSamples(self.proposalId,self.sessionId,self.sampleBarcodes)
        try:
            in_session=samples_in_session['loaded_sample']
        except KeyError:
            try:
                message=samples_in_session['status']['message']
            except:
                message="No samples whatsoever for proposal id %d, session %d, bar codes %r" % (int(self.proposalId),int(self.sessionId),self.sampleBarcodes)
            self.postDbServerErrorEvent(self.scLocations,message)
        else:
            self.postDbServerSamplesEvent(in_session,self.scLocations)

    def postDbServerSamplesEvent(self,loaded_samples,sc_locations):
        #logging.getLogger().debug("SampleListBrick: queue samples event")
        method=SampleListBrick.updateListDatabase
        arguments=(self.Brick,loaded_samples,sc_locations,self.prevSelSamples,self.oscillations2enqueue)
        custom_event=SampleListGUIEvent(method,arguments)
        self.postEvent(self.Brick,custom_event)
    
    def postDbServerErrorEvent(self,loaded_samples,msg):
        #logging.getLogger().debug("SampleListBrick: queue db error event")
        error_msg="Got the following error from the ISPyB server:\n%s" % msg
        method=SampleListBrick.updateListSampleChanger
        arguments=(self.Brick,loaded_samples,error_msg,self.oscillations2enqueue)
        custom_event=SampleListGUIEvent(method,arguments)
        self.postEvent(self.Brick,custom_event)
