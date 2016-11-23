from pyparsing import (printables, originalTextFor, OneOrMore, quotedString, Word, delimitedList)

class Cmd:
	def __init__(self):
		self.string = ""
		self.description = ""
		self.arg_count = 0

	def parse_command(self, cmd):
		printables_less_comma = printables.replace(",", "")
		content = originalTextFor(OneOrMore(quotedString | Word(printables_less_comma)))

		i = cmd.find(" ")
		if i != -1:
			## Get command string
			cmd_str = cmd[:i].lower().strip(" \n\r")

			## Get arguments
			args = []
			_args = delimitedList(content, ",").parseString(cmd[i+1:].strip(" \n\r"))
			__args = [arg.strip(" ,\n\r") for arg in _args]

			for arg in __args:
				narg = arg
				try:
					narg = float(arg)
				except:
					pass
				if arg != cmd_str:
					args.append(narg)
		else:
			cmd_str = cmd
			args = []

		print(cmd_str, args)
		return (cmd_str, args)

	def is_valid(self, cmd):
		cmdstr, args = self.parse_command(cmd)
		return len(args) == self.arg_count

	def on_join(self, sender, target, bot):
		pass

	def on_quit(self, bot):
		pass

	def execute(self, sender, target, bot, cmd):
		## !cmd arg1, arg2, arg3, arg4, arg5, ... !
		return self.parse_command(cmd)