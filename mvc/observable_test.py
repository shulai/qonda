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

import unittest
import observable


class Observable(observable.Observable):

    def action1(self):
        self._notify('action1')

    def action2(self, data):
        self._notify('action2', data)


class Observer(object):
    def __init__(self):
        self.events = []

    def clearEvents(self):
        self.events = []

    def observe(self, sender, event_type, observer_data, event_data):
        self.events.append([sender, event_type, observer_data, event_data])


class ObservableObject(observable.ObservableObject):
    _notifiables = ('z',)

    def __init__(self):
        observable.ObservableObject.__init__(self)
        self.w = 0
        self.x = 0
        self.y = 0
        self.z = 0

    def set_x(self, x):
        self.x = x
        self.y = x * 2
        self._notify('update', ('x', 'y'))

    def set_y(self, y):
        self.y = y
        self.x = y / 2
        self._notify('update', ('x', 'y'))


class ObservableDataTestCase(unittest.TestCase):

    def test_add_remove_observers(self):
        """
            Test proper subscription and desuscription
        """
        observable = Observable()
        observer1 = Observer()
        observer2 = Observer()
        observer3 = Observer()

        observable.add_observer(observer1, "observe")
        observable.action1()
        self.assertEqual(len(observer1.events), 1,
            "Observer1 didn't observe an event? Event count: {0}, expected 1".
            format(len(observer1.events)))

        observable.add_observer(observer2, "observe")
        observable.action1()
        self.assertEqual(len(observer1.events), 2,
            "Observer1 didn't observe an event? Event count: {0}, expected 2".
            format(len(observer1.events)))
        self.assertEqual(len(observer2.events), 1,
            "Observer2 didn't observe an event? Event count: {0}, expected 1".
            format(len(observer2.events)))

        observable.add_observer(observer3, "observe")
        observable.remove_observer(observer1)
        observable.action1()
        self.assertEqual(len(observer1.events), 2,
            "Observer1 still observes events? Event count: {0}, expected 2".
            format(len(observer1.events)))
        self.assertEqual(len(observer2.events), 2,
            "Observer2 didn't observe an event? Event count: {0}, expected 2".
            format(len(observer2.events)))
        self.assertEqual(len(observer3.events), 1,
            "Observer3 didn't observe an event. Event count: {0}, expected 1".
            format(len(observer3.events)))

        observable.remove_observer(observer3)
        observable.action1()
        self.assertEqual(len(observer1.events), 2,
            "Observer1 still observes events? Event count: {0}, expected 2".
            format(len(observer1.events)))
        self.assertEqual(len(observer2.events), 3,
            "Observer2 didn't observe an event? Event count: {0}, expected 2".
            format(len(observer2.events)))
        self.assertEqual(len(observer3.events), 1,
            "Observer3 still observes events? Event count: {0}, expected 1".
            format(len(observer3.events)))

        observable.remove_observer(observer2)
        observable.action1()
        self.assertEqual(len(observer1.events), 2,
            "Observer1 still observes events? Event count: {0}, expected 2".
            format(len(observer1.events)))
        self.assertEqual(len(observer2.events), 3,
            "Observer2 still observes events? Event count: {0}, expected 2".
            format(len(observer2.events)))
        self.assertEqual(len(observer3.events), 1,
            "Observer3 still observes events? Event count: {0}, expected 1".
            format(len(observer3.events)))

    def test_nodata(self):
        """
            Test Observable when neither event or observer data are provided
        """
        observable = Observable()
        observer = Observer()
        observable.add_observer(observer, "observe")
        observable.action1()

        self.assertEqual(len(observer.events), 1,
            "Observer didn't observe an event. Event count: {0}".
            format(len(observer.events)))
        self.assertEqual(observer.events[0][0], observable,
            "Observer didn't receive the observable as event source")
        self.assertEqual(observer.events[0][1], 'action1',
            "Observer didn't receive the right event type")
        self.assertEqual(observer.events[0][2], None,
            "Observer should receive None as observer data. Received: {0}".
            format(observer.events[0][2]))
        self.assertEqual(observer.events[0][3], None,
            "Observer should receive None as event data. Received {0}".
            format(observer.events[0][3]))

    def test_observer_data(self):
        """
            Test Observable when no event data but observer data are provided
        """
        observable = Observable()
        observer = Observer()
        observable.add_observer(observer, "observe", "**Observer data**")
        observable.action1()

        self.assertEqual(len(observer.events), 1,
            "Observer didn't observe an event. Event count: {0}".
            format(len(observer.events)))
        self.assertEqual(observer.events[0][0], observable,
            "Observer didn't receive the observable as event source")
        self.assertEqual(observer.events[0][1], 'action1',
            "Observer didn't receive the right event type")
        self.assertEqual(observer.events[0][2], "**Observer data**",
            "Observer should receive the provided observer data "
            "'**Observer data**'. Received: {0}".format(observer.events[0][2]))
        self.assertEqual(observer.events[0][3], None,
            "Observer should receive None as event data. Received {0}".
            format(observer.events[0][3]))

    def test_event_data(self):
        """
            Test Observable when neither event or event data are provided
        """
        observable = Observable()
        observer = Observer()
        observable.add_observer(observer, "observe")
        observable.action2("**Event Data**")

        self.assertEqual(len(observer.events), 1,
            "Observer didn't observe an event. Event count: {0}".
            format(len(observer.events)))
        self.assertEqual(observer.events[0][0], observable,
            "Observer didn't receive the observable as event source")
        self.assertEqual(observer.events[0][1], 'action2',
            "Observer didn't receive the right event type")
        self.assertEqual(observer.events[0][2], None,
            "Observer should receive None as observer data. Received: {0}".
            format(observer.events[0][2]))
        self.assertEqual(observer.events[0][3], "**Event Data**",
            "Observer should receive 'Event Data' as event data. Received {0}".
            format(observer.events[0][3]))

    def test_observer_event_data(self):
        """
            Test Observable when both event and event data are provided
        """
        observable = Observable()
        observer = Observer()
        observable.add_observer(observer, "observe", "Sendme this back!")
        observable.action2("Interesting data")

        self.assertEqual(len(observer.events), 1,
            "Observer didn't observe an event. Event count: {0}".
            format(len(observer.events)))
        self.assertEqual(observer.events[0][0], observable,
            "Observer didn't receive the observable as event source")
        self.assertEqual(observer.events[0][1], 'action2',
            "Observer didn't receive the right event type")
        self.assertEqual(observer.events[0][2], "Sendme this back!",
            "Observer should receive 'Sendme this back!' as observer data. "
            "Received: {0}".format(observer.events[0][2]))
        self.assertEqual(observer.events[0][3], "Interesting data",
            "Observer should receive 'Interesting data' as event data. "
            "Received {0}".format(observer.events[0][3]))

    def test_get_set_observer_data(self):
        """
            Test getting and setting observer data
        """
        observable = Observable()
        observer = Observer()
        observable.add_observer(observer, "observe", "Send this back")
        # Get sure that works fine even if events happen
        observable.action2("**Event Data**")

        self.assertEqual(observable.get_observer_data(observer),
            "Send this back", "get_observer_data returned wrong data")

        observable.set_observer_data(observer, "New data")
        observable.action2("**Event Data**")
        self.assertEqual(observable.get_observer_data(observer), "New data",
            "set_observer_data failed")


class ObservableObjectTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = ObservableObject()
        self.observer = Observer()
        self.obj.add_observer(self.observer, "observe")

    def test_event_attribute(self):

        self.obj.z = "Attribute value"
        self.assertEqual(len(self.observer.events), 1,
            "Observer didn't observe the event")
        self.assertEqual(self.observer.events[0][0], self.obj,
            "Observer didn't receive the object as event source")
        self.assertEqual(self.observer.events[0][1], 'update',
            "Observer didn't receive the right event type")
        self.assertEqual(self.observer.events[0][3], ('z',),
            "Observer expected ('z',) as event data. Received {0}".
            format(self.observer.events[0][3]))
        self.obj.w = 42
        self.assertEqual(len(self.observer.events), 1,
            "Observer observe event for non-notifiable attribute")

    def test_event_method(self):

        self.obj.set_x(25)
        self.assertEqual(len(self.observer.events), 1,
            "Observer didn't observe the event")
        self.assertEqual(self.observer.events[0][0], self.obj,
            "Observer didn't receive the object as event source")
        self.assertEqual(self.observer.events[0][1], 'update',
            "Observer didn't receive the right event type")
        self.assertEqual(self.observer.events[0][3], ('x', 'y'),
            "Observer expected ('x', 'y') as event data. Received {0}".
            format(self.observer.events[0][3]))

        self.assertEqual(self.obj.x, 25, "Expected obj.x==25, not {0}".
            format(self.obj.x))
        self.assertEqual(self.obj.y, 50, "Expected obj.y==50, not {0}".
            format(self.obj.y))

#class ObservableObjectTestCase(unittest.TestCase):

#class ObservableProxyTestCase(unittest.TestCase):


if __name__ == '__main__':
    unittest.main()
