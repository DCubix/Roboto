import socket


IRC_MSG_PRIVMSG = "PRIVMSG"
IRC_MSG_NICK = "NICK"
IRC_MSG_JOIN = "JOIN"
IRC_MSG_AWAY = "AWAY"
IRC_MSG_BACK = "BACK"
IRC_MSG_PONG = "PONG"
IRC_MSG_PING = "PING"
IRC_MSG_USER = "USER"
IRC_MSG_QUIT = "QUIT"


class IRC:
	def __init__(self, server="irc.freenode.net", port=6667):
		self.server = server
		self.port = port

		self.__sock = None

	@property
	def sock(self):
		return self.__sock

	def connect(self):
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__sock.connect((self.server, self.port))

	def listen(self, bytes):
		return self.__sock.recv(bytes).decode("utf-8")

	def send(self, msgtype, to, message=""):
		tsend = (msgtype + " " + to + message + "\r\n").encode("utf-8")
		self.__sock.send(tsend)

	def join(self, channel):
		self.send(IRC_MSG_JOIN, channel, "")

	def quit(self):
		self.send(IRC_MSG_QUIT, "", ":Bye!")
		self.__sock.close()