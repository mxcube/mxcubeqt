How to create new GUI brick in Qt version
#########################################

Before creating and submiting a new brick to the git repository, 
please inspect `BlissFramework/Bricks <https://github.com/mxcube/BlissFramework/tree/master/Bricks>`_ 
and `mxcube/Bricks <https://github.com/mxcube/mxcube/tree/master/Bricks>`_ 
if there is a brick that might fit to your need.
The main idea is to keep a commot graphical layout among many software users and 
try to keep optimal set of bricks.

Simple brick
************

It is recommended to copy an existing brick and add all necessary gui element.
A template for a new brick based on Qt4 graphics:

.. code-block:: python

   from PyQt4 import QtGui
   from PyQt4 import QtCore

   from BlissFramework.Qt4_BaseComponents import BlissWidget

   __category__ = "General"

   class Qt4_ExampleBrick(BlissWidget):

       def __init__(self):
           BlissWidget.__init__(self)

           # Hardware objects ----------------------------------------------------

           # Internal variables --------------------------------------------------

           # Properties ---------------------------------------------------------- 

           # Signals ------------------------------------------------------------

           # Slots ---------------------------------------------------------------

           # Graphic elements ----------------------------------------------------

           # Layout --------------------------------------------------------------
           _main_vlayout = QtGui.QVBoxLayout(self)
           _main_vlayout.setSpacing(2)
           _main_vlayout.setContentsMargins(2, 2, 2, 2)

           # SizePolicies --------------------------------------------------------

           # Qt signal/slot connections ------------------------------------------
 
           # Other ---------------------------------------------------------------


Pogramming guidlines:

* Follow :doc:`Best practices <qt_framework_overview>` when programming in Qt.
* Use code sections (hardware objects, internal variables, properties). in ``__init__``  method to structarize code.

 


Brick based on widgets
---------------------------------

Brick with Qt designer
---------------------------------

Adding hardware object to the brick
-----------------------------------
