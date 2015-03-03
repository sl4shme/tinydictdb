from json import load, dump
from os import path
try:
    from yaml import safe_load as yamlLoad, dump as yamlDump
except ImportError:
    pass


class TinyDictDb:
    def __init__(self, dbPath, encoding='json', indent=None):
        self.__indent = indent
        if encoding in ['json', 'yaml']:
            self.__encoding = encoding
        else:
            raise ValueError("Encoding must be json or yaml.")
        if self.__encoding == 'yaml':
            try:
                self.load, self.dump = yamlLoad, yamlDump
            except NameError:
                raise ImportError("You selected yaml, but PyYaml does not "
                                  "seems to be not installed.")
        else:
            self.load, self.dump = load, dump
        self.path = path.expanduser(dbPath)
        self.path = path.normpath(self.path)
        if not path.isfile(self.path) or path.getsize(self.path) == 0:
            self.__writeDb([])
        self.__readDb()

    def __str__(self):
        return("TinyDictDb instance stored in {}, containing {} "
               "entries in {} format.".format(self.path,
                                              len(self.findEntries()),
                                              self.__encoding))

    def __readDb(self):
        with open(self.path) as f:
            try:
                datas = self.load(f)
            except:
                raise ValueError("Datas contained in {} are not "
                                 "valid {}.".format(self.path,
                                                    self.__encoding))
        return datas

    def __writeDb(self, newDatas):
        with open(self.path, 'w') as f:
            self.dump(newDatas, f, indent=self.__indent)

    def addEntries(self, entries):
        if type(entries) == dict:
            entries = [entries]
        newDatas = self.__readDb()
        for entry in entries:
            newDatas.append(entry)
        self.__writeDb(newDatas)

    def deleteEntries(self, entries):
        if type(entries) == dict:
            entries = [entries]
        newDatas = self.__readDb()
        count = 0
        for entry in entries:
            try:
                newDatas.remove(entry)
                count += 1
            except ValueError:
                raise ValueError("This entry was not present in the db: "
                                 "{}".format(entry))
        self.__writeDb(newDatas)
        return count

    def editEntries(self, entries, fct):
        newDatas = self.__readDb()
        for entry in entries:
            newDatas.remove(entry)
            newDatas.append(fct(entry))
        self.__writeDb(newDatas)

    def isPresent(self, entry):
        datas = self.__readDb()
        return datas.count(entry)

    def findEntries(self, **toSearch):
        result = self.__readDb()
        for searchField in toSearch.keys():
            if type(toSearch[searchField]) == str:
                result = [item for item in result if toSearch[searchField]
                          in item[searchField]]
            if type(toSearch[searchField]) == list:
                result = [item for item in result if set(
                          toSearch[searchField]).issubset(item[searchField])]
            if callable(toSearch[searchField]):
                result = [item for item in result if
                          toSearch[searchField](item[searchField])]
        return(result)
