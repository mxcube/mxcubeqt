Qt framework based GUI
===============

Best Practices
--------------
PEP-8 (http://www.python.org/dev/peps/pep-0008/) is used in general. However,
Qt diverges from PEP-8 and uses camel case notation. This can be seen in the diagrams
that contain Qt derived objects. New code should as much as possible confirm to PEP-8.

Qt Signals
----------
Qt signals provides an elegant way of decoupling Qt objects from each other. However
it can sometimes be difficult to understand the function of certain signals. Its therefore
very important that both signals and slots are properly documented. Some objects might
need alot of interaction/signals, it is in those cases recommended to use one signal to
get a reference to the receiver object. The reference can be used to access the receiver
object directly instead of defining alot of signals. This approach makes the code cleaner
and easier to understand.

Widget Logic
------------
Its recommended to separate widget logic from widget layout. One way of achieving that
is to implement the layout in one widget and then use that layout from a widget which
implements the logic. This pattern can be observed in a almost all new framework-2
bricks. The brick implements the logic and it has a widget which implements the layout.

Naming Conventions
-----------------
Attributes which reference Framework-2 hardware objects should end with hwobj, for in-
stance characterization hwobj or data collection hwobj. Names that are used frequently
and/or which together with other names create long attribute names are abbreviated.
The general rule is to use the first letter in each word. For instance, data collection
group and data collection would be abbreviated dcg and dc.

How to create a new brick
-------------------------

