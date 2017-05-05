from math import *
from commands import *
import time, random, re


class User:
	def __init__(self, name):
		self.name = name
		self.reputation = 0


class Bot(IRC):
	def __init__(self, name="bot", info="", server="irc.freenode.net", port=6667):
		super(Bot, self).__init__(server, port)

		self.name = name
		self.info = info
		self.running = False
		self.irc_command = ""
		self.recon_attempts = 20

		self.__commands = [
			Calculator(),
			Tell(),
			Joke(),
			ShowTell()
		]

		self.version = [2, 0]

		self.start_messages = [
			"Hello everyone!",
			"Hello!",
			"Hi!",
			"Olá!",
			"Salut!",
			"Bonjour!"
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
		self.rand_greet_suff = ["it's nice to see you!", ":)", ":D", "", "hey, what's up?"]

		self.questions = {
			"how are you": ["I'm fine, thanks!", "All gears working!"],
			"who are you": ["I'm " + name + "! The UPBGE's Help Bot!", "I'm the UPBGE's Help Bot!"],
			"what can you do": ["I can do a lot of things. Inform new users, tell jokes, calculate big numbers, just type !cmdhelp"],
			"why did the chicken cross the road": ["To get to the other side.", "For fun.", "Out of common sense.", "You tell me.", "The chicken wanted to expose the myth of the road..."],
			"what are you": ["I'm " + name + "! The UPBGE's Help Bot!", "I'm the UPBGE's Help Bot!", "I am a human, and you are the bot."],
			"are you ok": ["I'm fine now, thanks... :(", "I'm fine", "Yes", "My head hurts but I'm fine!", "If I was a human I would say no"]
		}

		self.show_startup_greeting = True

		# load user database
		if not os.path.exists("userdb.dat"):
			open("userdb.dat", "wb").close()

		try:
			with open("userdb.dat", "rb") as f:
				d = pickle.load(f)
				self.user_database = d["db"]
		except:
			self.user_database = []
		
		self.__recon_cnt = 0

	def get_user(self, name):
		for user in self.user_database:
			if user.name == name:
				return user
		return None

	def get_user_names(self):
		names = []
		for user in self.user_database:
			names.append(user.name)
		return names

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

	def __save_user_db(self):
		with open("userdb.dat", "wb") as f:
			d = { "db": self.user_database }
			pickle.dump(d, f)

	def quit(self):
		self.__save_user_db()
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
				
				## Register user if he's not already in the database
				if SENDER != self.name:
					if self.get_user(SENDER) is None:
						new_usr = User(SENDER)
						self.user_database.append(new_usr)
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET, " :Welcome, " + SENDER + "!"
						)
					else:
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET, " :Welcome back, " + SENDER + "!"
						)
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
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET,
							" :\t!register: Register yourself in the user database"
						)
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET,
							" :\t!reps: Check your reputation points"
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
				elif lmsg == "!version":
					self.send(
						IRC_MSG_PRIVMSG,
						TARGET,
						" :" + name + " is in version " + ".".join([str(i) for i in self.version])
					)
				elif lmsg == "!quit":
					if SENDER == "TwisterGE":
						self.running = False
				elif lmsg == "!reps":
					user = self.get_user(SENDER)
					if user:
						reps = user.reputation
						if reps > 0:
							self.send(
								IRC_MSG_PRIVMSG,
								TARGET, " :%s, you have %d reputation point%s." % (user.name, reps, "" if reps <= 1 else "s")
							)
						else:
							self.send(
								IRC_MSG_PRIVMSG,
								TARGET, " :%s, you have no reputation points." % (user.name)
							)
				elif lmsg == "!register":
					if self.get_user(SENDER) is None:
						new_usr = User(SENDER)
						self.user_database.append(new_usr)
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET, " :You are now registered, " + SENDER + "!"
						)
					else:
						self.send(
							IRC_MSG_PRIVMSG,
							TARGET, " :You are already registered, " + SENDER + "..."
						)
				else:
					## Check if someone gave reputation to a user
					## The user is mentioned by adding @ before their name
					## Like this, @user, thanks!
					thanks = ["thanks", "thank you", "thx"]
					for t in thanks:
						if t in lmsg:
							users = self.get_user_names()
							if len(users) > 0:
								rstr = r"\b(%s)\b" % "|".join(users)
								mobj = re.search(rstr, MESSAGE)
								if mobj:
									for user_name in mobj.groups():
										if user_name == SENDER:
											continue # Can't give reputation to yourself
										user = self.get_user(user_name)
										if user:
											user.reputation += 1
											self.send(
												IRC_MSG_PRIVMSG,
												TARGET, " :%s earned reputation points!" % user_name
											)
							break
					
					## Checks if MESSAGE is a !command
					## It must:
					## - Start with a command
					## - Have a command character !
					for command in self.__commands:
						if command.string.lower() in lmsg:
							wholecmd = lmsg[:lmsg.find(" ")+1].strip(" \n\r")
							if " " not in lmsg:
								wholecmd = lmsg

							if wholecmd == command.string:
								if command.is_valid(MESSAGE):
									command.on_call(SENDER, TARGET, self, MESSAGE)
								else:
									self.send(
										IRC_MSG_PRIVMSG,
										TARGET,
										" :" + SENDER + ", invalid command!"
									)


			time.sleep(1.0 / 30)

		self.quit()