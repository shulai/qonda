
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
