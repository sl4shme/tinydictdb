from json import load, dump, dumps
from os import path, SEEK_END
from copy import deepcopy
try:
    from yaml import safe_load as yamlLoad, dump as yamlDump
except ImportError:
    pass

# TODO : Add unsafe which does not re read the file
# TODO : Append to file if write
# TODO : Add readMode ; full memory, half memory, file
# TODO : Add writeMode ; full memory, append, file
# TODO : StrictSearch ?


class TinyDictDb:
    def __init__(self, **kwargs):
        enc = kwargs.get('encoding', 'json')
        if enc in ['json', 'yaml']:
            self.encoding = enc
        else:
            raise ValueError("Encoding must be json or yaml.")
        if self.encoding == 'yaml':
            try:
                self.load, self.dump = yamlLoad, yamlDump
            except NameError:
                raise ImportError("You selected yaml, but PyYaml does not "
                                  "seems to be not installed.")
        else:
            self.load, self.dump = load, dump

        # manage what should get here by default
        self.path = kwargs.get('dbPath')
        self.rMode = kwargs.get('rMode')
        self.wMode = kwargs.get('wMode')

        if self.path is not None:
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
                    self.__datas = self.load(f)
                except:
                    raise ValueError("Datas contained in {} are not "
                                     "valid {}.".format(self.path,
                                                        self.encoding))

    def __writeDb(self):
        if self.wMode in ['file', 'append']:
            with open(self.path, 'w') as f:
                self.dump(self.__datas, f)

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
            self.appendEntriesToFile(entries)

    def appendEntriesToFile(self, entries):
        if self.encoding == 'yaml':
            with open(self.path, 'a') as f:
                self.dump(entries, f)
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

    def isPresent(self, entry):
        self.__readDb()
        return self.__datas.count(entry)

    def findEntries(self, **toSearch):
        self.__readDb()
        result = self.__datas
        for searchField in toSearch.keys():
            if type(toSearch[searchField]) == str:
                result = [item for item in result if
                          toSearch[searchField] in item.get(searchField, "")]
            elif type(toSearch[searchField]) in [int, float, bool, list]:
                result = [item for item in result if
                          toSearch[searchField] == item.get(searchField)]
            elif type(toSearch[searchField]) == set:
                result = [item for item in result if
                          toSearch[searchField].issubset(
                              item.get(searchField, []))]
            elif callable(toSearch[searchField]):
                result = [item for item in result if
                          toSearch[searchField](item.get(searchField))]
        if self.rMode in ['fileMem', 'mem']:
            return(deepcopy(result))
        else:
            return(result)


class prettyPrinter:
    def __init__(self, providedEntries, fields=None, header="full"):
        self.genHeader = header
        self.entries = deepcopy(providedEntries)
        self.fields = self.generateFieldsAndHeader(deepcopy(fields))
        self.entries = self.cleanup(self.entries, self.fields)
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
        if self.genHeader in ['full', 'head']:
            self.entries.insert(0, header)
        return fields

    def cleanup(self, entries, fields):
        for entry in entries:
            for field in fields:
                entry[field] = str(entry.get(field, None))
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
        delimLine = "+-"
        for (field, size) in self.columns:
            for i in range(0, size):
                delimLine += '-'
            delimLine += '-+-'
        delimLine = delimLine[:-1]

        if self.genHeader in ['full', 'lines']:
            lines.append(delimLine)
        for lineNumber, entry in enumerate(self.entries):
            line = "| "
            for (field, size) in self.columns:
                line += entry[field]
                for i in range(0, (size - len(entry[field]))):
                    line += " "
                line += " | "
            lines.append(line.strip())
            if (lineNumber == 0) and (self.genHeader == 'full'):
                lines.append(delimLine)
        if self.genHeader in ['full', 'lines']:
            lines.append(delimLine)
        if self.fields == []:
            lines = []
        return lines

    def __str__(self):
        for line in self.lines:
            print(line)
        return ""

    def getOneString(self):
        ret = ""
        for line in self.lines:
            ret += line
            ret += "\n"
        return ret
