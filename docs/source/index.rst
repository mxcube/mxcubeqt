MxCuBE Documentation
####################

MXCuBE stands for Macromolecular Xtallography CUstomized Beamline Environment.
The project started in 2005 at `ESRF <http://www.esrf.eu>`_, since then it has
been adopted by other institutes in Europe. In 2010, a collaboration
agreement has been signed for the development of MXCuBE with the following
partners:

* `ESRF <http://www.esrf.eu>`_
* `Soleil <http://www.synchrotron-soleil.fr/>`_
* `Max lab <https://www.maxlab.lu.se/>`_
* `HZB <http://www.helmholtz-berlin.de/>`_
* `EMBL <http://www.embl.org/>`_
* `Global Phasing Ltd. <http://www.globalphasing.com/>`_
* `ALBA <https://www.cells.es/en>`_
* `DESY <https://www.desy.de>`_

Latest news about the MXCuBE project can be found in the `project website <http://mxcube.github.io/mxcube/>`_.


MXCuBE consist of separated data acquisition control layer and graphical user interface.

.. rubric:: Data acquisition control

Data acquisition control is based on Hardware Objects as Python classes associated with a configuration XML file. Hardware Objects are instanciated by the `Hardware Repository <http://github.com/mxcube/HardwareRepository>`_.
Each Hardware Object should be based on an abstract class, defining a common API for MXCuBE. Then, implementation differs at each site depending on hardware and beamline specificities.
See the :doc:`design_overview` and :doc:`feature_overview` for more details.

.. rubric:: Graphical user interface

MXCuBE has two graphical user interfaces:

* :doc:`qt_framework_overview` 
* :doc:`web_framework_overview` 

Information for users
*********************

* :doc:`gui_overview`
* :doc:`feature_overview`
* :doc:`user_manual`
* If you cite MXCuBE, please use the reference:
.. note:: 
   Gabadinho, J. et al. (2010). MxCuBE: a synchrotron beamline control environment customized for macromolecular crystallography experiments. J. Synchrotron Rad. 17, 700-707

* `Article <http://www.ncbi.nlm.nih.gov/pubmed/20724792>`_


Information for developers
**************************

Installation instructions
=========================
* :doc:`installation_instructions_qt4`
* :doc:`installation_instructions_web`

Tutorials and How to's
======================
* :doc:`how_to_create_hwobj`
* :doc:`how_to_create_qt_brick`
* :doc:`how_to_define_qt_gui` 
* :doc:`tutorial_qt_gui`

API
===
* :doc:`packages/HardwareObjects`
* :doc:`packages/example_files`

Other information
*****************
* :doc:`mxcube_meetings`
* :doc:`changelog`
