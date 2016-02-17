How to define GUI in Qt version
###############################

* Start MXCuBE with **-d** argument (:doc:`see <installation_instructions_qt4>`).
* MXCuBE gui is based on a tree structure, composed from bricks and layout items (window, horizontal box, vertical box, horizontal groupbox, vertical groupbox, tab widget, spacers and images).
* All available brick are categorized on the left side.
* To add a new brick: select tree element and double click on the brick name. New brick will be added next to the selected brick element.
* Use **up** and **down** buttons to change the location of the brick.
* Use **delete** button to remove selected brick
* To change item properties click on the tree entry or click directly on the gui preview. Property window will be updated. If propery window is not available go to **Window/Properties**.

.. figure:: images/qt_gui_builder.png
   :scale: 50 %
   :alt: qt_gui_builder

* To manage signal/slot connection between bricks, click icon to open Connection editor.
* To add new connection choose emitter by selecting  window, object and signal, choose receiver by selecting window, object and signal, and press **Add connection**.
* Ro remove a connection, select established connection and press **Remove connection**.

.. figure:: images/qt_signals_slots.png
   :scale: 60 %
   :alt: qt_signals_slots


Other information
*****************

* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
