#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import sqlite3

from fuse import FUSE, FuseOSError, Operations
from stat import *
from os.path import abspath, join
import thread

class CommandHandler:

    def __init__(self, db):
        self.db = db
        self.db_conn = db.conn

    def process(self, inp_arr, db):
        command = inp_arr[0]
        if command == "tag":
            file_name = abspath(join(os.getcwd(), inp_arr[1]))
            tag_name = inp_arr[2]

            if not self.FileExists(file_name):
                print "File does not exist"
                return

            files = self.getDirectoryFiles(file_name)
            for file in files:
                inode = self.getInode(file)
                self.storeTagInDB(file, inode, tag_name)

        elif command == "exit":
            sys.exit()

        elif command == "lstag":
            if len(inp_arr) == 1:
                # Display all files in current directory having tags
                dir_path = os.getcwd()
            elif len(inp_arr) == 2:
                dir_path = inp_arr[1]
            cursor = self.db_conn.execute("SELECT FILE_NAME, inode, tag from TAGS where FILE_NAME like ?", (dir_path+'%',))
            for row in cursor:
                print "File = ", row[0]
                #print "Inode = ", row[1]
                print "tag = ", row[2], "\n"

        elif command == "lscmd":
            print "use lstag to see all tagged files in PWD"
            print "use tag <filename> <tagname> to tag a file"
            print "use exit to exit the program"

        else:
            print "Command not found, use lscmd to see list of available commands"


    def getDirectoryFiles(self, path):
        '''recursively descend the directory tree rooted at path,
        return list of files under path'''

        if S_ISREG(os.stat(path)[ST_MODE]):
            print path + " is regular file"
            return [path]

        files = []

        for sub_path in os.listdir(path):
            pathname = os.path.join(path, sub_path)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
                # It's a directory, recurse into it
                print path + " is directory file"
                files += getDirectoryFiles(pathname)
            elif S_ISREG(mode):
                print path + " is regular file"
                # It's a file, call the callback function
                files.append(pathname)
        return files



    def FileExists(self, file_name):
        if os.path.exists(file_name): 
            return True
        else:
            return False

    def getInode(self, file_path):
        stat = os.stat(file_path);
        return stat[ST_INO]

    def storeTagInDB(self, file_name, inode, tag_name):
        params = (file_name, inode, tag_name)
        self.db_conn.execute("INSERT INTO TAGS (FILE_NAME, INODE, TAG) \
            VALUES (?, ?, ? )", params);
        self.db_conn.commit()


def main(db_path):
    db_conn = sqlite3.connect(db_path);
    chandler = CommandHandler(db)
    print "use lscmd command to view all commands and their usage"
    while(True):
        inp = raw_input('tagfs#: ')
        inp_arr = inp.strip().split(" ")
        chandler.process(inp_arr, db)

if __name__ == '__main__':
    main(sys.argv[1])
