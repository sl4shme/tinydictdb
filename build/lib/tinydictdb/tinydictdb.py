from json import load, dump, dumps
from os import path, SEEK_END
from copy import deepcopy
try:
    from yaml import safe_load as yamlLoad, dump as yamlDump
except ImportError:
    pass


class TinyDictDb:
    def __init__(self, **kwargs):
        enc = kwargs.get('encoding', 'json')
        if enc in ['json', 'yaml']:
            self.encoding = enc
        else:
            raise ValueError("Encoding must be json or yaml.")
        if self.encoding == 'yaml':
            try:
                self.__load, self.__dump = yamlLoad, yamlDump
            except NameError:
                raise ImportError("You selected yaml, but PyYaml does not "
                                  "seems to be installed.")
        else:
            self.__load, self.__dump = load, dump

        self.dCopy = kwargs.get('dCopy', True)
        self.path = kwargs.get('path', None)
        if self.path is None:
            self.rMode = kwargs.get('rMode', 'mem')
            self.wMode = kwargs.get('wMode', 'mem')
            if self.rMode != 'mem' or self.wMode != 'mem':
                raise ValueError("Path is needed if rMode or wMode"
                                 " differ from 'mem'.")
        else:
            self.rMode = kwargs.get('rMode', 'file')
            self.wMode = kwargs.get('wMode', 'file')
            self.path = path.expanduser(self.path)
            self.path = path.normpath(self.path)
            if not path.isfile(self.path) or path.getsize(self.path) == 0:
                with open(self.path, 'w') as f:
                    f.write('[]')

        if self.rMode == 'mem':
            self.__datas = []
        else:
            self.__datas = None
            self.__readDb()

    def __str__(self):
        return("<TinyDictDb instance> containing {} "
               "entries".format(len(self.findEntries())))

    def __readDb(self):
        if (self.rMode == 'file') or (self.__datas is None):
            with open(self.path) as f:
                try:
                    self.__datas = self.__load(f)
                except:
                    raise ValueError("Datas contained in {} are not "
                                     "valid {}.".format(self.path,
                                                        self.encoding))

    def __writeDb(self, bypass=False):
        if self.wMode in ['file', 'append'] or bypass is True:
            with open(self.path, 'w') as f:
                self.__dump(self.__datas, f)

    def writeDb(self):
        if self.path is not None:
            self.__writeDb(True)
        else:
            raise ValueError("You need to set the path attribute of this DB"
                             " before writing it.")

    def addEntries(self, entries, index=None):
        if isinstance(entries, dict):
            entries = [entries]
        else:
            if set([type(i) for i in entries]) != {dict}:
                raise TypeError("The addEntries method only accepts a"
                                " dictionary or a list of dictionaries")
        self.__readDb()
        classicWrite = False
        if len(self.__datas) <= 1:
            classicWrite = True

        if index is not None:
            if isinstance(index, int):
                self.__datas[index:index] = entries
                classicWrite = True
            else:
                raise TypeError("index : expected int"
                                ", got {}".format(type(index)))
        else:
            self.__datas.extend(entries)

        if (self.wMode != 'append') or classicWrite is True:
            self.__writeDb()
        else:
            self.__appendEntriesToFile(entries)

    def __appendEntriesToFile(self, entries):
        if self.encoding == 'yaml':
            with open(self.path, 'a') as f:
                self.__dump(entries, f)
        else:
            t = dumps(entries)
            t = ", " + t[1:]
            with open(self.path, 'rb+') as f:
                f.seek(-1, SEEK_END)
                f.truncate()
                f.write(t.encode('UTF-8'))

    def deleteEntries(self, entries, index=None):
        if isinstance(entries, dict):
            entries = [entries]
        self.__readDb()
        count = 0
        if entries == [] and isinstance(index, int):
            try:
                self.__datas.pop(index)
                count = 1
            except IndexError:
                pass
        for entry in entries:
            try:
                self.__datas.remove(entry)
                count += 1
            except ValueError:
                pass
        self.__writeDb()
        return count

    def editEntries(self, fct, entries=None):
        self.__readDb()
        if entries is None:
            for entry in self.__datas:
                entry = fct(entry)
        else:
            for entry in entries:
                index = self.__datas.index(entry)
                self.__datas[index] = fct(self.__datas[index])
        self.__writeDb()

    def count(self, entry):
        self.__readDb()
        return self.__datas.count(entry)

    def sort(self, field, reverse=False, strict=True):
        self.__readDb()
        if field is not None:
            try:
                self.__datas = sorted(self.__datas, key=lambda k: k[field])
            except (KeyError, TypeError):
                if strict is True:
                    raise TypeError("Either at least one entry doesn't contain"
                                    " the sorting field either the type of the"
                                    " corresponding value is inconsistent.")
                else:
                    self.__datas.sort(key=lambda k: str(k.get(field, "")))
        if reverse is True:
            self.__datas.reverse()
        self.__writeDb()

    def findEntries(self, **kwargs):
        self.__readDb()
        result = self.__datas
        for field in kwargs.keys():
            if isinstance(kwargs[field], tuple) and kwargs[field][1] is False:
                if isinstance(kwargs[field][0], str):
                    result = [item for item in result if
                              kwargs[field][0] in item.get(field, "")]
                elif isinstance(kwargs[field][0], (list, set)):
                    result = [item for item in result if
                              set(kwargs[field][0]).issubset(
                                  item.get(field, []))]
            elif callable(kwargs[field]):
                result = [item for item in result if
                          kwargs[field](item.get(field))]
            else:
                result = [item for item in result if
                          kwargs[field] == item.get(field)]

        if (self.rMode in ['hybrid', 'mem']) and (self.dCopy is True):
            return(deepcopy(result))
        else:
            return(result)
