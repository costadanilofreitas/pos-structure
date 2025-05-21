from collections import defaultdict


class CustomStorage(object):

    """ class CustomStorage(object)
    Superclass of ProductionOrder and Item, which adds "custom storage" capability
    to instances of those classes (write_data, read_data and delete_data methods).
    """
    __slots__ = ['_storage', 'full_storage']

    def __init__(self):
        """contructor"""
        self._storage = defaultdict(dict)
        self.full_storage = defaultdict(dict)

    def clear_data(self):
        """ obj.clear_data()
        Clears all custom storage data.
        """
        self._storage = defaultdict(dict)
        self.full_storage = defaultdict(dict)

    def write_data(self, context, key, value, write_to_xml=True):
        """ obj.write_data(context, key, value)
        Writes some data to this instance.
        @param context: {str} - Some unique identification of who writing
                        the data (avoids namespace conflics with keys)
        @param key: {str} - A key for the value being written
        @param value: {object} - The value to store (this can be basically any "serializable" object, but
                      it's recommended to be a string).
                      Please note that objects are serialized using the "cPickle" module, and that its
                      "str" representation is also written as an XML attribute by OrderXml, unless the key
                      starts with an underscore ('_') character .
        """
        self.full_storage[context][key] = value
        if write_to_xml:
            self._storage[context][key] = value

    def read_data(self, context, key):
        """ obj.read_data(context, key) -> value
        Reads some previously written data.
        @param context: {str} - The context used to write the data
        @param key: {str or iterable} - The key used to write the data.
                    If a non-string iterable is passed, then this will
                    read all keys in that iterable at once, and return
                    the values as a list.
        @return the previously written value, or None if it does not exist.
                If a non-string iterable has been passed on "key" parameter, this
                will return a list of values in the same sequence of the keys.
        """
        dic = self.full_storage[context]
        if hasattr(key, "__iter__"):
            # "key" is actually a list of keys to retrieve at once
            return map(dic.get, key)
        # single key to retrieve
        return dic.get(key)

    def delete_data(self, context, key):
        """ obj.delete_data(context, key)
        Deletes some previously written data (if existent).
        @param context: {str} - The context used to write the data
        @param key: {str} - The key used to write the data.
        """
        try:
            del self._storage[context][key]
            del self.full_storage[context][key]
        except KeyError:
            pass

    def locate_data(self, key):
        """ obj.contains_data(key)
        Checks in which contexts the required key exists.
        @param key: {str} - A key for the value being checked
        """
        result = []
        for context in self._storage:
            if key in self._storage[context]:
                result.append(context)

        return result
