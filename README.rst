**TinyDictDb**
==============

What is it ?
------------

TinyDictDb is a very small flat file (JSON or YAML) database meant to store dictionaries.

**Exemple of the datas stored:**

.. code:: json

    [
    {"id":4242,"name":"foo","tags":["aa","bb"]},
    {"id":4243,"name":"bar","tags":["bb","cc"]},
    {"id":4244,"name":"fobar","tags":["dd"]}
    ]

.. code:: yaml

   - id: 4242
     name: foo
     tags: [aa, bb]
   - id: 4243
     name: bar
     tags: [bb, cc]
   - id: 4244
     name: fobar
     tags: [dd]]


It also comes with a fully configurable `PrettyPrinter`_. in order to display this kind of data:

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    +------+-------+--------------+


Table of Content
----------------

- `TinyDictDb`_

 - `Installation`_
 - Usage
 - Methods

  - `Create or open a database (a JSON/YAML file):`_
  - `Add entry/entries:`_
  - `Retrieve/find entry / entries:`_
  - `Delete entry / entries:`_
  - `Count the number of occurences of an entry in the db:`_
  - `Edit entries:`_
  - `Sort database:`_
  - `Get informations about the db:`_

 - `Itialization parameters:`_

  - rMode
  - wMode
  - encoding
  - path
  - dCopy

- `PrettyPrinter`_


Installation
------------

    pip install tinydictdb

Note: If you want to use yaml (not recommended due to poor performances), you have to install PyYaml by yourself.

Usage
-----

.. code :: python

    from tinydictdb import TinyDictDb


Create or open a database (a JSON/YAML file):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code :: python

    db = TinyDictDb(path="/tmp/db.json")  # Json Backed
    db = TinyDictDb(path="/tmp/db.yaml", encoding='yaml')  # Yaml backed
    db = TinyDictDb()  # In memory

For more initialization parameters see: `Itialization parameters:`_.


Add entry/entries:
~~~~~~~~~~~~~~~~~~
.. code :: python

    addEntries(entries, index=None)

.. code :: python

    a = {"id":4242,"name":"foo"}
    b = [{"id":4242,"name":"foo"},{"id":4243,"name":"bar"}]
    db.addEntries(a)
    db.addEntries(b)

It is possible to add an entry at a specific index of the list using:

.. code :: python

    db.addEntries(a, 5)  # Will add the entry a as the 6th entry of the db


Retrieve/find entry / entries:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code :: python

    findEntries(**kwargs)

Retrieve the full db:

.. code :: python

    db.findEntries()

Retrieve only entries where key == value:

.. code :: python

    db.findEntries(name="foo")  # Will return all entries with entry["name"] == "foo".
    db.findEntries(tags=["aa", "bb"])  # Will return all entries with entry['tag'] == ["aa", "bb"].

Less strict (for string or list):

.. code :: python

    db.findEntries(name=("foo", False))  # Will return all entries with foo in entry["name"].
    db.findEntries(tags=(["aa"], False))  # Will return all entries with {"aa"}.issubset(entry['tag']).

Using a function:

.. code :: python

    db.findEntries(key=function)  # Will return all entries for which function(entry["key"]) return true.
    db.findEntries(id=(lambda x: True if x < 4243 else False))  # Will return all entry with id < 4243

You can cumulate as much as you want:

.. code :: python

    db.findEntries(id=1, name="plop", tag=(["aa", False]))


Delete entry / entries:
~~~~~~~~~~~~~~~~~~~~~~~
.. code :: python

    deleteEntries(entries, index=None)

.. code :: python

    a = {"id":4242,"name":"foo"}
    b = [{"id":4242,"name":"foo"},{"id":4243,"name":"bar"}]
    db.deleteEntries(a)
    db.deleteEntries(b)
    db.deleteEntries(db.findEntries(name="foo"))
    db.deleteEntries([], 0)  # Will delete the first entry of the db

It will return the number of deleted entries


Count the number of occurences of an entry in the db:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code :: python

    count(entry)

**count** will return the number of occurence of an entry in the db

.. code :: python

    a = {"id":4242,"name":"foo"}
    db.count(a)  # Will return the number of occurence of a in the db.


Edit entries:
~~~~~~~~~~~~~
.. code :: python

    findEntries(fct, entries=None)

**editEntries** will apply a function to each entry in the db.

.. code :: python

    def fct(in):
        in["id"] += 1
        return in

    db.editEntries(fct) # will increment the id’s of all the db.

As an optional parameter, you can pass a subset of entry it should use instead of the whole db.

.. code :: python

    db.editEntries(fct, db.findEntries(name="foo"))  # will increment the id’s of entries having foo as name.


Sort database:
~~~~~~~~~~~~~~
.. code :: python

    sort(field, reverse=False, strict=True)

**sort** will the database in function of the value associated with a key

.. code :: python

    db.sort("id")

You can also/aditionally reverse the db

.. code :: python

    db.sort("id", True)  # Will reverse sort in function of the id field of each entry
    db.sort(None, True)  # Will reverse the db

By default, you will get an error if one or more dictionnaries doesn't contain
the key you specifief or if the type of the value correponding to it is not
consistent throughout the db.

You can turn of this strict behavior with the third parameter (and everything
will be analized as strings)

.. code :: python

    db.sort("id", False, False)

Warning: With this last method the order will be like : [1, 11, 12, 2, 21, 3]


Get informations about the db:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code :: python

    print(db)

Will output:
    <TinyDictDb instance> containing 4 entries.


Itialization parameters:
~~~~~~~~~~~~~~~~~~~~~~~~

Available initialization patameters are:

**rMode**: How datas are read

Possible value:

- file: The backing file will be re-read before each action [default]
- mem: The content of the database is only read from the memory, this will always initialize as an empty database [default if no path specified]
- hybrid: The backing file is read once at the initialization and after that datas are read from memory

You should select 'file' if more than one process is going to acces the file (not a really good idea anyway because no locking ATM).


**wMode**: How datas are written

Possible value:

- file: Every time you modify the content of the database, the whole file is re-written. [default]
- append: Same thing as file, but on the specific case of adding entry, append to the file rather than re-writing the whole thing.
- mem: Nothing is written on disk everything on memory [default if no path specified]

Every combination of rMode and wMode are possible, some just make no sense.


**encoding**: Format of the file to read from / write to (if applicable)

Possible value:

- json
- yaml: **good to know: yaml performances are REALLY REALLY AWFUL**


**path**: Path of the file to read from / write to (if applicable)


**dCopy**: Default to True

Because of how python pass list and dictionnaries (ie: by reference), and to avoid damaging the internal database, if rMode is set to mem or hybrid, the datas are deepCopy-ed (This is a time consuming operation). If you know what you are doing or you are not going to modify the return data (for example just print them), you can turn that of and win a few extra milisec's.


Most sensitive choices:

.. code :: python

    db = TinyDictDb(path="/home/db.json")  # wMode='file', rMode='file' : Safest option, slowest also.
    db = TinyDictDb()  # Full in memory : Fastest : no dump of datas
    db = TinyDictDb(path="/home/db.json", rMode="hybrid", wMode="append")  # Good compromise

Good to know:

You can use a full memory database (wMode='mem', rMode='mem') and choose to dump manually the database to a file (if the path is specified) using the writeDb() method.


**PrettyPrinter**
=================

This class is meant to display the informations stored in TinyDictDb (or any
list of dictionnaries for that matter).

Table of Content
----------------

- `TinyDictDb`_
- `PrettyPrinter`_

 - Usage
 - `Parameters:`_

  - `header`_
  - `border`_
  - `vDelim, hDelim, xDelim`_
  - `padding`_
  - `fields`_
  - `sort`_
  - `reverse`_
  - `truncate`_
  - `cleanupFct`_

 - `Methods and attributes:`_


Usage
-----

.. code :: python

    import tinydictdb

    datas = [{"id":4242,"name":"foo","tags":["aa","bb"]},
             {"id":4243,"name":"bar","tags":["bb","cc"]},
             {"id":4244,"name":"fobar","tags":["dd"]}]

    p = PrettyPrinter(datas)
    print(p)

or shorter:

.. code :: python

    print(PrettyPrinter(db.findEntries()))

Will output:

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    +------+-------+--------------+


Parameters:
-----------

header
~~~~~~
True [Default]

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    +------+-------+--------------+

False

.. code::

    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    +------+-------+--------------+


border
~~~~~~
True [Default]

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    +------+-------+--------------+

False

.. code::

    id   | name  | tags
    4242 | foo   | ['aa', 'bb']
    4243 | bar   | ['bb', 'cc']
    4244 | fobar | ['dd']


vDelim, hDelim, xDelim
~~~~~~~~~~~~~~~~~~~~~~

Characters used for borders:

.. code :: python

    print(PrettyPrinter(datas, vDelim="/", hDelim="~", xDelim="*"))

Will output:

.. code::

    *~~~~~~*~~~~~~~*~~~~~~~~~~~~~~*
    / id   / name  / tags         /
    *~~~~~~*~~~~~~~*~~~~~~~~~~~~~~*
    / 4242 / foo   / ['aa', 'bb'] /
    / 4243 / bar   / ['bb', 'cc'] /
    / 4244 / fobar / ['dd']       /
    *~~~~~~*~~~~~~~*~~~~~~~~~~~~~~*


padding
~~~~~~~

Defaults to True

If set to False, will disable the padding (and disable borders as well). Usefull in combination of the vDelim parameter to produce CSV


.. code :: python

    print(PrettyPrinter(datas, vDelim=",", padding=False))

Will output:

.. code::

    id,name,tags
    4242,foo,['aa', 'bb']
    4243,bar,['bb', 'cc']
    4244,fobar,['dd']


fields
~~~~~~

You can choose to display only specific fields in a specific order:

.. code :: python

    print(PrettyPrinter(datas, fields=[ "tags","name"]))

Will output

.. code::

    +--------------+-------+
    | tags         | name  |
    +--------------+-------+
    | ['aa', 'bb'] | foo   |
    | ['bb', 'cc'] | bar   |
    | ['dd']       | fobar |
    +--------------+-------+

Instead of just the name of the field, you can pass a tuple with the name and how it should be displayed.

.. code :: python

    print(PrettyPrinter(datas, fields=[("name", "NAME"), "tags"]))

Will output

.. code::

    +-------+--------------+
    | NAME  | tags         |
    +-------+--------------+
    | foo   | ['aa', 'bb'] |
    | bar   | ['bb', 'cc'] |
    | fobar | ['dd']       |
    +-------+--------------+


sort
~~~~

Will sort the datas in function of the provided field

.. code :: python

    print(PrettyPrinter(datas, sort="name"))

Will output

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    | 4242 | foo   | ['aa', 'bb'] |
    +------+-------+--------------+

    
sort
~~~~

Will number the lines outputed

.. code :: python

    print(PrettyPrinter(datas, numbered=True))

Will output

.. code::

    +---+------+-------+--------------+
    | 0 | id   | name  | tags         |
    +---+------+-------+--------------+
    | 1 | 4243 | bar   | ['bb', 'cc'] |
    | 2 | 4244 | fobar | ['dd']       |
    | 3 | 4242 | foo   | ['aa', 'bb'] |
    +---+------+-------+--------------+


reverse
~~~~~~~

Will reverse the order in which datas are printed

.. code :: python

    print(PrettyPrinter(datas, reverse=True))

Will output

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4244 | fobar | ['dd']       |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4242 | foo   | ['aa', 'bb'] |
    +------+-------+--------------+


truncate
~~~~~~~~

Will truncate columns to specified length

.. code :: python

    print(PrettyPrinter(datas, truncate=4))

Will output

.. code::

    +------+------+------+
    | id   | name | tags |
    +------+------+------+
    | 4242 | foo  | ['aa |
    | 4243 | bar  | ['bb |
    | 4244 | foba | ['dd |
    +------+------+------+

You can provide a dictionnary in order to truncate only specific columns:

.. code :: python

    print(PrettyPrinter(datas, truncate={"name":4, "tags":10}))

Will output

.. code::

    +------+------+------------+
    | id   | name | tags       |
    +------+------+------------+
    | 4242 | foo  | ['aa', 'bb |
    | 4243 | bar  | ['bb', 'cc |
    | 4244 | foba | ['dd']     |
    +------+------+------------+


cleanupFct
~~~~~~~~~~

A function that will be passed the content of each cell to do some cleanup action.

For example to print lists in a more beautifull manner:

.. code :: python

    def clean(cell):
        if isinstance(cell, list):
            cell = " ; ".join(cell)
        return cell

    print(PrettyPrinter(datas, cleanupFct=clean))

Will output

.. code::

    +------+-------+---------+
    | id   | name  | tags    |
    +------+-------+---------+
    | 4242 | foo   | aa ; bb |
    | 4243 | bar   | bb ; cc |
    | 4244 | fobar | dd      |
    +------+-------+---------+


Methods and attributes:
----------------------

When it is instanciated, the PrettyPrinter class will generate the visual and store it in the form of a list of lines under the **lines** attribute.

.. code :: python

    print(p.lines)

    ['+------+-------+--------------+',
     '| id   | name  | tags         |',
     '+------+-------+--------------+',
     "| 4242 | foo   | ['aa', 'bb'] |",
     "| 4243 | bar   | ['bb', 'cc'] |",
     "| 4244 | fobar | ['dd']       |",
     '+------+-------+--------------+']

You can get what will be displayed (with \n escaping) using the **getOneString()** method. This is also bound to the special method **__str__()** to allow to use print(PrettyPrinter(datas))

.. code :: python

    p.getOneString()
    "+------+-------+--------------+\n| id   | name  | tags         |\n+------+-------+--------------+\n| 4242 | foo   | ['aa', 'bb'] |\n| 4243 | bar   | ['bb', 'cc'] |\n| 4244 | fobar | ['dd']       |\n+------+-------+--------------+\n"


Every parameters passed to the class is also stored as an attribute. If you want modify those ones, you have to call the **generate()** method afterwards to regenerate the lines.

.. code :: python

    p = PrettyPrinter(datas)
    p.header = False
    p.generate()
    print(p)

.. code::

    +------+-------+---------+
    | 4242 | foo   | aa ; bb |
    | 4243 | bar   | bb ; cc |
    | 4244 | fobar | dd      |
    +------+-------+---------+

Same thing goes for the datas printed (stored under the entries attribute):

.. code :: python

    p.entries.append({'id': 4245, 'name': 'plop', 'tags': []})
    p.generate()
    print(p)

.. code::

    +------+-------+--------------+
    | id   | name  | tags         |
    +------+-------+--------------+
    | 4242 | foo   | ['aa', 'bb'] |
    | 4243 | bar   | ['bb', 'cc'] |
    | 4244 | fobar | ['dd']       |
    | 4245 | plop  | []           |
    +------+-------+--------------+
