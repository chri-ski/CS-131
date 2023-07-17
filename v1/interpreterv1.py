from intbase import ErrorType, InterpreterBase
from bparser import BParser
from classv1 import ClassDef
from objectv1 import ObjectDef


class Interpreter (InterpreterBase):
	def __init__(self, console_output=True, inp=None, trace_output=False):
		super().__init__(console_output, inp)
		self.trace_output = trace_output
		self.class_map = {}
		self.obj_map = {}
	
	def run(self, program):
		result, parsed_program = BParser.parse(program)
		
		if result == False:
			super().error(ErrorType.SYNTAX_ERROR) # add description and linenum

		# map class name to definition 
		for class_def in parsed_program:
			if class_def[0] == InterpreterBase.CLASS_DEF:
				if class_def[1] in self.class_map:
					super().error(ErrorType.TYPE_ERROR) # add description and linenum
				self.class_map[class_def[1]] = ClassDef(class_def, self)

		# instantiate main class
		self.obj_map[InterpreterBase.MAIN_CLASS_DEF] = self.instantiate_object(InterpreterBase.MAIN_CLASS_DEF)
		self.obj_map[InterpreterBase.MAIN_CLASS_DEF].call_method(InterpreterBase.MAIN_FUNC_DEF, [])


	def instantiate_object(self, class_name):
		if class_name not in self.class_map:
			super().error(ErrorType.TYPE_ERROR)
		class_def = self.class_map[class_name]
		obj = ObjectDef(class_def, self)
		
		for method in class_def.method_map:
			obj.add_method(class_def.method_map[method])

		for field in class_def.field_map:
			obj.add_field(class_def.field_map[field])

		return obj


		# self.__discover_all_classes_and_track_them(parsed_program)
		# class_def = self.__find_definition_for_class("main")
		# obj = class_def.instantiate_object() 
		# obj.run_method("main")

