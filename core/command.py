class StringReader:
	def __init__(self, string):
		self.string = string
		self.length = len(string) if string is not None else 0
		self.__pos = 0

	def read(self):
		if self.__pos == self.length: return None
		self.__pos += 1
		return self.string[self.__pos-1]

	def peek(self):
		if self.__pos == self.length: return None
		return self.string[self.__pos+1]

def parse_command(cmd):
	spl = cmd.split(" ", 1)
	if len(spl) == 2:
		cmd_name, cmd_args = spl
		
		cmd_str = cmd_name.strip(" \n\r")
		_args = cmd_args.strip(" \n\r")

		## Get the arguments
		sr = StringReader(_args)
		args = []
		
		char = sr.read()
		while char is not None:
			if char.isspace() or char == ',':
				char = sr.read()
			elif char.isalpha() or char in ["'", '"']: # read strings
				arg = ""
				quoted = char in ["'", '"']
				
				if not quoted:
					while char != ',' and char is not None:
						arg += char
						char = sr.read()
				else:
					arg += char
					char = sr.read()
					while char not in ["'", '"'] and char is not None:
						arg += char
						char = sr.read()
					char = sr.read()
				
				arg = arg.strip(' ",')

				args.append(arg)
			elif char.isdigit():
				arg = ""
				isFloat = False
				isString = False
				while char != ',' and char is not None:
					arg += char
					if char == '.':
						isFloat = True
					if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
						isString = True  
					char = sr.read()
				arg = arg.strip(' ,')
				
				if not isString:
					if isFloat:
						args.append(float(arg))
					else:
						args.append(int(arg))
				else:
					args.append(arg)

	else:
		cmd_str = cmd.strip(" \n\r")
		args = []

# 	print(cmd_str, args)
	return (cmd_str, args)

class Command:
	def __init__(self):
		self.string = ""
		self.description = ""
		self.arg_count = 0

	def is_valid(self, cmd):
		cmd_str, args = parse_command(cmd)
		return len(args) == self.arg_count and cmd_str == self.string

	def on_join(self, sender, target, bot):
		pass

	def on_quit(self, bot):
		pass

	def on_call(self, sender, target, bot, cmd):
		## !cmd arg1, arg2, arg3, arg4, arg5, ... !
		pass