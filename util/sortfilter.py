# -*- coding: utf-8 -*-

from PyQt4.QtGui import QSortFilterProxyModel
from ..mvc.adapters import PythonObjectRole


class SortFilterProxyModel(QSortFilterProxyModel):
    """
        A minimal extension to QSortFilterProxyModel implementing
        Qonda's adapters API, notably getPyObject(), required by
        currentPyObject() methods in DataWidgetMapper and *View widgets
    """

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
        return left.data(PythonObjectRole) < right.data(PythonObjectRole)
