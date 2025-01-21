from filesystem.dir import Dir
from filesystem.file import File
from datetime import datetime

class Logger:

	def __init__(self, path, rid, **kwargs):
	
		self.__path = Dir(path)
		self.__verbose = kwargs.get('verbose', False)
		self.__debug = kwargs.get('debug', False)
		self.__rid = rid
		self.__rotation = 0
		self.__hasError = False
		self.__maxLogLines = kwargs.get('maxLogLines', None)
		self.__maxFilesCount = kwargs.get('maxFilesCount', 5)
		self.__writtenLines = 0

		#Init dir
		if not self.__path.exists():
			self.__path.create()
		
	def log(self, section, status, message):
	
		log = '[' + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '][' + section.upper() + '][' + status.upper() + '] - ' + message

		if self.__verbose and ((status != 'debug') or (status == 'debug' and self.__debug)):
			print(log)

		if self.__debug and status == 'debug':
			return

		f = open(self.__path.getPath() + 'Log_' +  self.__rid + '_' + ( '{0:0=3d}'.format(self.__rotation) ) + '.log' , 'a')
		f.write(log + "\n")
		f.close()
		
		if status == 'error':
			self.__hasError = True

		self.__writtenLines += 1

		self.__rotate()

	def info(self, section = 'global', message = ''):
		self.log(section,'info',message)

	def warning(self, section='global', message=''):
		self.log(section, 'warning', message)
	
	def error(self, section = 'global', message = ''):
		self.log(section,'error',message)

	def debug(self, section='global', message=''):
		self.log(section, 'debug', message)
		
	def hasErrors(self):
		return self.__hasError
		
	def purge(self):
	
		logs = sorted(self.__path.list(), reverse=True)

		for filename in logs[:(self.__maxFilesCount*-1)]:
			log = File(self.__path.getPath()+filename)
			log.delete()

	def __rotate(self):

		if self.__maxLogLines is None or self.__writtenLines < self.__maxLogLines:
			return

		self.__rotation += 1
		self.__writtenLines = 0

		self.purge()


