from core.IRC import *
from math import *
from urllib import request
from core.cmd import Cmd
from datetime import datetime, timezone
import os, pickle


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
			res = str(args[0]) + " is equal to " + str(ans)
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", " + res)
			self.ans = ans
		except:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", sorry, that didn't work.")

class Tell(Cmd):
	def __init__(self):
		super(Tell, self).__init__()
		self.string = "!tell"
		self.description = "Save message for an offline user. Usage: !tell username, \"something\""
		self.arg_count = 2

		self.tell = []

		# load tell
		if not os.path.exists("tell.dat"):
			open("tell.dat", "wb").close()

		try:
			with open("tell.dat", "rb") as f:
				d = pickle.load(f)
				self.tell = d["data"]
		except:
			self.tell = []

		print(self.tell)

	def execute(self, sender, target, bot, cmd):
		dt = datetime.now(timezone.utc)  # UTC time

		_, args = Cmd.execute(self, sender, target, bot, cmd)
		user = str(args[0])
		what = str(args[1])

		self.tell.append([user, sender, what, dt, False])
		bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", Ok!")

	def on_join(self, sender, target, bot):
		for i, v in enumerate(self.tell):
			user, sen, what, date, ok = v
			dt = datetime.now(timezone.utc)
			c = dt - date

			m, s = divmod(c.seconds, 60)
			h, m = divmod(m, 60)

			htxt = "hours" if h > 1 or h == 0 else "hour"
			mtxt = "minutes" if m > 1 or m == 0 else "minute"
			stxt = "seconds" if s > 1 or s == 0 else "seconds"

			t = "%02d %s, %02d %s %02d %s" % (h, htxt, m, mtxt, s, stxt)
			if user == sender and not ok:
				_who = sen if sen != sender else "you" 
				bot.send(IRC_MSG_PRIVMSG, target, " :%s, %s said %s ago: %s" % (sender, _who, t, what))
				self.tell[i][4] = True

		for i, v in enumerate(self.tell):
			if v[4]:
				del self.tell[i]
			
	def on_quit(self, bot):
		with open("tell.dat", "wb") as f:
			d = {"data": self.tell}
			pickle.dump(d, f)

class ShowTell(Cmd):
	def __init__(self):
		super(ShowTell, self).__init__()
		self.string = "!showtell"
		self.description = "Shows messages stored for you."
		self.arg_count = 0

	def execute(self, sender, target, bot, cmd):
		_tell = []
		try:
			with open("tell.dat", "rb") as f:
				d = pickle.load(f)
				_tell = d["data"]
		except:
			pass

		tell = [msg for msg in _tell if msg[0] == sender]
		if len(tell) > 0:
			msgtxt = "messages" if len(tell) > 1 else "message"
			isare = "are" if len(tell) > 1 else "is"
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", there %s %d %s for you: " % (isare, len(tell), msgtxt))

			for _, sen, what, date, _ in tell:
				dt = datetime.now(timezone.utc)
				c = dt - date

				m, s = divmod(c.seconds, 60)
				h, m = divmod(m, 60)

				htxt = "hours" if h > 1 or h == 0 else "hour"
				mtxt = "minutes" if m > 1 or m == 0 else "minute"
				stxt = "seconds" if s > 1 or s == 0 else "seconds"

				t = "%02d %s, %02d %s, %02d %s" % (h, htxt, m, mtxt, s, stxt)
				bot.send(IRC_MSG_PRIVMSG, target, " :\t%s ago: %s | by %s" % (t, what, sen))
		else:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", there are no messages for you.")

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


class TellStack(Cmd):
	def __init__(self):
		super(TellStack, self).__init__()
		self.string = "!tellstack"
		self.description = "Print all messages stored in !tell."
		self.arg_count = 0

	def execute(self, sender, target, bot, cmd):
		tell = []
		try:
			with open("tell.dat", "rb") as f:
				d = pickle.load(f)
				tell = d["data"]
		except:
			pass

		if len(tell) > 0:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ": ")
			for _, sen, what, date, _ in tell:
				dt = datetime.now(timezone.utc)
				c = dt - date

				m, s = divmod(c.seconds, 60)
				h, m = divmod(m, 60)

				htxt = "hours" if h > 1 or h == 0 else "hour"
				mtxt = "minutes" if m > 1 or m == 0 else "minute"
				stxt = "seconds" if s > 1 or s == 0 else "seconds"

				t = "%02d %s, %02d %s, %02d %s" % (h, htxt, m, mtxt, s, stxt)
				bot.send(IRC_MSG_PRIVMSG, target, " :\t%s ago: %s | by %s" % (t, what, sen))
		else:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", there are no messages.")
