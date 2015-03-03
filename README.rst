**TinyDictDb**
==============

What is it ?
------------

TinyDictDb is a very small flat file (JSON or YAML) database meant to store dictionaries.

**Exemple:**

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


Installation
------------

    pip install tinydictdb

Note: If you want to use yaml file, you have to install PyYaml by yourself.

Usage
-----

    import tinydictdb as tddb

Create or open a database (a JSON/YAML file):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    db = tddb.TinyDictDb(“path”)

    db = tddb.TinyDictDb(“path”, 'yaml')

Add entry/entries :
~~~~~~~~~~~~~~~~~~~

    a = {“id”:4242,“name”:“foo”}

    b = [{“id”:4242,“name”:“foo”},{“id”:4243,“name”:“bar”}]

    db.addEntries(a)

    db.addEntries(b)

Find entry / entries:
~~~~~~~~~~~~~~~~~~~~~

Four kinds of research are implemented : 
    
    db.findEntries() # Will return the full db 

    db.findEntries(name=“foo”) # Will return all entries with “name” containing “foo”. 

    db.findEntries(tags=[“aa”]) # Will return all entries with tag “aa”.

    db.findEntries(key=function) # Will return all entries for which function(entry[“key”]) return true.


It’s even possible to use it inline with a lambda.

    db.findEntries(id=(lambda x: True if x < 4243 else False))

Delete entry / entries:
~~~~~~~~~~~~~~~~~~~~~~~

    a = {“id”:4242,“name”:“foo”}

    b = [{“id”:4242,“name”:“foo”},{“id”:4243,“name”:“bar”}]

    db.deleteEntries(a)

    db.deleteEntries(b)

    db.deleteEntries(db.findEntries(name=“foo”))

Verify if an entry / count the number of its occurences:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    a = {“id”:4242,“name”:“foo”}

    db.isPresent(a) #Will return the number of occurence of a in the db.

Edit entries:
~~~~~~~~~~~~~

editEntries will take a subset of entries and a function to apply to
them.

.. code :: python

   def fct(in):
       in["id"] += 1
       return in

db.editEntries(db.findEntries(), fct) # will increment the id’s of all the db.

Get informations about the db:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print(db)

    TinyDictDb instance stored in /tmp/plop, containing 4 entries in yaml format.


