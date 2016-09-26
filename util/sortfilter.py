# -*- coding: utf-8 -*-
from .. import PYQT_VERSION

if PYQT_VERSION == 5:
    from PyQt5.QtCore import QSortFilterProxyModel
else:
    from PyQt4.QtGui import QSortFilterProxyModel
from ..mvc.adapters import PythonObjectRole


class NoneOrdering:

    FIRST = 1
    LAST = 2


class SortFilterProxyModel(QSortFilterProxyModel):
    """
        A minimal extension to QSortFilterProxyModel implementing
        Qonda's adapters API, notably getPyObject(), required by
        currentPyObject() methods in DataWidgetMapper and *View widgets
    """

    def __init__(self, parent=None, none_ordering=NoneOrdering.FIRST):
        super(SortFilterProxyModel, self).__init__(parent)
        self._none_ordering = none_ordering

    def getPyModel(self):
        return self.sourceModel.getPyModel()

    def getPyObject(self, index):
        return self.sourceModel().getPyObject(self.mapToSource(index))

    def getPropertyColumn(self, propertyName):
        return self.sourceModel().getPropertyColumn(propertyName)

    def getColumnProperty(self, col):
        return self.sourceModel().getColumnProperty(col)

    def properties(self):
        return self.sourceModel().properties()

    def lessThan(self, left, right):
        """
            Sort using Python ordering
        """
        left_data = left.data(PythonObjectRole)
        right_data = right.data(PythonObjectRole)
        if left_data is None:
            # None is less if NoneOrdering == FIRST
            return self._none_ordering == NoneOrdering.FIRST
        if right_data is None:
            # None is less if NoneOrdering == FIRST
            return self._none_ordering == NoneOrdering.LAST
        return left_data < right_data
