from copy import deepcopy


class PrettyPrinter:
    def __init__(self, providedEntries, **kwargs):
        self.border = kwargs.get('border', True)
        self.header = kwargs.get('header', True)
        self.vDelim = kwargs.get('vDelim', '|')
        self.hDelim = kwargs.get('hDelim', '-')
        self.xDelim = kwargs.get('xDelim', '+')
        self.padding = kwargs.get('padding', True)
        self.truncate = kwargs.get('truncate')
        self.sort = kwargs.get('sort')
        self.reverse = kwargs.get('reverse', False)
        self.numbered = kwargs.get('numbered', False)
        self.cleanupFct = kwargs.get('cleanupFct')
        self.fields = kwargs.get('fields')
        self.entries = providedEntries
        self.generate()

    def generate(self):
        self.__entries = deepcopy(self.entries)
        if self.sort is not None:
            try:
                self.__entries = sorted(self.__entries,
                                        key=lambda k: k[self.sort])
            except (KeyError, TypeError):
                self.__entries.sort(key=lambda k: str(k.get(self.sort, "")))
        if self.reverse is True:
            self.__entries.reverse()
        self.__fields = self.__generateFieldsAndHeader(deepcopy(self.fields))
        if self.numbered is True:
            for i, entry in enumerate(self.__entries):
                if self.header is False:
                    lineNumber = i + 1
                else:
                    lineNumber = i
                self.__entries[i]['prettyPrinterIndex'] = lineNumber
            self.__fields = ['prettyPrinterIndex'] + self.__fields
        self.__cleanup()
        self.__generateColumns()
        self.lines = self.__genLines()

    def __generateFieldsAndHeader(self, fields):
        header = {}
        if fields is None:
            fields = list(set([i for sublist in self.__entries
                               for i in sublist.keys()]))
            fields.sort()
            for field in fields:
                header[field] = field
        else:
            if not isinstance(fields, list):
                raise TypeError("Expected a list of: str or tuples of str")
            for i, field in enumerate(fields):
                if isinstance(field, str):
                    header[field] = field
                elif isinstance(field, tuple):
                    header[field[0]] = field[1]
                    fields[i] = field[0]
                else:
                    raise TypeError("Expected a list of: str or tuples of str")
        if self.header is True:
            self.__entries.insert(0, header)
        return fields

    def __cleanup(self):
        for entry in self.__entries:
            for field in self.__fields:
                entry[field] = entry.get(field)
                if callable(self.cleanupFct):
                    entry[field] = self.cleanupFct(entry[field])
                entry[field] = str(entry[field])
                if isinstance(self.truncate, int) and self.truncate > 0:
                    entry[field] = entry[field][:self.truncate]
                elif isinstance(self.truncate, dict):
                    limit = self.truncate.get(field)
                    if limit is not None:
                        entry[field] = entry[field][:limit]

    def __generateColumns(self):
        self.__columns = []
        for field in self.__fields:
            lenght = [len(i[field])for i in self.__entries]
            lenght.sort()
            self.__columns.append((field, lenght.pop()))

    def __genLines(self):
        lines = []
        if self.padding is False:
            for e in self.__entries:
                line = ""
                for (field, s) in self.__columns:
                    line += e[field] + self.vDelim
                lines.append(line[:-1])
            return lines
        if self.border is True:
            delimLine = self.xDelim + self.hDelim
            for (field, size) in self.__columns:
                for i in range(0, size):
                    delimLine += self.hDelim
                delimLine += self.hDelim + self.xDelim + self.hDelim
            delimLine = delimLine[:-1]
            lines.append(delimLine)
        for lineNumber, entry in enumerate(self.__entries):
            if self.border is True:
                line = self.vDelim + " "
            else:
                line = ""
            for (field, size) in self.__columns:
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
        if self.__fields == []:
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
