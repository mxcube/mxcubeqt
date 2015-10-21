import qt
import logging
import weakref
import new

from BlissFramework.Utils import widget_colors
from BlissFramework.BaseLayoutItems import BrickCfg, SpacerCfg, LabelCfg, WindowCfg, ContainerCfg, TabCfg
from BlissFramework.BaseComponents import BlissWidget
from BlissFramework import Icons


class MenuBar(qt.QMenuBar):
    # parent *must* be the window ; it contains a centralWidget in its viewport
    def __init__(self, parent, data, expert_pwd, executionMode=False):
        qt.QMenuBar.__init__(self, parent.centralWidget)

        parent.centralWidget.layout().addWidget(self)
        self.setSizePolicy(qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Fixed)
        
        self.data = data
        self.expertPwd = expert_pwd
        # the emitter is the top parent (the window itself, not the centralWidget)
        self.topParent = parent
        self.executionMode = executionMode
        
        self.file = qt.QPopupMenu(self)
        self.file.insertItem("Quit", self.quit)
        self.help = qt.QPopupMenu(self)
        self.help.insertItem("What's this ?", self.whatsthis)

        self.insertItem("File", self.file)
        self.insertItem("Help", self.help)
        self.insertSeparator()
        self.expertMode=qt.QCheckBox("Expert mode",self)
        self.expertModeStdColor=None
        qt.QObject.connect(self.expertMode, qt.SIGNAL('clicked()'), self.expertModeClicked)
        self.insertItem(self.expertMode)


    def expertModeClicked(self):
        if self.expertMode.isChecked():
            res=qt.QInputDialog.getText("Switch to expert mode","Please enter the password:",qt.QLineEdit.Password)
            if res[1]:
                if str(res[0])==self.expertPwd:
                    self.expertMode.setPaletteBackgroundColor(qt.QWidget.yellow)
                    self.setExpertMode(True)
                else:
                    self.expertMode.setChecked(False)
                    qt.QMessageBox.critical(self, "Switch to expert mode", "Wrong password!",qt.QMessageBox.Ok)
            else:
                self.expertMode.setChecked(False)
        else:
            self.expertMode.setPaletteBackgroundColor(self.expertMode.parent().paletteBackgroundColor())
            self.setExpertMode(False)


    def setExpertMode(self,state):
        if not self.executionMode:
            return
        
        if state:
            # switch to expert mode
            qt.QObject.emit(self.topParent, qt.PYSIGNAL("enableExpertMode"), (True, ))

            # go through all bricks and execute the method
            for w in qt.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    try:
                        w.setExpertMode(True)
                    except:
                        logging.getLogger().exception("Could not set %s to expert mode", w.name())
        else:
            # switch to user mode
            #print self, "emitting: enableExpertMode, False"
            qt.QObject.emit(self.topParent, qt.PYSIGNAL("enableExpertMode"), (False, ))

            # go through all bricks and execute the method
            for w in qt.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    qt.QWhatsThis.remove(w)
                    try:
                        w.setExpertMode(False)
                    except:
                        logging.getLogger().exception("Could not set %s to user mode", w.name())


    def whatsthis(self):
        if self.executionMode:
            BlissWidget.updateWhatsThis()


    def quit(self):
        if self.executionMode:
            qt.QObject.emit(self.topParent, qt.PYSIGNAL("quit"), ())
            qt.qApp.quit()


class StatusBar(qt.QStatusBar):
    # parent *must* be the window ; it contains a centralWidget in its viewport
    def __init__(self, parent, *args):
        qt.QStatusBar.__init__(self, parent.centralWidget, *args)
        parent.centralWidget.layout().addWidget(self)


class tabBar(qt.QTabBar):
    def paintLabel(self,p,br,t,has_focus):
        current_index=self.parent().currentPageIndex()
        current_tab=self.tabAt(current_index)
        warn_mode=False
        if current_tab is not t:
            for i in range(self.count()):
                t2=self.tabAt(i)
                if t2 is t:
                    if self.parent().hasCountChanged(i):
                        warn_mode=True
                        break
        if warn_mode:
            p.setBackgroundMode(qt.Qt.OpaqueMode)
            p.setBackgroundColor(qt.Qt.yellow)
        else:
            p.setBackgroundMode(qt.Qt.TransparentMode)
        qt.QTabBar.paintLabel(self,p,br,t,has_focus)


class WindowDisplayWidget(qt.QScrollView):

    class Spacer(qt.QFrame):
        def __init__(self, *args, **kwargs):
            qt.QFrame.__init__(self, *args)

            self.orientation = kwargs.get("orientation", "horizontal")
            self.executionMode = kwargs.get("executionMode", False)

            self.setFixedSize(-1)


        def setFixedSize(self, fixed_size):
            if fixed_size >= 0:
                hor_size_policy = self.orientation == "horizontal" and qt.QSizePolicy.Fixed or qt.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == qt.QSizePolicy.Fixed and qt.QSizePolicy.MinimumExpanding or qt.QSizePolicy.Fixed
                
                if self.orientation == "horizontal":
                    self.setFixedWidth(fixed_size)
                else:
                    self.setFixedHeight(fixed_size)
            else:
                hor_size_policy = self.orientation == "horizontal" and qt.QSizePolicy.Expanding or qt.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == qt.QSizePolicy.Expanding and qt.QSizePolicy.MinimumExpanding or qt.QSizePolicy.Expanding
            
            self.setSizePolicy(hor_size_policy, ver_size_policy)
                
            
        def paintEvent(self, event):
            qt.QFrame.paintEvent(self, event)

            if self.executionMode:
                return

            p = qt.QPainter(self)
            p.setPen(qt.QPen(qt.Qt.black, 3))

            if self.orientation == 'horizontal':
                h = self.height() / 2
                p.drawLine(0, h, self.width(), h)
                p.drawLine(0, h, 5, h - 5)
                p.drawLine(0, h, 5, h + 5)
                p.drawLine(self.width(), h, self.width() - 5, h - 5)
                p.drawLine(self.width(), h, self.width() - 5, h + 5)
            else:
                w = self.width() / 2
                p.drawLine(self.width() / 2, 0, self.width() / 2, self.height())
                p.drawLine(w, 0, w - 5, 5)
                p.drawLine(w, 0, w + 5, 5)
                p.drawLine(w, self.height(), w - 5, self.height() - 5)
                p.drawLine(w, self.height(), w + 5, self.height() - 5)

                

    def verticalSpacer(*args, **kwargs):
        kwargs["orientation"]="vertical"
        return WindowDisplayWidget.Spacer(*args, **kwargs)


    def horizontalSpacer(*args, **kwargs):
        kwargs["orientation"]="horizontal"
        return WindowDisplayWidget.Spacer(*args, **kwargs)


    def horizontalSplitter(*args, **kwargs):
        return qt.QSplitter(qt.Qt.Horizontal, *args)


    def verticalSplitter(*args, **kwargs):
        return qt.QSplitter(qt.Qt.Vertical, *args)
    

    def verticalBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)

        frame = qt.QFrame(*args)
        frame.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        
        if not executionMode:
            frame.setFrameStyle(qt.QFrame.Box | qt.QFrame.Plain)

        qt.QVBoxLayout(frame)

        return frame
 

    def horizontalBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)
        
        frame = qt.QFrame(*args)
        frame.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        
        if not executionMode:
            frame.setFrameStyle(qt.QFrame.Box | qt.QFrame.Plain)

        qt.QHBoxLayout(frame)

        return frame
       
        
    def horizontalGroupBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)
        
        groupbox = qt.QGroupBox(*args)
        groupbox.setColumnLayout(0, qt.Qt.Vertical)
        groupbox._preferred_layout = qt.QHBoxLayout(groupbox.layout())    
        groupbox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        return groupbox


    def verticalGroupBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)
        
        groupbox = qt.QGroupBox(*args)
        groupbox.setColumnLayout(0, qt.Qt.Vertical)
        groupbox.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        return groupbox


    class tabWidget(qt.QTabWidget):
        def __init__(self, *args, **kwargs):
            qt.QTabWidget.__init__(self, *args)

            tab_bar=tabBar(self)
            tab_bar.palette()
            self.setTabBar(tab_bar)

            self.countChanged={}

            qt.QObject.connect(self, qt.SIGNAL('currentChanged( QWidget * )'), self._pageChanged)

            self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        
        def _pageChanged(self, page):
            index=self.indexOf(page)
            self.countChanged[index]=False

            tab_label=str(self.tabLabel(page))
            label_list=tab_label.split()
            found=False
            try:
                count=label_list[-1]
                try:
                    found=count[0]=="("
                except:
                    pass
                else:
                    try:
                        found=count[-1]==")"
                    except:
                        pass
            except:
                pass
            if found:
                orig_label=" ".join(label_list[0:-1])
            else:
                orig_label=" ".join(label_list)
            self.emit(qt.PYSIGNAL("notebookPageChanged"), (orig_label, ))
            qt.qApp.emit(qt.PYSIGNAL('tab_changed'), (index, page))

            tab_name=self.name()
            BlissWidget.updateTabWidget(tab_name,index)


        def hasCountChanged(self,tab_index):
            try:
                changed=self.countChanged[tab_index]
            except KeyError:
                changed=False
            return changed


        def addTab(self, page_widget, label, icon=""):
            scrollview = qt.QScrollView(self)
            scrollview.setFrameStyle(qt.QFrame.NoFrame)
            scrollview.setResizePolicy(qt.QScrollView.AutoOneFit)
            if icon!="":
                pxmap=Icons.load(icon)
                icon_set=qt.QIconSet(pxmap,pxmap)
                qt.QTabWidget.addTab(self, scrollview, icon_set, label)
            else:
                qt.QTabWidget.addTab(self, scrollview, label)
            page_widget.reparent(scrollview.viewport(), 0, qt.QPoint(0,0), True)
            scrollview.addChild(page_widget)
                
            # add 'show page' slot
            slotName = "showPage_%s" % label
            def tab_slot(self, page_index=self.indexOf(scrollview)):
                #print 'tab slot', page_index
                self.showPage(self.page(page_index))
            try:
                self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'hide page' slot
            slotName = "hidePage_%s" % label
            def tab_slot(self, hide=True, page={"widget":scrollview, "label":self.tabLabel(scrollview) , "index":self.indexOf(scrollview), "icon": icon,"hidden":False}):
                if hide:
                  if not page["hidden"]:
                    self.removePage(page["widget"])
                    page["hidden"] = True
                else:
                  if page["hidden"]:
                    if icon:
                      pixmap = Icons.load(icon)
                      self.insertTab(page["widget"], qt.QIconSet(pixmap,pixmap), label, page["index"])
                    else:
                      self.insertTab(page["widget"], page["label"], page["index"])
                    self.showPage(page["widget"])
                    page["hidden"] = False
                  else:
                    self.showPage(page["widget"])
                #page_info =""
                #for i in range(self.count()):
                #  page_info+="PAGE %d: %s, %s "% (i, self.tabLabel(self.page(i)), self.page(i))
                #logging.info(page_info)
            try:
              self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except: 
              logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name())) 
        
            # add 'enable page' slot
            slotName = "enablePage_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scrollview)):
                self.page(page_index).setEnabled(enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'enable tab' slot
            slotName = "enableTab_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scrollview)):
                self.setTabEnabled(self.page(page_index),enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'tab reset count' slot
            slotName = "resetTabCount_%s" % label
            def tab_slot(self, erase_count, page_index=self.indexOf(scrollview)):
                tab_label=str(self.tabLabel(self.page(page_index)))
                label_list=tab_label.split()
                found=False
                try:
                    count=label_list[-1]
                    try:
                        found=count[0]=="("
                    except:
                        pass
                    else:
                        try:
                            found=count[-1]==")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num=int(count[1:-1])
                    except:
                        pass
                    else:
                        new_label=" ".join(label_list[0:-1])
                        if not erase_count:
                            new_label+=" (0)"
                        self.countChanged[page_index]=False
                        self.setTabLabel(self.page(page_index),new_label)
                else:
                    if not erase_count:
                        new_label=" ".join(label_list)
                        new_label+=" (0)"
                        self.countChanged[page_index]=False
                        self.setTabLabel(self.page(page_index),new_label)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'tab increase count' slot
            slotName = "incTabCount_%s" % label
            def tab_slot(self, delta, only_if_hidden, page_index=self.indexOf(scrollview)):
                if only_if_hidden and page_index==self.currentPageIndex():
                    return
                tab_label=str(self.tabLabel(self.page(page_index)))
                label_list=tab_label.split()
                found=False
                try:
                    count=label_list[-1]
                    try:
                        found=count[0]=="("
                    except:
                        pass
                    else:
                        try:
                            found=count[-1]==")"
                        except:
                            pass
                except:
                    pass
                if found:
                    try:
                        num=int(count[1:-1])
                    except:
                        pass
                    else:
                        new_label=" ".join(label_list[0:-1])
                        new_label+=" (%d)" % (num+delta)
                        self.countChanged[page_index]=True
                        self.setTabLabel(self.page(page_index),new_label)
                else:
                    new_label=" ".join(label_list)
                    new_label+=" (%d)" % delta
                    self.countChanged[page_index]=True
                    self.setTabLabel(self.page(page_index),new_label)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # that's the real page
            return scrollview


    class label(qt.QLabel):
        def __init__(self, *args, **kwargs):
            qt.QLabel.__init__(self, *args)

            self.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)

 
    items = { "vbox": verticalBox,
              "hbox": horizontalBox,
              "vgroupbox": verticalGroupBox,
              "hgroupbox": horizontalGroupBox,
              "vspacer": verticalSpacer,
              "hspacer": horizontalSpacer,
              "icon": label,
              "label": label,
              "tab": tabWidget,
              "hsplitter": horizontalSplitter,
              "vsplitter": verticalSplitter }


    def __init__(self, *args, **kwargs):
        if kwargs.get('noBorder', False):
            _args = [None, "", qt.Qt.WStyle_Customize | qt.Qt.WStyle_Splash]
            for i in range(len(args)):
                _args[i]=args[i]
            qt.QScrollView.__init__(self, *_args)
        else:
            qt.QScrollView.__init__(self, *args)

        self.additionalWindows = {}
        self.__putBackColors = None
        self.executionMode=kwargs.get('executionMode', False)
        self.previewItems = {}
        self.currentWindow = None
        
        self.setCaption("GUI preview")
        self.setResizePolicy(qt.QScrollView.AutoOneFit)
        
        self.centralWidget = qt.QWidget(self.viewport())
        self.addChild(self.centralWidget)
        qt.QVBoxLayout(self.centralWidget)
        

    def show(self, *args):
        ret=qt.QWidget.show(self)

        self.emit(qt.PYSIGNAL("isShown"), ())

        return ret
    

    def hide(self, *args):
        ret=qt.QWidget.hide(self)

        self.emit(qt.PYSIGNAL("isHidden"), ())

        return ret
    

    def setCaption(self, *args):
        ret=qt.QWidget.setCaption(self, *args)

        return ret

    def exitExpertMode(self, *args):
        if len(args) > 0:
          if args[0]:
            return
        BlissWidget._menuBar.setExpertMode(False)
        BlissWidget._menuBar.expertMode.setChecked(False)

    def addItem(self, item_cfg, parent):
        type = item_cfg["type"]
        item_name = item_cfg["name"]
        newItem = None

        try:
            klass = WindowDisplayWidget.items[type]
        except KeyError:
            # item is a brick
            newItem = item_cfg["brick"]
            newItem.reparent(parent, 0, qt.QPoint(0,0), True)
        else:
            #print 'adding %s, executionMode=%s' % (item_cfg["name"], self.executionMode)
            newItem = klass(parent, item_cfg["name"], executionMode=self.executionMode)
            
            if type in ("vbox", "hbox", "vgroupbox", "hgroupbox"):
                if item_cfg["properties"]["color"] is not None:
                    try:
                        qtcolor = qt.QColor(item_cfg["properties"]["color"])
                        newItem.setPaletteBackgroundColor(qt.QColor(qtcolor.red(),
                                                                    qtcolor.green(),
                                                                    qtcolor.blue()))
                    except:
                        logging.getLogger().exception("Could not set color on item %s", item_cfg["name"])

                if type.endswith("groupbox"):
                    newItem.setTitle(item_cfg["properties"]["label"])
                    
                newItem.layout().setSpacing(item_cfg["properties"]["spacing"])
                newItem.layout().setMargin(item_cfg["properties"]["margin"])

                frame_style=qt.QFrame.NoFrame
                if item_cfg["properties"]["frameshape"]!="default":
                    print "frameshape... ", item_cfg["properties"]["frameshape"]
                    frame_style = getattr(qt.QFrame, item_cfg["properties"]["frameshape"].capitalize())
                if item_cfg["properties"]["shadowstyle"]!="default":
                    frame_style = frame_style | getattr(qt.QFrame, item_cfg["properties"]["shadowstyle"].capitalize())
                if frame_style!=qt.QFrame.NoFrame:
                    try:
                        newItem.setFrameStyle(frame_style)
                    except:
                        logging.getLogger().exception("Could not set frame style on item %s", item_cfg["name"])
            elif type == "icon":
                img = qt.QPixmap()
                if img.load(item_cfg["properties"]["filename"]):
                    newItem.setPixmap(img)
            elif type == "label":
                newItem.setText(item_cfg["properties"]["text"])
            elif type == "tab":
                item_cfg.widget = newItem
                newItem.cmdCloseTab = qt.QToolButton(newItem)
                newItem.cmdCloseTab.setIconSet(qt.QIconSet(Icons.load('delete_small')))
                newItem.setCornerWidget(newItem.cmdCloseTab)
                newItem.cmdCloseTab.hide()
                def close_current_page(tab=newItem):
                  slotName = "hidePage_%s" % str(tab.tabLabel(tab.currentPage()))
                  slotName = slotName.replace(" ", "_")
                  getattr(tab, slotName)()
                  qt.qApp.emit(qt.PYSIGNAL('tab_closed'), (tab, slotName))
                  
                newItem._close_current_page_cb = close_current_page
                qt.QObject.connect(newItem, qt.SIGNAL('currentChanged( QWidget * )'), item_cfg.notebookPageChanged)
                qt.QObject.connect(newItem.cmdCloseTab, qt.SIGNAL("clicked()"), close_current_page)
            elif type == "vsplitter" or type == "hsplitter":
                pass
                
            newItem.show()
                                                                             
        return newItem

    
    def makeItem(self, item_cfg, parent, containerIds):
        if isinstance(item_cfg, ContainerCfg):
            self.containerNum += 1
            previewItemsList = [parent]

            try:
                self.previewItems[self.currentWindow][containerIds[self.containerNum]] = previewItemsList
            except:
                pass
            
        for child in item_cfg["children"]:
            try:
                newItem = self.addItem(child, parent)
            except:
                logging.getLogger().exception("Cannot add item %s", child["name"])
            else:
                if not self.executionMode:
                    # install event filter to react on left mouse button released
                    newItem.installEventFilter(self)
                    
                previewItemsList.append(newItem)

            if parent.__class__ == WindowDisplayWidget.items["tab"]:
                # adding to tab widget
                parent.hide()
                newTab = parent.addTab(newItem, child["properties"]["label"], child["properties"]["icon"])
                newTab.item_cfg = child
                previewItemsList.append(newTab)
                parent.show()
            else:
                if isinstance(child, ContainerCfg):
                    #print 'setting size policy ; hsizepolicy=%s, vsizepolicy=%s' % (child["properties"]["hsizepolicy"], child["properties"]["vsizepolicy"])
                    newItem.setSizePolicy(self.getSizePolicy(child["properties"]["hsizepolicy"], child["properties"]["vsizepolicy"]))

                # handles fontSize, except for bricks
                if not isinstance(child, BrickCfg):
                    if child["properties"].hasProperty("fontSize"):
                        f = newItem.font()
                        if child["properties"]["fontSize"] <= 0:
                            child["properties"].getProperty("fontSize").setValue(f.pointSize())
                        else:
                            f.setPointSize(child["properties"]["fontSize"])
                            newItem.setFont(f)

                if hasattr(parent, "_preferred_layout"):
                    layout = parent._preferred_layout
                else:
                    layout = parent.layout()

                if layout is not None:
                    # layout can be none if parent is a Splitter for example
                    if not isinstance(child, BrickCfg):
                        alignment_flags = self.getAlignmentFlags(child["properties"]["alignment"])
                    else:
                        alignment_flags = 0
                    #print 'alignment flags for %s: %s (%d)' % (child["name"], child["properties"]["alignment"], alignment_flags)

                    if isinstance(child, SpacerCfg):
                        stretch = 1

                        if child["properties"]["fixed_size"]:
                            newItem.setFixedSize(child["properties"]["size"])
                    else:
                        stretch = 0

                    layout.addWidget(newItem, stretch, alignment_flags)

            self.makeItem(child, newItem, containerIds)


    def updatePreview(self, container_cfg, window_id, container_ids = [], selected_item=""):
        # remove additional windows
        for (w, m) in self.additionalWindows.itervalues():
            w.close()
        
        # reset colors
        if callable(self.__putBackColors):
            self.__putBackColors()
            self.__putBackColors = None

        #print 'updating', container_cfg["name"], container_ids
 
        if self.currentWindow is not None and self.currentWindow != window_id:
            # remove all bricks and destroy all other items
            previewItems = self.previewItems[self.currentWindow]
            
            for container_id, itemsList in previewItems.iteritems():
                for widget in itemsList:
                    if isinstance(widget, BlissWidget):
                        i = itemsList.index(widget)
                        
                        widget.hide()
                        widget.reparent(None, 0, qt.QPoint(0,0))

            self.previewItems = {}
            
            self.centralWidget.close(True)
            self.centralWidget = qt.QWidget(self.viewport())
            self.addChild(self.centralWidget)
            qt.QVBoxLayout(self.centralWidget)
            self.centralWidget.show()

        self.currentWindow = window_id
        self.containerNum = -1
        
        try:
            previewItems = self.previewItems[window_id]
        except KeyError:
            # new window
            previewItems = {}
            self.previewItems[window_id] = previewItems

        #print previewItems
            
        try:
            parent = previewItems[container_ids[0]][0]
        except:
            #print 'except ! parent of', container_cfg["name"], 'will be central widget'
            parent = self.centralWidget
        else:
            #print 'parent of', container_cfg["name"], 'will be', parent
            pass
        
        # reparent bricks to prevent them from being deleted,
        # and remove them from the previewItems list 
        for container_id in container_ids:
            for widget in previewItems.get(container_id, ()):
                if isinstance(widget, BlissWidget):
                    i = previewItems[container_id].index(widget)
                    widget.hide()
                    widget.reparent(None, 0, qt.QPoint(0,0))
                        
                    previewItems[container_id][i] = None

        try:
            for w in filter(None, previewItems[container_ids[0]][1:]):
                w.close(True)
        except Exception:
            pass

        if isinstance(container_cfg, WindowCfg):
            # update entire window
            previewItems = {}

            self.setName(container_cfg["name"])

            # update menubar ?
            if container_cfg.properties["menubar"]:
                if not window_id in self.additionalWindows:
                    menubar = MenuBar(self, container_cfg.properties["menudata"], container_cfg.properties["expertPwd"], executionMode=self.executionMode)
                    #self._menuBar = menubar
                    BlissWidget._menuBar=menubar
                    self.additionalWindows[window_id] = (container_cfg.menuEditor(), menubar)

                # this is to show menu configuration - NOT DONE YET
                #if not self.executionMode:
                #    self.additionalWindows[window_id][0].show()
                self.additionalWindows[window_id][1].show()
            else:
                try:
                    self.additionalWindows[window_id][1].hide()
                except:
                    pass
        else:
            try:
                del previewItems[container_ids[0]][1:]
            except KeyError:
                # preview items does not exist, no need to delete it
                pass
            
        self.makeItem(container_cfg, parent, container_ids)

        if len(selected_item):
            for item_list in previewItems.itervalues():
                for item in item_list:
                    if item.name() == selected_item:
                        self.selectWidget(item)
                        return

        if isinstance(container_cfg, WindowCfg):
            if container_cfg.properties["statusbar"]:
                StatusBar(self)


    def selectWidget(self, w):
        if callable(self.__putBackColors):
            self.__putBackColors()

        orig_bkgd_color = w.paletteBackgroundColor()
        r = orig_bkgd_color.red()
        g = orig_bkgd_color.green()
        b = orig_bkgd_color.blue()
        bkgd_color=w.palette().active().highlight()
        bkgd_color2=qt.QColor()
        #bkgd_color2.setRgb(255,0,0)
        bkgd_color2.setRgb(qt.qRgba(bkgd_color.red(), bkgd_color.green(), bkgd_color.blue(), 127))
        w.setPaletteBackgroundColor(bkgd_color2)
     
        def putBackColors(wref=weakref.ref(w), bkgd_color=(r,g,b)):
            #print 'should put back colors', wref
            w = wref()
            if w is not None:
                w.setPaletteBackgroundColor(qt.QColor(*bkgd_color))

        self.__putBackColors = putBackColors
        #qt.QTimer.singleShot(300, putBackColors)


    def eventFilter(self, w, e):
        if w is not None and e is not None:
            if e.type() == qt.QEvent.MouseButtonRelease and e.button() == qt.Qt.LeftButton:
                self.emit(qt.PYSIGNAL("itemClicked"), (w.name(), ))
                return True
        
        return qt.QScrollView.eventFilter(self, w, e)


    def getAlignmentFlags(self, alignment_directives_string):
        alignment_directives =  alignment_directives_string.split()
        alignment_flags = 0

        if "none" in alignment_directives:
            return alignment_flags

        if "hcenter" in alignment_directives:
            return qt.Qt.AlignHCenter

        if "vcenter" in alignment_directives:
            return qt.Qt.AlignVCenter
        
        if "top" in alignment_directives:
            alignment_flags = qt.Qt.AlignTop
        if "bottom" in alignment_directives:
            alignment_flags = qt.Qt.AlignBottom
        if "center" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = qt.Qt.AlignCenter
            else:
                alignment_flags = alignment_flags | qt.Qt.AlignHCenter
        if "left" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = qt.Qt.AlignLeft | qt.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | qt.Qt.AlignLeft
        if "right" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = qt.Qt.AlignRight | qt.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | qt.Qt.AlignRight
        return alignment_flags


    def getSizePolicy(self, hsizepolicy, vsizepolicy):
        def _getSizePolicyFlag(policy_flag):
            if policy_flag == "expanding":
                return qt.QSizePolicy.Ignored
            elif policy_flag == "fixed":
                return qt.QSizePolicy.Fixed
            else:
                # default
                return qt.QSizePolicy.Preferred

        return qt.QSizePolicy(_getSizePolicyFlag(hsizepolicy), _getSizePolicyFlag(vsizepolicy))


def display(configuration, noBorder=False):
    windows = []
    
    for window in configuration.windows_list:
        display = WindowDisplayWidget(None, window["name"], executionMode=True, noBorder=noBorder)
        windows.append(display)
        
        display.setCaption(window["properties"]["caption"])
        
        display.updatePreview(window, id(display))

        if window["properties"]["show"]:
            display._show=True
        else:
            display._show=False

        display.hide()

        restoreSizes(configuration, window, display)

    return windows

def restoreSizes(configuration, window, display, configurationSuffix="",moveWindowFlag = True):
    splitters = configuration.findAllChildrenWType("splitter", window)
    
    if len(splitters):
        for sw in display.queryList("QSplitter"):
            try:
                splitter = splitters[sw.name()]
                sw.setSizes(eval(splitter["properties"]["sizes%s" % configurationSuffix]))
            except KeyError:
                continue

    if(window["properties"]["x%s" % configurationSuffix] + 
       window["properties"]["y%s" % configurationSuffix] +
       window["properties"]["w%s" % configurationSuffix] +
       window["properties"]["h%s" % configurationSuffix] > 0):
        if moveWindowFlag: display.move(window["properties"]["x%s" % configurationSuffix], window["properties"]["y%s" % configurationSuffix])
        display.resize(qt.QSize(window["properties"]["w%s" % configurationSuffix], window["properties"]["h%s" % configurationSuffix]))
    
   
