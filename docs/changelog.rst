Changelog
=========

0.6.7:
------
* Fix: Handle empty value in NumberEdit when has focus.
* Fix: Force value from QComboBox options whe value is None and combo
  doesn't allow an empty value.

0.6.6:
------
* Fix: Calendar popup shows current month from empty value when using 
  DateEditDelegate.
* Ignoring KeyError when a cycling dependency between attributes mess with 
  attribute chain observing logic.

0.6.5:
------
* Fix: When DateEdit is empty, calendar popup shows current month instead 
  Sep 1752.
* Fix: Don't process insertion/deletion keypresses in view widgets when there 
  is no model set
* Change LookupWidget behavior: Mouse clicks and enter key don't erase current 
  value.

0.6.4:
------
* SortFilterProxyModel sorts using Python ordering.
* Fix role color handling in QLabels.
* Don't call callable metadata when object is None
* Add setPyModel() method to adapter classes

0.6.3:
------

* Fix: Define ObservableObject.__update_set attribute in reconstructor method.
* Return/Enter keys advance fields/appends records in TableView, ListView
* Fix: Use self.item_factory instead of self._class in ObjectListAdapter
  when appending the first row

0.6.2:
------

* ObservableObject handles recursion in update notifications when the observed
  object and related object have references to each other.
* Adapters now recognizes the flag key when defined in row_meta argument.
* SortFilterProxyModel proxy class added
* Add selectedObject() method to TableView, TreeView and ListView

0.6.1:
------

* Aggregators ignore None values
* ObjectAdapter doesn't emit a invalid property warn if there are None values
  along the attribute path

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

