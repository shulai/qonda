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
