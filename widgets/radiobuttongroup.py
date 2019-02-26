
from .. import PYQT_VERSION

if PYQT_VERSION == 5:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
else:
    from PyQt4 import QtCore  # lint:ok
    from PyQt4 import QtGui  # lint:ok
    QtWidgets = QtGui  # lint:ok

import functools


PythonObjectRole = 32


class RadioButtonGroupDelegate(QtWidgets.QStyledItemDelegate):

    def setEditorData(self, editor, index):
        value = index.data(role=PythonObjectRole)
        try:
            editor.setValue(value)
            editor.valueChanged.connect(self.widgetValueChanged)
        except KeyError:
            raise ValueError(
                'Value "{0}" not present in {1} RadioButtonGroup values!'
                .format(value, editor.objectName()))

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, role=PythonObjectRole)

    @QtCore.pyqtSlot()
    def widgetValueChanged(self):
        self.commitData.emit(self.sender())


class RadioButtonGroup(QtWidgets.QWidget):

    _mappingDelegateClass = RadioButtonGroupDelegate

    valueChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(RadioButtonGroup, self).__init__(parent)
        self._value = None
        self._values = {}
        self._buttons = {}
        #layout = QtWidgets.QVBoxLayout(self)
        #self.setLayout(layout)

    def addButton(self, button, value):
        """
        Add an existing child button as an option button
        """
        self._values[button] = value
        self._buttons[value] = button
        button.clicked.connect(functools.partial(self._button_clicked,
            value=value))

    def addButtons(self, l):
        for button, value in l:
            self.addButton(button, value)

    def addOption(self, text, value):
        """
        Create a new option button
        """
        button = QtWidgets.QRadioButton(text, self)
        self.layout().addWidget(button)
        self.addButton(button, value)

    def addOptions(self, options):
        for text, value in options:
            self.addOption(text, value)

    def _button_clicked(self, value=None):
        self._value = value
        self.valueChanged.emit()

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self._buttons[value].setChecked(True)
        self.valueChanged.emit()
