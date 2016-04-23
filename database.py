import sqlite3
import json
class Database:
    def __init__(self):
        self.conn = None
        with open('/usr/local/bin/TBFS/config.json') as config_file:
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
        self.conn.execute('''CREATE TABLE IF NOT EXISTS TAGS
                        ( FILE_NAME           TEXT    NOT NULL,
                          INODE            INT     NOT NULL,
                          TAG            TEXT     NOT NULL,
                          primary key (FILE_NAME, INODE, TAG));''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS TAGREL
                        ( SRC_TAG                 TEXT      NOT NULL,
                          DEST_TAG                 TEXT      NOT NULL,
                          primary key (SRC_TAG, DEST_TAG));''')