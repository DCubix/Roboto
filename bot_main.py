import sys
from core.bot import *
# from core.cmd import Cmd

bot = Bot(name="upBot", info="UPBGE's Bot")
try:
	bot.start("#upbgecoders")
except KeyboardInterrupt:
	bot.quit()
	sys.exit(0)
c = Cmd()
# c.parse_command("!tell user, \"Hello, this is a quoted string\", this is what hapens, in this")