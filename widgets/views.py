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

from .. import PYQT_VERSION
if PYQT_VERSION == 5:
    from PyQt5 import QtGui
    from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty
else:
    #lint:disable
    from PyQt4 import QtGui, QtCore
    from PyQt4.QtCore import Qt, pyqtSignal, pyqtProperty
    QtWidgets = QtGui
    QtCore.QItemSelectionModel = QtGui.QItemSelectionModel
    #lint:enable

QondaResizeRole = 64


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
                    selection = QtCore.QItemSelectionModel(self.model())
                    selection.select(idx, QtCore.QItemSelectionModel.Select)
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

    def _adjustColumnsToModel(self, header, model):
        for i in range(0, model.columnCount()):
            size = model.headerData(i, Qt.Horizontal, Qt.SizeHintRole)
            if size is not None:
                header.resizeSection(i, size.width())
            mode = model.headerData(i, Qt.Horizontal, QondaResizeRole)
            if mode is None:
                mode = header.Interactive
            header.setResizeMode(i, mode)


class TableView(QtWidgets.QTableView, EditableView):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        EditableView.__init__(self)
        QtWidgets.QTableView.__init__(self, parent)

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(TableView, self).keyPressEvent(event)

    def currentChanged(self, current, previous):
        super(TableView, self).currentChanged(current, previous)
        row = current.row()
        if row != previous.row():
            self.currentRowChanged.emit(row)

    def setModel(self, model):
        QtWidgets.QTableView.setModel(self, model)
        if model is not None:
            self._adjustColumnsToModel(self.horizontalHeader(), model)


class TreeView(QtWidgets.QTreeView, EditableView):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        EditableView.__init__(self)
        QtWidgets.QTreeView.__init__(self, parent)

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

    def setModel(self, model):
        QtWidgets.QTreeView.setModel(self, model)
        if model is not None:
            self._adjustColumnsToModel(self.header(), model)
