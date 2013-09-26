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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

PythonObjectRole = 32


class LookupWidgetDelegate(QtGui.QItemDelegate):

    def __init__(self, parent=None, search_function=None, search_window=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.search_function = search_function
        self.search_window = search_window

    def createEditor(self, parent, option, index):
        editor = LookupWidget(parent)
        editor.search_function = self.search_function
        editor.search_window = self.search_window
        return editor

    def setSearchWindow(self, window):
        self.search_window = window

    def setEditorData(self, editor, index):
        editor.setValue(index.data(role=PythonObjectRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), role=PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, options, index):
        try:
            model = index.model().data(index, Qt.EditRole)
            value = unicode(model)
        except AttributeError:
            value = ''

        painter.save()
        self.drawBackground(painter, options, index)
        # if not options edicion
        self.drawDisplay(painter, options, options.rect, value)
        painter.restore()


class LookupWidget(QtGui.QFrame):

    _mappingDelegateClass = LookupWidgetDelegate

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameStyle(QtGui.QFrame.Sunken)
        self.label = QtGui.QLabel('The label', self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.label.setFocusPolicy(Qt.StrongFocus)

        self.editor_widget = QtGui.QWidget(self)
        self.editor_widget.setFocusPolicy(Qt.NoFocus)
        self.editor = QtGui.QLineEdit(self.editor_widget)

        self.button = QtGui.QToolButton(self.editor_widget)
        # Should be able to get focus when the QLineEdit is empty
        # but then when value is set it is grabbing focus when it shouldn't
        self.button.setFocusPolicy(Qt.NoFocus)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/actions/icons/lookup.svg"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button.setIcon(icon1)
        self.button.clicked.connect(self.openSearchWindow)

        self.editor.editingFinished.connect(self._search_value)

        def focusInEvent(event):
            self.setFrameShape(QtGui.QFrame.Panel)

        def focusOutEvent(event):
            self._search_value()
            self.setFrameShape(QtGui.QFrame.NoFrame)

        self.label.focusInEvent = focusInEvent
        self.editor.focusOutEvent = focusOutEvent

        hlayout = QtGui.QHBoxLayout(self.editor_widget)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(self.editor)
        hlayout.addWidget(self.button)
        self.editor_widget.setLayout(hlayout)

        self.layout = QtGui.QStackedLayout()
        self.layout.addWidget(self.label)

        self.layout.addWidget(self.editor_widget)
        self.setLayout(self.layout)

        self.menu = QtGui.QMenu(self)
        self.placeholder = None
        self._value = None
        self._show_value()

        self.search_function = None
        self.search_window = None
        self.search_flag = False

    def focusInEvent(self, event):
        self.label.setFocus()

    def _show_value(self):
        if self._value:
            self.label.setText(unicode(self._value))
        else:
            if self.placeholder:
                self.label.setText(self.placeholder)
            else:
                self.label.setText('')

    def mousePressEvent(self, event):
        self.layout.setCurrentWidget(self.editor_widget)
        self.editor.setText('')

    def keyPressEvent(self, event):
        #if self.search_flag:
        #    self.search_flag = False
        #    return
        if event.key() == Qt.Key_Escape:  # no anda!
            self.layout.setCurrentWidget(self.label)
            self.label.setFocus()
            return
        if event.text() == '':  # Avoid dead keys events erasing the text
            event.ignore()
            return
        self.layout.setCurrentWidget(self.editor_widget)
        self.editor.setText(event.text().strip())
        self.editor.setFocus()

    def value(self):
        return self._value

    def setValue(self, value):
        self.search_flag = True
        self._value = value
        self._show_value()
        self.layout.setCurrentWidget(self.label)

    def buttonVisible(self, v):
        self.button.setVisible(v)

    def _search_value(self):
        text = self.editor.text()
        if text == '':
            self.setValue(None)
            return

        values = self.search_function(self.editor.text())
        if len(values) == 0:
            self.editor.setFocus()
            return  # Nothing found, back to editing
        elif len(values) == 1:
            self.setValue(values[0])
        else:
            actions = {}
            self.menu.clear()
            for i, value in enumerate(values):
                action = self.menu.addAction(unicode(value))
                actions[action] = i
                if i == 0:
                    self.menu.setActiveAction(action)
            action = self.menu.exec_(self.mapToGlobal(QtCore.QPoint(0,
                self.size().height())))
            if action:
                self.setValue(values[actions[action]])
            else:
                self.editor.setFocus()
            return  # Nothing found, back to editing

    @QtCore.pyqtSignature("")
    def openSearchWindow(self):
        if self.search_window:
            self.search_window.setWindowModality(Qt.WindowModal)
            self.search_window.show()
            value = self.search_window.value()
            if value:
                self.setValue(value)
            else:
                self.editor.setFocus()  # Nothing found, back to editing
