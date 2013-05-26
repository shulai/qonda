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

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, pyqtProperty


class DateEdit(QtGui.QDateEdit):

    def __init__(self, parent=None):
        super(QtGui.QDateEdit, self).__init__(parent)
        self.setMinimumDate(datetime.date(1752, 9, 14))
        self.setSpecialValueText(u'\xa0')  # Qt ignores '' and regular space
        self.__allowEmpty = True

    def clear(self):
        if self.__allowEmpty:
            self.setDate(self.minimumDate())

    def keyPressEvent(self, event):
        print "keyPressEvent"
        if event.key() == Qt.Key_Delete:
            self.clear()
            event.accept()
            return
        super(DateEdit, self).keyPressEvent(event)

    def getAllowEmpty(self):
        return self.__allowEmpty

    def setAllowEmpty(self, value):
        self.__allowEmpty = value

    def resetAllowEmpty(self):
        self.__allowEmpty = True

    allowEmpty = pyqtProperty('bool', getAllowEmpty, setAllowEmpty)


class DateTimeEdit(QtGui.QDateTimeEdit):

    def __init__(self, parent=None):
        super(QtGui.QDateTimeEdit, self).__init__(parent)
        self.setMinimumDate(datetime.date(1752, 9, 14))
        self.setSpecialValueText(u'\xa0')  # Qt ignores '' and regular space
        self.__allowEmpty = True

    def clear(self):
        if self.__allowEmpty:
            self.setDate(self.minimumDate())

    def keyPressEvent(self, event):
        print "keyPressEvent"
        if event.key() == Qt.Key_Delete:
            self.clear()
            event.accept()
            return
        super(DateEdit, self).keyPressEvent(event)

    def getAllowEmpty(self):
        return self.__allowEmpty

    def setAllowEmpty(self, value):
        self.__allowEmpty = value

    def resetAllowEmpty(self):
        self.__allowEmpty = True

    allowEmpty = pyqtProperty('bool', getAllowEmpty, setAllowEmpty)


class ComboBox(QtGui.QComboBox):

    def __init__(self, parent=None):
        super(QtGui.QComboBox, self).__init__(parent)
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
