==============
Qonda tutorial
==============

Intro
=====

Qt includes since version 4 support for a model/view architecture,
dubbed the Interview framework, and PyQt exposes said functionality.
Yet, using it directly could be burdensome, specially in applications
whose data models involve a large number of entity classes, as such
classes should either inherit from the ``QAbstractItemModel`` class and
reimplement its abstract methods, or build adapters that
wraps the model into ``QAbstractItemModel``-derived objects.

Qonda relieves this works providing generic adapter classes for
Python models, along a number of enhancements over the Qt classes
in order to make use of Interview easier in Python, yet preserving
most of its raw power.

Requisites
==========

A basic knowledge of Python and PyQt programming are required to follow
this tutorial. If you are able to build a widget based UI with PyQt and
make it work you are ready to go!

Interview overview
==================

All models in Interview inherits from ``QAbstractItemModel``, with a 
structure of a tree of nested tables, adequate to represent tables,
trees and lists.

Items in the model are usually referenced using ``QModelIndex`` objects.
Indexes have the row and column of the item in its containing table, 
and the index of the parent item of that table, with an "invalid index" 
used to represent the parent of the top level table.

While most of the time you do a light use of this concepts while using
Qonda, sometimes you have to deal with them.

Models are then used in views. Views in traditional Qt are either widgets 
like tables (``QTableView``) and trees (``QTreeView``), or sets of widgets like 
edits and combos that become part of a view using a ``QDataWidgetMapper`` 
object.

First steps
===========

Let's start with a simple model for a contact list::

    class Contact(object):

        def __init__(self, name=None, phone=None):
            self.name = name
            self.phone = phone


Then, we can build a form to show and edit contacts::

    from PyQt4.QtGui import QWidget
    from qonda.mvc.adapters import ObjectAdapter
    from qonda.mvc.datawidgetmapper import DataWidgetMapper

    
    class ContactEditor(QWidget):

        def __init__(self):
            super(QWidget, self).__init__()
            from editor_ui import Ui_Form
            self.ui = Ui_Form()
            self.ui.setupUi(self)

            self.model = Contact("Bert", 554)

            adapter = ObjectAdapter(
                ('name', 'phone'), 
                self.model)

            mapper = DataWidgetMapper()
            mapper.addMappings(
                self.ui.name,
                self.ui.phone)

            mapper.setModel(adapter)


In this example, after the standard PyQt boilerplate, a new contact 
model is created in the editor window, and the attribute values should be 
properly shown in the editor fields.

Also, an ``ObjectAdapter`` is created. ``ObjectAdapter`` is part of the core 
Qonda functionality, presenting the attributes of a Python object a Qt 
Interview model suitable to be used in a Qt view::

    adapter = ObjectAdapter(
        ('name', 'phone'), 
        model)

The first argument is the list of attributes that will be presented as part
of the Interview Model. The second argument is the model itself. Additional
arguments will be used in further chapters of this tutorial, and also could
be found in the reference.

In order to build a view from independend widgets, Qt provides the 
``QDataWidgetMapper`` class. ``QDataWidgetMapper`` has the ``addMapping()`` 
method, that maps a widget to a column of the Interview model. 
Qonda has an improved version, ``qonda.mvc.datawidgetmapper.DataWidgetMapper``.
The example uses ``DataWidgetMapper`` and its ``addMappings()`` method, 
less verbose than using regular ``QDataWidgetMapper``'s
``addMapping()`` method.

Finally, ``mapper.setModel()`` connects the model to the view.

Changes made in the fields propagate automatically to the model. 
The inverse, changes in the model propagating to the view also can be achieved,
but are described later in this tutorial.

List of entities and tables
===========================

Working with a list of entities and a ``QTableView`` is somewhat easier.

The example code for this case is::

    from PyQt4.QtGui import QWidget
    from qonda.mvc.adapters import ObjectListAdapter

    
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


The adapter in this case is an ``ObjectListAdapter``, that adapts a list of
entities of the same class::

    adapter = ObjectListAdapter(
        ('name', 'phone'), 
        self.model)

Of course, you also could use ``ObjectListAdapter`` with ``DataWidgetMapper``,
showing an entity at once (check ``QDataWidgetMapper`` documentation for 
details), or ``ObjectAdapter`` with a ``QTableView``, although silly as 
``ObjectAdapter`` is a one row model.

Observable models
=================

Both examples have a limitation: As soon as you modify your Python model,
you'll find your view won't get updated. In order to have model changes
automatically updated, you either need to make your model observable,
or use proxy objects.

To make your model observable, you need to make your class inherit from
``Observable``. You usually will use ``ObservableObject``, that emits update
events when you set your object attributes::
    
    from qonda.mvc.observable import ObservableObject
    

    class Contact(ObservableObject):

    def __init__(self, name=None, phone=None):
        ObservableObject.__init__(self)
        self.name = name
        self.phone = phone

        
By default, update events occurs when any public attribute (not starting 
with underscore) is set. If you want to restrict events to a subset of 
attributes, use the ``_notifiables_`` class attribute:

    class Contact(ObservableObject):

    _notifiables_ = ('name', 'phone')
    
    def __init__(self, name=None, phone=None):
        ObservableObject.__init__(self)
        self.name = name
        self.phone = phone

If you need to use ObservableObject along with other parent class, please
note that ``__init__()`` in Observable objects don't call ``super()``, hence you 
will need to write your own ``__init__()`` method and call either ``__init__()`` 
individually there.

Adapters observe observable objects automatically, no further action is
required.

Observable proxies
------------------

As an alternative, if you don't want to have your model coupled with Qonda,
you can use ``ObservableProxy``::
    
    from qonda.mvc.observable import ObservableProxy
    
    ...
    self.model = ObservableProxy(model)
    self.mapper.setModel(self.model)

    
Of course, the catch is that any further changes to the model should be done 
through the proxy in order to get the views updated. Eventually you could wrap
any methods of the model update the attributes in order to emit the update 
events after the change.

Observable lists
----------------

Observable lists are always implemented as proxies, but the target argument 
is optional. If you don't provide a target, a new empty list is used::
    
    from qonda.mvc.observable import ObservableListProxy
    
    ...
    self.model = ObservableListProxy(contacts)
    self.mapper.setModel(self.model)

Observable lists track list operations like insertions or removals, but they
don't observe changes on its items, to do so those must be observable (and 
observed) as well. 

    
Qonda and metadata
==================

There are several customizations in the handling of the model available, 
those are done using model metadata. Most metadata properties are related
to Qt Interview roles.

You can set metadata:
    
* In the model class
* In the adapter

Class level Metadata
--------------------
    
You can add metadata to your model classes, using the ``_qonda_column_meta_`` 
class. Those are dicts, with keys being the name of the attributes the 
metadata is being defined, and values are either dicts of attribute specific 
metadata, or the class of the attribute values. In that case, the key '.' in
the attribute class metadata is used for such attribute::
        
    class Contact(ObservableObject):

    _qonda_column_meta_ = {
        'name': {
            'width': 30
            }
        }

    def __init__(self, name=None, phone=None):
        ObservableObject.__init__(self)
        self.name = name
        self.phone = phone

            
Alternatively lack of coupling can be preserved assigning 
``_qonda_column_meta_`` outside the class definition::
    
    Contact._qonda_column_meta_ = {
        'name': {
            'width': 30
            }
        }

Using class level metadata only works when the class argument is set in the 
adapter constructor. See next section for details.
        
        
Adapter level metadata
----------------------

You can add or override metadata in each adapter, using the ``column_meta``
argument. The argument is a tuple of dicts, one as many columns
have the adapter::

        adapter = ObjectListAdapter(
            ('name', 'phone'), 
            self.model, column_meta=
            (
                {'width': 30},
                {}
            ))

If class metadata is also available, adapter uses both. Individual
metadata properties set in the adapter override properties in class
metadata when both are set.

Metadata properties
-------------------

The next metadata properties are available, column wise:

==================  ======================  ========================  =============  ========================================
Property            Property type           Value type                Qt Role        Description
==================  ======================  ========================  =============  ========================================
title               Constant                unicode                   DisplayRole    Column title in QTableView and QTreeView
size                Constant                int                       SizeHintRole   Column width in characters. Used in
                                                                                     table and tree views along 
                                                                                     ``resizeColumnsToContents()``
==================  ======================  ========================  =============  ========================================
    
The next metadata properties are available, attribute value wise:

================== ====================== ======================== ============== ============================================
Property           Property type          Value type               Qt Role        Description
================== ====================== ======================== ============== ============================================
displayFormatter   Callable               unicode                  DisplayRole    A callable that receives the attribute value
                                                                                  and returns the formatted for displaying in 
                                                                                  a view.
editFormatter      Callable               unicode                  EditRole       A callable that receives the attribute value
                                                                                  and returns the formatted for displaying in 
                                                                                  editors.
decoration         Callable or constant   ``QIcon``, ``QColor``    DecorationRole Icon for the attribute. If it's a callable
                                          or ``QPixmap``                          it receives the entity as argument.
tooltip            Callable or constant   unicode                  ToolTipRole    Tooltip for the attribute. If it's a callable
                                                                                  it receives the entity as argument.
statustip          Callable or constant   unicode                  StatusTipRole  Statustip for the attribute. If it's a 
                                                                                  callable it receives the entity as argument.
whatsthis          Callable or constant   unicode                  WhatsThisRole  What's this help text for the attribute. If 
                                                                                  it's a callable it receives the entity as 
                                                                                  argument.
font               Callable or constant   ``QFont``                FontRole       Font family/size/style/weight used to show 
                                                                                  the value. If it's a callable it receives 
                                                                                  the entity as argument.
alignment          Constant               ``Qt.Alignment``         AlignmentRole  Field alignment.
background         Callable or constant   ``QBrush`` or ``QColor`` BackgroundRole Color/brush used to paint the background of 
                                                                                  the widget or field. If it's a callable it 
                                                                                  receives the entity as argument.
foreground         Callable or constant   ``QBrush`` or ``QColor`` ForegroundRole Color/brush used to paint the value on the 
                                                                                  widget or field. If it's a callable it 
                                                                                  receives the entity as argument.
flags              dict, keys are 
                   ``Qt.ItemFlags``,      bool                                    Flags of the Interview model item, such as 
                   values are callables                                           the item being enabled, editable or 
                   or constants                                                   selectable.  
================== ====================== ======================== ============== ============================================


Adapters, in detail
===================

The full syntax for ``ObjectAdapter`` creation is::

    ObjectAdapter(properties, model=None, class_=None,
            column_meta=None, parent=None)
            
* properties: A list (but usually a Python tuple) of attribute names
* model: The model entity object
* class\_: The class of the model, for metadata purposes, as model eventually could be None. See also ``ObjectListAdapter``.
* column_meta: The adapter level metadata, a list or tuple.
* parent: As adapters are QObject inheritors, can have parents for memory management purposes. Usually not used.

The syntax for ``ObjectListAdapter`` is similar::
    
    ObjectListAdapter(properties, model=None, class_=None, column_meta=None,
        parent=None, options=None, item_factory=None)

* class\_: For metadata purposes, but also for row appending. See also ``item_factory``.
* options: A set of options, by default assumes {'edit', 'append'}:
    # edit: Allow item editing (currently not 
    # append: Allows visual appending by showing a fake row at the bottom of the model.
* item_factory: Callable that return a new entity to be inserted into the model when ``insertRows()`` is called from the Qt side. If not set, ``class_`` constructor is used.

Adapter API
-----------

Adapters inherits from ``QAbstractItemModel``, and as such implements all 
of its methods and properties. Also implements the next methods.

* ``getPyObject(index)``: Gets the entity matching the given ``QModelIndex``.

Other adapters
--------------

``ValueListAdapter`` wraps a list of objects to be interpreted as values,
implementing a single column Interview model where each item matches one 
value::

    ValueListAdapter(model, parent=None, class_=None, column_meta=None)

Note that no property argument is required, however ``column_meta`` is
still a sequence, in order to be consistent with other adapters.

Common use of ``ValueListAdapter`` is as the model for combo boxes::
    
    choices = ["Apple", "Orange", "Banana"]  # Any kind of object allowed
    self.choices_adapter = ValueListAdapter(choices)
    self.ui.comboBox.setModel(self.choices_adapter)

``ObjectTreeAdapter`` is a more powerful version of ``ObjectListAdapter``,
able to wrap a tree-like structure of objects of the same type::
           
    ObjectTreeAdapter(properties, model=None, class_=None,
            column_meta=None, qparent=None,
            rootless=False, options=None, parent_attr='parent',
            children_attr='children'):

* qparent: Same as parent in previous cases.
* rootless: If ``False``, the model tree have a root object. If ``True``, the provided model is a list with no common root.
* parent_attr: Name of the model's attribute that reference each item parent
* children_attr: Name of the model's attribute that references each item children.


Mappers, widgets and delegates
==============================

Delegates
---------

Delegates are objects that copy values from the model to the view, and vice 
versa. When used in views like ``QTableView``, also build alternate editors 
and draw values in the view.

Qonda provides several custom delegates, in order to use alternative editor
in views, and being able to customize the editor properties:

* ComboBoxDelegate
* SpinBoxDelegate
* DateEditDelegate
* LineEditDelegate
* CheckBoxDelegate
* LookupWidgetDelegate

Also delegates uses the customized widgets (see below).

``ComboBoxDelegate`` is also special. Working with anilla ``QComboBox`` 
means working with the chosen value index. ``ComboBoxDelegate`` uses
the model value directly, so setting a model attribute to the selected
value transparent.

``DataWidgetMapper`` use this delegates automatically when appropiate. If
you need to use a customized delegate (e.g. setting editor properties),
use the ``addMapping()`` method with the ``delegate`` argument::

    from qonda.mvc.delegates import LineEditDelegate

    ...
    
    mapper.addMapping(self.ui.name, 0)
    mapper.addMapping(self.ui.phone, 1, 
        delegate=LineEditDelegate(self, inputMask="999-9999"))


In views, you must use the ``setItemDelegateForColumn()`` method::        
        
    self.ui.contacts.setItemDelegateForColumn(1, 
        LineEditDelegate(self, inputMask="999-9999"))

DataWidgetMapper
----------------

``DataWidgetMapper`` provides a more powerful and convenient alternative 
to stock ``QDataWidgetMapper``:

* Uses the appropiate, alternative delegate if registered in the ``_mappingDelegateClass`` attribute of the widget class, or via the delegate attribute in the ``addMapping()`` method
* Uses an enhanced ``ItemDelegate`` delegate, in order to set widget colors and fonts along the value.
* Enhances the ``addMapping()`` method to specify an alternate delegate.
* Adds an ``addMappings`` method for quick setting of mappings
* Widgets can be mapped with no model assigned, and mappings persists after a call to ``setModel()``
* ``setModel()`` automatically do ``toFirst()``

Widgets
-------

Qonda also provides a set of enhanced widgets:
    
* DateEdit: A ``QDateEdit`` allowing empty values
* DateTimeEdit: A ``QDateTimeEdit`` allowing empty values
* ComboBox: A ``QComboBox`` allowing empty values

LookupWidget
------------

Besides enhancing standard widgets, Qonda provides ``LookupWidget`` and it's 
very useful to set attributes when the number of allowable values is too 
large for a combo box. At first sight, ``LookupWidget`` is a regular 
``QLineEdit``, but input is not taken the value for the attribute but as 
input for a search function that returns the real value::

    cities = (
        u'Barcelona', u'Berlin', u'Bordeaux', u'Buenos Aires', u'Madrid',
        u'Manchester', u'Liverpool', u'London', u'Lyon', u'New York',
        u'Paris', u'Zurich')

        
    def lookup_city(s):
        result = []
        s = s.lower()
        for city in cities:
            if city[:len(s)].lower() == s:
                result.append(city)
        return result

    ...
    # Set the search function in the form setup:
    self.ui.city.search_function = lookup_city

    
TableView and TreeView
----------------------

``QTableView`` and ``QTreeView`` also received some extra love, adding these 
key combinations:
    
* Delete: Erases the selected value
* Down: If pressed while the current row is the last row, appends a new row.
* Control + Insert: Inserts a new row.
* Control + Delete: Deletes the current row.

``TreeView`` also implements the handy ``resizeColumnsToContents()`` method,
already present in ``QTreeView``.

Other goodies
=============

Qonda also includes the following classes, providing functionality useful
for common cases in business apps:

Aggregator
----------

``Aggregator`` calculates sum of attributes and/or count of elements in
list of entities, setting a attributes in a provided summary object.
Entities must be observable to allow aggregators update the summary 
values.::

    import qonda.util.aggregator
    
    class GroceryItem(ObservableObject):
        self __init__(self):
            self.description = None
            self.amount = 0
        
    class Summary(object):
        self __init__(self):
            self.count = 0
            self.total = 0
           
    ...
    summary = Summary()
    aggregator = qonda.util.aggregator.Aggregator(
        grocery_list,
        summary,
        {
            '*': 'count',
            'amount': 'total'
        })

ListSessionManager
------------------

``ListSessionManager`` manages automatic adding of deleting of items
of an ObservableListProxy into the associated SQLAlchemy session::

    from qonda.sqlalchemy import ListSessionManager

    ...
    model = ObservableListProxy(self.session.query(Stuff).all())
    # Adding and removing items from the model automatically
    # adds and deletes them from the session.
    self.session_manager = ListSessionManager(self.session, model)


QueryResult
-----------

``QueryResult`` is a list like object whose items comes from the provided 
SQLAlchemy query, but retrieving the items incrementally as required.

``QueryResult`` is not meant for arbitrary item insertion or deletion,
but mostly read only data display, as that would change item indexes 
and confuses incremental retrieving mechanism.
