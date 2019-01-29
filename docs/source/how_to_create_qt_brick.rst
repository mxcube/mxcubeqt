How to create GUI brick in Qt version
#####################################

* MXCuBE is based on building bricks that are linked together with GUI designer.
* Before creating and submiting a new brick to the git repository, please inspect `gui/bricks <https://github.com/mxcube/gui/tree/master/bricks>`_  directory if there is a brick that might fit to your needs.
* The main idea is to keep a commot graphical layout among many software users and try to keep optimal set of bricks.
* If it is necessary to create a new brick then use starting template and add necessary graphical elements:

.. code-block:: python

   import QtImport

   from gui.BaseComponents import BaseWidget

   __category__ = "General"

   class ExampleBrick(BaseWidget):

       def __init__(self):
           BaseWidget.__init__(self)

           # Hardware objects ----------------------------------------------------
           self.test_hwobj = None       

           # Internal variables --------------------------------------------------
           self.test_internal_variable = None

           # Properties ---------------------------------------------------------- 
           self.add_property('mnemonic', 'string', '')  
           self.add_property('booleanProperty', 'boolean', False)
           self.add_property('stringProperty', 'string', 'initString')
           self.add_property('integerPropery', 'integer', 0)
           self.add_property('comboProperty', 'combo', ("combo1", "combo2", "combo3"), "combo1")

           # Signals ------------------------------------------------------------
           self.defineSignal("test_brick_signal", ())

           # Slots ---------------------------------------------------------------
           self.defineSlot("test_brick_slot", ())

           # Graphic elements ----------------------------------------------------
           self.test_ledit = QtImport.QLineEdit("Test linedit", self)
           self.test_button = QtImport.QPushButton("Test button", self)
           self.test_combo = QtImport.QComboBox(self)

           # Layout --------------------------------------------------------------
           _main_vlayout = QtImport.QVBoxLayout(self)
           _main_vlayout.addWidget(self.test_ledit)
           _main_vlayout.addWidget(self.test_button)
           _main_vlayout.addWidget(self.test_combo)
           _main_vlayout.setSpacing(2)
           _main_vlayout.setContentsMargins(2, 2, 2, 2)

           # SizePolicies --------------------------------------------------------

           # Qt signal/slot connections ------------------------------------------
           self.test_ledit.textChanged.connect(self.test_ledit_text_changed)
           self.test_button.pressed.connect(self.test_button_pressed)
           self.test_combo.activated.connect(self.test_combo_activated)
 
           # Other ---------------------------------------------------------------


Pogramming guidlines
********************

* Follow :doc:`Best practices <qt_framework_overview>` when programming in Qt.
* ``Hardware objects`` defines used hardware objects. Use syntax ``self.***_hwobj``.
* ``Internal variables`` defines internal variables (booleans, strings, integers, lists etc). Use reasonable variable names (for example: self.energy_limits_list clearly defines that variable is a list that contains energy limits) and assign None or a default value.
* In ``Properties`` section properties of the brick are defined. With GUI designer these properties are defined. They are stored in the gui file and preserved when MXCuBE is closed. Method ``property_changed`` is executed at the startup and can be used to read these properties.

.. code-block:: python

   def property_changed(self, property_name, old_values, new_value):

        if property_name == "mnemonic":
            # property mnemonic is reserved for hardware objects
            # if there is a necessaty for more than one hardware object then
            # name the property based on hardware object (for example "energy")

            # disconnect signals if hwobj already exists

            if self.test_hwobj is not None:
                self.disconnect(self.test_hwobj, "testQtSignal", self.test_method)

            # with method getHardwareObject necessary hardware object is initialized
            # The value of the property should be the name of xml file that
            # contains the configuration of the hardware object.

            self.test_hwobj = self.get_hardware_object(new_value)

            # If hwobj is not initialized then function returns None

            if self.test_hwobj is not None:
                # If the hwobj is initialized then do necessary methods.
                # For example next line create qt signal/slot connection:
                # it binds "testQtSignal" of self.test_hwobj to self.test_method method
                # it means that when hwovj emits "testQtSignal" signal, self.test_method
                # will be called
                self.connect(self.test_hwobj, "testQtSignal", self.test_method)
            else:

                # If hwobj is not initialized then the brick is disabled
                self.setEnabled(False)
        elif property_name == "booleanProperty":
  
            # Do something with a boolean value
            pass
        elif property_name == "stringProperty":

            # Do something with a string value
            pass 
        elif property_name == "integerPropery":

            # Do something with an integer value
            pass
        elif property_name == "comboProperty":

            # combo style property is in a string type
            pass
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

* Use ``Signals`` and ``Slots`` to define interface between bricks. The only way how two separate bricks can communicate is via this signal and slot mechanism. Example code:

.. code-block:: python
   
   # in the code use method "emit" to emit neccessary signal
   self.emit("testBrickSignal", value_to_send)

   # define method with slot name to receive emited value
   self.test_brick_slot(self, received_value):
        pass

In the GUI builder define signal/slot connection:

.. figure:: images/qt_signals_slots.png
   :scale: 60 %
   :alt: qt_signals_slots

.. note::
   The number of variables emited via signal should much the number of variables received by a slot.
   
* ``Graphical elements`` section is used to define all graphical elements.
* ``Layout`` defines brick layout. All Qt widgets are grouped within the brick based on ``QHBoxLayout``, ``QVBoxLayout`` and ``QGridLayout``. Use ``addWidget`` to add widget to the layout, ``setSpacing`` to set spacing between tge wt widget, ``setContentsMargins`` to set the contents margins.
* ``SizePolicies`` define size policy (fixed size, expanding etc) of a widget.
* ``Qt signal/slot connections`` define signals/slots used within a brick. Here basic interations between basic Qt widgets are defined. Example:

.. code-block:: python

   self.test_ledit.textChanged.connect(self.test_ledit_text_changed)
   self.test_button.pressed.connect(self.test_button_pressed)
   self.test_combo.activated.connect(self.test_combo_activated)

   def test_ledit_text_changed(self, text_value):
       pass

   def test_button_pressed(self):
       pass

   def test_combo_activated(self, selected_index):
       pass

* ``Other``. It is recommended to add all other code here. It is recommended to just define (not write additional code) GUI element in ``Graphical elements`` and then all necessary code define in ``Other`` section.

Brick based on widgets
**********************

It is recommended to use widgets to compose a brick. A widget in the MXCuBE context is a basic graphical element that has a defined function. Widgets are not bricks and can not be used as a stand alone brick via GUI designer. All widget are located in `widgets directory <https://github.com/mxcube/mxcube/tree/master/gui/widgets>`_. 

In this example ``dc_tree_widget.py`` is used in  ``TreeBrick``.

.. code-block:: python
   class DataCollectTree(QtImport.QWidget):
         def __init__(self, parent = None, name = "data_collect",
                      selection_changed = None):
             """
             Descript. :
             """
             QtImport.QWidget.__init__(self, parent)
             self.setObjectName(name)



.. code-block:: python

   # ...
   from widgets.dc_tree_widget import DataCollectTree
   # ...

   self.dc_tree_widget = DataCollectTree(self)
  
   # ...
   main_layout = QtImport.QVBoxLayout(self)
   # ...
   main_layout.addWidget(self.dc_tree_widget)
   main_layout.setSpacing(0)
   main_layout.setContentsMargins(0, 0, 0, 0)
   
Bricks and widgets build by Qt designer
***************************************

Qt designer is a powefull tool that allows to create layout for widgets and bricks. When many graphical elements are used then the layout management becomes difficult and it is easy to get lost. With Qt designer a layout is designed and stored in ui file (see `ui files directory <https://github.com/mxcube/mxcube/tree/master/gui/ui_files>`_). This ui file is initialized and used via widget or Brick.

1. Use Qt designer to create layout and save ui file:

.. figure:: images/qt_designer.png
   :scale: 60 %
   :alt: qt_designer

2. Intiate ui file and use it in the graphics:

.. code-block:: python

   # ...
   self.sample_changer_widget = QtImport.load_ui_file(
        "sample_changer_widget_layout.ui")

   # ...
   # Access ui widget by its name
   self.sample_changer_widget.details_button.clicked.connect(\
        self.toggle_sample_changer_tab)
   self.sample_changer_widget.filter_cbox.activated.connect(\
        self.mount_mode_combo_changed)
   self.sample_changer_widget.centring_cbox.activated.connect(\
        self.dc_tree_widget.set_centring_method)
   self.sample_changer_widget.synch_ispyb_button.clicked.connect(\
        self.refresh_sample_list)

In this case ui file is used in the brick. If it was used in the widget then remove ``widget`` from the ui file path.

.. seealso::

   * `<http://doc.qt.io/qt-4.8/index.html>`_
   * `<http://doc.qt.io/qt-4.8/demos.html>`_
   * `<http://doc.qt.io/qt-4.8/tutorials.html>`_
   * `<http://doc.qt.io/qt-4.8/gettingstarted-develop.html>`_
   * `<http://doc.qt.io/qt-4.8/classes.html>`_
   * `<http://doc.qt.io/qt-4.8/qt.html>`_

Other information
*****************

* :doc:`how_to_create_hwobj`
* :doc:`how_to_define_qt_gui`
