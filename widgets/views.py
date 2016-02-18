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
    from PyQt5 import QtGui, QtWidgets
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
        self.__confirmDeletion = False

    # TODO: Add attribute confirmDeletion
    def _keyPressEvent(self, event):
        # TODO: Implement confirmDeletion
        key = event.key()
        mod = event.modifiers()
        idx = self.currentIndex()
        current_row = idx.row()
        parent = idx.parent()
        try:
            row_count = self.model().rowCount(parent)
        except AttributeError:  # No model
            return
        if mod in (Qt.NoModifier, Qt.KeypadModifier):
            if key in (Qt.Key_Return, Qt.Key_Enter):
                col = idx.column()
                column_count = self.model().columnCount(parent)
                # Go to next column if exist and is not hidden
                new_col = col + 1
                processed = False
                while new_col < column_count:
                    print(new_col, column_count)
                    if self.isColumnHidden(new_col):
                        new_col += 1
                        continue
                    idx = self.model().index(current_row, new_col, parent)
                    self.setCurrentIndex(idx)
                    processed = True
                    break
                if not processed:
                    if current_row + 1 < row_count:
                        # Next row
                        # First non hidden column
                        new_col = next((acol for acol in range(column_count)
                            if not self.isColumnHidden(acol)))
                        idx = self.model().index(current_row + 1, new_col,
                            parent)
                        self.setCurrentIndex(idx)
                        event.accept()
                    else:
                        if self.__allowAppends:
                            # Appends row
                            self.model().insertRow(row_count, parent)
                            # First non hidden column
                            new_col = next((acol for acol in range(column_count)
                                if not self.isColumnHidden(acol)))
                            idx = self.model().index(current_row + 1, new_col,
                                parent)
                            self.setCurrentIndex(idx)
                            event.accept()
            elif key == Qt.Key_Delete:
                self.model().setData(idx, u'', Qt.EditRole)
                self.dataChanged(idx, idx)
                event.accept()
            elif key == Qt.Key_Down and current_row + 1 == row_count:
                if self.__allowAppends:
                    self.model().insertRow(row_count, parent)
                    idx = self.model().index(current_row + 1, 0, parent)
                    self.setCurrentIndex(idx)
                    event.accept()
        elif mod == Qt.ControlModifier:
            if key == Qt.Key_Insert:
                if self.__allowInserts:
                    idx = self.model().index(idx.row(), 0, parent)
                    self.model().insertRow(current_row, parent)
                    # Selections get funny after insert
                    selection = QtCore.QItemSelectionModel(self.model())
                    selection.select(idx, QtCore.QItemSelectionModel.Select)
                    self.setSelectionModel(selection)
                    self.setCurrentIndex(idx)
                    event.accept()
            elif key == Qt.Key_Delete:
                if self.__allowDeletes:
                    if self.__confirmDeletion:
                        if QtGui.QMessageBox.question(None,
                                'Borra fila', '¿Confirma?',
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                            event.accept()
                            return
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

    def getConfirmDeletion(self):
        return self.__confirmDeletion

    def setConfirmDeletion(self, value):
        self.__confirmDeletion = value

    def resetConfirmDeletion(self):
        self.__confirmDeletion = False

    confirmDeletion = pyqtProperty('bool', getConfirmDeletion,
        setConfirmDeletion)

    def _adjustColumnsToModel(self, header, model):
        for i in range(0, model.columnCount()):
            size = model.headerData(i, Qt.Horizontal, Qt.SizeHintRole)
            if size is not None:
                header.resizeSection(i, size.width())
            mode = model.headerData(i, Qt.Horizontal, QondaResizeRole)
            if mode is None:
                mode = header.Interactive
            header.setResizeMode(i, mode)

    def setItemDelegatesForColumns(self, *delegates):
        for column, delegate in enumerate(delegates):
            if delegate:
                self.setItemDelegateForColumn(column, delegate)

    def currentPyObject(self):
        return self.model().getPyObject(self.currentIndex())

    def selectedObjects(self):
        return [self.model().getPyObject(idx)
            for idx in self.selectionModel().selectedRows()]


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


class ListView(QtWidgets.QListView, EditableView):

    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        EditableView.__init__(self)
        QtWidgets.QListView.__init__(self, parent)

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(ListView, self).keyPressEvent(event)

    def currentChanged(self, current, previous):
        super(ListView, self).currentChanged(current, previous)
        row = current.row()
        if row != previous.row():
            self.currentRowChanged.emit(row)
