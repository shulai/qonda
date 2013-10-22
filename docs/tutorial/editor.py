from PyQt4.QtGui import QWidget, QApplication
from qonda.mvc.adapters import ObjectAdapter
from qonda.mvc.datawidgetmapper import DataWidgetMapper


class Contact(object):

    def __init__(self, name=None, phone=None):
        self.name = name
        self.phone = phone


class ContactEditor(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        from editor_ui import Ui_Form
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.model = Contact()

        adapter = ObjectAdapter(
            ('name', 'phone'), 
            self.model)

        mapper = DataWidgetMapper()
        mapper.addMappings(
            self.ui.name,
            self.ui.phone)

        mapper.setModel(adapter)

        
app = QApplication([])
form = ContactEditor()
form.show()
app.exec_()