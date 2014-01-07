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

import datetime
from decimal import Decimal
import locale
from .. import PYQT_VERSION
if PYQT_VERSION == 5:
    from PyQt5 import QtGui
    from PyQt5.QtCore import Qt, QEvent, pyqtProperty
else:
    from PyQt4 import QtGui  # lint:ok
    from PyQt4.QtCore import Qt, QEvent, pyqtProperty  # lint:ok
    QtWidgets = QtGui


class DateEdit(QtWidgets.QDateEdit):

    def __init__(self, parent=None):
        super(DateEdit, self).__init__(parent)
        self.setMinimumDate(datetime.date(1752, 9, 14))
        self.setSpecialValueText(u'\xa0')  # Qt ignores '' and regular space
        self.__allowEmpty = True

    def clear(self):
        if self.__allowEmpty:
            self.setDate(self.minimumDate())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.clear()
            event.accept()
            return
        elif self.__allowEmpty and self.date() == self.minimumDate():
            # Make input possible when the edit is empty
            self.setDate(datetime.date.today())
            self.setSelectedSection(self.sectionAt(0))
        super(DateEdit, self).keyPressEvent(event)

    def getAllowEmpty(self):
        return self.__allowEmpty

    def setAllowEmpty(self, value):
        self.__allowEmpty = value

    def resetAllowEmpty(self):
        self.__allowEmpty = True

    allowEmpty = pyqtProperty('bool', getAllowEmpty, setAllowEmpty)


class DateTimeEdit(QtWidgets.QDateTimeEdit):

    def __init__(self, parent=None):
        super(DateTimeEdit, self).__init__(parent)
        self.setMinimumDate(datetime.date(1752, 9, 14))
        self.setSpecialValueText(u'\xa0')  # Qt ignores '' and regular space
        self.__allowEmpty = True

    def clear(self):
        if self.__allowEmpty:
            self.setDate(self.minimumDate())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.clear()
            event.accept()
            return
        elif self.__allowEmpty and self.date() == self.minimumDate():
            # Make input possible when the edit is empty
            self.setDateTime(datetime.datetime.now())
            self.setSelectedSection(self.sectionAt(0))
        super(DateTimeEdit, self).keyPressEvent(event)

    def getAllowEmpty(self):
        return self.__allowEmpty

    def setAllowEmpty(self, value):
        self.__allowEmpty = value

    def resetAllowEmpty(self):
        self.__allowEmpty = True

    allowEmpty = pyqtProperty('bool', getAllowEmpty, setAllowEmpty)


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)
        self.__allowEmpty = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.__allowEmpty:
            self.setCurrentIndex(-1)
            event.accept()
            return
        super(ComboBox, self).keyPressEvent(event)

    def getAllowEmpty(self):
        return self.__allowEmpty

    def setAllowEmpty(self, value):
        self.__allowEmpty = value

    def resetAllowEmpty(self):
        self.__allowEmpty = True

    allowEmpty = pyqtProperty('bool', getAllowEmpty, setAllowEmpty)


class MaskedLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args):
        super(MaskedLineEdit, self).__init__(*args)

    def text(self):
        text = super(MaskedLineEdit, self).text()
        mask = self.inputMask()

        def unmaskgen(s):
            i = 0
            for c in s:
                try:
                    if mask[i] in 'AaNnXx90Dd#HhBb><!':
                        yield c
                except IndexError:
                    yield c
                i += 1

        return ''.join([x for x in unmaskgen(text)])


class NumberEdit(QtWidgets.QLineEdit):

    returnFloat = 1
    returnDecimal = 2

    def __init__(self, parent=None):
        super(NumberEdit, self).__init__(parent)
        self.setAlignment(Qt.AlignRight)
        self._decimal_point = locale.localeconv()['decimal_point']
        self._decimals = 0
        self._return_format = NumberEdit.returnFloat

    def getDecimals(self):
        return self._decimals

    def setDecimals(self, decimals):
        if decimals != self._decimals:
            self._decimals = decimals
            # Reformat
            self.setValue(self.getValue())

    decimals = pyqtProperty('int', getDecimals, setDecimals)

    def getReturnFormat(self):
        return self._return_format

    def setReturnFormat(self, value):
        self._return_format = value

    returnFormat = pyqtProperty('int', getReturnFormat, setReturnFormat)

    def _addMask(self, s):
        try:
            n = locale.atof(s)
        except ValueError:  # Invalid, value is None
            print "NumberEdit: basura!"
            self.clear()
            return
        return locale.format('%.*f', (self._decimals, n), grouping=True)

    def _removeMask(self, s):
        return ''.join([c for c in s if c != '.'])

    def getValue(self):
        s = self.text()
        if not self.hasFocus():
            s = self._removeMask(s)
        try:
            v = locale.atof(s) if self._decimals > 0 else int(s)
            return (Decimal(v)
                if self._return_format == NumberEdit.returnDecimal else v)
        except ValueError:
            return None

    def setValue(self, value):
        if self.hasFocus():
            self.setText(str(value))
        else:
            if value is None:
                self.clear()
            else:
                self.setText(locale.format('%.*f', (self._decimals,
                    float(value)), grouping=True))

    value = pyqtProperty('float', getValue, setValue)

    def focusInEvent(self, event):
        self.setText(self._removeMask(self.text()))
        super(NumberEdit, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.setText(self._addMask(self.text()))
        super(NumberEdit, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if (self._decimal_point == ',' and event.key() == Qt.Key_Period
                and event.modifiers() == Qt.KeypadModifier):
            event = QtGui.QKeyEvent(QEvent.KeyPress, Qt.Key_Comma,
                event.modifiers(), ',')
        before = self.text()
        super(NumberEdit, self).keyPressEvent(event)
        after = self.text()
        if after == '':
            return
        try:
            if self._decimals == 0:
                n = int(after)
            else:
                n = locale.atof(after)
        except ValueError:
            self.setText(before)
