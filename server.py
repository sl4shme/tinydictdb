import web
import urlparse
import json
import tinydictdb as tddb


urls = (
     '/(.*)', 'index'
 )
DBS = {}


class index:
    def GET(self, url):
        dbname = url.split('/')[0]
        if DBS.get(dbname) is None:
            DBS[dbname] = tddb.TinyDictDb(path="{}.json".format(dbname))
        db = DBS[dbname]
        return json.dumps(db.findEntries())

    def POST(self, url):
        s = web.data()
        L = urlparse.parse_qsl(s)
        req = {}
        for k, v in L:
            req[k] = json.loads(v)

        action = url.split('/')[0]

        if action == 'add':
            dbname = url.split('/')[1]
            entries = req.get("datas")
            index = req.get("index")
            if DBS.get(dbname) is None:
                DBS[dbname] = tddb.TinyDictDb(path="{}.json".format(dbname))
            db = DBS[dbname]
            db.addEntries(entries, index)
            return "200"

        elif action == 'del':
            dbname = url.split('/')[1]
            entries = req.get("datas", [])
            index = req.get("index")
            if DBS.get(dbname) is None:
                DBS[dbname] = tddb.TinyDictDb(path="{}.json".format(dbname))
            db = DBS[dbname]
            db.deleteEntries(entries, index)
            return "200"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
