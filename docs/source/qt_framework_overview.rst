Qt framework based GUI
######################

`BlissFramework <https://github.com/mxcube/BlissFramework.git>`_ is the graphical user interface 
based on bricks (available in 
`BlissFramework/Bricks <https://github.com/mxcube/BlissFramework/tree/master/Bricks>`_ and 
`mxcube/Bricks <https://github.com/mxcube/mxcube/tree/master/Bricks>`_)  
and basic layout items (horizonal box, vertical box, groupbox etc.). 
Originaly it was written in Qt3 and later adopted to the Qt4 platform. 
It is possible to run MXCuBE on both Qt versions (:doc:`installation_instructions_qt4`), but 
it is not possible to run both versions of Qt simultaneously. 
To clearly separate these two Qt version, Qt4 bricks, widgets and other 
files have prefix Qt4_.

Best Practices
**************
To format code PEP-8 (http://www.python.org/dev/peps/pep-0008/) is used in general. 
However, Qt diverges from PEP-8 and uses camel case notation. This can be seen in the diagrams
that contain Qt derived objects. New code should as much as possible confirm to PEP-8.

Qt Signals
**********
Qt signals provides an elegant way of decoupling Qt objects from each other. However
it can sometimes be difficult to understand the function of certain signals. Its therefore
very important that both signals and slots are properly documented. Some objects might
need alot of interaction/signals, it is in those cases recommended to use one signal to
get a reference to the receiver object. The reference can be used to access the receiver
object directly instead of defining alot of signals. This approach makes the code cleaner
and easier to understand.

Widget Logic
************
Its recommended to separate widget logic from widget layout. One way of achieving that
is to implement the layout in one widget and then use that layout from a widget which
implements the logic.

Naming Conventions
******************
Attributes which reference hardware objects should end with hwobj, for in-
stance characterization hwobj or data collection hwobj. Names that are used frequently
and/or which together with other names create long attribute names are abbreviated.
The general rule is to use the first letter in each word. For instance, data collection
group and data collection would be abbreviated dcg and dc.

Tutorials
*********
* :doc:`installation_instructions_qt4`
* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
* :doc:`how_to_define_gui`
