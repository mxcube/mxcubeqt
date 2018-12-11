
'''
[Name] 

[Description]

This brick ..  

[Properties]
----------------------------------------------------------------------
| name                | type     | description
----------------------------------------------------------------------
|                     |          | 
|                     |          | 
|                     |          | 
----------------------------------------------------------------------
'''

from qt import *

from BlissFramework import BaseComponents

__category__ = 'GuiUtils'

class SpacerBrick(BaseComponents.BlissWidget):
    def __init__(self, *args):
        BaseComponents.BlissWidget.__init__(self, *args)

        self.addProperty('direction', 'combo', ('horizontal', 'vertical'), 'horizontal')
        self.addProperty('fixedSize', 'integer', 100)
        self.addProperty('autoSize', 'boolean', False)

        QHBoxLayout(self)
        self.layoutItem = QSpacerItem(100, 100, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout().addItem(self.layoutItem)
       
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._rowStretchFactor = 1000
        self._colStretchFactor = 1000


    def paintEvent(self, event):
        if not self.isRunning():
            p = QPainter(self)
            p.setPen(QPen(Qt.black, 3))
            
            if self['direction'] == 'horizontal':
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

        
    def propertyChanged(self, propertyName, oldValue, newValue):
        if propertyName == 'autoSize':
            self.layout().removeItem(self.layoutItem)

            if self['direction'] == 'horizontal':
                x = self['fixedSize']
                y = 10
            else:
                x = 10
                y = self['fixedSize']
                                     
            if self['direction'] == 'horizontal':
                if newValue:
                    xs = QSizePolicy.Expanding
                else:
                    xs = QSizePolicy.Fixed
                ys = QSizePolicy.Fixed
            else:
                xs = QSizePolicy.Fixed
                if newValue:
                    ys = QSizePolicy.Expanding
                else:
                    ys = QSizePolicy.Fixed

            self.layoutItem = QSpacerItem(x, y, xs, ys)
            self.layout().addItem(self.layoutItem)
            self.setSizePolicy(xs, ys)
            self.updateGeometry()
        elif propertyName == 'fixedSize':
            if newValue < 10:
                self.getProperty('fixedSize').setValue(10)

            #force refresh
            self['autoSize'] = self['autoSize']
        elif propertyName == 'direction':
            self['autoSize'] = self['autoSize']
            self.update()
            

