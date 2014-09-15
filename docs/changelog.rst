Changelog
=========

0.6.0:
------

* Adjust sizeHint calculation
* ValueListAdapter now is editable.
* Add DataWidgetMapper.addMappingsFromPropertyList() and
  BaseAdapter.properties()
* Adds currentPyObject() method to TableView, TreeView and DataWidgetMapper
* Add DecimalSpinBoxDelegate.
* Add ListView (editable) widget
* Add RadioButtonGroup widget
* Fix: ObservableObject observe related objects when recreated by SQLAlchemy
* Fix: ObservableObject generates proper event for related object attributes
* Fix: ObservableObject must relay only events from other ObservableObject
* Fix: Make ObjectTreeAdapter understand properties as tuples (name, metadata)

0.5.5:
------

* Add use of '*' metadata key for properties common to all the attributes
* Add columnResizeMode metadata property
* Fix: Circular references in ObservableObject
* Fix: Make adapters work with updates on multiple attributes at once
* Fix: Ignore null/invalid values in Aggregator

0.5.4:
------
* Add SpinBox and DecimalSpinBox widgets and delegates
* ComboBoxDelegate supports empty combo models and editable combos.

0.5.3:
------

* Fix: Mapping of QLabel is read-only
* Fix: Proper float-str conversion in NumberEdit

0.5.2:
------

* PyQt5 compatibility
* Add property returnFormat to NumberEdit, value() can return either float or Decimal

0.5.1:
------

* Add new signal currentRowChanged to TableView and TreeView.
* Add properties allowAppends, allowInserts and allowDeletes to TableView and
  TreeView, in order to control editing capabilities.
* Add currentRowChanged signal to TableView and TreeView.

0.5.0:
------

* Definition of metadata in adapters as part of the property list.
* DataWidgetMapper handles QPushButton text.
* Adds NumberEdit, NumberEditDelegate, and MaskedLineEdit.
* Bug fixes

0.4.1:
------

* Add documentation and more examples
* Defining _notifiables_ in ObservableObject subclases made optional
* ListSessionManager observes automatically its target
* New methods in Adapter classes
* Bug fixes

0.4.0:
------

* First public release

