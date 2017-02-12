class StringReader:
	def __init__(self, string):
		self.string = string
		self.length = len(string) if string is not None else 0
		self.__pos = 0
	
	def eol(self):
		return self.__pos >= self.length
	
	def read(self):
		if self.eol(): return None
		self.__pos += 1
		return self.string[self.__pos-1]


class Cmd:
	def __init__(self):
		self.string = ""
		self.description = ""
		self.arg_count = 0

	def parse_command(self, cmd):
		i = cmd.find(" ")
		
		if i != -1:
			## Get command string
			cmd_str = cmd[:i].lower().strip(" \n\r")
			_args = cmd[i:].strip(" \n\r")

			## Get the arguments
			sr = StringReader(_args)
			args = []
			
			char = sr.read()
			while not sr.eol():
				if char.isspace():
					char = sr.read()
				elif char == ',':
					char = sr.read()
				elif char.isalpha() or char == '"' or char == "'": # read strings
					arg = ""
					while not sr.eol() and char != ',':
						arg += char
						char = sr.read()
					if sr.eol():
						arg += char
						
					args.append(arg.strip(" '\""))
				elif char.isdigit():
					arg = ""
					isnum = True
					isfloat = False
					while not sr.eol() and char != ',':
						arg += char
						char = sr.read()
						if char == '.':
							isfloat = True
						if not char.isdigit():
							isnum = False
					if sr.eol():
						arg += char
						
					if isnum:
						if isfloat:
							args.append(float(arg))
						else:
							args.append(int(arg))
					else:
						args.append(arg)
		else:
			cmd_str = cmd.strip(" \n\r")
			args = []

		print(cmd_str, args)
		return (cmd_str, args)

	def is_valid(self, cmd):
		_, args = self.parse_command(cmd)
		return len(args) == self.arg_count

	def on_join(self, sender, target, bot):
		pass

	def on_quit(self, bot):
		pass

	def execute(self, sender, target, bot, cmd):
		## !cmd arg1, arg2, arg3, arg4, arg5, ... !
		return self.parse_command(cmd)