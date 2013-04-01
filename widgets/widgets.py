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
from PyQt4.QtCore import Qt


class DateEdit(QtGui.QDateEdit):

    def keyPressEvent(self, event):
        print "keyPressEvent"
        if True:  # self.currentSection == QtGui.QDateTimeEdit.NoSection:

            if event.key() == Qt.Key_Delete:
                self.setDate(datetime.date(1752, 9, 14))
                event.accept()
                return
        super(DateEdit, self).keyPressEvent(event)


class DateTimeEdit(QtGui.QDateTimeEdit):

    def keyPressEvent(self, event):
        print "keyPressEvent"
        if True:  # self.currentSection == QtGui.QDateTimeEdit.NoSection:
            if event.key() == Qt.Key_Delete:
                self.clear()
        super(DateTimeEdit, self).keyPressEvent(event)
