"""
FiltersBrick

[Description]
The Filters brick allow to move filters on the beamline.

[Properties]
---------------------------------------------
|  name    |  type  | description 
---------------------------------------------
| mnemonic | string | Filters Hardware Object
---------------------------------------------

[Signals]

[Slots]

[HardwareObjects]
Each filter axis is represented as a column, rows being the different
filters that can be put in the beam.

A cursor indicates which filter is set for each axis. The cursor color
shows if the axis is moving (yellow), if it is in error (red) or if it
is set properly (green).

User have to click on a cell in order to trigger the move.


Example of a valid Hardware Object XML file:
============================================
<equipment class = "Filters">
  <username>OH Filters</username>
  <axis>
    <device class="FilterAxis">
      <username>attf</username>
      <motor>/oh/motors/attf</motor>
      <filter>
       <username>Out</username>
       <offset>1</offset>
      </filter>
      <filter>
       <username>3mm PyroC</username>
       <offset>2</offset>
      </filter>
      <filter>
       <username>unusable</username>
       <offset>3</offset>
      </filter>
      <filter>
       <username>5mm PyroC</username>
       <offset>4</offset>
      </filter>
      <filter>
       <username>10mm PyroC</username>
       <offset>5</offset>
      </filter>
    </device>
  </axis>
  ...
  <axis>
  </axis>
</equipment>
"""

from BlissFramework import BaseComponents
from HardwareRepository import HardwareRepository
from BlissFramework import Icons
from qt import *

from qttable    import QTable, QTableItem
from functools import reduce

(OFF, MOVING, ON, ERROR) = (0,1,2,3) 


class FilterItem( QTableItem ):
    def __init__(self, table, text):
        QTableItem.__init__( self, table, QTableItem.Never, text)

        self.pixs  = [ Icons.load('blank'),        # OFF
                       Icons.load('red_led'),      # MOVING
                       Icons.load('green_led'),    # ON
                       Icons.load('yellow_led') ]  # ERROR
        self.off()

    def setState(self,state):
        self.setPixmap( self.pixs[state] )  

    def on(self):
        self.setPixmap(self.pixs[ON])
    def moving(self):
        self.setPixmap(self.pixs[MOVING])
    def off(self):
        self.setPixmap(self.pixs[OFF])
    def error(self):
        self.setPixmap(self.pixs[ERROR])


class FilterMotor:
    def __init__(self, table, motor, axisno ):
        self.table  = table
        self.motor  = motor
        self.axisno = axisno
        if self.motor is not None:
             self.motor.connect("positionChanged", self.positionChanged)
             self.motor.connect("stateChanged", self.stateChanged)
                     

    def move(self, posto):
         self.motor.move(posto) 


    def positionChanged( self, newPosition ):
        filterno = self.find_filter( newPosition )
        self.table.selectFilter( self.axisno, filterno )


    def find_filter( self, position ):
        filterno  = 0
        dist      = 10
        no        = 0  
        newpos    = float( position )

        for pos in self.table.filtpos[self.axisno]:
           calcdist = abs(position - float(pos))
           if calcdist < dist:
              filterno =  no
              dist     = calcdist
           no += 1

        return filterno

    def stateChanged( self, newState ):
        if newState == 2:
           self.table.setAxisState( self.axisno, ON)
        elif newState == 4:
           self.table.setAxisState( self.axisno, MOVING)
        else:
           self.table.setAxisState( self.axisno, ERROR)



class FilterTable_form( QTable ):

    def __init__(self,parent,*pars):

        QTable.__init__(self,parent,*pars)

        # Defaults
        self.setNumAxes    ( 1 )
        self.setLeftMargin ( 0 )

    def setNumAxes(self,naxes):

        self.naxes   = naxes
        self.current = [0,]    * self.naxes
        self.states  = [None,] * self.naxes
        self.nfilt   = [2,]    * self.naxes
        QTable.setNumCols( self, self.naxes )

        self.header  = self.horizontalHeader()
        self.header.setClickEnabled( 0 )

        self.current = [0,]   * self.naxes
        self.states  = [ON,]  * self.naxes
        self.nfilt   = [2,]   * self.naxes

    def setAxisLabel(self,axisno,label): 
        self.header.setLabel( axisno, label )

    def setFilterLabel(self,axisno,filterno,label):
        self.item(filterno, axisno).setText(label)
        self.updateCell( filterno, axisno )

    def setFilters(self,axisno,filters):

        self.nfilt[axisno] = len(filters)
        nrows = reduce( lambda a,b: a>b and a or b, self.nfilt ) 
        QTable.setNumRows( self, nrows )

        filtno = 0

        for filterlab in filters:
           self.setItem(filtno, axisno, FilterItem( self, filterlab )  )
           self.updateCell( filtno, axisno )
           filtno += 1

        self.nfilt[axisno] = filtno

class FilterTable( FilterTable_form ):

    def __init__(self,parent,*pars):
        FilterTable_form.__init__(self,parent,*pars)
        self.connect( self, SIGNAL("clicked(int,int,int,const QPoint &)"), self.clicked )

    def clicked(self,filtno,axisno,button=None,pos=None): 
        if self.states[axisno] == ON:
           self.selectFilter(axisno,filtno)
           self.emit( PYSIGNAL("filterChanged"),(axisno,filtno)) 
           self.moveFilterEvent(axisno,filtno)
        self.emit( PYSIGNAL("clicked"),(axisno,filtno)) 

    def moveFilterEvent(self,filtno,axisno):
        pass

    def selectFilter(self,axisno,filtno):

        curfilt = self.current[axisno]
        self.current[axisno] = filtno

        try:
           self.item(curfilt,axisno).off()
           self.item(filtno,axisno).setState( self.states[axisno] )

           self.updateCell(curfilt,axisno)
           self.updateCell(filtno,axisno)
        except:
            print("Filtno was ",filtno)

    def setAxisState(self,axisno,state):
        try:
           self.states[axisno] = state
           filtno = self.current[axisno]
           self.item(filtno,axisno).setState( self.states[axisno] )
           self.updateCell(filtno,axisno)
        except:
            print("Filtno was ",filtno)


class MotorizedFilterTable( FilterTable ):

   def setNumAxes( self, naxes ):
      FilterTable.setNumAxes( self, naxes )
      self.motors  = [None,] * naxes
      self.filtpos = [None,] * naxes

   def setFilterLabel(self,axisno,filterno,label):
        self.item(filterno, axisno).setText(label)
        self.updateCell( filterno, axisno )

   def setFilters(self,axisno,filters):
        self.filtpos[axisno] = list(range(len(filters)))

	filts = []
        for filterno in range(len(filters)):
            filter = filters[filterno][0] #username
            pos = filters[filterno][1] #offset
            self.filtpos[axisno][filterno] = pos
            filts.append(filter)
           
        FilterTable.setFilters( self, axisno, filts )

   def setMotor(self, axisno, mot):
      self.motors[axisno]  = FilterMotor( self, mot, axisno )

   def moveFilterEvent(self,axisno,filtno):
      pos = self.filtpos[axisno][filtno]
      mot = self.motors[axisno]
      if mot:
          mot.move(pos)


class FiltersBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.axes  = {}
        self.filterHwObj = None

        self.addProperty('mnemonic', 'string')
        
        #
        # create GUI elements
        #
        self.table        = MotorizedFilterTable( self )

        QGridLayout(self, 1, 1, 5, 5)
        self.layout().addWidget(self.table, 0, 0)

          
    def setMnemonic(self, mne):
        self['mnemonic'] = mne
        

    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'mnemonic':
            self.filterHwObj = self.getHardwareObject( newValue )

            if self.filterHwObj is not None:
                self.axes = self.filterHwObj.getAxes()
                self.table.setNumAxes( len(self.axes) )
                axisno = 0
                for axis in self.axes:
                    if not axis: continue
                    self.table.setAxisLabel( axisno, axis.userName() )
                    labels = axis.getAxisLabels() 
                    self.table.setFilters( axisno, labels ) 
                    self.table.setMotor( axisno, axis.getAxisMotor() )
                    axisno += 1   
            else:
                print("Cannot find filter object")















