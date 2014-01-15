
# Required to enable PyQt do automatic type conversion
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QDateTime', 2)
#sip.setapi('QDate', 2)
#sip.setapi('QTime', 2)
#sip.setapi('QVariant', 2)

from PyQt4.QtGui import QWidget, QApplication
from PyQt4.QtCore import Qt
from qonda.mvc.observable import ObservableObject, ObservableListProxy
from qonda.mvc.adapters import ObjectAdapter, ObjectListAdapter
from qonda.mvc.datawidgetmapper import DataWidgetMapper
from qonda.util.aggregator import Aggregator
from qonda.mvc.delegates import SpinBoxDelegate


class GroceryItem(ObservableObject):

    _qonda_column_meta_ = {
        'description': {
            'width': 50
            },
        'price': {
            'alignment': Qt.AlignRight
            }
        }

    def __init__(self, description=None, amount=0):
        ObservableObject.__init__(self)
        self.description = description
        self.amount = amount


class Summary(ObservableObject):

    def __init__(self):
        ObservableObject.__init__(self)
        self.count = 0
        self.total = 0


class GroceryListWindow(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        from aggregator_ui import Ui_Form
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.groceries.setItemDelegateForColumn(1, SpinBoxDelegate())

        grocery_list = ObservableListProxy([
            GroceryItem("Apples", 12),
            GroceryItem("Peaches", 18)
        ])

        summary = Summary()

        self.aggregator = Aggregator(
            grocery_list,
            summary,
            {
                '*': 'count',
                'amount': 'total'
            })

        groceries_adapter = ObjectListAdapter(
            ('description', 'amount'),
            grocery_list,
            GroceryItem)

        self.ui.groceries.setModel(groceries_adapter)
        self.ui.groceries.resizeColumnsToContents()

        summary_adapter = ObjectAdapter(
            ('count', 'total'),
            summary)

        self.mapper = DataWidgetMapper()
        self.mapper.addMappings(self.ui.count, self.ui.total)
        self.mapper.setModel(summary_adapter)


app = QApplication([])
form = GroceryListWindow()
form.show()
app.exec_()