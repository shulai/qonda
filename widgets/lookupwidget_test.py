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

import sys
import sip
sip.setapi('QString', 2)
from PyQt4 import QtGui

from lookupwidget import LookupWidget


class TestFrame(QtGui.QFrame):

    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.lookupwidget = LookupWidget(self)
        self.button1 = QtGui.QPushButton('Set')
        self.button2 = QtGui.QPushButton('Query')
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.lookupwidget)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.setLayout(layout)
        self.button1.clicked.connect(self.lookup_set)
        self.button2.clicked.connect(self.lookup_query)

    def lookup_set(self):
        self.lookupwidget.setValue('BOSSERT HECTOR CARLOS')

    def lookup_query(self):
        print self.lookupwidget.value()


def search_value(search_string):
    if search_string == '426':
        return  ['AVILA, DIEGO']
    elif search_string == '1675':
        return ['GAZQUEZ, JULIO']
    elif search_string[0] == 'A':
        return ['AVILA, DIEGO', 'AVILA, EDUARDO']
    else:
        return []

app = QtGui.QApplication(sys.argv)

frame = TestFrame()
frame.lookupwidget.search_function = search_value
frame.show()


#app.setMainWidget(editor);
app.exec_()
