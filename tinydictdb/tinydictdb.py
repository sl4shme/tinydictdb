from json import load, dump, dumps
from os import path, SEEK_END
from copy import deepcopy
from operator import itemgetter
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
                                 "differ from 'mem'.")
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
        return("TinyDictDb instance stored in {}, containing {} "
               "entries in {} format.".format(self.path,
                                              len(self.findEntries()),
                                              self.encoding))

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

    def addEntries(self, entries):
        if type(entries) == dict:
            entries = [entries]
        self.__readDb()
        classicWrite = False
        if len(self.__datas) <= 1:
            classicWrite = True
        for entry in entries:
            self.__datas.append(entry)
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
            t = t[1:]
            with open(self.path, 'rb+') as f:
                f.seek(-1, SEEK_END)
                f.truncate()
                f.seek(-1, SEEK_END)
                lastChar = f.read()
                if lastChar != b"[":
                    t = ", " + t
                f.write(bytes(t, 'UTF-8'))

    def deleteEntries(self, entries):
        if type(entries) == dict:
            entries = [entries]
        self.__readDb()
        count = 0
        for entry in entries:
            try:
                self.__datas.remove(entry)
                count += 1
            except ValueError:
                pass
        self.__writeDb()
        return count

    def editEntries(self, entries, fct):
        self.__readDb()
        for entry in entries:
            self.__datas.remove(entry)
            self.__datas.append(fct(entry))
        self.__writeDb()

    def count(self, entry):
        self.__readDb()
        return self.__datas.count(entry)

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


class PrettyPrinter:
    def __init__(self, providedEntries, **kwargs):
        self.border = kwargs.get('border', True)
        self.header = kwargs.get('header', True)
        self.vDelim = kwargs.get('delim', '|')
        self.hDelim = kwargs.get('hDelim', '-')
        self.xDelim = kwargs.get('xDelim', '+')
        self.padding = kwargs.get('padding', True)
        self.truncate = kwargs.get('truncate')
        self.entries = deepcopy(providedEntries)
        self.sortField = kwargs.get('sort', None)
        if self.sortField is not None:
            self.entries = self.sort(self.entries, self.sortField)
        self.fields = deepcopy(kwargs.get('fields', None))
        self.fields = self.generateFieldsAndHeader(self.fields)
        self.entries = self.cleanup(self.entries, self.fields, self.truncate)
        self.generateColumns()
        self.lines = self.genLines()

    def generateFieldsAndHeader(self, fields):
        header = {}
        if fields is None:
            fields = list(set([i for sublist in self.entries
                               for i in sublist.keys()]))
            fields.sort()
            for field in fields:
                header[field] = field
        else:
            if type(fields) != list:
                raise TypeError("Expected a list of: str or tuples of str")
            for i, field in enumerate(fields):
                if type(field) == str:
                    header[field] = field
                elif type(field) == tuple:
                    header[field[0]] = field[1]
                    fields[i] = field[0]
                else:
                    raise TypeError("Expected a list of: str or tuples of str")
        if self.header is True:
            self.entries.insert(0, header)
        return fields

    def sort(self, entries, key):
        newlist = sorted(entries, key=itemgetter(key))
        return newlist

    def cleanup(self, entries, fields, truncate):
        for entry in entries:
            for field in fields:
                entry[field] = str(entry.get(field, None))
                if isinstance(truncate, int) and truncate > 0:
                    entry[field] = entry[field][:truncate]
                elif isinstance(truncate, dict):
                    limit = truncate.get(field)
                    if limit is not None:
                        entry[field] = entry[field][:limit]
        return entries

    def generateColumns(self):
        self.columns = []
        for field in self.fields:
            lenght = [len(i[field])for i in self.entries]
            lenght.sort()
            lenght.reverse()
            self.columns.append((field, lenght[0]))

    def genLines(self):
        lines = []
        if self.padding is False:
            for e in self.entries:
                line = ""
                for (field, s) in self.columns:
                    line += e[field] + self.vDelim
                lines.append(line[:-1])
            return lines
        if self.border is True:
            delimLine = self.xDelim + self.hDelim
            for (field, size) in self.columns:
                for i in range(0, size):
                    delimLine += self.hDelim
                delimLine += self.hDelim + self.xDelim + self.hDelim
            delimLine = delimLine[:-1]
            lines.append(delimLine)
        for lineNumber, entry in enumerate(self.entries):
            if self.border is True:
                line = self.vDelim + " "
            else:
                line = ""
            for (field, size) in self.columns:
                line += entry[field]
                for i in range(0, (size - len(entry[field]))):
                    line += " "
                line += " " + self.vDelim + " "
            if self.border is False:
                line = line[:-3]
            lines.append(line.strip())
            if (self.border is True and lineNumber == 0 and
                    self.header is True):
                lines.append(delimLine)
        if self.border is True:
            lines.append(delimLine)
        if self.fields == []:
            lines = []
        return lines

    def __str__(self):
        return self.getOneString()

    def getOneString(self):
        ret = ""
        for line in self.lines:
            ret += line
            ret += "\n"
        return ret
