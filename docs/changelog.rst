Changelog
=========

0.8.0:
------

* Raises AttributeError on ObservableObject.__setattr__ if attribute doesn't
  exist. *BREAKS COMPATIBILITY WITH OLDER RELEASES*. Set
  qonda.IGNORE_ATTRIBUTE_ERRORS_ON_CALLBACKS = True to override.
* QCheckBox tristate support
* Adds ObjectListManager class to replace ListSessionManager without keeping
  a session open.
* Adds aliases for adapter properties, to ease binding the same attribute to
  multiple widgets.
* Adds prefix parameter to DataWidgetMapper.mapPropertyList(), to ease binding
  of multiple mappers in the same form.
* Adds on_value_set attribute to LookupWidget to allow changing the lookup
  value on the fly. This is useful in certain scenarios using SQLAlchemy.
* SortFilterProxyModel sorts None value both in Python 2 and 3, optionally
  sorting None as last values.

0.7.1:
------
* Adds setProperty method to delegates to be able to change properties used
  in editor creation.
* Fix: When setting allowEmpty to False in SpinBox, DateEdit, don't show empty
  as value for minimumValue()
*

0.7.0:
-------
* Proper PyQt5 support: use of PyQt4 and PyQt4 are determined at run time.
* Allow empty string in adapter property lists as a reference to object iself.
* Adapters now strip strings by default
* Fix: Use of formatters with composite adapter properties.
* Enhanced Documentation.

0.6.10:
-------
* PyQt5 compatibility imports
* Adds method LookupWidget.clear()
* Proper key navigation in views when there are hidden columns
* Fix: Emit dataChanged signal on row appending if fake row was present

0.6.9:
------
* Fix: When appending a row using down arrow on TableView and the
  model is a QSortFilterProxyModel instance, the new row didn't
  become active, but first row was instead.

0.6.8:
------
* Fix: Allow typing a negative sign in an empty NumberEdit
* Make widgets commit its value immediately when appropiate.

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

