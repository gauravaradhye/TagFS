#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import sqlite3
import json
from fuse import FUSE, FuseOSError, Operations
from stat import *
from os.path import abspath, join
import thread

class CommandHandler:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def process(self, cwd, *inp_arr):
        command = inp_arr[0][0]
        tagdata = " ".join(inp_arr[0][1:])
        print command, tagdata
        if command == "tag":
            os.system("echo %s >> %s/.tag" % (tagdata, cwd))
        elif command == "exit":
            sys.exit()
        elif command == "lstag":
            os.system("echo %s >> %s/.ls" % (tagdata, cwd))
        elif command == "getfiles":
            os.system("echo %s >> %s/.gf" % (tagdata, cwd))
        elif command == "tagrel":
            os.system("echo %s >> %s/.graph" % (tagdata, cwd))
            
        elif command == "lscmd":
            print "use lstag to see all tagged files in PWD"
            print "use tag <filename> <tagname> to tag a file"
            print "use exit to exit the program" 
        elif command == "tagr":
            os.system("echo %s >> %s/.tagr" %(tagdata, cwd))
        else:
            print "Command not found, use lscmd to see list of available commands"


def main(cwd, *args):
    with open('/home/aniket/bin/TBFS/config.json') as config_file:  
        config = json.load(config_file)
    db_conn = sqlite3.connect(config["path"]+"/TBFS/tags.db");
    chandler = CommandHandler(db_conn)
    chandler.process(cwd, *args)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
