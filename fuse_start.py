#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import errno
import sqlite3

from collections import defaultdict
from pprint import pprint

from hachoir_metadata import metadata
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from fuse import FUSE, FuseOSError, Operations
from stat import *
from os.path import abspath, join
import thread
import ntpath


class Database:

    def __init__(self):
        self.conn = None

    def initialize(self):
        with sqlite3.connect('testDB.db') as self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT SQLITE_VERSION()')
            data = cursor.fetchone()
            print 'SQLite version: ', data

            self.createTables()

    def createTables(self):

        self.conn.execute('''CREATE TABLE IF NOT EXISTS TAGS
            ( FILE_NAME           TEXT    NOT NULL,
                INODE            INT     NOT NULL,
                TAG            TEXT     NOT NULL);''')

class MiscFunctions:

    @classmethod
    def getDirectoryFiles(cls, path):
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

    @classmethod
    def FileExists(cls, file_name):
        if os.path.exists(file_name): 
            return True
        else:
            return False

    @classmethod
    def storeTagInDB(cls, file_name, inode, tag_name):
        params = (file_name, inode, tag_name)
        db_conn.execute("INSERT INTO TAGS (FILE_NAME, INODE, TAG) \
            VALUES (?, ?, ? )", params);
        db_conn.commit()

    @classmethod
    def getInode(cls, file_path):
        stat = os.stat(file_path);
        return stat[ST_INO]



class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)
	#print(path)
        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        path = self._full_path(path)[:-4]
        if ntpath.basename(path) == ".tag":
            for line in buf:
                contents  = line.split(" ")
                if len(contents) == 1:
                    tag_name = contents[0]
                    if os.path.exists(path):
                        files = MiscFunctions.getDirectoryFiles(path)
                        for file in files:
                            print "file is %s" % file
                            filename = path[:-4] + file
                            if MiscFunctions.FileExists(filename):
                                inode = MiscFunctions.getInode(filename)
                                MiscFunctions.storeTagInDB(filename, inode, tag_name)
                    else:
                        print "Path does not exist"
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
    	#print(path)
        return os.fsync(fh)

    def release(self, path, fh):
    	#print(os.path.splitext(path)[1])
    	#print(os.path.splitext(path))
    	if(os.path.splitext(path)[1] == '.mp3'):
    		full_path = self._full_path(path)
    		#filename = path
    		#filename, realname = unicodeFilename(filename), filename
    		parser = createParser(full_path)

    		metalist = metadata.extractMetadata(parser).exportPlaintext()
    		
    		for item in metalist:
    			print(item)

    	return os.close(fh)

    def fsync(self, path, fdatasync, fh):
    	return self.flush(path,fh)



def main(mountpoint, root):
    global db_conn
    global mnt_pnt
    mnt_pnt = mountpoint
    db = Database()
    db_conn = db.conn
    db.initialize()
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
