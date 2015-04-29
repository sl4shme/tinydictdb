import tinydictdb as tddb
import time
import os
from copy import deepcopy
import random
import string


def createLoad(num):
    data = []
    for num in range(0, num):
        obj = {"id": num,
               "name": randStr(32),
               "type": "text",
               "tags": [randStr(10), randStr(5)],
               "encrypt": "false",
               "c_date": "2015-01-12 16:03:44"}
        data.append(obj)
    return data


def randStr(length):
    r = ''.join([random.choice(string.ascii_letters + string.digits)
                for n in range(length)])
    return r


def createTypes():
    types = []
    for r in ['mem', 'fileMem', 'file']:
        for w in ['mem', 'append', 'file']:
            for e in ['json', 'yaml']:
                types.append((r, w, e))
    return types


def doTest(i, rm, wm, enc, en):
    entry = {"id": i, "rMode": rm, 'wMode': wm, 'encoding': enc}
    path = '/tmp/dbdbdb.json'

    print("creating")
    t1 = time.time()
    o = tddb.TinyDictDb(dbPath=path, rMode=rm, wMode=wm, encoding=enc)
    t2 = time.time()
    ttot = t2 - t1
    entry['creation'] = ttot

    print("aB")
    t1 = time.time()
    o.addEntries(en)
    t2 = time.time()
    ttot = t2 - t1
    entry['addBatch'] = ttot

    print("aO")
    t1 = time.time()
    for l in en:
        o.addEntries(l)
    t2 = time.time()
    ttot = t2 - t1
    entry['addEach'] = ttot

    print("gA")
    temp = None
    t1 = time.time()
    temp = o.findEntries()
    t2 = time.time()
    ttot = t2 - t1
    entry['getAll'] = ttot

    print("gAa")
    temp = None
    t1 = time.time()
    temp = o.findEntries(name="aa")
    t2 = time.time()
    ttot = t2 - t1
    entry['getAa'] = ttot

    hundred1 = o.findEntries(id=(lambda x: True if 100 < x < 200 else False))
    hundred2 = o.findEntries(id=(lambda x: True if 300 < x < 400 else False))

    print("rA")
    t1 = time.time()
    o.deleteEntries(hundred1)
    t2 = time.time()
    ttot = t2 - t1
    entry['delBatch'] = ttot

    print("rO")
    t1 = time.time()
    for l in hundred2:
        o.deleteEntries(l)
    t2 = time.time()
    ttot = t2 - t1
    entry['delEach'] = ttot

    try:
        os.remove(path)
    except:
        pass

    return entry


def tester(num):
    load = createLoad(num)
    types = createTypes()
    result = []
    for itoo, it in enumerate(types):
        thisLoad = deepcopy(load)
        print("starting iteration "+str(it))
        result.append(doTest(itoo, it[0], it[1], it[2], thisLoad))
    return result
