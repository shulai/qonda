# -*- coding: utf-8 -*-
"""
Second tutorial
"""

import sys

# Required to set up PyQt
import sip
sip.setapi('QString', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QDate', 2)
sip.setapi('QTime', 2)
sip.setapi('QVariant', 2)

import pickle
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from qonda.mvc.observable import ObservableObject
from qonda.mvc.adapters import (ObjectAdapter, ObjectListAdapter,
    ValueListAdapter)
from qonda.mvc.datawidgetmapper import DataWidgetMapper
from qonda.mvc import delegates

# Please note that all these are strings for the sake of simplicity
# You could use entity objects as well, and happily associated to
# the main object, and managing them thru the combo and lookup boxes
# The only requisite is having a unicode representation
phone_types = (u'Work', u'Home', u'Mobile')

contact_categories = (u'Family', u'Business', u'Other')

cities = (
    u'Barcelona',
    u'Berlin',
    u'Bordeaux',
    u'Buenos Aires',
    u'Madrid',
    u'Manchester',
    u'Liverpool',
    u'London',
    u'Lyon',
    u'New York',
    u'Paris',
    u'Zurich'
    )


def lookup_city(s):
    result = []
    s = s.lower()
    for city in cities:
        if city[:len(s)].lower() == s:
            result.append(city)
    return result


class Phone(object):

    def __init__(self, number=u'', type_=u'Work'):
        self.number = number
        self.type_ = type_

    def __unicode__(self):
        return u'{0} ({1})'.format(self.number, self.type_)


class Phones(list):

    def __unicode__(self):
        return u', '.join((unicode(ph) for ph in self))


class Contact(ObservableObject):

    _notifiables = ('name', 'address', 'city', 'category', 'loaned')

    def __init__(self):
        ObservableObject.__init__(self)
        self.name = u''
        self.address = u''
        self.city = None
        self.phones = Phones()
        self.category = u'Business'
        self.loaned = 0.0

    def __str__(self):
        return "Contact " + self.name.encode()


class ContactView(QtGui.QFrame):

    def __init__(self):
        from contacts_ui import Ui_Frame
        QtGui.QFrame.__init__(self)
        self.ui = Ui_Frame()
        self.ui.setupUi(self)

        self.category_adapter = ValueListAdapter(contact_categories)
        self.ui.category.setModel(self.category_adapter)

        self.phone_types_adapter = ValueListAdapter(phone_types)
        self.ui.phones.setItemDelegateForColumn(1,
            delegates.ComboBoxDelegate(self, self.phone_types_adapter))
        self.ui.city.search_function = lookup_city

        self.mapper = DataWidgetMapper()
        self.mapper.addMappings(
            self.ui.name,
            self.ui.address,
            self.ui.city,
            self.ui.category,
            self.ui.loaned)

    def setModel(self, model):
        # Set up model adapter and widget mapper
        self.model = model
        self.list_adapter = ObjectListAdapter(
            ('name', 'phones', 'loaned'),
            self.model, Contact,
            column_meta=[
                {'title': u'Nombre'},
                {
                    'width': 10,
		    'flags': {Qt.ItemIsSelectable: True, Qt.ItemIsEnabled: True} 
                },
                {
                    'displayFormatter': lambda(v): u'{0:.2f}'.format(v),
                    'editFormatter': lambda(v): u'{0:.2f}'.format(v),
                    'parser': lambda(v): float(v),
                    'font': lambda(o): None if o.loaned < 100
                        else QtGui.QFont('Arial', weight=QtGui.QFont.Bold),
                    'foreground': lambda(o): None if o.loaned < 100
                        else QtGui.QColor(255, 0, 0),
                    'background': lambda(o): None if o.loaned < 50
                        else QtGui.QColor(255, 255, 0)
                }])
        self.ui.tableView.setModel(self.list_adapter)
        self.ui.tableView.resizeColumnsToContents()
        self.setEditorModel(model[0])

    def setEditorModel(self, model):
        self.edit_adapter = ObjectAdapter(('name', 'address', 'city',
            'category', 'loaned'), model,
            column_meta=[
                {},
                {},
                {},
                {},
                {
                    'editFormatter': lambda(v): u'{0:.2f}'.format(v),
                    'parser': lambda(v): float(v),
                    'font': lambda(o): None if o.loaned < 100
                        else QtGui.QFont('Arial', weight=QtGui.QFont.Bold),
                    'foreground': lambda(o): None if o.loaned < 100
                        else QtGui.QColor(255, 0, 0),
                    'background': lambda(o): None if o.loaned < 50
                        else QtGui.QColor(255, 255, 0)

                }
            ])
        self.mapper.setModel(self.edit_adapter)

        self.phones_adapter = ObjectListAdapter(('number', 'type_'),
            model.phones, Phone, 
            column_meta=[
                {},
                {'title': u'Type',
                    'size': 10}
            ])
        self.ui.phones.setModel(self.phones_adapter)

    def on_tableView_clicked(self):
        # Debería implementar un método en los adapter para obtener
        # el item a partir del indice
        model = self.ui.tableView.currentIndex().internalPointer()
        self.setEditorModel(model)

    def on_clear_clicked(self):
        model = self.ui.tableView.currentIndex().internalPointer()
        model.loaned = 0


class ContactsApp(QtGui.QApplication):

    def exec_(self):

        # Set up model
        try:
            self.model = pickle.load(file('contacts.pickle', 'r'))
        except IOError:
            print "Can't unpickle, creating sample contact list"
            self.model = []
            contact = Contact()
            contact.name = u'Sherlock Holmes'
            contact.address = u'221B Baker St'
            contact.city = u'London'
            contact.phones = Phones([Phone('555-5678'), Phone('512-2281')])
            contact.category = u'Business'
            self.model.append(contact)
            contact = Contact()
            contact.name = u'Phileas Fogg'
            contact.address = u'7 Savile Row, Burlington Gardens'
            contact.phones = Phones([Phone('555-0123')])
            contact.category = u'Other'
            self.model.append(contact)

        # Set up view
        self.mainWindow = ContactView()
        self.mainWindow.setModel(self.model)
        self.mainWindow.show()

        QtGui.QApplication.exec_()

        #try:
            #pickle.dump(self.model, file('contacts.pickle', 'w'))
        #except IOError:
            #print "Error pickling the contact"

app = None


def main():

    app = ContactsApp(sys.argv)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
