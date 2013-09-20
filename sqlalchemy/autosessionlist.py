
from qonda.mvc.observable import ObservableListProxy


class AutoSessionList(ObservableListProxy):
    """AutoSessionList manages automatic adding of deleting of items
       into the associated SQLAlchemy session
    """
    def __init__(self, session, target=None, parent=None, target_class=None):
        super().__init__(target, parent, target_class)
        self.__session = session
        self.add_callback(self._observe)

    def _observe(self, sender, event_type, list_index, attrs):

        def before_setitem(i):

            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)

            for i in range(start, stop):
                self.__session.delete(self._target[i])

        def setitem(i):
            i, l = attrs
            start = i if type(i) == int else i.start
            stop = start + l
            for i in range(start, stop):
                self.__session.add(self._target[i])

        def before_delitem(i):
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            for i in range(start, stop):
                self.__session.delete(self._target[i])

        def insert(i):
            self.__session.add(self._target[i])

        def append(dummy):
            self.__session.add(self._target[-1])

        def extend(n):
            for i in range(-n, 0):
                self.__session.add(self._target[-1])

        # Llamo a la función asociada al event_type
        locals()[event_type](attrs)
