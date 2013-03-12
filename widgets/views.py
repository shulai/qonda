# -*- coding: utf-8 *-*

from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class EditableView(object):

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
            elif key == Qt.Key_Down and current_row + 1 == row_count:
                self.model().insertRow(row_count, parent)
        elif mod == Qt.ControlModifier:
            if key == Qt.Key_Insert:
                self.model().insertRow(current_row, parent)
                self.setCurrentIndex(idx)
            elif key == Qt.Key_Delete:
                if current_row + 1 == row_count:
                    self.setCurrentIndex(self.model().index(current_row - 1,
                        idx.column(), parent))
                self.model().removeRow(current_row, parent)


class TableView(QtGui.QTableView, EditableView):

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(TableView, self).keyPressEvent(event)


class TreeView(QtGui.QTreeView, EditableView):

    def keyPressEvent(self, event):
        self._keyPressEvent(event)
        super(TreeView, self).keyPressEvent(event)

    def resizeColumnsToContents(self):
        for i in range(0, self.model().columnCount(self.rootIndex())):
            self.resizeColumnToContents(i)
