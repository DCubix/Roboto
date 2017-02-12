from math import *
from commands import *

import time, random
#, re, lxml.html


class Bot(IRC):
	def __init__(self, name="bot", info="", server="irc.freenode.net", port=6667):
		super(Bot, self).__init__(server, port)

		self.name = name
		self.info = info
		self.running = False
		self.showUpdateMessage = True
		self.irc_command = ""
		self.recon_attempts = 20

		self.__commands = [
			Calculator(),
			Tell(),
			Joke(),
			TellStack(),
			ShowTell()
		]

		self.version = [1, 5]
		self.update_message = name + " has been updated to version "

		self.start_messages = [
			"Hello everyone!",
			"Hello!",
			"Hi!",
			"Olá!",
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
			"why did the chicken cross the road": ["To get to the other side.", "For fun.", "Out of common sense.", "You tell me.", "The chicken wanted to expose the myth of the road..."],
			"what are you": ["I'm " + name + "! The UPBGE's Help Bot!", "I'm the UPBGE's Help Bot!", "I am a robot *beep* *boop*"]
		}

		self.show_startup_greeting = True

		self.__recon_cnt = 0

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
			_msg = random.choice(self.start_messages)
			if self.showUpdateMessage:
				_msg += " " + self.update_message + ".".join(self.version) + "!"
				self.showUpdateMessage = False
			self.send(IRC_MSG_PRIVMSG, channel, " :" + _msg)

		self.running = True
		while self.running:
			try:
				text = self.listen(2048)
			except socket.error:
				if e.errno == socket.errno.ECONNRESET:
					print("Connection Reset... Reconnecting...")
					self.sock.close()
					self.connect()
					self.send(IRC_MSG_USER, name + " " + name + " " + name, " :" + self.info)
					self.send(IRC_MSG_NICK, name, "")
					self.send(IRC_MSG_PRIVMSG, "nickserv", " :iNOOPE")
					self.join(channel)

					self.__recon_cnt += 1
					if self.__recon_cnt >= self.recon_attempts:
						self.__recon_cnt = 0
						self.quit()
				else:
					self.quit()
					raise

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
					## Checks if MESSAGE is a !command
					## It must:
					## - Start with a command
					## - Have a command character !
					for command in self.__commands:
						if command.string.lower() in lmsg:
							wholecmd = lmsg[:lmsg.find(" ")+1].strip(" \n\r")
							if " " not in lmsg:
								wholecmd = lmsg

							print("'%s'" % wholecmd)
							if wholecmd == command.string:
								print("ok")
								if command.is_valid(MESSAGE):
									command.execute(SENDER, TARGET, self, MESSAGE)
								else:
									self.send(
										IRC_MSG_PRIVMSG,
										TARGET,
										" :" + SENDER + ", invalid command!"
									)


			time.sleep(1.0 / 30)

		self.quit()