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


import logging
import weakref
import new

from PyQt4 import QtCore
from PyQt4 import QtGui

from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseLayoutItems import BrickCfg, SpacerCfg, LabelCfg, WindowCfg, ContainerCfg, TabCfg
from BlissFramework.Qt4_BaseComponents import BlissWidget
from BlissFramework import Qt4_Icons


class MenuBar(QtGui.QMenuBar):
    # parent *must* be the window ; it contains a centralWidget in its viewport
    def __init__(self, parent, data, expert_pwd, executionMode=False):
        QtGui.QMenuBar.__init__(self, parent.centralWidget)
        self.parent = parent
        self.parent.widget().layout().addWidget(self)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        
        self.data = data
        self.expertPwd = expert_pwd
        # the emitter is the top parent (the window itself, not the centralWidget)
        self.topParent = parent
        self.executionMode = executionMode
        
        self.file = QtGui.QPopupMenu(self)
        self.file.insertItem("Quit", self.quit)
        self.help = QtGui.QPopupMenu(self)
        self.help.insertItem("What's this ?", self.whatsthis)

        self.insertItem("File", self.file)
        self.insertItem("Help", self.help)
        self.insertSeparator()
        self.expertMode = QtGui.QCheckBox("Expert mode",self)
        self.expertModeStdColor=None
        QtCore.QObject.connect(self.expertMode, QtCore.SIGNAL('clicked()'), self.expertModeClicked)
        self.insertItem(self.expertMode)


    def expertModeClicked(self):
        if self.expertMode.isChecked():
            res=qt.QInputDialog.getText("Switch to expert mode","Please enter the password:",qt.QLineEdit.Password)
            if res[1]:
                if str(res[0])==self.expertPwd:
                    self.expertMode.setPaletteBackgroundColor(QtGui.QWidget.yellow)
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
            QtCore.QObject.emit(self.topParent, QtCore.SIGNAL("enableExpertMode"), (True, ))

            # go through all bricks and execute the method
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    try:
                        w.setExpertMode(True)
                    except:
                        logging.getLogger().exception("Could not set %s to expert mode", w.name())
        else:
            # switch to user mode
            QtCore.QObject.emit(self.topParent, QtCore.SIGNAL("enableExpertMode"), (False, ))

            # go through all bricks and execute the method
            for w in QtGui.QApplication.allWidgets():
                if isinstance(w, BlissWidget):
                    QtGui.QWhatsThis.remove(w)
                    try:
                        w.setExpertMode(False)
                    except:
                        logging.getLogger().exception("Could not set %s to user mode", w.name())


    def whatsthis(self):
        if self.executionMode:
            BlissWidget.updateWhatsThis()


    def quit(self):
        if self.executionMode:
            QtCore.QObject.emit(self.topParent, QtCore.SIGNAL("quit"), ())
            QtGui.QApplication.quit()


class StatusBar(QtGui.QStatusBar):
    # parent *must* be the window ; it contains a centralWidget in its viewport
    def __init__(self, parent, *args):
        QtGui.QStatusBar.__init__(self, parent.centralWidget, *args)
        parent.centralWidget.layout().addWidget(self)


class tabBar(QtGui.QTabBar):
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


class WindowDisplayWidget(QtGui.QScrollArea):

    class Spacer(QtGui.QFrame):
        def __init__(self, *args, **kwargs):
            QtGui.QFrame.__init__(self, args[0])
            self.setObjectName(args[1])

            self.orientation = kwargs.get("orientation", "horizontal")
            self.executionMode = kwargs.get("executionMode", False)

            self.setFixedSize(-1)

            if self.orientation == "horizontal":
                self.main_layout = QtGui.QHBoxLayout()
            else:
                self.main_layout = QtGui.QVBoxLayout() 
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(0,0,0,0)
            self.setLayout(self.main_layout)


        def setFixedSize(self, fixed_size):
            if fixed_size >= 0:
                hor_size_policy = self.orientation == "horizontal" and \
                                  QtGui.QSizePolicy.Fixed or QtGui.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == QtGui.QSizePolicy.Fixed and \
                                  QtGui.QSizePolicy.MinimumExpanding or QtGui.QSizePolicy.Fixed
                
                if self.orientation == "horizontal":
                    self.setFixedWidth(fixed_size)
                else:
                    self.setFixedHeight(fixed_size)
            else:
                hor_size_policy = self.orientation == "horizontal" and \
                                  QtGui.QSizePolicy.Expanding or QtGui.QSizePolicy.MinimumExpanding
                ver_size_policy = hor_size_policy == QtGui.QSizePolicy.Expanding and \
                                  QtGui.QSizePolicy.MinimumExpanding or QtGui.QSizePolicy.Expanding
            self.setSizePolicy(hor_size_policy, ver_size_policy)
                
            
        def paintEvent(self, event):
            QtGui.QFrame.paintEvent(self, event)

            if self.executionMode:
                return

            p = QtGui.QPainter(self)
            p.setPen(QtGui.QPen(QtCore.Qt.black, 3))

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
        return QtGui.QSplitter(QtCore.Qt.Horizontal, *args)


    def verticalSplitter(*args, **kwargs):
        return QtGui.QSplitter(QtCore.Qt.Vertical, *args)
    

    def verticalBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)

        frame = QtGui.QFrame(args[0])
        frame.setObjectName(args[1])
        frame.setFrameStyle(QtGui.QFrame.Box)
        if not executionMode:
            frame.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        frame_layout = QtGui.QVBoxLayout() 
        frame_layout.setSpacing(0) 
        frame_layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame_layout)
 
        return frame
 

    def horizontalBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)

        frame = QtGui.QFrame(args[0])
        frame.setObjectName(args[1])

        frame.setFrameStyle(QtGui.QFrame.Box)
        if not executionMode:
            frame.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        frame_layout = QtGui.QHBoxLayout()
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(0,0,0,0)
        frame.setLayout(frame_layout) 

        return frame
       
        
    def horizontalGroupBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)
       
        groupbox = QtGui.QGroupBox(args[0])
        groupbox.setObjectName(args[1])      
        groupbox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
 
        group_box_layout = QtGui.QHBoxLayout()
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0,0,0,0)
        groupbox.setLayout(group_box_layout) 

        return groupbox


    def verticalGroupBox(*args, **kwargs):
        executionMode = kwargs.get('executionMode', False)

        groupbox = QtGui.QGroupBox(args[0])
        groupbox.setObjectName(args[1])
        groupbox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        group_box_layout = QtGui.QVBoxLayout()
        group_box_layout.setSpacing(0)
        group_box_layout.setContentsMargins(0,0,0,0)
        groupbox.setLayout(group_box_layout)

        return groupbox        

    class tabWidget(QtGui.QTabWidget):
        def __init__(self, *args, **kwargs):
            QtGui.QTabWidget.__init__(self, args[0])
            self.setObjectName(args[1])

            tab_bar=tabBar(self)
            tab_bar.palette()
            self.setTabBar(tab_bar)
            self.countChanged={}

            main_layout = QtGui.QVBoxLayout()
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0,0,0,0)
            self.setLayout(main_layout)

            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

            QtCore.QObject.connect(self, QtCore.SIGNAL('currentChanged( QWidget * )'), self._pageChanged)
        
        def _pageChanged(self, page):
            index=self.indexOf(page)
            self.countChanged[index]=False

            tab_label=str(self.tabText(self.indexOf(page)))
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
            self.emit(QtCore.SIGNAL("notebookPageChanged"), orig_label)
            QtGui.QApplication.emit(self, QtCore.SIGNAL('tab_changed'), index, page)

            tab_name = self.objectName()
            BlissWidget.updateTabWidget(tab_name,index)


        def hasCountChanged(self,tab_index):
            try:
                changed=self.countChanged[tab_index]
            except KeyError:
                changed=False
            return changed


        def addTab(self, page_widget, label, icon=""):
            print "addTab: ", page_widget, label, icon
            scroll_area = QtGui.QScrollArea(self)
            scroll_area.setFrameStyle(QtGui.QFrame.NoFrame)
          
            self.centralWidget = QtGui.QWidget(scroll_area.widget())
            self.centralWidget_layout = QtGui.QVBoxLayout()
            self.centralWidget.setLayout(self.centralWidget_layout)

            self.centralWidget.show()

            main_layout = QtGui.QVBoxLayout()
            main_layout.addWidget(self.centralWidget)
            scroll_area.setLayout(main_layout) 
             


            #scrollview.setResizePolicy(QtGui.QScrollArea.AutoOneFit)
            if icon!="":
                icon = QtGui.QIcon(Qt4_Icons.load(icon))
                QtGui.QTabWidget.addTab(self, scroll_area, icon, label)
            else:
                QtGui.QTabWidget.addTab(self, scroll_area, label)
            #page_widget.setParent(scroll_area.viewport())

            #scroll_area.widget().layout().addWidget(page_widget) 
            #page_widget.reparent(scrollview.widget())
            #page_widget.show()
            

            scroll_area.setWidget(page_widget)
                
            # add 'show page' slot
            slotName = "showPage_%s" % label
            def tab_slot(self, page_index=self.indexOf(scroll_area)):
                self.setCurrentWidget(self.page(page_index))
            try:
                self.__dict__[slotName.replace(" ", "_")] = new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.name()))

            # add 'hide page' slot
            slotName = "hidePage_%s" % label
            def tab_slot(self, hide=True, page = {"widget" : scroll_area, \
                         "label": self.tabText(self.indexOf(scroll_area)), 
                         "index" : self.indexOf(scroll_area), 
                         "icon": icon, "hidden" : False}):
                if hide:
                  if not page["hidden"]:
                    self.removePage(page["widget"])
                    page["hidden"] = True
                else:
                  if page["hidden"]:
                    if icon:
                      pixmap = Qt4_Icons.load(icon)
                      self.insertTab(page["widget"], QtGui.QIcon(pixmap,pixmap), label, page["index"])
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
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.page(page_index).setEnabled(enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # add 'enable tab' slot
            slotName = "enableTab_%s" % label
            def tab_slot(self, enable, page_index=self.indexOf(scroll_area)):
                self.setTabEnabled(self.page(page_index),enable)
            try:
                self.__dict__[slotName.replace(" ", "_")]=new.instancemethod(tab_slot, self, None)
            except:
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # add 'tab reset count' slot
            slotName = "resetTabCount_%s" % label
            def tab_slot(self, erase_count, page_index=self.indexOf(scroll_area)):
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
            def tab_slot(self, delta, only_if_hidden, page_index=self.indexOf(scroll_area)):
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
                logging.getLogger().exception("Could not add slot %s in %s", slotName, str(self.objectName()))

            # that's the real page
            return scroll_area


    class label(QtGui.QLabel):
        def __init__(self, *args, **kwargs):
            QtGui.QLabel.__init__(self, args[0])
            self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
 
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
        QtGui.QScrollArea.__init__(self, args[0])

        self.additionalWindows = {}
        self.__putBackColors = None
        self.executionMode=kwargs.get('executionMode', False)
        self.preview_items = []
        self.currentWindow = None
        self.setWindowTitle("GUI preview")
       
        self.centralWidget = QtGui.QWidget(self.widget())
        #self.centralWidget.setObjectName("deee")
        self.centralWidget_layout = QtGui.QVBoxLayout() 
        self.centralWidget.setLayout(self.centralWidget_layout)

        self.centralWidget.show()

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.centralWidget)
        self.setLayout(main_layout)

    def show(self, *args):
        ret = QtGui.QWidget.show(self)
        self.emit(QtCore.SIGNAL("isShown"), ())
        return ret
    

    def hide(self, *args):
        ret = QtGui.QWidget.hide(self)
        self.emit(QtCore.SIGNAL("isHidden"), ())
        return ret
    

    def setCaption(self, *args):
        ret=QtGui.QWidget.setWindowTitle(self, *args)
        return ret

    def exitExpertMode(self, *args):
        if len(args) > 0:
          if args[0]:
            return
        BlissWidget._menuBar.setExpertMode(False)
        BlissWidget._menuBar.expertMode.setChecked(False)

    def addItem(self, item_cfg, parent):
        item_type = item_cfg["type"]
        item_name = item_cfg["name"]
        newItem = None
        try:
            klass = WindowDisplayWidget.items[item_type]
        except KeyError:
            newItem = item_cfg["brick"]
          
            #newItem.reparent(parent)
        else:
            newItem = klass(parent, item_cfg["name"], executionMode=self.executionMode)
            
            if item_type in ("vbox", "hbox", "vgroupbox", "hgroupbox"):
                if item_cfg["properties"]["color"] is not None:
                    try:
                        qtcolor = QtGui.QColor(item_cfg["properties"]["color"])
                        newItem_palette = newItem.palette()
                        newItem_palette.setColor(QtGui.QPalette.Background, 
                                                 QtGui.QColor(qtcolor.red(),
                                                 qtcolor.green(),
                                                 qtcolor.blue())) 
                        newItem.setPalette(newItem_palette)
                        #newItem.setPaletteBackgroundColor(QtGui.QColor(qtcolor.red(),
                        #                                            qtcolor.green(),
                        #                                            qtcolor.blue()))
                    except:
                        logging.getLogger().exception("Could not set color on item %s", item_cfg["name"])

                if item_type.endswith("groupbox"):
                    newItem.setTitle(item_cfg["properties"]["label"])
                    
                newItem.layout().setSpacing(item_cfg["properties"]["spacing"])
                newItem.layout().setMargin(item_cfg["properties"]["margin"])
                frame_style = QtGui.QFrame.NoFrame
                if item_cfg["properties"]["frameshape"]!="default":
                    frame_style = getattr(QtGui.QFrame, item_cfg["properties"]["frameshape"].capitalize())
                if item_cfg["properties"]["shadowstyle"]!="default":
                    frame_style = frame_style | getattr(QtGui.QFrame, item_cfg["properties"]["shadowstyle"].capitalize())
                if frame_style != QtGui.QFrame.NoFrame:
                    try:
                        newItem.setFrameStyle(frame_style)
                    except:
                        logging.getLogger().exception("Could not set frame style on item %s", item_cfg["name"])
            elif item_type == "icon":
                img = QtGui.QPixmap()
                if img.load(item_cfg["properties"]["filename"]):
                    newItem.setPixmap(img)
            elif item_type == "label":
                newItem.setText(item_cfg["properties"]["text"])
            elif item_type == "tab":
                item_cfg.widget = newItem
                newItem.cmdCloseTab = QtGui.QToolButton(newItem)
                newItem.cmdCloseTab.setIcon(QtGui.QIcon(Qt4_Icons.load('delete_small')))
                newItem.setCornerWidget(newItem.cmdCloseTab)
                newItem.cmdCloseTab.hide()
                def close_current_page(tab=newItem):
                  slotName = "hidePage_%s" % str(tab.tabLabel(tab.currentPage()))
                  slotName = slotName.replace(" ", "_")
                  getattr(tab, slotName)()
                  QtGui.QApplicaiton.emit(QtCore.SIGNAL('tab_closed'), tab, slotName)
                def current_item_changed(item_index):
                  item_cfg.notebookPageChanged(newItem.widget(item_index))                  
                newItem._close_current_page_cb = close_current_page
               
                QtCore.QObject.connect(newItem, QtCore.SIGNAL('currentChanged(int)'), current_item_changed)
                QtCore.QObject.connect(newItem.cmdCloseTab, QtCore.SIGNAL("clicked()"), close_current_page)
            elif item_type == "vsplitter" or type == "hsplitter":
                pass
                
            newItem.show()
                                                                             
        return newItem
 
    def makeItem(self, item_cfg, parent):
        previewItemsList = []
        if isinstance(item_cfg, ContainerCfg):
            self.containerNum += 1
        for child in item_cfg["children"]:
            try:
                newItem = self.addItem(child, parent)
            except:
                logging.getLogger().exception("Cannot add item %s", child["name"])
            else:
                if not self.executionMode:
                    # install event filter to react on left mouse button released
                    newItem.installEventFilter(self)
                #previewItemsList.append(newItem)

            print "m"
            if parent.__class__ == WindowDisplayWidget.items["tab"]:
                print 1
                # adding to tab widget
                parent.hide()
                print newItem
                newItem.setFixedWidth(300)
                print newItem.sizePolicy()
                newTab = parent.addTab(newItem, child["properties"]["label"], child["properties"]["icon"])
                newTab2 = parent.addTab(QtGui.QLabel("demmmoo"), "2", child["properties"]["icon"])

                newTab.item_cfg = child
                previewItemsList.append(newTab)
                parent.show()
            else:
               
                if isinstance(child, ContainerCfg):
                    newItem.setSizePolicy(self.getSizePolicy(child["properties"]["hsizepolicy"], child["properties"]["vsizepolicy"]))                 
                # handles fontSize, except for bricks
                if not isinstance(child, BrickCfg):
                    if child["properties"].hasProperty("fontSize"):
                        f = newItem.font()
                        if child["properties"]["fontSize"] <= 0:
                            child["properties"].getProperty("fontSize").setValue(f.pointSize())
                        else:
                            f.setPointSize(int(child["properties"]["fontSize"]))
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
                    if isinstance(child, SpacerCfg):
                        stretch = 1

                        if child["properties"]["fixed_size"]:
                            newItem.setFixedSize(child["properties"]["size"])
                    else:
                        stretch = 0

                    
                    self.preview_items.append(newItem)
                    if alignment_flags is not None:
                        layout.addWidget(newItem, stretch, QtCore.Qt.Alignment(alignment_flags))
                    else:
                        layout.addWidget(newItem, stretch)
           
            self.makeItem(child, newItem)


    def drawPreview(self, container_cfg, window_id, container_ids = [], selected_item=""):
        for (w, m) in self.additionalWindows.itervalues():
            w.close()

        # reset colors
        if callable(self.__putBackColors):
            self.__putBackColors()
            self.__putBackColors = None

        if self.currentWindow is not None and self.currentWindow != window_id:
            # remove all bricks and destroy all other items
            previewItems = self.preview_items[self.currentWindow]
            self.preview_items = []
            self.centralWidget.close()
            self.centralWidget = QtGui.QWidget(self.viewport())
            self.central_widget_layout = QtGui.QVBoxLayout()
            self.centralWidget.setLayout(self.central_widget_layout)
            self.centralWidget.show()

        self.currentWindow = window_id
        self.containerNum = -1
        
        try:
            parent = previewItems[container_ids[0]][0]
        except:
            parent = self.centralWidget
        else:
            pass

        #self.preview_items.append(self.centralWidget)
        
        # reparent bricks to prevent them from being deleted,
        # and remove them from the previewItems list 
        self.setObjectName(container_cfg["name"])
        self.preview_items.append(self)

        if isinstance(container_cfg, WindowCfg):
            previewItems = {}
            self.setObjectName(container_cfg["name"])
            # update menubar ?
            if container_cfg.properties["menubar"]:
                if not window_id in self.additionalWindows:
                    menubar = MenuBar(self, container_cfg.properties["menudata"],\
                                      container_cfg.properties["expertPwd"],\
                                      executionMode=self.executionMode)
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

        self.makeItem(container_cfg, parent)

        if isinstance(container_cfg, WindowCfg):
            if container_cfg.properties["statusbar"]:
                StatusBar(self)

    def remove_widget(self, item_name, child_name_list):
        remove_item_list = child_name_list
        remove_item_list.append(item_name)

        for name in remove_item_list:
            for item_widget in self.preview_items:
                if item_widget.objectName() == name:
                    self.preview_items.remove(item_widget) 
                    item_widget.setParent(None)
        #item_widget.deleteLater()

    def add_widget(self, child, parent):
        #main window
        if parent is None:
            self.drawPreview(child, 0, [])
            
            #newItem = self.addItem(child, self)
            #self.preview_items.append(newItem)
            #self.layout.addWidget(newItem) 
        else:
            for item in self.preview_items:
                if item.objectName() == parent.name:
                    parent_item = item
            newItem = self.addItem(child, parent_item)
            if isinstance(parent, TabCfg):
                newTab = parent_item.addTab(newItem, child["properties"]["label"], child["properties"]["icon"])
                newTab.item_cfg = child
            else:   
                parent_item.layout().addWidget(newItem)
            self.preview_items.append(newItem)
  
    def updatePreview(self, container_cfg, window_id, container_ids = [], selected_item=""):
        if callable(self.__putBackColors):
            self.__putBackColors()
            self.__putBackColors = None
        if (len(selected_item) and 
            len(self.preview_items) > 0):
            for item in self.preview_items:
                if item.objectName() == selected_item:
                    self.selectWidget(item)
                    return

    def selectWidget(self, widget):
        """
        Descript. :
        Arguments : widget - widget which 
        Return    : None
        """
        if callable(self.__putBackColors):
            self.__putBackColors()
        widget_palette = widget.palette()
        orig_bkgd_color = widget_palette.color(QtGui.QPalette.Window)
        r = orig_bkgd_color.red()
        g = orig_bkgd_color.green()
        b = orig_bkgd_color.blue()
        bkgd_color = widget_palette.color(QtGui.QPalette.Window)
        bkgd_color2 = QtGui.QColor()
        #bkgd_color2.setRgb(255,0,0)
        #bkgd_color2.setRgb(QtGui.qRgba(bkgd_color.red(), bkgd_color.green(), bkgd_color.blue(), 127))
        bkgd_color2.setRgb(150,150,200)
        widget_palette.setColor(QtGui.QPalette.Background, bkgd_color2)         
        widget.setAutoFillBackground(True)
        widget.setPalette(widget_palette)

        #widet.setPaletteBackgroundColor(bkgd_color2)
     
        def putBackColors(wref=weakref.ref(widget), bkgd_color=(r,g,b)):
            widget = wref()
            if widget is not None:
                widget.setAutoFillBackground(False)
                widget_palette = widget.palette()
                widget_palette.setColor(QtGui.QPalette.Background, QtGui.QColor(*bkgd_color))
                widget.setPalette(widget_palette)
                #w.setPaletteBackgroundColor(QtGui.QColor(*bkgd_color))
        self.__putBackColors = putBackColors
        #qt.QTimer.singleShot(300, putBackColors)


    def eventFilter(self, widget, event):
        if widget is not None and event is not None:
            if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                self.emit(QtCore.SIGNAL("itemClicked"), widget.objectName())
                return True
        
        return QtGui.QScrollArea.eventFilter(self, widget, event)


    def getAlignmentFlags(self, alignment_directives_string):
        if alignment_directives_string is None:
            alignment_directives = ['none']
        else:
            alignment_directives =  alignment_directives_string.split()
        alignment_flags = 0

        if "none" in alignment_directives:
            return alignment_flags

        if "hcenter" in alignment_directives:
            return QtCore.Qt.AlignHCenter

        if "vcenter" in alignment_directives:
            return QtCore.Qt.AlignVCenter
        
        if "top" in alignment_directives:
            alignment_flags = QtCore.Qt.AlignTop
        if "bottom" in alignment_directives:
            alignment_flags = QtCore.Qt.AlignBottom
        if "center" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = QtCore.Qt.AlignCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignHCenter
        if "left" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = qt.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignLeft
        if "right" in alignment_directives:
            if alignment_flags == 0:
                alignment_flags = qt.Qt.AlignRight | QtCore.Qt.AlignVCenter
            else:
                alignment_flags = alignment_flags | QtCore.Qt.AlignRight
        return alignment_flags


    def getSizePolicy(self, hsizepolicy, vsizepolicy):
        def _getSizePolicyFlag(policy_flag):
            if policy_flag == "expanding":
                return QtGui.QSizePolicy.Expanding
            elif policy_flag == "fixed":
                return QtGui.QSizePolicy.Fixed
            else:
                # default
                return QtGui.QSizePolicy.Preferred

        return QtGui.QSizePolicy(_getSizePolicyFlag(hsizepolicy), _getSizePolicyFlag(vsizepolicy))


def display(configuration, noBorder=False):
    windows = []
    for window in configuration.windows_list:
        display = WindowDisplayWidget(None, window["name"], executionMode=True, noBorder=noBorder)
        windows.append(display)
        display.setCaption(window["properties"]["caption"])
        display.drawPreview(window, id(display))
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
        if moveWindowFlag: display.move(window["properties"]["x%s" % configurationSuffix], 
                                        window["properties"]["y%s" % configurationSuffix])
        display.resize(QtCore.QSize(window["properties"]["w%s" % configurationSuffix], 
                                    window["properties"]["h%s" % configurationSuffix]))
    
   
