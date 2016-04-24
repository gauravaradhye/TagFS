import sqlite3
import json
class Database:
    def __init__(self):
        self.conn = None
        with open('/home/aniket/bin/TBFS/config.json') as config_file:
            self.config = json.load(config_file)

    def initialize(self):
        print self.config
        with sqlite3.connect(self.config["path"]+"/TBFS/tags.db") as self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SQLITE_VERSION()')
            data = cursor.fetchone()
            print 'SQLite version: ', data
            self.createTables()
        return self.conn

    def createTables(self):

        self.conn.execute('''CREATE TABLE IF NOT EXISTS FILES
                            (   
                                PATH TEXT,
                                TAGID INTEGER,
                                FOREIGN KEY(TAGID) REFERENCES TAGS(ID),
                                PRIMARY KEY(TAGID, PATH)

                            );''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS TAGS 
                            (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                NAME TEXT UNIQUE

                            );''');

        self.conn.execute('''CREATE TABLE IF NOT EXISTS TAGREL
                            (   
                                SRC_TAGID INTEGER,
                                DEST_TAGID INTEGER,
                                FOREIGN KEY(SRC_TAGID) REFERENCES TAGS(ID),
                                FOREIGN KEY(DEST_TAGID) REFERENCES TAGS(ID),
                                PRIMARY KEY(SRC_TAGID, DEST_TAGID)

                            );''')
        
