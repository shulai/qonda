
from qonda.mvc.observable import ObservableListProxy


class QueryResult(ObservableListProxy):

    CHUNKSIZE = 20

    def __init__(self, query):
        super().__init__([])
        self.__query = query
        self.__len = query.count()

    def __len__(self):
        return self.__len

    def __getitem__(self, i):
        try:
            items = self._target[i]
        except IndexError:
            if type(i) == int:
                new_capacity = (i // self.CHUNKSIZE) + 1
            else:
                new_capacity = (i.stop - 1 // self.CHUNKSIZE) + 1
            additional = new_capacity - len(self._target)
            self._target.extend([None] * additional)
            items = None
        if items is None:
            if type(i) == int:
                first_index = (i // self.CHUNKSIZE)
            else:
                first_index = (i.start // self.CHUNKSIZE)
            new_items = self.__query[first_index:first_index + self.CHUNKSIZE]
            self._target[first_index:first_index + self.CHUNKSIZE] = new_items
            items = self._target[i]
        return items
