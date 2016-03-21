# -*- coding: utf-8 -*-

from .. import PYQT_VERSION
if PYQT_VERSION == 5:
    from .icons_pyqt5_rc import *
else:
    from .icons_pyqt4_rc import *