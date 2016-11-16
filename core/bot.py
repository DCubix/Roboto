from math import *
from core.IRC import *

from pws import Bing
from urllib import request

import time
import random
import os
import pickle


class Cmd:
	def __init__(self):
		self.string = ""
		self.description = ""
		self.arg_count = 0

	def parse_command(self, cmd):
		from pyparsing import (printables, originalTextFor, OneOrMore, quotedString, Word, delimitedList)
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


class Calculator(Cmd):
	def __init__(self):
		super(Calculator, self).__init__()
		self.string = "!calc"
		self.description = "Simple calculator.  Usage: !calc 2+2, !calc sin(pi)."
		self.arg_count = 1
		self.ans = 0

	def execute(self, sender, target, bot, cmd):
		_, args = Cmd.execute(self, sender, target, bot, cmd)
		try:
			ans = self.ans
			ans = eval(str(args[0]))
			res = str(args[0]) + " equals " + str(ans)
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", " + res)
			self.ans = ans
		except:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", sorry, that didn't work.")


class Search(Cmd):
	def __init__(self):
		super(Search, self).__init__()
		self.string = "!search"
		self.description = "Search for something on the internet. Usage: !search something."
		self.arg_count = 1

	def is_valid(self, cmd):
		cmdstr, args = self.parse_command(cmd)
		return len(args) >= self.arg_count

	def execute(self, sender, target, bot, cmd):
		_, args = Cmd.execute(self, sender, target, bot, cmd)
		query = str(args[0])
		acc = str(args[1]) if len(args) > 1 else ""
		list_accessor = "[0]" if "[" not in acc and "]" not in acc else acc[acc.find("["):acc.find("]")+1]

		try:
			ret = Bing.search(query, 5, 1)
			results = []
			for res in ret["results"]:
				link = res["link"]
				link_text = res["link_text"].title()
				results.append((link_text, link))

			if len(results) > 0:
				accs = "results" + list_accessor
				items = eval(accs)
				if isinstance(items, list):
					bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ":")
					for item in items:
						bot.send(IRC_MSG_PRIVMSG, target, " :\t" + item[0] + " - " + item[1])
				else:
					bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", " + items[0] + " - " + items[1])
			else:
				bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ",  I didn't find anything about that :-/")
		except:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", sorry, that didn't work.")


class Tell(Cmd):
	def __init__(self):
		super(Tell, self).__init__()
		self.string = "!tell"
		self.description = "Save message for an offline user. Usage: !tell username, something"
		self.arg_count = 2

		self.tell = []

		# load tell
		if not os.path.exists("tell.tf"):
			open("tell.tf", "wb").close()

		try:
			with open("tell.tf", "rb") as f:
				d = pickle.load(f)
				self.tell = d["data"]
		except EOFError:
			self.tell = []

		print(self.tell)

	def execute(self, sender, target, bot, cmd):
		from datetime import datetime, timezone
		dt = datetime.now(timezone.utc)  # UTC time

		_, args = Cmd.execute(self, sender, target, bot, cmd)
		user = str(args[0])
		what = str(args[1])

		self.tell.append((user, sender, what, dt))
		bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", Ok!")

	def on_join(self, sender, target, bot):
		i = 0
		for user, sen, what, date in self.tell:
			t = "%02d/%02d/%04d at %02d:%02d UTC" % (date.month, date.day, date.year, date.hour, date.minute)

			if user == sender:
				bot.send(IRC_MSG_PRIVMSG, target, " :%s, %s said, on %s: %s" % (sender, sen, t, what))
				del self.tell[i]
			i += 1

	def on_quit(self, bot):
		with open("tell.tf", "wb") as f:
			d = {"data": self.tell}
			pickle.dump(d, f)


class Joke(Cmd):
	def __init__(self):
		super(Joke, self).__init__()
		self.string = "!joke"
		self.description = "Tells a random joke."
		self.arg_count = 0

	def execute(self, sender, target, bot, cmd):
		import json
		response = request.urlopen("http://tambal.azurewebsites.net/joke/random")
		joke_json = json.loads(response.read().decode("utf-8"))
		joke_text = joke_json["joke"]

		bot.send(IRC_MSG_PRIVMSG, target, " :" + joke_text)


class Bot(IRC):
	def __init__(self, name="bot", info="", server="irc.freenode.net", port=6667):
		super(Bot, self).__init__(server, port)

		self.name = name
		self.info = info
		self.running = False
		self.irc_command = ""

		self.__commands = [
			Calculator(),
			Search(),
			Tell(),
			Joke()
		]

		self.start_messages = [
			"Hello everyone!",
			"Hello!",
			"Hi!",
			"Olá!",
			"Привет!",
			"Привіт!",
			"Здрасти!",
			"Salut!",
			"Bonjour à tous!"
		]

		self.help_message = \
			"If you are new to UPBGE, download it at https://download.upbge.org/, " + \
			"and check the docs and release notes at https://doc.upbge.org/. " + \
			"If you are a Python programmer, check out our Python API at https://pythonapi.upbge.org/, " + \
			"and If you want to help us with C/C++ stuff, look at the doxygen page at http://doxygen.upbge.org/. " + \
			"For issues/feature requests, see https://github.com/UPBGE/blender. For bot commands, type !cmdhelp."

		self.greetings = [
			"hi", "hi!", "hello", "hello!",
			"olá", "olá!", "ola", "ola!",
			"bonjour", "salut", "bonjour!", "salut!"
		]
		self.rand_greet_suff = ["it's nice to see you!", ":)", ":D", ""]

		self.questions = {
			"how are you": ["I'm fine, thanks!", "All gears working!", "Not in the mood for bad mood!"],
			"who are you": ["I'm " + name + "! The UPBGE's Help Bot!", "I'm the UPBGE's Help Bot!"],
			"what can you do": ["I can do a lot of things. Inform new users, tell jokes, calculate big numbers, just type !cmdhelp"],
			"why did the chicken cross the road": ["To get to the other side.", "For fun.", "Out of common sense.", "You tell me.", "The chicken wanted to expose the myth of the road..."]
		}

		self.show_startup_greeting = True

	def register_command(self, cmd):
		if cmd not in self.__commands:
			self.__commands.append(cmd)

	def __parse(self, s):
		prefix = ''
		trailing = []

		if s[0] == ':':
			prefix, s = s[1:].split(' ', 1)
		if s.find(' :') != -1:
			s, trailing = s.split(' :', 1)
			args = s.split()
			args.append(trailing)
		else:
			args = s.split()
		command = args.pop(0)
		return prefix, command, args

	def quit(self):
		print("Quit!")
		for command in self.__commands:
			command.on_quit(self)
		IRC.quit(self)
		self.running = False

	def start(self, channel):
		name = self.name
		self.connect()
		self.send(IRC_MSG_USER, name + " " + name + " " + name, " :" + self.info)
		self.send(IRC_MSG_NICK, name, "")
		self.send(IRC_MSG_PRIVMSG, "nickserv", " :iNOOPE")
		self.join(channel)

		if self.show_startup_greeting:
			self.send(IRC_MSG_PRIVMSG, channel, " :" + random.choice(self.start_messages))

		self.running = True
		while self.running:
			text = self.listen(2048)
			print(text.strip(" \n\r"))

			msg = self.__parse(text.strip(" \n\r"))

			SENDER  = msg[0][:msg[0].rfind("!")].strip(" :\n\r")
			IRC_CMD = msg[1].lower().strip(" \n\r")
			IS_PRIV = not msg[2][0].startswith("#")
			TARGET  = SENDER if IS_PRIV else channel

			self.irc_command = IRC_CMD

			## Prevent disconnect
			if IRC_CMD == "ping":
				self.send(IRC_MSG_PONG, "", text.split()[1])
			elif IRC_CMD == "join":
				for command in self.__commands:
					command.on_join(SENDER, TARGET, self)
			elif IRC_CMD == "privmsg":
				MESSAGE = msg[2][1].strip(" \n\r")

				## Checks if SENDER greets BOT
				for greeting in self.greetings:
					grets = [
						greeting + " " + name.lower(),
						greeting + ", " + name.lower(),
						greeting + "," + name.lower(),
						name.lower() + " " + greeting,
						name.lower() + ", " + greeting,
						name.lower() + "," + greeting
					]
					if MESSAGE.lower() in grets:
						self.send(
							IRC_MSG_PRIVMSG, TARGET,
							" :Hello, " + SENDER + " " + random.choice(self.rand_greet_suff)
						)
						break

				## Checks if SENDER asks a question from the question dict
				for question in list(self.questions.keys()):
					qst = [
						question + " " + name.lower() + "?",
						question + ", " + name.lower() + "?",
						question + "," + name.lower() + "?",
						name.lower() + " " + question + "?",
						name.lower() + ", " + question + "?",
						name.lower() + "," + question + "?",
					]
					if MESSAGE.lower() in qst:
						random_answer = random.choice(self.questions[question])
						self.send(
							IRC_MSG_PRIVMSG, TARGET,
							" :" + SENDER + ", " + random_answer
						)
						break

				lmsg = MESSAGE.lower()

				## Builtin commands
				if lmsg == "!cmdhelp":
					self.send(
						IRC_MSG_PRIVMSG,
						TARGET, " :" + SENDER + ", These are the commands: "
					)
					self.send(
						IRC_MSG_PRIVMSG,
						TARGET,
						" :\t!cmdhelp: Shows this message."
					)
					if len(self.__commands) > 0:
						for command in self.__commands:
							self.send(
								IRC_MSG_PRIVMSG,
								TARGET,
								" :\t" + command.string + ": " + command.description
							)
					else:
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET,
							" :" + SENDER + ", there are no commands installed in this bot."
						)
				elif lmsg == "!help":
					self.send(
						IRC_MSG_PRIVMSG,
						TARGET,
						" :" + SENDER + ", " + self.help_message
					)
				elif lmsg == "!quit":
					if SENDER == "TwisterGE":
						self.running = False
				else:
					## Checks if MESSAGE is a command
					## It must:
					## - Start with a command
					## - Have a command character !
					for command in self.__commands:
						if lmsg.startswith(command.string.lower()):
							if command.is_valid(MESSAGE):
								command.execute(SENDER, TARGET, self, MESSAGE)
							else:
								self.send(
									IRC_MSG_PRIVMSG,
									TARGET,
									" :" + SENDER + ", malformed command!"
								)


			time.sleep(1.0 / 24)

		self.quit()