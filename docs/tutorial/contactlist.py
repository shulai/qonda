
# Required to enable PyQt do automatic type conversion
import sip
sip.setapi('QString', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QDate', 2)
sip.setapi('QTime', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtGui import QWidget, QApplication
from qonda.mvc.adapters import ObjectListAdapter


class Contact(object):

    def __init__(self, name=None, phone=None):
        self.name = name
        self.phone = phone

    
class ContactList(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        from contactlist_ui import Ui_Form
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.model = [
            Contact("Bert", 554), 
            Contact("Ernie", 555)
        ]

        adapter = ObjectListAdapter(
            ('name', 'phone'), 
            self.model)

        self.ui.contacts.setModel(adapter)


app = QApplication([])
form = ContactList()
form.show()
app.exec_()