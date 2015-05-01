import tinydictdb as tddb
import time
import os
from copy import deepcopy
import random
import string
import sqlite3
import pickle
import json


def createLoad(num):
    data = []
    for num in range(0, num):
        obj = {"id": num,
               "name": randStr(32),
               "type": "text",
               "tags": [randStr(10), randStr(5)],
               "date": "2015-01-12 16:03:44"}
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
                for d in [True, False]:
                    types.append((r, w, e, d))
    return types


def doTest(i, rm, wm, enc, d, en):
    entry = {"id": i, "rMode": rm, 'wMode': wm, 'encoding': enc, 'dCopy': d}
    path = '/tmp/dbdbdb.json'

    print("creating")
    t1 = time.time()
    o = tddb.TinyDictDb(dbPath=path, rMode=rm, wMode=wm, encoding=enc, dCopy=d)
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

    for k in entry.keys():
        if type(entry[k]) == float:
            entry[k] = '{0:f}'.format(entry[k])

    return entry


def tester(num):
    load = createLoad(num)
    types = createTypes()
    result = []
    for itoo, it in enumerate(types):
        thisLoad = deepcopy(load)
        print("starting iteration "+str(it))
        result.append(doTest(itoo, it[0], it[1], it[2], it[3], thisLoad))
    return result


def testSqlite(lo):
    conn = sqlite3.connect('/tmp/dbdbdb.json')
    c = conn.cursor()
    c.execute('''CREATE TABLE entries (id integer, name text, type text, tags blob, date text)''')
    for i in lo:
        t = (i["id"], i["name"], i["type"], pickle.dumps(i['tags']), i["date"])
        c.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)", t)
        conn.commit()
    conn.close()


def testJson(lo):
    # d = tddb.TinyDictDb(dbPath='/tmp/dbdbdb1.json', rMode='fileMem', wMode="append")
    # for i in lo:
        # d.addEntries(i)
    # d = tddb.TinyDictDb(rMode='mem', wMode="mem")
    # d.addEntries(lo)
    with open('/tmp/dbdbdb1.json', 'w') as f:
        json.dump(lo, f)


def testTddb(lo):
    d = tddb.TinyDictDb(dbPath='/tmp/dbdbdb2.json', rMode='fileMem', wMode="append")
    for i in lo:
        d.addEntries(i)
    # d.addEntries(lo)


def vs(num):
    loa = createLoad(num)
    try:
        os.remove('/tmp/dbdbdb.json')
    except:
        pass

    t1 = time.time()
    testSqlite(loa)
    t2 = time.time()
    ttot = t2 - t1
    print(ttot)

    try:
        os.remove('/tmp/dbdbdb1.json')
    except:
        pass
    t1 = time.time()
    testJson(loa)
    t2 = time.time()
    ttot = t2 - t1
    print(ttot)

    try:
        os.remove('/tmp/dbdbdb2.json')
    except:
        pass
    t1 = time.time()
    testTddb(loa)
    t2 = time.time()
    ttot = t2 - t1
    print(ttot)
