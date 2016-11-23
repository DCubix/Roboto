from core.IRC import *
from pws import Bing
from urllib import request
from core.cmd import Cmd
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
		from datetime import datetime, timezone
		i = 0
		for user, sen, what, date in self.tell:
			dt = datetime.now(timezone.utc)
			c = dt - date

			m, s = divmod(c.seconds, 60)
			h, m = divmod(m, 60)

			htxt = "hours" if h > 1 or h == 0 else "hour"
			mtxt = "minutes" if m > 1 or m == 0 else "minute"
			stxt = "seconds" if s > 1 or s == 0 else "seconds"

			t = "%02d %s, %02d %s %02d %s" % (h, htxt, m, mtxt, s, stxt)
			if user == sender:
				bot.send(IRC_MSG_PRIVMSG, target, " :%s, %s said %s ago: %s" % (sender, sen, t, what))
				del self.tell[i]
			i += 1

	def on_quit(self, bot):
		with open("tell.tf", "wb") as f:
			d = {"data": self.tell}
			pickle.dump(d, f)

class ShowTell(Cmd):
	def __init__(self):
		super(ShowTell, self).__init__()
		self.string = "!showtell"
		self.description = "Shows messages stored for you."
		self.arg_count = 0

	def execute(self, sender, target, bot, cmd):
		from datetime import datetime, timezone
		_tell = []
		try:
			with open("tell.tf", "rb") as f:
				d = pickle.load(f)
				_tell = d["data"]
		except EOFError:
			pass

		tell = [msg for msg in _tell if msg[0] == sender]
		if len(tell) > 0:
			msgtxt = "messages" if len(tell) > 1 else "message"
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", there are %d %s for you: " % (len(tell), msgtxt))

			for user, sen, what, date in tell:
				dt = datetime.now(timezone.utc)
				c = dt - date

				m, s = divmod(c.seconds, 60)
				h, m = divmod(m, 60)

				htxt = "hours" if h > 1 or h == 0 else "hour"
				mtxt = "minutes" if m > 1 or m == 0 else "minute"
				stxt = "seconds" if s > 1 or s == 0 else "seconds"

				t = "%02d %s, %02d %s, %02d %s" % (h, htxt, m, mtxt, s, stxt)
				bot.send(IRC_MSG_PRIVMSG, target, " :\t%s: %s ago | by %s" % (t, what, sen))
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
		from datetime import datetime, timezone
		tell = []
		try:
			with open("tell.tf", "rb") as f:
				d = pickle.load(f)
				tell = d["data"]
		except EOFError:
			pass

		if len(tell) > 0:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ": ")
			bot.send(IRC_MSG_PRIVMSG, target, " :%s | %s: %s" % ("Sender", "Date/Time", "Message"))
			for user, sen, what, date in tell:
				dt = datetime.now(timezone.utc)
				c = dt - date

				m, s = divmod(c.seconds, 60)
				h, m = divmod(m, 60)

				htxt = "hours" if h > 1 or h == 0 else "hour"
				mtxt = "minutes" if m > 1 or m == 0 else "minute"
				stxt = "seconds" if s > 1 or s == 0 else "seconds"

				t = "%02d %s, %02d %s, %02d %s" % (h, htxt, m, mtxt, s, stxt)
				bot.send(IRC_MSG_PRIVMSG, target, " :\t%s: %s ago | by %s" % (t, what, sen))
		else:
			bot.send(IRC_MSG_PRIVMSG, target, " :" + sender + ", there are no messages.")
