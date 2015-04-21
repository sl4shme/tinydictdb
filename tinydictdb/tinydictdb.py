from json import load, dump
from os import path
from copy import deepcopy
try:
    from yaml import safe_load as yamlLoad, dump as yamlDump
except ImportError:
    pass

# TODO : Add unsafe which does not re read the file
# TODO : Append to file if write


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
                result = [item for item in result if
                          toSearch[searchField] in item.get(searchField, "")]
            if type(toSearch[searchField]) in [int, float]:
                result = [item for item in result if
                          toSearch[searchField] == item.get(searchField)]
            if type(toSearch[searchField]) == list:
                result = [item for item in result if
                          set(toSearch[searchField]).issubset(
                              item.get(searchField, []))]
            if callable(toSearch[searchField]):
                result = [item for item in result if
                          toSearch[searchField](item.get(searchField))]
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
