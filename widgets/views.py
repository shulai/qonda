# -*- coding: utf-8 -*-
#
# This file is part of the Qonda framework
# Qonda is (C)2010,2013 Julio César Gázquez
#
# Qonda is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Qonda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Qonda; If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, pyqtSignal, pyqtProperty


class EditableView(object):

    def __init__(self):
        self.__allowAppends = True
        self.__allowInserts = True
        self.__allowDeletes = True

    # TODO: Add attribute confirmDeletion
    def _keyPressEvent(self, event):
        # TODO: Implement confirmDeletion
        key = event.key()
        mod = event.modifiers()
        idx = self.currentIndex()
        current_row = idx.row()
        parent = idx.parent()
        row_count = self.model().rowCount(parent)
        if mod == Qt.NoModifier:
            if key == Qt.Key_Delete:
                self.model().setData(idx, u'', Qt.EditRole)
                self.dataChanged(idx, idx)
                event.accept()
            elif key == Qt.Key_Down and current_row + 1 == row_count:
                if self.__allowAppends:
                    idx = self.model().index(current_row + 1, 0, idx.parent())
                    self.model().insertRow(row_count, parent)
                    self.setCurrentIndex(idx)
                    event.accept()
        elif mod == Qt.ControlModifier:
            if key == Qt.Key_Insert:
                if self.__allowInserts:
                    idx = self.model().index(idx.row(), 0, idx.parent())
                    self.model().insertRow(current_row, parent)
                    # Selections get funny after insert
                    selection = QtGui.QItemSelectionModel(self.model())
                    selection.select(idx, QtGui.QItemSelectionModel.Select)
                    self.setSelectionModel(selection)
                    self.setCurrentIndex(idx)
                    event.accept()
            elif key == Qt.Key_Delete:
                if self.__allowDeletes:
                    if current_row + 1 == row_count:
                        self.setCurrentIndex(self.model().index(
                            current_row - 1, idx.column(), parent))
                    self.model().removeRow(current_row, parent)
                    event.accept()

    def getAllowAppends(self):
        return self.__allowAppends

    def setAllowAppends(self, value):
        self.__allowAppends = value

    def resetAllowAppends(self):
        self.__allowAppends = True

    allowAppends = pyqtProperty('bool', getAllowAppends, setAllowAppends)

    def getAllowInserts(self):
        return self.__allowInserts

    def setAllowInserts(self, value):
        self.__allowInserts = value

    def resetAllowInserts(self):
        self.__allowInserts = True

    allowInserts = pyqtProperty('bool', getAllowInserts, setAllowInserts)

    def getAllowDeletes(self):
        return self.__allowDeletes

    def setAllowDeletes(self, value):
        self.__allowDeletes = value

    def resetAllowDeletes(self):
        self.__allowDeletes = True

    allowDeletes = pyqtProperty('bool', getAllowDeletes, setAllowDeletes)


class TableView(QtGui.QTableView, EditableView):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        EditableView.__init__(self)
        QtGui.QTableView.__init__(self, parent)

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(TableView, self).keyPressEvent(event)

    def currentChanged(self, current, previous):
        super(TableView, self).currentChanged(current, previous)
        row = current.row()
        if row != previous.row():
            self.currentRowChanged.emit(row)


class TreeView(QtGui.QTreeView, EditableView):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        EditableView.__init__(self)
        QtGui.QTreeView.__init__(self, parent)

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(TreeView, self).keyPressEvent(event)

    def resizeColumnsToContents(self):
        for i in range(0, self.model().columnCount(self.rootIndex())):
            self.resizeColumnToContents(i)

    def currentChanged(self, current, previous):
        super(TreeView, self).currentChanged(current, previous)
        row = current.row()
        if row != previous.row():
            self.currentRowChanged.emit(row)
