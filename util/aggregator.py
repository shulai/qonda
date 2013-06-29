# -*- coding: utf-8 *-*

from operator import attrgetter


class Aggregator(object):
    """
        source: list of objects
        target: object
        operations: dict:
            keys = attribute names or '*' for count
            values = tuples: operation, destination attribute
            Operations:
                'count', 'sum', 'avg', 'min', 'max'
    """
    def __init__(self, source, target, operations):
        super().__init__()
        self.__source = source
        self.__target = target
        self.__operations = operations
        source.add_observer(self, 'observe')
        self.__count = len(source)
        for attr, attr_ops in operations:
            if attr == '*':
                if attr_ops[0][0] == 'count':
                    setattr(target, attr_ops[0][1], self.__count)
                else:
                    raise ValueException('Invalid aggregate operator {0}(*)'.
                        format(attr_ops[0][0])

                continue

            for op, dest in attr_ops:
                agg_value = None
                for item in source:
                    if value is None:
                        agg_value = attrgetter(attr)(item)
                    elif op in ('sum', 'avg'):
                        agg_value += attrgetter(attr)(item)
                    elif op == 'min':
                        item_value = attrgetter(attr)(item)
                        if agg_value > item_value:
                            agg_value = item_value
                    elif op == 'max':
                        item_value = attrgetter(attr)(item)
                        if agg_value < item_value:
                            agg_value = item_value
                    else:
                        raise ValueException('Invalid aggregate operator '
                            '{0}({1})'.format(op, attr))
                if op == 'avg':
                    agg_value /= self.__count
                #
                setattr(target, dest, agg_value)
        for item in source:
        item.add_observer(self, 'observe_item')

    def observe(self, sender, event_type, list_row, attrs):
        # Todo: Handle sliced indexes
        if sender != self.__source:
            return

        def before_setitem(i):
            self._notify('before_update', 'total')
            for i in (range(i, i + 1) if type(i) == int
                    else range(*i.indices(len(sender)))):
                self.total -= getattr(sender[i], self.__attribute)
                sender[i].remove_observer(self)

        def setitem(i):
            try:
                sender[i].add_observer(self, "observe_item", i)
            except AttributeError:
                pass
            self.total += getattr(sender[i], self.__attribute)
            print('Total:', self.total)
            self._notify('update', 'total')

        def before_delitem(i):
            self._notify('before_update', 'total')
            sender[i].remove_observer(self)
            self.total -= getattr(sender[i], self.__attribute)

        def delitem(i):
            self._notify('update', 'total')

        def insert(i):
            self._notify('before_update', 'total')
            try:
                sender[i].add_observer(self, "observe_item", i)
            except AttributeError:
                pass
            self.total += getattr(sender[i], self.__attribute)
            self._notify('update', 'total')

        def append(dummy):
            self._notify('before_update', 'total')
            try:
                sender[-1].add_observer(self, "observe_item", len(sender) - 1)
            except AttributeError:
                pass
            self.total += getattr(sender[-1], self.__attribute)
            self._notify('update', 'total')

        def extend(n):
            self._notify('before_update', 'total')
            for i in range(-n):
                try:
                    sender[i].add_observer(self, "observe_item", i)
                except AttributeError:
                    pass
                self.total += getattr(sender[i], self.__attribute)
            self._notify('update', 'total')

        # Llamo a la función asociada al event_type
        try:
            locals()[event_type](attrs)
        except KeyError:
            pass

    def observe_item(self, sender, event_type, _, attr):
        if attr == self.__attribute:
            if event_type == 'before_update':
                self._notify('before_update', 'total')
                self.total -= getattr(self.__source, self.__attribute)
            elif event_type == 'update':
                self.total += getattr(self.__source, self.__attribute)
                self._notify('update', 'total')
                print('Total:', self.total)
