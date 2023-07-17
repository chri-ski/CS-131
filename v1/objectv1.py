from intbase import InterpreterBase, ErrorType
from type_valuev1 import *
from env_v1 import EnvironmentManager

class ObjectDef:

	# Program Status constant
	STATUS_PROCEED = 0
	STATUS_RETURN = 1

	#constants:
	ARITHMETIC = ["+", "-", "*", "/", "%"]
	COMPARISON = ["<", ">", "<=", ">=", "==", "!="]
	CONCATENATION = "+"
	BOOLEAN = ["==", "!=", "&", "|"]
	COMP_NULL = ["==", "!="]
	NOT = "!"

	def __init__(self, object_def, interpreter):
		self.object_def = object_def
		self.interpreter = interpreter
		self.field_map = {}
		self.method_map = {}

	def add_field(self, field):
		self.field_map[field.name] = create_value(field.initial_value)

	def add_method(self,method):
		self.method_map[method.name] = method

  # Interpret the specified method using the provided parameters    
	def call_method(self, method_name, parameters):
		method = self.__find_method(method_name)
		if len(parameters) != len(method.parameters):
			return self.interpreter.error(ErrorType.TYPE_ERROR)

		environment = EnvironmentManager()

		for name, value in zip(method.parameters, parameters):
			environment.set(name, value)


		status, result = self.__run_statement(method.statement, environment)
		if status == self.STATUS_RETURN:
			return result
		return Value(Type.NOTHING, InterpreterBase.NOTHING_DEF)

	def __find_method(self, method_name):
		if method_name not in self.method_map:
			return self.interpreter.error(ErrorType.NAME_ERROR) #add description
		for method in self.method_map:
			if method == method_name:
				return self.method_map[method]

  # runs/interprets the passed-in statement until completion and 
  # gets the result, if any
	def __run_statement(self, statement, environment):
		if statement[0] == InterpreterBase.PRINT_DEF:
			return self.__execute_print_statement(statement, environment)
		elif statement[0] == InterpreterBase.INPUT_STRING_DEF:
			return self.__execute_input_statement(statement, environment, True)
		elif statement[0] == InterpreterBase.INPUT_INT_DEF:
			return self.__execute_input_statement(statement, environment, False)
		elif statement[0] == InterpreterBase.CALL_DEF:
			return self.__execute_call_statement(statement, environment)
		elif statement[0] == InterpreterBase.WHILE_DEF:
			return self.__execute_while_statement(statement, environment)
		elif statement[0] == InterpreterBase.IF_DEF:
			return self.__execute_if_statement(statement, environment)
		elif statement[0] == InterpreterBase.RETURN_DEF:
			return self.__execute_return_statement(statement, environment)
		elif statement[0] == InterpreterBase.BEGIN_DEF:
			return self.__execute_begin_statement(statement, environment) 
		elif statement[0] == InterpreterBase.SET_DEF:
			return self.__execute_set_statement(statement, environment)
		
		return self.interpreter.error(ErrorType.SYNTAX_ERROR)

	def __execute_print_statement(self, statement, environment):
		context = ""
		for arg in statement[1:]:
			result = self.__evaluate_expression(arg, environment)
			if result.type() == Type.BOOL:
				if result.value():
					context += InterpreterBase.TRUE_DEF
				else:
					context += InterpreterBase.FALSE_DEF
			else:
				context += str(result.value())
		
		return self.STATUS_PROCEED, self.interpreter.output(context)

	def __execute_input_statement(self, statement, environment, is_string):
		inp = self.interpreter.get_input()
		if is_string:
			value = Value(Type.STRING, inp)
		else:
			value = Value(Type.INT, inp)

		variable = statement[1]
		if variable in self.field_map:
			self.field_map[variable] = value
		elif environment.get(variable):
			environment.set(variable, value)
		return self.STATUS_PROCEED, None

	def __execute_call_statement(self, statement, environment):
		target_name = statement[1]
		evaluated_args = []
		for args in statement[3:]:
			evaluated_args.append(self.__evaluate_expression(args, environment))
		if target_name == InterpreterBase.ME_DEF:
			return self.STATUS_PROCEED, self.call_method(statement[2], evaluated_args)
		else:
			target = self.__evaluate_expression(target_name, environment)
		if target.type() == Type.NULL:
			return self.interpreter.error(ErrorType.FAULT_ERROR)
		return self.STATUS_PROCEED, target.value().call_method(statement[2], evaluated_args)

	def __execute_while_statement(self, statement, environment):
		condition = self.__evaluate_expression(statement[1], environment)
		while True:
			if condition.type() != Type.BOOL:
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			if condition.value():
				status, result = self.__run_statement(statement[2], environment)
				if status == self.STATUS_RETURN:
					return status, result
				condition = self.__evaluate_expression(statement[1], environment)
			else:
				return self.STATUS_PROCEED, None


	def __execute_if_statement(self, statement, environment):
		condition = self.__evaluate_expression(statement[1], environment)
		if condition.type() != Type.BOOL:
			return self.interpreter.error(ErrorType.TYPE_ERROR)
		if condition.value():
			return self.__run_statement(statement[2], environment)
		if len(statement) > 3:
			return self.__run_statement(statement[3], environment)
		return self.STATUS_PROCEED, None

	# add program status
	def __execute_return_statement(self, statement, environment):
		if len(statement) > 1:
			return self.STATUS_RETURN, self.__evaluate_expression(statement[1], environment)
		return self.STATUS_RETURN, create_value(InterpreterBase.NOTHING_DEF)

	def __execute_begin_statement(self, statement, environment):
		for sub_statement in statement[1:]:
			status, result = self.__run_statement(sub_statement, environment)
			if status == self.STATUS_RETURN:
				return status, result
		return self.STATUS_PROCEED, None


	# consider adding environment and program running status
	def __execute_set_statement(self, statement, environment):
		variable = statement[1]
		if (variable not in self.field_map) and (variable not in self.interpreter.obj_map) and (variable not in environment.environment):
			return self.interpreter.error(ErrorType.NAME_ERROR)
		value = self.__evaluate_expression(statement[2], environment)
		if variable in self.field_map:
			self.field_map[variable] = value
		elif variable in self.interpreter.obj_map:
			self.interpreter.obj_map[variable] = value
		elif environment.get(variable):
			environment.set(variable, value)
		return self.STATUS_PROCEED, None

	def __evaluate_expression(self, expression, environment):
		if not isinstance(expression, list):
			if expression in self.field_map:
				return self.field_map[expression]
			if expression in self.interpreter.obj_map:
				return Value(Type.OBJECT, self.interpreter.obj_map[expression])
			if expression in environment.environment:
				return environment.environment[expression]
			result = create_value(expression)
			if result:
				return result
			else:
				return self.interpreter.error(ErrorType.NAME_ERROR)
		operator = expression[0]

		if operator == InterpreterBase.NEW_DEF:
			obj = self.interpreter.instantiate_object(expression[1])
			return Value(Type.OBJECT, obj)

		if operator == InterpreterBase.CALL_DEF:
			status, result = self.__execute_call_statement(expression, environment)
			return result
		
		operand1 = self.__evaluate_expression(expression[1], environment)
		type1 = operand1.type()

		if operator == self.NOT:
			if type1 != Type.BOOL:
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			if operand1.value():
				return create_value(InterpreterBase.FALSE_DEF)
			else:
				return create_value(InterpreterBase.TRUE_DEF)

		operand2 = self.__evaluate_expression(expression[2], environment)
		type2 = operand2.type()

		if (type1 == Type.NULL) or (type2 == Type.NULL):
			if operator not in self.COMP_NULL:
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			else:
				match operator:
					case "==":
						return Value(Type.BOOL, operand1.type() == operand2.type())
					case "!=":
						return Value(Type.BOOL, operand1.type() != operand2.type())

		if type1 != type2:
			return self.interpreter.error(ErrorType.TYPE_ERROR)

		if type1 == Type.INT:
			if operator not in (self.ARITHMETIC + self.COMPARISON):
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			else:
				match operator:
					case "+":
						return Value(Type.INT, operand1.value() + operand2.value())
					case "-":
						return Value(Type.INT, operand1.value() - operand2.value())
					case "*":
						return Value(Type.INT, operand1.value() * operand2.value())
					case "/":
						return Value(Type.INT, operand1.value() // operand2.value())
					case "%":
						return Value(Type.INT, operand1.value() % operand2.value())
					case "<":
						return Value(Type.BOOL, operand1.value() < operand2.value())
					case ">":
						return Value(Type.BOOL, operand1.value() > operand2.value())
					case "<=":
						return Value(Type.BOOL, operand1.value() <= operand2.value())
					case ">=":
						return Value(Type.BOOL, operand1.value() >= operand2.value())
					case "==":
						return Value(Type.BOOL, operand1.value() == operand2.value())
					case "!=":
						return Value(Type.BOOL, operand1.value() != operand2.value())

		if type1 == Type.BOOL:
			if operator not in self.BOOLEAN:
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			else:
				match operator:
					case "==":
						return Value(Type.BOOL, operand1.value() == operand2.value())
					case "!=":
						return Value(Type.BOOL, operand1.value() != operand2.value())
					case "&":
						return Value(Type.BOOL, operand1.value() and operand2.value())
					case "|":
						return Value(Type.BOOL, operand1.value() or operand2.value())

		if type1 == Type.STRING:
			if (operator not in self.COMPARISON) and (operator not in self.CONCATENATION):
				return self.interpreter.error(ErrorType.TYPE_ERROR)
			else:
				match operator:
					case "<":
						return Value(Type.BOOL, operand1.value() < operand2.value())
					case ">":
						return Value(Type.BOOL, operand1.value() > operand2.value())
					case "<=":
						return Value(Type.BOOL, operand1.value() <= operand2.value())
					case ">=":
						return Value(Type.BOOL, operand1.value() >= operand2.value())
					case "==":
						return Value(Type.BOOL, operand1.value() == operand2.value())
					case "!=":
						return Value(Type.BOOL, operand1.value() != operand2.value())
					case "+":
						return Value(Type.STRING, operand1.value() + operand2.value())




