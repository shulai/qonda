# -*- coding: utf-8 *-*

from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class EditableView(object):

    def keyPressEvent(self, event):
        # TODO: Implement
        key = event.key()
        mod = event.modifiers()
        current_row = self.currentIndex().row()
        root = self.rootIndex()
        row_count = self.model.rowCount(root)
        if (mod == Qt.NoModifier and key == Qt.Key_Down and
            current_row + 1 == row_count):
            self.model().insertRow(row_count, root)
        elif mod == Qt.ControlModifier:
            if key == Qt.Key_Insert:
                self.model().insertRow(current_row, root)
            elif key == Qt.Key_Delete:
                self.removeRow(current_row, root)
        super(TableView, self).keyPressEvent(event)


class TableView(QtGui.QTableView, EditableView):

    pass


class TreeView(QtGui.QTreeView, EditableView):

    pass
