import socket
import sys, os
import time
import random
import ast
from pws import Bing
from math import *

def tbytes(s):
	return s.encode("utf-8")

def parsemsg(s):
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

server = "irc.freenode.net"
channel = "#upbgecoders"
nick = "help_bot"
show_start_message = True

greetings = ["hi", "hi!", "hello", "hello!", "olá", "olá!", "ola", "ola!", "bonjour", "salut", "bonjour!", "salut!"]
rand_greet_suff = ["it's nice to see you!", ":)", ":D", ""]

questions = {
	"how are you": ["I'm fine, thanks!", "All gears working!", "Not in the mood for bad mood!"],
	"who are you": ["I'm " + nick + "! The UPBGE's Help Bot!", "I'm the UPBGE's Help Bot!"],
	"what can you do": ["I can do a lot of things. Inform new users, tell jokes, calculate big numbers, just type !cmdhelp"],
	"why did the chicken cross the road": ["To get to the other side.", "For fun.", "Out of common sense.", "You tell me.", "The chicken wanted to expose the myth of the road..."]
}

helpMessage = "If you are new to UPBGE, download it at https://download.upbge.org/, " + \
			"and check the docs and release notes at https://doc.upbge.org/. " + \
			"If you are a Python programmer, check out our Python API at https://pythonapi.upbge.org/, " + \
			"and If you want to help us with C/C++ stuff, look at the doxygen page at http://doxygen.upbge.org/. " + \
			"For issues/feature requests, see https://github.com/UPBGE/blender."

cmd_help_message = [
	"Each bot command must start with my name:",
	" !help : Shows general help for beginners.",
	" !cmdhelp : Shows this message.",
	" !calc : Calculator. Usage: !calc 1+1 or !calc sqrt(25).",
	" !tell : Saves a message for an offline user. The bot sends it when the user connects. Usage: !tell username: Message.",
	" !showtell : Shows a saved message from an user. Usage: !showtell username.",
	" !search : Search for a link on the internet using Bing. Usage: !search something, optionally you can choose the result index: !search something[2].",
	" !joke : Tells a joke."
]

start_messages = [
	"Hello everyone!",
	"Hello!",
	"Hi!",
	"Olá!",
	"Привет!",
	"Привіт!",
	"Здрасти!",
	"Salut!",
	"Bonjour à tous!",
	"Bună tuturor!"
]

jokes = [
	"A foo walks into a bar, takes a look around and says \"Hello World!\"",
	"Hide and seek champion ; since 1958",
	"Why did the programmer quit his job? Because he didn't get arrays. (a raise)",
	"\"Knock-Knock!\" \"Who's there?\" [long pause...] \"Java\"",
	"Hardware is what you can KICK, Software is what you can yell at.",
	"No Keyboard Detected. Press Any Key to Continue.",
	"To understand what recursion is, you must first understand recursion.",
	"Seven has the word 'even' in it, which is odd.",
	"How many programmers does it take to change a light bulb? None, it's a hardware problem.",
	"There’s no place like 127.0.0.1",
	"Unix is user-friendly. It's just picky about who its friends are.",
	"$ cat \"food in cans\" -> cat: can't open food in cans",
	"There are only 10 kinds of people in this world: those who know binary and those who don’t.",
	"Have you heard about the new Cray super computer? It’s so fast, it executes an infinite loop in 6 seconds.",
	"I don't see women as objects I see them in a class of her own."
]

tell = []

if not os.path.exists("tell.tf"):
	open("tell.tf", "w").close()

with open("tell.tf", "r") as f:
	lines = f.readlines()

	for line in lines:
		# name§what
		if "§" in line:
			name, what = line.split("§")
			name = name.strip(" ")
			what = what.strip(" ")
	
			tell.append((name, what))
print(tell)

# Calculator variables
ans = 0

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

irc.connect((server, 6667))
irc.send(tbytes("USER "+ nick +" "+ nick +" "+ nick +" :UPBGE's Help Bot\n"))
irc.send(tbytes("NICK "+ nick +"\n"))
irc.send(tbytes("PRIVMSG nickserv :iNOOPE\r\n"))
irc.send(tbytes("JOIN "+ channel +"\n"))

running = True
while running:
	text = irc.recv(2040).decode("utf-8")
	print(text.strip(" \n\r"))

	if text.find('PING') != -1:
		irc.send(tbytes('PONG ' + text.split() [1] + '\r\n'))
	
	msg = parsemsg(text)

	irc_cmd = msg[1].lower().strip(" ")
	sender = msg[0][:msg[0].rfind("!")].strip(" \n\r")
	
	if show_start_message:
		irc.send(tbytes("PRIVMSG " + channel + " :" + random.choice(start_messages) + "\r\n"))
		show_start_message = False

	if irc_cmd == "join":
		i = 0
		for totell in tell:
			nickname, what = totell
			if sender in nickname:
				irc.send(tbytes("PRIVMSG " + channel + " :" + nickname + ", "+ what +"\r\n"))
				del tell[i]
			i += 1

	if irc_cmd == "privmsg":
		cmd = msg[2][1].lower().strip(" \n\r")
		
		fromchannel = msg[2][0].startswith("#")
		to_cu = channel if fromchannel else sender
		
		for greeting in greetings:
			grets = [
				greeting + " " + nick.lower(),
				greeting + ", " + nick.lower(),
				greeting + "," + nick.lower(),
				nick.lower() + " " + greeting,
				nick.lower() + ", " + greeting,
				nick.lower() + "," + greeting
			]
			if cmd in grets:
				irc.send(tbytes("PRIVMSG " + channel + " :Hello, " + sender + " " + random.choice(rand_greet_suff) + "\r\n"))
				break
		for question in list(questions.keys()):
			qst = [
				question + " " + nick.lower() + "?",
				question + ", " + nick.lower() + "?",
				question + "," + nick.lower() + "?",
				nick.lower() + " " + question + "?",
				nick.lower() + ", " + question + "?",
				nick.lower() + "," + question + "?",
			]
			if cmd in qst:
				random_answer = random.choice(questions[question])
				irc.send(tbytes("PRIVMSG " + channel + " :" + sender + ", " + random_answer + "\r\n"))
				break

		n = nick.lower()
		if cmd.startswith(n):
			acmd = cmd[cmd.find(" ")+1:].strip(" :")
			if acmd == "!help":
				irc.send(tbytes("PRIVMSG " + sender + " :" + sender + ", " + helpMessage + "\r\n"))
			elif acmd == "!cmdhelp":
				for help_line in cmd_help_message:
					irc.send(tbytes("PRIVMSG " + sender + " :" + help_line + "\r\n"))
			elif acmd.startswith("!calc"):
				# !calc 1+1
				try:
					expr = acmd[5:].strip(" ")
					exec("ans = " + expr)
					irc.send(tbytes("PRIVMSG " + to_cu + " :" + sender + ", " + expr + " = " + str(ans) + "\r\n"))
				except:
					irc.send(tbytes("PRIVMSG " + to_cu + " :"+sender+", Sorry, that didn't work :-/\r\n"))
			elif acmd.startswith("!tell"):
				# !tell nick: Did you see this? ...
				if ":" in cmd:
					to = cmd[5:cmd.find(":")].strip(" ,")
					message = cmd[cmd.find(":")+1:].strip(" ,")
					tell.append((to, sender+" told you this: "+message))
					irc.send(tbytes("PRIVMSG " + to_cu + " :" + sender + ", Ok, I will tell.\r\n"))
			elif acmd.startswith("!showtell"):
				# !showtell nick
				to = acmd[9:].strip(" ,:")
				has_tell = False
				i = 0
				for t in tell:
					name, what = t
					if name == to:
						irc.send(tbytes("PRIVMSG " + sender + " :" + name + ", "+ what +"\r\n"))
						has_tell = True
						break
					i += 1
				if not has_tell:
					irc.send(tbytes("PRIVMSG " + to_cu + " :Sorry, I have nothing to tell :-/\r\n"))
			elif acmd == "!joke":
				random_joke = random.choice(jokes)
				irc.send(tbytes("PRIVMSG " + to_cu + " :" + random_joke + "\r\n"))
			elif acmd.startswith("!search"):
				# !search query [result_index = 0]
				query = acmd[7:].strip(" ,:")
				list_accessor = "[0]" if "[" not in cmd and "]" not in cmd else cmd[cmd.find("["):cmd.find("]")+1]
			
				try:
					ret = Bing.search(query, 5, 1)
					results = []
					for res in ret["results"]:
						link = res["link"]
						link_text = res["link_text"].title()
						results.append((link_text, link))

					if len(results) > 0:
						accs = "results"+list_accessor
						items = eval(accs)
						if isinstance(items, list):
							irc.send(tbytes("PRIVMSG " + to_cu + " :"+sender+":\r\n"))
							for item in items:
								irc.send(tbytes("PRIVMSG " + to_cu + " :\t"+ item[0] + " - " + item[1] + "\r\n"))
						else:
							irc.send(tbytes("PRIVMSG " + to_cu + " :"+sender+", " + items[0] + " - " + items[1] + "\r\n"))
					else:
						irc.send(tbytes("PRIVMSG " + to_cu + " :"+sender+", I didn't find anything about that :-/\r\n"))
				except:
					irc.send(tbytes("PRIVMSG " + to_cu + " :"+sender+", Sorry, that didn't work :-/\r\n"))
			elif acmd == "!quit":
				if sender == "TwisterGE":
					irc.send(tbytes("QUIT :Bye!\r\n"))
					running = False
	
	time.sleep(1.0 / 30)

irc.close()
with open("tell.tf", "w") as f:
	for t in tell:
		print("Writing...", t[0], t[1])
		f.write(t[0]+"§"+t[1]+"\n")
