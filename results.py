
import sys
import os
import errno
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class ResultsFS(Operations):
	def __init__(self, results, files):
		self.results = results
		self.files = files

		print 'Obtained Files: ', self.files

		# Clean Up the previous results directory
		for path in os.listdir(self.results):
			try:
				os.unlink(os.path.join(self.results, path))
			except:
				pass

		# Generate hard links for the files in the results directory
		for filepath in self.files:
			partial = filepath.split('/')[-1]
			path = os.path.join(self.results, partial)
			os.link(filepath, path)

	## Helper Methods
	def virtual_path(self, path):
		if (path.startswith('/')):
			path = path[1:]
		path = os.path.join(self.results, path)
		return path

	## Filesystem Methods 

	def access(self, path, mode):
		full_path = self.virtual_path(path)
		if not os.access(full_path, mode):
			raise FuseOSError(errno.EACCES)

	def chmod(self, path, mode):
		full_path = self.virtual_path(path)
		return os.chmod(full_path, mode)

	def chown(self, path, uid, gid):
		full_path = self.virtual_path(path)
		return os.chown(full_path, uid, gid)

	def getattr(self, path, fh=None):
		full_path = self.virtual_path(path)
		st = os.lstat(full_path)
		return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
					 'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

	def readdir(self, path, fh):
		full_path = self.virtual_path(path)

		dirents = ['.', '..']
		if os.path.isdir(full_path):
			dirents.extend(os.listdir(full_path))
		for r in dirents:
			yield r

	def readlink(self, path):
		pathname = os.readlink(self.virtual_path(path))
		if pathname.startswith("/"):
			# Path name is absolute, sanitize it.
			return os.path.relpath(pathname, self.root)
		else:
			return pathname

	def mknod(self, path, mode, dev):
		return os.mknod(self.virtual_path(path), mode, dev)

	def rmdir(self, path):
		full_path = self.virtual_path(path)
		return os.rmdir(full_path)

	def mkdir(self, path, mode):
		return os.mkdir(self.virtual_path(path), mode)

	def statfs(self, path):
		full_path = self.virtual_path(path)
		stv = os.statvfs(full_path)
		return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
			'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
			'f_frsize', 'f_namemax'))

	def unlink(self, path):
		return os.unlink(self.virtual_path(path))

	def symlink(self, target, name):
		return os.symlink(self.virtual_path(target), self.virtual_path(name))

	def rename(self, old, new):
		return os.rename(self.virtual_path(old), self.virtual_path(new))

	def link(self, target, name):
		return os.link(self.virtual_path(target), self.virtual_path(name))

	def utimens(self, path, times=None):
		return os.utime(self.virtual_path(path), times)

	# File methods
	# ============

	def open(self, path, flags):
		full_path = self.virtual_path(path)
		return os.open(full_path, flags)

	def create(self, path, mode, fi=None):
		full_path = self.virtual_path(path)
		return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

	def read(self, path, length, offset, fh):
		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, length)

	def write(self, path, buf, offset, fh):
		os.lseek(fh, offset, os.SEEK_SET)
		return os.write(fh, buf)

	def truncate(self, path, length, fh=None):
		full_path = self.virtual_path(path)
		with open(full_path, 'r+') as f:
			f.truncate(length)

	def flush(self, path, fh):
		return os.fsync(fh)

	def release(self, path, fh):
		return os.close(fh)

	def fsync(self, path, fdatasync, fh):
		return self.flush(path, fh)


if __name__ == '__main__':
	results_directory = '/home/ryuk/results/'
	files = ['/home/ryuk/fuck1.txt', '/home/ryuk/fuck2.txt']

	FUSE(ResultsFS(results_directory, files), '/home/ryuk/mount-point', foreground=True)
