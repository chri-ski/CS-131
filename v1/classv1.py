from intbase import ErrorType, InterpreterBase

class FieldDef:
	def __init__(self, field_def):
		self.name = field_def[1]
		self.initial_value = field_def[2]


class MethodDef:
	def __init__(self, method_def):
		self.name = method_def[1]
		self.parameters = method_def[2]	# maybe seperate?
		self.statement = method_def[3]	# object


class ClassDef:

	def __init__ (self, class_def, interpreter):
		self.name = class_def[1]
		self.interpreter = interpreter
		self.__create_field_map(class_def[2:])
		self.__create_method_map(class_def[2:])

	def __create_field_map(self, items):
		self.field_map = {}

		for item in items:
			if item[0] == InterpreterBase.FIELD_DEF:
				if item[1] in self.field_map:
					self.interpreter.error(ErrorType.NAME_ERROR) # add description..
				self.field_map[item[1]] = FieldDef(item)

	def __create_method_map(self, items):
		self.method_map = {}

		for item in items:
			if item[0] == InterpreterBase.METHOD_DEF:
				if item[1] in self.method_map:
					self.interpreter.error(ErrorType.NAME_ERROR) # add description..
				self.method_map[item[1]] = MethodDef(item)

