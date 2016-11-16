import sys
from core.bot import *

bot = Bot(name="upbge_bot", info="UPBGE's Help Bot")
try:
	bot.start("#upbgecoders")
except KeyboardInterrupt:
	bot.quit()
	sys.exit(0)