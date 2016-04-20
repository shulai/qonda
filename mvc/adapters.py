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

import cPickle
from functools import partial

from .. import PYQT_VERSION
try:
    from UserDict import UserDict    # Python 2
except ImportError:
    from collections import UserDict  # Python 3, 2to3 doesn't fix it
from warnings import warn

if PYQT_VERSION == 5:
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.QtCore import Qt
else:
    from PyQt4 import QtCore, QtGui  # lint:ok
    from PyQt4.QtCore import Qt  # lint:ok
    QtWidgets = QtGui

from .observable import ObservableObject, ObservableListProxy

PythonObjectRole = 32
QondaResizeRole = 64


class QondaMetadataError(Exception):
    pass


class AdapterReader(object):
    """
        Convenient base for implementing value reading (data() method) in
        Adapter classes

        Child classes should implement the following:

        Method _get_value(self, index)
        Method index() (reimplement QAbstractItemView.index so internalPointer
            attribute must reference the Python object)
        Attribute _column_meta

        Of course, they should call super().__init__ in order to
        get the role metadata resolving stuff working.

    """

    def __init__(self):

        def formatter(key, self, index):
            "Partial function for functional, value derived metadata"
            #try:
            v = self._get_value(index)
            #except:
            #    return None
            try:
                f = self._column_meta[index.column()][key]
            except (IndexError, KeyError):
                # No column meta, no metadata key,
                return unicode(v) if v is not None else u''
            return f(v)

        def callable_constant_meta(key, self, index):
            """Partial function for functional, object entity derived, or
            constant metadata"""
            #try:
            o = self._get_value_object(index)
            #except Exception as e:
            #    print "Error!!!", str(e)
            #    return None
            try:
                m = self._column_meta[index.column()][key]
                if callable(m):
                    return m(o) if o else None
                else:
                    return m
            except KeyError:  # No key in the column meta
                o = self.getPyObject(index)
                try:
                    m = self._row_meta[key]
                    if callable(m):
                        return m(o) if o else None
                    else:
                        return m
                except KeyError:  # No key in row meta
                    return None
            except IndexError:  # No column meta
                return None

        def constant_meta(key, self, index):
            "Partial function for constant metadata"
            try:
                return self._column_meta[index.column()][key]
            except KeyError:  # No key in the column meta
                try:
                    return self._row_meta[key]
                except KeyError:  # No key in the row meta
                    return None
            except IndexError:  # No column meta
                return None

        self._get_display_role = partial(formatter, 'displayFormatter',
            self)
        self._get_edit_role = partial(formatter, 'editFormatter', self)
        self._get_decoration_role = partial(callable_constant_meta,
            'decoration', self)
        self._get_tool_tip_role = partial(callable_constant_meta, 'tooltip',
            self)
        self._get_status_tip_role = partial(callable_constant_meta,
            'statustip', self)
        self._get_whats_this_role = partial(constant_meta, 'whatsthis', self)
        self._get_font_role = partial(callable_constant_meta, 'font', self)
        self._get_text_alignment_role = partial(constant_meta, 'alignment',
            self)
        self._get_background_role = partial(callable_constant_meta,
            'background', self)
        self._get_foreground_role = partial(callable_constant_meta,
            'foreground', self)

    def data(self, index, role=Qt.DisplayRole):

        def get_size_hint_role(index):
            # Note there is other get_size_hint_role in headerData
            # *Both* seems to be called by the views
            section = index.column()
            try:
                w = self._column_meta[section]['width']
                return QtCore.QSize(w * QtWidgets.QApplication.instance()
                    .fontMetrics().averageCharWidth() * 1.4, 20)
            except (IndexError, KeyError):
                return None

        if not index.isValid():
            return None

        role_resolvers = {
            Qt.DisplayRole: self._get_display_role,
            Qt.EditRole: self._get_edit_role,
            Qt.DecorationRole: self._get_decoration_role,
            Qt.ToolTipRole: self._get_tool_tip_role,
            Qt.StatusTipRole: self._get_status_tip_role,
            Qt.WhatsThisRole: self._get_whats_this_role,
            Qt.SizeHintRole: get_size_hint_role,
            Qt.FontRole: self._get_font_role,
            Qt.TextAlignmentRole: self._get_text_alignment_role,
            Qt.BackgroundRole: self._get_background_role,
            Qt.ForegroundRole: self._get_foreground_role,
            PythonObjectRole: self._get_value,
        }
        try:
            return role_resolvers[role](index)
        except KeyError:  # Role resolver not specified
            return None

    def headerData(self, section, orientation, role):

        def get_title(section):
            try:
                return self._column_meta[section]['title']
            except (IndexError, KeyError):  # No column meta or no meta key
                return (self._properties[section].split('.').pop().
                    title().replace('_', ' '))

        def get_size_hint_role(section):
            # Note there is other get_size_hint_role in headerData
            # *Both* seems to be called by the views
            try:
                w = self._column_meta[section]['width']
                return QtCore.QSize(w * QtWidgets.QApplication.instance()
                    .fontMetrics().averageCharWidth() * 1.4, 20)
            except (IndexError, KeyError):  # No column meta or no meta key
                return None

        # Qonda extension: Handle QHeaderView resizemodes using roles
        def get_resize_role(section):
            try:
                return self._column_meta[section]['columnResizeMode']
            except (IndexError, KeyError):  # No column meta or no meta key
                return None

        if orientation == Qt.Horizontal:
            role_resolvers = {
                Qt.DisplayRole: get_title,
#                Qt.EditRole: self._get_edit_role,
#                Qt.DecorationRole: self._get_decoration_role,
#                Qt.ToolTipRole: self._get_tool_tip_role,
#                Qt.StatusTipRole: self._get_status_tip_role,
#                Qt.WhatsThisRole: self._get_whats_this_role,
                 Qt.SizeHintRole: get_size_hint_role,
#                Qt.FontRole: self._get_font_role,
#                Qt.TextAlignmentRole: self._get_text_alignment_role,
#                Qt.BackgroundRole: self._get_background_role,
#                Qt.ForegroundRole: self._get_foreground_role,
                 QondaResizeRole: get_resize_role
            }
            try:
                return role_resolvers[role](section)
            except KeyError:  # Role resolver not specified
                return None

            if role == Qt.DisplayRole:
                return get_title(section)
            elif role == Qt.SizeHintRole:
                return get_size_hint_role(section)
            return None
        else:
            if role == Qt.DisplayRole:
                return unicode(section)
            elif role == Qt.SizeHintRole:
                return QtCore.QSize(20, 20)
            return None

    # For DnD
    def mimeTypes(self):
        return ['application/qonda.pyobject', 'text/plain']

    # For DnD
    def mimeData(self, indexes):

        def mime_data(index):
            o = self.getPyObject(index)
            if o:
                try:
                    m = self._column_meta[index.column()]['mime']
                    return m(o)
                except (IndexError, KeyError):
                    return None
            return None

        mime = QtCore.QMimeData()
        if len(indexes) == 0:
            return 0
        elif len(indexes) == 1:
            mime.setText(self.data(indexes[0], Qt.DisplayRole))
            data = mime_data(indexes[0])
            if data is None:
                data = self.getPyObject(indexes[0])
            mime.setData('application/qonda.pyobject', cPickle.dumps(data))
        else:
            text_list = []
            object_list = []
            for index in indexes:
                text_list.append(self.data(index, Qt.DisplayRole))
                data = mime_data(index)
                if not data:
                    data = self.getPyObject(index)
                object_list.append(cPickle.dumps(data))
            mime.setText('\n'.join(text_list))
            mime.setData('application/qonda.pyobject',
                cPickle.dumps(object_list))

        return mime

    def flags(self, index):
        """
            Returns the item flags for the given index.
            This implementation checks the flags information from metadata,
            and returns ItemIsSelectable, ItemIsEditable and ItemIsEnabled
            if no flags info is available.
        """
        i_c = index.column()
        i_p = index.parent()
        if (not index.isValid() or index.row() >= self.rowCount(i_p)
                or i_c >= self.columnCount(i_p)):
            return Qt.NoItemFlags

        try:
            o = self.getPyObject(index)
        except:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

        flags = Qt.ItemFlags()
        try:
            for flagbit, flagvalue in (
                    self._column_meta[i_c]['flags'].iteritems()):
                if callable(flagvalue):
                    if flagvalue(o):
                        flags |= flagbit
                else:
                    if flagvalue:
                        flags |= flagbit
            return flags
        except (IndexError, KeyError):  # No column meta, no meta key
            try:
                for flagbit, flagvalue in (
                        self._row_meta['flags'].iteritems()):
                    if callable(flagvalue):
                        if flagvalue(o):
                            flags |= flagbit
                    else:
                        if flagvalue:
                            flags |= flagbit
                return flags
            except KeyError:  # no meta key
                return (Qt.ItemIsSelectable | Qt.ItemIsEditable
                    | Qt.ItemIsEnabled)


class AdapterWriter(object):
    """
        Convenient base for implementing value reading (data() method) in
        Adapter classes

        Child classes should implement the following:

            Method _set_value(self, index, value)
    """

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid():
            return False
        if role == Qt.EditRole:
            try:
                value = self._column_meta[index.column()]['parser'](value)
            except (IndexError, KeyError):
                if value == u'':
                    value = None
                elif isinstance(value, basestring):
                    value = value.strip()
            if self._get_value(index) == value:
                return True
            return self._set_value(index, value)
        elif role == PythonObjectRole:
            if self._get_value(index) == value:
                return True
            return self._set_value(index, value)

        return False


class MetaPropertyWrapper(object):
    """
    A metadata property wrapper that pass the proper object to callables
    """
    def __init__(self, property_name, meta_property):
        self._property_name = property_name
        self._meta_property = meta_property

    def __call__(self, *a, **kw):
        o = a[0]
        return self._meta_property(getattr(o, self._property_name))


class MetaFormatterPropertyWrapper(object):
    """
    A metadata property wrapper that pass the proper object to callables
    """
    def __init__(self, meta_property):
        self._meta_property = meta_property

    def __call__(self, *a, **kw):
        o = a[0]
        return self._meta_property(o)


class PropertyMetadataWrapper(UserDict):
    """
    A wrapper for attribute metadata that wraps individual metadata properties
    in MetaPropertyWrapper.
    Used to pass the right object to the callables present when the metadata
    is a reference to metadata in the attribute class (marked with '.')
    """
    def __init__(self, property_name, meta):
        super(PropertyMetadataWrapper, self).__init__()
        self.data.update(meta)
        self._property_name = property_name

    def __getitem__(self, key):
        meta_property = self.data[key]
        if callable(meta_property):
            if key in ('displayFormatter', 'editFormatter'):
                return MetaFormatterPropertyWrapper(meta_property)
            else:
                return MetaPropertyWrapper(self._property_name, meta_property)
        else:
            return meta_property

    def copy(self):
        return PropertyMetadataWrapper(self._property_name, self.data)


def _build_class_meta(class_, properties):

    def resolve_meta(class_, p):
        try:
            v = class_._qonda_column_meta_[p]
            # Property can be a reference and meta a link to expected class
            if isinstance(v, type):
                v = PropertyMetadataWrapper(p, v._qonda_column_meta_['.'])
        except KeyError:
            head, tail = p.split('.', 1)
            try:
                v = class_._qonda_column_meta_[head]
                if isinstance(v, type):
                    v = resolve_meta(v, tail)
                else:
                    print ("Warning: Composite attribute found metadata "
                        "doesn't point to a class. "
                        "The attribute won't use class metadata")
                    v = {}
            except KeyError:
                v = {}
        return v

    meta = []
    for p in properties:
        try:
            v = resolve_meta(class_, p)
        except (ValueError, AttributeError):
            v = {}
        meta.append(v)
    return meta


def _combine_column_metas(class_, adapter_meta, properties):

    if class_ is None:
        print ("Warning: Adapter has no model class defined. Will use only "
            "provided metadata")
        return () if adapter_meta is None else adapter_meta

    class_meta = _build_class_meta(class_, properties)
    if adapter_meta is None:
        return class_meta
    if len(adapter_meta) != len(properties):
        print ("Warning: Adapter provided metadata count and property count"
            "doesn't match.")
        if len(adapter_meta) < len(properties):
            adapter_meta = adapter_meta + [{}] * (len(properties)
                - len(adapter_meta))
    meta = []
    for am, cm in zip(adapter_meta, class_meta):
        m = cm.copy()
        m.update(am)
        meta.append(m)
    return meta


def _combine_row_metas(class_, adapter_meta):

    if class_ is None:
        return {} if adapter_meta is None else adapter_meta

    try:
        class_meta = class_._qonda_column_meta_['*']
    except (AttributeError, KeyError):
        class_meta = {}

    if adapter_meta is None:
        return class_meta

    meta = class_meta.copy()
    meta.update(adapter_meta)
    return meta


class BaseAdapter(QtCore.QAbstractTableModel):
    """
        Base class for adapting Python objects into a PyQt QAbstractTableModel
        compatible wrapper.
    """
    def __init__(self, properties, model=None, class_=None, column_meta=None,
            row_meta=None, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._model = model
        self._class = class_
        if column_meta is not None:
            # Up to 0.4.x behavior: Meta declarations separate
            # from property list
            self._properties = tuple(properties)
        else:
            # 0.5 behavior:
            self._properties = [x if isinstance(x, str) else x[0]
                for x in properties]
            column_meta = [{} if isinstance(x, str) else x[1]
                for x in properties]

        self._column_meta = _combine_column_metas(class_, column_meta,
            self._properties)
        self._row_meta = _combine_row_metas(class_, row_meta)

        try:
            model.add_callback(self.observe)
        except AttributeError:
            # If not observable (ok if the model doesn't change)
            "Notice: " + str(type(model)) + " is not observable"

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return 0
        return len(self._properties)

    def getPyModel(self):
        return self._model

    def properties(self):
        return self._properties

    def getPropertyColumn(self, prop):
        return self._properties.index(prop)

    def getColumnProperty(self, col):
        return self._properties[col]

    def setPyModel(self, model):
        """Changes the underlying python model"""
        self.beginResetModel()
        self._model = model
        self.endResetModel()


class ObjectAdapter(AdapterReader, AdapterWriter, BaseAdapter):
    """
        Adapts a Python object into a single row PyQt QAbstractTableModel.
    """

    def __init__(self, properties, model=None, class_=None,
            column_meta=None, row_meta=None, parent=None):
        # super is *really* harmful
        AdapterReader.__init__(self)
        BaseAdapter.__init__(self, properties, model, class_, column_meta,
            row_meta, parent)

    def index(self, row, column, parent=None):

        if parent is not None and parent.isValid():
            # Non hierarchical item model has no valid parent
            return QtCore.QModelIndex()

        if row != 0 or column < 0 or column >= len(self._properties):
            return QtCore.QModelIndex()

        return self.createIndex(row, column, self._model)

    def getPyObject(self, index):
        if index.row() != 0:
            return None
        return self._model

    def _get_value(self, index):
        value = None
        if index.row() != 0:
            raise IndexError
        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))

        try:
            obj = self._model
            prop = propertyparts.pop(0)
            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
            value = getattr(obj, prop) if prop != '' else obj
        except AttributeError:
            if obj is not None:
                warn("Adapter property {} ({}) not found in the model {}({})"
                    .format(propertyname, prop, self._model, self._class))
        return value

    def _set_value(self, index, value):

        try:
            propertyparts = self._properties[index.column()].split('.')
            obj = self._model
            prop = propertyparts.pop(0)

            while len(propertyparts):
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
            setattr(obj, prop, value)
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
            return False
        except AttributeError:
            warn("Adapter property " + prop + "not found in the model")
            return False
        return True

    def _get_value_object(self, index):
        """
        Return the object currently holding the value
        """
        if index.row() != 0:
            raise IndexError
        propertyname = self._properties[index.column()]
        propertyparts = propertyname.split('.')
        try:
            obj = self._model
            prop = propertyparts.pop(0)
            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
        except AttributeError:
            warn("Adapter property " + propertyname
                + "not found in the model" + str(obj))

        return obj

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return 0
        return 1

    def observe(self, sender, event_type, observer_data, attrs):
        if sender != self._model:
            warn("Received an event but the sender isn't the adapter's model.")
            return
        if event_type == "update":
            for updated_prop in attrs:
                lu = len(updated_prop)
                for i, prop in enumerate(self._properties):
                    lp = len(prop)
                    if lu > lp:
                        continue
                    if updated_prop == prop[0:lu] and (lp == lu or
                            prop[lu] == '.'):
                        index = self.createIndex(0, i)
                        self.dataChanged.emit(index, index)


class BaseListAdapter(AdapterReader, AdapterWriter):

    def observe(self, sender, event_type, list_row, attrs):
        if sender != self._model:
            return

        def before_setitem(attrs):
            i, inserting = attrs
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            if start is None:
                start = 0
            if stop is None:
                stop = len(sender)
            removing = stop - start
            for i in range(start, stop):
                try:
                    sender[i].remove_callback(self.observe_item)
                except AttributeError:  # list item is not Observable
                    pass
            # Insert/remove the difference of lines
            if removing > inserting:
                self.beginRemoveRows(QtCore.QModelIndex(), start,
                    start + removing - inserting - 1)
            else:
                self.beginInsertRows(QtCore.QModelIndex(), start,
                    start + inserting - removing - 1)

        def setitem(attrs):
            i, inserting = attrs
            start, removing = ((i, 1) if type(i) == int
                else (i.start, i.stop - i.start))
            stop = start + inserting
            for i in range(start, stop):
                try:
                    sender[i].add_callback(self.observe_item, i)
                except AttributeError:  # list item is not Observable
                    pass
            # Update observer_data after the slice
            for i, row in enumerate(sender[stop:]):
                try:
                    row.set_callback_data(self.observe_item, stop + i)
                except AttributeError:  # list item is not Observable
                    pass
            if removing > inserting:
                self.endRemoveRows()
            else:
                self.endInsertRows()
                self.dataChanged.emit(self.index(stop, 0),
                    self.createIndex(start + inserting - 1,
                    len(self._properties) - 1))

            if 'append' in self.options and len(sender) == 0:
                self._insert_placeholder()

        def before_delitem(i):
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            if start is None:
                start = 0
            if stop is None:
                stop = len(sender)
            for i in range(start, stop):
                try:
                    sender[i].remove_callback(self.observe_item)
                except AttributeError:  # list item is not Observable
                    pass
            self.beginRemoveRows(QtCore.QModelIndex(), start, stop - 1)

        def delitem(i):
            start = i if type(i) == int else i.start
            # Update observer_data starting in the slice (as elements shifted)
            for i, row in enumerate(sender[start:]):
                try:
                    row.set_callback_data(self.observe_item, start + i)
                except AttributeError:  # Item is not observable
                    pass
            self.endRemoveRows()
            if 'append' in self.options and len(sender) == 0:
                self._insert_placeholder()

        def before_insert(i):
            if 'append' in self.options and len(sender) == 0:
                self._remove_placeholder()
            self.beginInsertRows(QtCore.QModelIndex(), i, i)

        def insert(i):
            try:
                sender[i].add_callback(self.observe_item, i)
            except AttributeError:  # list item is not Observable
                pass
            # Update observer_data after the inserted element
            for j, row in enumerate(sender[i + 1:]):
                try:
                    row.set_callback_data(self.observe_item, j + i)
                except AttributeError:  # list item is not Observable
                    pass
            self.endInsertRows()

        def before_append(dummy):
            if not ('append' in self.options and len(sender) == 0):
                self.beginInsertRows(QtCore.QModelIndex(), len(sender),
                    len(sender))

        def append(dummy):
            try:
                sender[-1].add_callback(self.observe_item, len(sender) - 1)
            except AttributeError:  # list item is not Observable
                pass
            if ('append' in self.options and len(sender) == 1):
                self.dataChanged.emit(self.index(0, 0),
                    self.createIndex(0, self.columnCount() - 1))
            else:
                self.endInsertRows()

        def before_extend(n):
            if 'append' in self.options and len(sender) == 0:
                self._remove_placeholder()
            self.beginInsertRows(QtCore.QModelIndex(), len(sender),
                len(sender) + attrs - 1)

        def extend(n):
            for i in range(-n):
                try:
                    sender[i].add_callback(self.observe_item, i)
                except AttributeError:  # list item is not Observable
                    pass
            self.endInsertRows()

        # Call the function matching event_type
        locals()[event_type](attrs)

    def observe_item(self, sender, event_type, list_index, attrs):
        if event_type != "update":
            return

        for updated_prop in attrs:
            # FIXME: This look ugly, and probably is wrong
            lu = len(updated_prop)
            for i, prop in enumerate(self._properties):
                lp = len(prop)
                if lu > lp:
                    continue
                if updated_prop == prop[0:lu] and (lp == lu or prop[lu] == '.'):
                    index = self.createIndex(list_index, i)
                    self.dataChanged.emit(index, index)


class ValueListAdapter(BaseListAdapter, QtCore.QAbstractListModel):
    """
        Adapts a list of Python values into a single column
        PyQt QAbstractTableModel.
    """
    def __init__(self, model, parent=None, class_=None, column_meta=None,
            row_meta=None, options=None, item_factory=None):
        # super is *really* harmful
        BaseListAdapter.__init__(self)
        QtCore.QAbstractListModel.__init__(self, parent)
        self._model = model
        self._column_meta = _combine_column_metas(class_, column_meta, '.')
        self._row_meta = _combine_row_metas(class_, row_meta)
        self.options = set(['edit', 'append']) if options is None else options
        self.item_factory = item_factory if item_factory is not None else class_
        try:
            model.add_callback(self.observe)
        except AttributeError:
            # If not observable (ok if the model doesn't change)
            "Notice: " + str(type(model)) + " is not observable"

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return 0
        count = len(self._model)
        if count == 0 and 'append' in self.options:
            count = 1
        return count

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return 0
        return 1

    def index(self, row, column, parent=None):

        if parent is not None and parent.isValid():
            # Non hierarchical item model has no valid parent
            return QtCore.QModelIndex()

        if column != 0:
            print "Warning: ValueListAdapter: invalid column", column
            return QtCore.QModelIndex()

        if row == len(self._model) and 'append' in self.options:
            # Return index for placeholder append row
            # The row object will be appended in _set_value() if needed
            return self.createIndex(row, 0, None)

        if not (0 <= row < len(self._model)):  # item model has a single row
            print "Warning: ValueListAdapter: invalid row", row
            return QtCore.QModelIndex()

        return self.createIndex(row, column, self._model[row])

    def getPyModel(self):
        return self._model

    def setPyModel(self, model):
        """Changes the underlying python model"""
        self.beginResetModel()
        self._model = model
        self.endResetModel()

    def getPyObject(self, index):
        try:
            return self._model[index.row()]
        except IndexError:
            return None

    def _get_value(self, index):
        if index.column() != 0:
            raise IndexError
        try:
            return self._model[index.row()]
        except IndexError:
            return None

    def _set_value(self, index, value):
        if (index.row() == 0 and len(self._model) == 0
                and 'append' in self.options):
            self._model.append(value)
        else:
            try:
                self._model[index.row()] = value
            except (IndexError, AttributeError):
                return False
        return True

    def _get_value_object(self, index):
        if index.column() != 0:
            raise IndexError
        try:
            return self._model[index.row()]
        except IndexError:
            if not (index.row() == 0 and len(self._model) == 0
                    and 'append' in self.options):
                warn("There is no row " + str(index.column()) + " in the model")
            return None  # Index doesn't exist

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if index.parent().isValid():
            return None

        if index.column() != 0:
            return None

        return AdapterReader.data(self, index, role)

    def _insert_placeholder(self):
        self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
        self.endInsertRows()

    def _remove_placeholder(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        self.endRemoveRows()

    # TODO: Put insertRows and removeRows in BaseListAdapter
    # (use item_factory=lambda: None)
    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return False
        if row > len(self._model):
            return False
        # Observable models are managed in observe
        if not isinstance(self._model, ObservableListProxy):
            self.beginInsertRows(parent, row, row + count - 1)
        newrows = [None for x in range(0, count)]
        self._model[row:row] = newrows
        if not isinstance(self._model, ObservableListProxy):
            self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return False
        if count < 1 or row + count > len(self._model):
            return False
        # Observable models are managed in observe
        if not isinstance(self._model, ObservableListProxy):
            self.beginRemoveRows(parent, row, row + count - 1)
        self._model[row:row + count] = []
        if not isinstance(self._model, ObservableListProxy):
            self.endRemoveRows()
        return True


class ObjectListAdapter(BaseListAdapter, AdapterWriter, BaseAdapter):
    """
        Adapts a list of Python objects into a PyQt
        QAbstractTableModel.
        The list items should have all the same type.
    """

    def __init__(self, properties, model=None, class_=None, column_meta=None,
        row_meta=None, parent=None, options=None, item_factory=None):
        """
            Create a ObjectListAdapter.
            properties: list of properties of the elements to be shown in the
                        view.
            model: the model itself.
            class_: class of list elements. Used when inserting new elements in
                    the model.
        """
        AdapterReader.__init__(self)
        BaseAdapter.__init__(self, properties, model, class_, column_meta,
            row_meta, parent)
        # TODO: Check if edit_allowed is necessary (Can disable item editing
        # in the view)
        self.options = set(['edit', 'append']) if options is None else options
        self.item_factory = item_factory if item_factory is not None else class_
        for i, row in enumerate(self._model):
            try:
                row.add_callback(self.observe_item, i)
            except AttributeError:
                # If not observable (ok if the model doesn't change)
                pass

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return 0
        count = len(self._model)
        if count == 0 and 'append' in self.options:
            count = 1
        return count

    def index(self, row, column, parent=None):

        if parent is not None and parent.isValid():
            # Non hierarchical item model has no valid parent
            return QtCore.QModelIndex()

        if row < 0 or column < 0 or column >= len(self._properties):
            return QtCore.QModelIndex()

        try:
            if row == len(self._model):
                if 'append' in self.options:
                    # Return index for placeholder append row
                    # The row object will be appended in _set_value() if needed
                    return self.createIndex(row, column, None)
                else:
                    return QtCore.QModelIndex()
            return self.createIndex(row, column, self._model[row])
        except IndexError:
            return QtCore.QModelIndex()

    def getPyObject(self, index):
        try:
            return self._model[index.row()]
        except IndexError:
            return None

    def _get_value(self, index):
        value = None
        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
            return None
        try:
            obj = self._model[index.row()]
        except IndexError:
            # Ok if "shadow" append row
            if not (index.row() == 0 and len(self._model) == 0
                    and 'append' in self.options):
                warn("There is no row " + str(index.column()) + " in the model")
            return None
        try:
            prop = propertyparts.pop(0)
            #while True:
                #value = getattr(obj, prop)
                #if not propertyparts:
                    #break
                #obj = value
                #prop = propertyparts.pop(0)
            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
            value = getattr(obj, prop) if prop != '' else obj
        except AttributeError:
            if obj is not None:
                warn("Adapter property {} ({}) not found in the model {}"
                    .format(propertyname, prop, obj))

        return value

    def _set_value(self, index, value):

        if (index.row() == 0 and len(self._model) == 0
                and 'append' in self.options):
            self._model.append(self.item_factory())

        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
        try:
            obj = self._model[index.row()]
        except IndexError:
            if not (index.row() == 0 and len(self._model) == 0
                    and 'append' in self.options):
                warn("There is no row " + str(index.column()) + " in the model")
            return None
        try:
            prop = propertyparts.pop(0)
            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
            setattr(obj, prop, value)
        except AttributeError:
            warn("Adapter property " + propertyname
                + "not found in the model " + str(obj))
            return False
        return True

    def _get_value_object(self, index):
        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
        try:
            obj = self._model[index.row()]
        except IndexError:
            # Ok if "shadow" append row
            if not (index.row() == 0 and len(self._model) == 0
                    and 'append' in self.options):
                warn("There is no row " + str(index.column()) + " in the model")
            return None
        try:
            prop = propertyparts.pop(0)
            #while True:
                #value = getattr(obj, prop)
                #prop = propertyparts.pop(0)
                #obj = value
            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)

        except AttributeError:
            warn("Adapter property " + propertyname
                + "not found in the model " + str(obj))

        return obj

    def _insert_placeholder(self):
        self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
        self.endInsertRows()

    def _remove_placeholder(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        self.endRemoveRows()

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return False
        if row > len(self._model):
            return False
        # Observable models are managed in observe
        if not isinstance(self._model, ObservableListProxy):
            self.beginInsertRows(parent, row, row + count - 1)
        newrows = [self.item_factory() for x in range(0, count)]
        self._model[row:row] = newrows
        if not isinstance(self._model, ObservableListProxy):
            self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            return False
        if count < 1 or row + count > len(self._model):
            return False
        # Observable models are managed in observe
        if not isinstance(self._model, ObservableListProxy):
            self.beginRemoveRows(parent, row, row + count - 1)
        self._model[row:row + count] = []
        if not isinstance(self._model, ObservableListProxy):
            self.endRemoveRows()
        return True


class ObjectTreeAdapter(AdapterReader, AdapterWriter,
        QtCore.QAbstractItemModel):
    """
        Adapts a tree of Python objects into a PyQt
        QAbstractTableModel.
        The items should have all the same type.
    """

    class RootNode(ObservableObject):
        def __init__(self, children=[], parent_attr='parent',
                children_attr='children'):
            ObservableObject.__init__(self)
            setattr(self, children_attr, children)
            setattr(self, parent_attr, None)

    def __init__(self, properties, model=None, class_=None,
            column_meta=None, row_meta=None, qparent=None,
            rootless=False, options=None, parent_attr='parent',
            children_attr='children'):

        AdapterReader.__init__(self)
        QtCore.QAbstractItemModel.__init__(self, qparent)

        self._class = class_

        if column_meta is not None:
            # Up to 0.4.x behavior: Meta declarations separate
            # from property list
            self._properties = properties
        else:
            # 0.5 behavior:
            self._properties = [x if isinstance(x, str) else x[0]
                for x in properties]
            column_meta = [{} if isinstance(x, str) else x[1]
                for x in properties]

        self.rootless = rootless
        if rootless:
            model = ObjectTreeAdapter.RootNode(model, parent_attr,
                children_attr)

        self._model = model
        self._column_meta = _combine_column_metas(class_, column_meta,
            properties)
        self._row_meta = _combine_row_metas(class_, row_meta)
        self.options = set(['edit', 'append']) if options is None else options
        self.parent_attr = parent_attr
        self.children_attr = children_attr

        root_index = QtCore.QModelIndex()

        self._model.add_callback(self.observe_item, root_index)
        self._observe(getattr(self._model, self.children_attr, None),
            root_index)

    def _observe(self, submodel, model_index):
        if submodel is None:
            return
        try:
            submodel.add_callback(self.observe,
                QtCore.QModelIndex(model_index))
        except AttributeError:
            print "Notice: " + str(type(submodel)) + " is not observable"

        for i, row in enumerate(submodel):
            row_index = self.index(i, 0, model_index)
            try:
                row.add_callback(self.observe_item,
                    QtCore.QModelIndex(row_index))
            except AttributeError:
                print "Warning: " + str(type(submodel)) + " is not observable"

            self._observe(getattr(row, self.children_attr, None), row_index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._properties)

    def index(self, row, column, parent=None):

        if parent is not None and parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self._model

        if row < 0 or column < 0 or column >= len(self._properties):
            return QtCore.QModelIndex()

        try:
            submodel = getattr(parentItem, self.children_attr, [])
            if row == len(submodel):
                if 'append' in self.options:
                    ## Return index for placeholder append row
                    ## The row object will be appended in _set_value() if needed
                    return self.createIndex(row, column, None)
                else:
                    return QtCore.QModelIndex()
            childItem = submodel[row]
            idx = self.createIndex(row, column, childItem)
        except IndexError:
            idx = QtCore.QModelIndex()

        return idx

    def getPyModel(self):
        return self._model

    def setPyModel(self, model):
        """Changes the underlying python model"""
        self.beginResetModel()
        self._model = model
        self.endResetModel()

    def getPyObject(self, index):
        return index.internalPointer()

    def item_index(self, item):

        if item == self._model:
            return QtCore.QModelIndex()

        parentItem = getattr(item, self.parent_attr)

        if parentItem is None and self.rootless:
            parentItem = self._model

        parentChildren = getattr(parentItem, self.children_attr)
        row = parentChildren.index(item)
        return self.createIndex(row, 0, item)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = getattr(childItem, self.parent_attr)
        if parentItem is None and self.rootless:
            parentItem = self._model
        return self.item_index(parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):

        if not parent.isValid():
            parentItem = self._model
        else:
            if parent.column() > 0:
                return 0
            parentItem = parent.internalPointer()
            if parentItem is None and self.rootless:
                parentItem = self._model

        try:
            count = len(getattr(parentItem, self.children_attr))
        except (TypeError, AttributeError):
            count = 0

        if count == 0 and 'append' in self.options:
            count += 1

        return count

    def _get_value(self, index):
        value = None
        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
        try:
            obj = index.internalPointer()
            prop = propertyparts.pop(0)

            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
            value = getattr(obj, prop)
        except AttributeError:
            if obj is not None:
                warn("Adapter property {} ({}) not found in the model {}"
                    .format(propertyname, prop, obj))

        return value

    def _set_value(self, index, value):
        # TODO: Append
        # TODO: handling compound properties
        try:
            propertyname = self._properties[index.column()]
            obj = index.internalPointer()
            prop = propertyname
            setattr(obj, prop, value)
            return True
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
            return False
        except AttributeError:
            warn("Adapter property " + propertyname
                + "not found in the model " + str(obj))

    def _get_value_object(self, index):
        try:
            propertyname = self._properties[index.column()]
            propertyparts = propertyname.split('.')
        except IndexError:
            warn("No adapter property for the column " + str(index.column()))
        try:
            obj = index.internalPointer()
            prop = propertyparts.pop(0)

            while propertyparts:
                obj = getattr(obj, prop)
                prop = propertyparts.pop(0)
        except AttributeError:
            warn("Adapter property " + propertyname + "not found in the model"
                + str(obj))

        return obj

    def flags(self, index):
        """
            Returns the item flags for the given index.
            This implementation checks the flags information from metadata,
            and returns ItemIsSelectable, ItemIsEditable and ItemIsEnabled
            if no flags info is available.
        """
        i_c = index.column()
        i_p = index.parent()
        if (not index.isValid() or index.row() >= self.rowCount(i_p)
                or i_c >= self.columnCount(i_p)):
            return Qt.NoItemFlags

        o = index.internalPointer()
        flags = 0
        try:
            for flagbit, flagvalue in (self._column_meta[index.column()]
                ['flags'].iteritems()):
                try:
                    flags |= flagbit if flagvalue(o) else 0
                except TypeError:
                    flags |= flagbit if flagvalue else 0
            return flags
        except (KeyError, TypeError):
            try:
                for flagbit, flagvalue in (self._row_meta['flags'].iteritems()):
                    try:
                        flags |= flagbit if flagvalue(o) else 0
                    except TypeError:
                        flags |= flagbit if flagvalue else 0
                return flags
            except (KeyError, TypeError):
                return (Qt.ItemIsSelectable | Qt.ItemIsEditable
                    | Qt.ItemIsEnabled)

    def _insert_placeholder(self, parent):
        self.beginInsertRows(parent, 0, 0)
        self.endInsertRows()

    def _remove_placeholder(self, parent):
        self.beginRemoveRows(parent, 0, 0)
        self.endRemoveRows()

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent != QtCore.QModelIndex():
            if not self.hasIndex(parent.row(), parent.column(),
                    parent.parent()):
                return False
        parentItem = parent.internalPointer()
        if parentItem is None:
            parentItem = self._model
        item_list = getattr(parentItem, self.children_attr)
        if row > len(item_list):
            return False
        # Observable models are managed in observe
        if not isinstance(item_list, ObservableListProxy):
            self.beginInsertRows(parent, row, row + count - 1)
        newrows = [self._class() for x in range(0, count)]
        item_list[row:row] = newrows
        for item in newrows:
            setattr(item, self.parent_attr, parentItem)
        if not isinstance(item_list, ObservableListProxy):
            self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if count < 1:
            return False
        parentItem = parent.internalPointer()
        if parentItem is None:
            parentItem = self._model
        item_list = getattr(parentItem, self.children_attr)
        if row + count > len(item_list):
            return False
        # Observable models are managed in observe
        if not isinstance(item_list, ObservableListProxy):
            self.beginRemoveRows(parent, row, row + count - 1)
        for item in item_list[row:row + count]:
            setattr(item, self.parent_attr, None)
        item_list[row:row + count] = []
        if not isinstance(item_list, ObservableListProxy):
            self.endRemoveRows()
        # Keep a dummy row
        if 'append' in self.options and len(item_list) == 0:
            self.beginInsertRows(parent, 0, 0)
            self.endInsertRows()
        return True

    def observe(self, sender, event_type, list_index, attrs):
        # TODO: If tree works ok, unify

        # Please note that event attributes are passed as
        # arguments for legibility (semantics for attributes
        # varies depending each event) but sender
        # and list_index are directly available by scope
        def before_setitem(attrs):
            i, inserting = attrs
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            removing = stop - start
            for i in range(start, stop):
                try:
                    sender[i].remove_callback(self.observe_item)
                except AttributeError:  # Item not observable
                    pass
            # Insert/remove the difference of lines
            if removing > inserting:
                self.beginRemoveRows(list_index, start,
                    start + removing - inserting - 1)
            else:
                self.beginInsertRows(list_index, start,
                    start + inserting - removing - 1)

        def setitem(i):
            i, inserting = attrs
            start, removing = ((i, 1) if type(i) == int
                else (i.start, i.stop - i.start))
            stop = start + inserting
            for i in range(start, stop):
                try:
                    row_index = self.index(i, 0, list_index)
                    sender[i].add_callback(self.observe_item,
                        QtCore.QModelIndex(row_index))
                except AttributeError:  # Item not observable
                    pass
            # Update observer_data after the slice
            for i, row in enumerate(sender[stop:]):
                try:
                    row_index = self.index(stop + i, 0, list_index)
                    row.set_callback_data(self.observe_item, row_index)
                except AttributeError:  # Item not observable
                    pass

            if removing > inserting:
                self.endRemoveRows()
            else:
                self.endInsertRows()
                self.dataChanged.emit(self.index(stop, 0, list_index),
                    self.index(start + inserting - 1,
                    len(self._properties) - 1), list_index)

            if 'append' in self.options and len(sender) == 0:
                self._insert_placeholder(list_index)

        def before_delitem(i):
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            for i in range(start, stop):
                try:
                    sender[i].remove_callback(self.observe_item)
                except AttributeError:  # Item not observable
                    pass
            self.beginRemoveRows(list_index, start, stop - 1)

        def delitem(i):
            start = i if type(i) == int else i.start
            # Update observer_data starting in the slice (as elements shifted)
            for i, row in enumerate(sender[start:], start):
                try:
                    row_index = self.index(i, 0, list_index)
                    row.set_callback_data(self.observe_item, row_index)
                except AttributeError:  # Item is not observable
                    pass
            self.endRemoveRows()
            if 'append' in self.options and len(sender) == 0:
                self._insert_placeholder(list_index)

        def before_insert(i):
            self.beginInsertRows(list_index, i, i)

        def insert(i):
            try:
                row_index = self.index(i, 0, list_index)
                sender[i].add_callback(self.observe_item,
                    QtCore.QModelIndex(row_index))
            except AttributeError:  # Item not observable
                pass
            for j, row in enumerate(sender[i + 1:], i + 1):
                try:
                    row_index = self.index(j, 0, list_index)
                    row.set_callback_data(self.observe_item, row_index)
                except AttributeError:  # Item not observable
                    pass
            self.endInsertRows()

        def before_append(dummy):
            if not('append' in self.options and len(sender) == 0):
                self.beginInsertRows(list_index, len(sender),
                    len(sender))

        def append(dummy):
            try:
                row_index = self.index(len(sender) - 1, 0, list_index)
                sender[-1].add_callback(self.observe_item, row_index)
            except AttributeError:  # Item not observable
                pass
            # The view must reflect the append if there is no placeholder row
            if not('append' in self.options and len(sender) == 1):
                self.endInsertRows()

        def before_extend(n):
            if 'append' in self.options and len(sender) == 0:
                self._remove_placeholder(list_index)
            self.beginInsertRows(list_index, len(sender),
                len(sender) + attrs - 1)

        def extend(n):
            stop = len(sender)
            start = stop - n
            for i in range(start, stop):
                try:
                    row_index = self.index(i, 0, list_index)
                    sender[i].add_callback(self.observe_item,
                        QtCore.QModelIndex(row_index))
                except AttributeError:  # Item not observable
                    pass
            self.endInsertRows()

        # Call the function matching event_type
        locals()[event_type](attrs)

    def observe_item(self, sender, event_type, item_index, attrs):

        if event_type != "update":
            return

        for updated_prop in attrs:
            lu = len(updated_prop)
            for i, prop in enumerate(self._properties):
                lp = len(prop)
                if lu > lp:
                    continue
                if updated_prop == prop[0:lu] and (lp == lu or prop[lu] == '.'):
                    #print "dataChanged", attrs[0], item_indexlist_index, i
                    index = self.index(item_index.row(), i, item_index.parent())
                    self.dataChanged.emit(index, index)
