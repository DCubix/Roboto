import sys
from core.bot import *
from core.command import parse_command

bot = Bot(name="upBot", info="UPBGE's Bot")
try:
	bot.start("#upbgecoders")
except KeyboardInterrupt:
	bot.quit()
	sys.exit(0)
#parse_command("!tell user, \"a, b\", hi, 42, 3.14, 2+d")
