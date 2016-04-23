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

import shutil
import subprocess
import nltk
from collections import Counter
from string import punctuation
import docx2txt

from results import ResultsFS

from database import Database

class MiscFunctions:

    def __init__(self):
        with open('config.json') as config_file:
            self.config = json.load(config_file)

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
    def storeTagRelInDB(cls, tag1, tag2, db_conn):
        params = (tag1, tag2)
        try:
            db_conn.execute("INSERT INTO TAGREL (SRC_TAG, DEST_TAG) \
                             VALUES (?, ?, ? )", params);
        except sqlite3.IntegrityError:
            pass
        db_conn.commit()

    @classmethod
    def getTagID(cls, tag_name, db_conn):
        try:
            db_conn.execute("INSERT INTO TAGS (NAME) VALUES (?)", [tag_name])
        except Exception as e:
            print e
            pass
        tag_id = db_conn.execute("SELECT ID FROM TAGS WHERE NAME = ?", [tag_name]).fetchone()
        db_conn.commit()
        return tag_id

    @classmethod
    def storeTagInDB(cls, file_name, tag_name, db_conn):
        try:
            tag_id = MiscFunctions.getTagID(tag_name, db_conn);
            print tag_id
            params = (file_name, tag_id[0])
            db_conn.execute("INSERT INTO FILES (PATH, TAGID) \
                             VALUES (?,?)", params);
        except sqlite3.IntegrityError as e:
            print e
            pass
        db_conn.commit()
    
    
    @classmethod
    def getInode(cls, file_path):
        stat = os.stat(file_path);
        return stat[ST_INO]

    @classmethod
    def removeFromDB(cls, file_name, db_conn):
        print(file_name)
        db_conn.execute("DELETE FROM FILES WHERE PATH='%s'" % file_name)
        db_conn.commit()

    @classmethod
    def renameFile(cls, old_name, new_name, db_conn):
        db_conn.execute("UPDATE FILES SET PATH = ? WHERE PATH = ?", (new_name, old_name))


    @classmethod
    def getNFrequentWords(cls, nltkObj, n):
        stopwords = set(nltk.corpus.stopwords.words('english'))
        with_stp = Counter()
        without_stp  = Counter()
        for word in nltkObj:
            # update count off all words in the line that are in stopwords
            word = word.lower()
            if word not in stopwords:
            # update count off all words in the line that are not in stopwords
                without_stp.update([word])
        # return a list with top ten most common words from each
        return [y for y,_ in without_stp.most_common(n)]

    @classmethod
    def handleTextFiles(cls, file_path):
        filename, file_extension = os.path.splitext(file_path)
        if (file_extension == ".txt"):
            text = nltk.corpus.inaugural.words(file_path)
        elif (file_extension in [".docx", ".doc"]):
            text = str(docx2txt.process(file_path)).split()
        if file_extension in [".txt", ".doc", ".docx"]:
            freq_words = MiscFunctions.getNFrequentWords(text, 3)
            for word in freq_words:
                print word


class Passthrough(Operations):
    def __init__(self, root):
        self.db_conn = Database().initialize()
        self.root = root

    # Helpers
    # =======
    def add_tag(self, path, buf):
        orig_path = path
        print "buffer is %s" % buf
        for command in buf.splitlines():
            contents = command.split(" ")
            print "contents is %s" % contents
            if len(contents) == 1:
                if len(contents) == 1:
                    path = self._full_path(orig_path)[:-4]
                else:
                    path = orig_path

                tag_name = contents[0]
                print path, tag_name
                if os.path.exists(path):
                    files = MiscFunctions.getDirectoryFiles(path)
                    for filename in files:
                        if MiscFunctions.FileExists(filename):
                            MiscFunctions.storeTagInDB(filename, tag_name, self.db_conn)
                else:
                    print "Path does not exist"
            elif len(contents) == 2:
                file_name = contents[0]
                tag_name = contents[1]
                file_path = self._full_path(orig_path[:-4] + file_name)
                filename, file_extension = os.path.splitext(file_path)
                print file_extension
                if (file_extension == ".txt"):
                    print "inside"
                    freq_words = MiscFunctions.getNFrequentWords(nltk.corpus.inaugural.words(file_path), 3)
                    for word in freq_words:
                        print word

                if MiscFunctions.FileExists(file_path):
                    
                    MiscFunctions.storeTagInDB(file_path, tag_name, self.db_conn)
                else:
                    print "File does not exist"

    def ls_tags(self, path, buf):
        orig_path = path
        print "buffer is %s" % buf
        for command in buf.splitlines():
            contents = command.split(" ")
            print "contents is %s" % contents
            if contents[0].strip() == "":
                index = orig_path.index(".")
                path = self._full_path(orig_path)[:index]
            else:
                path = self._full_path(contents[0])
            #print path
            cursor = self.db_conn.execute("SELECT f.PATH, t.NAME FROM FILES f, TAGS t WHERE f.TAGID = t.ID AND f.PATH like ?", [path+'%'])
            result = dict()
            for row in cursor:
                if row[0] not in result:
                    result[row[0]] = []
                result[row[0]] += [row[1]]
            


            print result
            for item in result:
                print item
                print ",".join(result[item])

    def get_files(self, path, buf):
        orig_path = path
        print "buffer is %s" % buf
        for command in buf.splitlines():
            contents = command.split(" ")
            print "contents is %s" % contents  
            if contents[0].strip() == "":
                index = orig_path.index(".")
                path = self._full_path(orig_path)[:index]
            else:
                path = self._full_path(contents[0])
            print "Path is", path
            query = "SELECT f.PATH FROM FILES f, TAGS t WHERE f.TAGID = t.ID AND t.NAME IN (%s)" % ','.join('?'*len(contents))
            cursor = self.db_conn.execute(query, contents)
            result = set()
            for row in cursor:
                result.add(row[0])
            result = list(result)

            result_path = "/Users/gauravaradhye/Desktop/results/"

            for x in result:
                print x 
            print "Result is in", result_path
            

            for path in os.listdir(result_path):
                try:
                    print "REasdasda", os.path.join(result_path, path)
                    os.unlink(os.path.join(result_path, path))
                except:
                    pass

        # Generate hard links for the files in the results directory
            for filepath in result:
                partial = filepath.split('/')[-1]
                path = os.path.join(result_path, partial)
                os.symlink(filepath, path)

            #FUSE(ResultsFS('/Users/gauravaradhye/Desktop/results/', result), '/Users/gauravaradhye/Desktop/results-mp', foreground=True)
            
    def parseMetadata(self, path):
        if(os.path.splitext(path)[1][1:].lower() in ['mp3','bzip2','gzip','zip','tar','wav','midi','bmp','gif','jpeg','jpg','png','tiff','exe','wmv','mkv','mov']):
            full_path = self._full_path(path)
            parser = createParser(full_path)
            metalist = metadata.extractMetadata(parser).exportPlaintext()
            for item in metalist:
                x = item.split(':')[0] 
                if item.split(':')[0][2:].lower() in ["author","album","music genre"]:
                    print(item.split(':')[1][1:])
                    tag_name = item.split(':')[1][1:]
                    files = MiscFunctions.getDirectoryFiles(full_path)
                    for file in files:
                        #print file
                        #print full_path
                        
                        file_name = os.path.basename(path)
                        MiscFunctions.storeTagInDB(file, tag_name, self.db_conn)
                        
            print("Database storage successful")
        else:
            return

    def rel_tags(self, path, buf):
        orig_path = path
        print path
        print "buffer is %s" % buf
        for command in buf.splitlines():
            contents = command.strip().split(" ")
            print "contents is %s" % contents

            if len(contents)==1:
                print "Please add two tags"
            else:
                tag1 = contents[0] 
                tag2 = contents[1]
                if(tag1 is "" or tag2 is ""):
                    print ("One of the tags is empty")
                else:
                    query = "SELECT DISTINCT * FROM TAGS WHERE TAG = ?"
                    cursor = self.db_conn.execute(query, [tag1])
                    result = set()
                    for row in cursor:
                        print row

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
        print("Inside")
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
        #print path
        full_path = self._full_path(path)
        file_name = os.path.basename(path)
        print full_path, "&",file_name
        files = MiscFunctions.getDirectoryFiles(full_path)
        for file in files:
            print file
            if not (ntpath.basename(file) in ['.tag', '.ls', '.gf', '.graph']):
                MiscFunctions.removeFromDB(file, self.db_conn)
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        full_old_path = self._full_path(old)
        full_new_path = self._full_path(new)
        MiscFunctions.renameFile(full_old_path, full_new_path, self.db_conn)
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
        if ntpath.basename(path) == ".tag":
            self.add_tag(path, buf)
        elif ntpath.basename(path) == ".ls":
            self.ls_tags(path, buf)
        elif ntpath.basename(path) == ".gf":
            self.get_files(path, buf)
        elif ntpath.basename(path) == ".graph":
            self.rel_tags(path, buf)
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        if(os.path.splitext(path)[1][1:].lower() in ['mp3','bzip2','gzip','zip','tar','wav','midi','bmp','gif','jpeg','jpg','png','tiff','exe','wmv','mkv','mov']):
            full_path = self._full_path(path)
            parser = createParser(full_path)
            metalist = metadata.extractMetadata(parser).exportPlaintext()
            for item in metalist:
                x = item.split(':')[0] 
                if item.split(':')[0][2:].lower() in ["author","album","music genre"]:
                    print(item.split(':')[1][1:])
                    tag_name = item.split(':')[1][1:]
                    files = MiscFunctions.getDirectoryFiles(full_path)
                    for file in files:
                        #print file
                        #print full_path
                        
                        file_name = os.path.basename(path)
                        MiscFunctions.storeTagInDB(file, tag_name, self.db_conn)
                        
            print("Database storage successful")
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path,fh)

def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
