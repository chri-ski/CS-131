# class to control the environment, keep track of the in-scope variables

class EnvironmentManager:

	def __init__(self):
		self.environment = {}

	def get(self, item):
		if item in self.environment:
			return self.environment[item]

		return None

	def set(self, item, value):
		self.environment[item] = value
		return