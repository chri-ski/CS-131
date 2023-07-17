from enum import Enum
from intbase import InterpreterBase

class Type(Enum):

	NULL = 0
	BOOL = 1
	INT = 2
	STRING = 3
	OBJECT = 4
	NOTHING = 5


class Value:

	def __init__ (self, v_type, value=None):
		self.__type = v_type
		self.__value = value

	def type(self):
		return self.__type

	def value(self):
		return self.__value

	def set(value):
		self.__value = value


def create_value(value):
	if value.isnumeric():
		return Value(Type.INT, int(value))
	if value[0] == '"':
		return Value(Type.STRING, value.strip('"'))

	match value:
		case InterpreterBase.TRUE_DEF:
			return Value(Type.BOOL, True)
		case InterpreterBase.FALSE_DEF:
			return Value(Type.BOOL, False)
		case InterpreterBase.NULL_DEF:
			return Value(Type.NULL, None)
		case InterpreterBase.NOTHING_DEF:
			return Value(Type.NOTHING, None)
		case _:
			return None
	


		
