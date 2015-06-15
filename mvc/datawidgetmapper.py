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
    from PyQt5.QtCore import Qt
else:
    from PyQt4 import QtGui  # lint:ok
    from PyQt4.QtCore import Qt  # lint:ok
    QtWidgets = QtGui

import delegates
from .. import widgets


class ItemDelegate(QtWidgets.QItemDelegate):

    def setEditorData(self, editor, index):

        palette = editor.palette()

        # Quick workaround for unsupported flavor of setColor
        # on older PyQt versions
        try:
            fgcolor = index.data(Qt.ForegroundRole)
            if not fgcolor:
                fgcolor = QtWidgets.QApplication.palette().color(QtGui.QPalette.Text)
            # Edits and such
            palette.setColor(QtGui.QPalette.Text, fgcolor)
            # Labels, Group boxes and such
            palette.setColor(QtGui.QPalette.WindowText, fgcolor)

            bgcolor = index.data(Qt.BackgroundRole)
            if not bgcolor:
                bgcolor = QtWidgets.QApplication.palette().color(QtGui.QPalette.Base)
            palette.setColor(QtGui.QPalette.Base, bgcolor)

            if fgcolor or bgcolor:
                editor.setPalette(palette)

            font = index.data(Qt.FontRole)
            editor.setFont(font if font else QtGui.QFont())

            icon = index.data(Qt.DecorationRole)
            try:
                editor.setIcon(icon)
            except (AttributeError, TypeError):
                pass
        except TypeError:
            pass

        delegate = self.parent()._delegates.get(editor)
        if delegate:
            delegate.setEditorData(editor, index)
        else:
            #super(ItemDelegate, self).setEditorData(editor, index)
            v = index.data(Qt.EditRole)
            try:
                n = editor._mappingPropertyName
            except:
                n = editor.metaObject().userProperty().name()
            editor.setProperty(n, v)

    def setModelData(self, editor, model, index):
        delegate = self.parent()._delegates.get(editor)
        if delegate:
            delegate.setModelData(editor, model, index)
        else:
            try:
                if editor._mappingReadOnly:
                    return
            except:
                pass
            #super(ItemDelegate, self).setModelData(editor, model, index)
            try:
                n = editor._mappingPropertyName
            except:
                n = editor.metaObject().userProperty().name()
            v = editor.property(n)
            model.setData(index, v, Qt.EditRole)
            # Set the editor again, with new, possibly formatted, model value.
            self.setEditorData(editor, index)

    def dataCommited(self, sender):
        self.commitData.emit(sender)

class DataWidgetMapper(QtWidgets.QDataWidgetMapper):
    """
        An enhanced descendant of QDataWidgetMapper:
        * Uses the appropiate widget property if registered in the
          _mappingPropertyName attribute of the widget class.
          Required for QLabel as its text property isn't declared
          as the "User" property
        * Uses an appropiate, alternative delegate if registered in
          the _mappingDelegateClass attribute of the widget class,
          or via the delegate attribute in the addMapping method
        * Uses an enhanced ItemDelegate delegate, in order to set
          widget colors and fonts along the value
        * Adds an addMappings method for quick setting of mappings
        * Widgets can be mapped with no model assigned, and mappings
        * persists after a call to setModel()
          setModel() imply toFirst()
    """
    def __init__(self, parent=None):
        QtWidgets.QDataWidgetMapper.__init__(self, parent)
        self._delegates = {}
        self._delegate = ItemDelegate(self)
        self._mappings = {}
        self.setItemDelegate(self._delegate)

    def _addMapping(self, widget, section, delegate=None):
        # Don't use
        super(DataWidgetMapper, self).addMapping(widget, section)
        if not delegate:
            try:
                delegate = widget._mappingDelegateClass()
                delegate.commitData.connect(self._delegate.dataCommited)
            except AttributeError:
                pass
        self._delegates[widget] = delegate

    def addMapping(self, widget, section, delegate=None):
        self._mappings[widget] = (section, delegate)
        if self.model():
            self._addMapping(widget, section, delegate)

    def addMappings(self, *widgets):
        for section, widget in enumerate(widgets):
            self.addMapping(widget, section)

    def mapFromPropertyList(self, ui, properties):
        """
        Map widgets that match the adapter properties
        """
        self.addMappings(*[getattr(ui, prop.replace('.', '_'))
            for prop in properties])

    def setModel(self, model):
        super(DataWidgetMapper, self).setModel(model)
        for widget, (section, delegate) in self._mappings.iteritems():
            self._addMapping(widget, section, delegate)
        self.toFirst()

    def currentPyObject(self):
        index = self.model().index(self.currentIndex(), 0)
        return self.model().getPyObject(index)


QtWidgets.QComboBox._mappingDelegateClass = delegates.ComboBoxDelegate
QtWidgets.QLabel._mappingPropertyName = "text"
QtWidgets.QLabel._mappingReadOnly = True
QtWidgets.QPushButton._mappingPropertyName = "text"
QtWidgets.QPushButton._mappingReadOnly = True
QtWidgets.QCheckBox._mappingDelegateClass = delegates.CheckBoxDelegate
QtWidgets.QDateEdit._mappingDelegateClass = delegates.DateEditDelegate
widgets.NumberEdit._mappingDelegateClass = delegates.NumberEditDelegate
widgets.SpinBox._mappingDelegateClass = delegates.SpinBoxDelegate
widgets.DecimalSpinBox._mappingDelegateClass = delegates.DecimalSpinBoxDelegate