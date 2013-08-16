
from qonda.mvc.observable import ObservableListProxy


class QueryResult(ObservableListProxy):

    CHUNKSIZE = 20

    def __init__(self, query):
        super(ObservableListProxy, self).__init__([])
        self.__query = query
        self.__len = query.count()

    def __len__(self):
        return self.__len

    def __getitem__(self, i):
        try:
            if type(i) == slice:
                if i.stop - 1 > len(self._target):
                    raise IndexError
                items = self._target[i]
                if None in items:
                    items = None
            else:
                items = self._target[i]
        except IndexError:
            # Extend list to allocate the required index
            last_index = i if type(i) == int else i.stop - 1
            new_capacity = ((last_index // self.CHUNKSIZE) + 1) * self.CHUNKSIZE
            additional = new_capacity - len(self._target)
            self._target.extend([None] * additional)
            items = None
        if items is None:
            # Read required files
            if type(i) == int:
                first_index = (i // self.CHUNKSIZE) * self.CHUNKSIZE
                last_index = first_index + self.CHUNKSIZE
            else:
                first_index = (i.start // self.CHUNKSIZE) * self.CHUNKSIZE
                last_index = ((i.stop - 1) // self.CHUNKSIZE + 1
                    ) * self.CHUNKSIZE
            new_items = self.__query[first_index:last_index]
            self._target[first_index:last_index] = new_items
            items = self._target[i]
        return items
