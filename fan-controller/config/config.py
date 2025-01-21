import configparser

class Config:

	def __init__(self, file):
	
		self.storage = file
		self.parser = configparser.ConfigParser()
		
		# Read

		self.parser.read(self.storage)

	def get(self ,section, key):
		
		if self.parser.has_option(section, key) is False:
			return None
		
		return self.parser.get(section, key)
	