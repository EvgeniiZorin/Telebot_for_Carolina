import telebot

import time
import threading
import schedule
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import os



telebot_token = os.environ.get('TELEBOT_API_CARO')
bot = telebot.TeleBot(telebot_token)

def read_file():
	with open('status.txt', 'r') as f:
		text = f.readline()
	return text

def write_to_file(switch:int):
	dict1 = {0:'not_running', 1:'running'}
	print(f"Switched to {dict1[switch]}")
	with open('status.txt', 'w') as f:
		f.write(dict1[switch])

# Initially, make sure that nothing is running as reflected in the 
# "status.txt" file
write_to_file(0)

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, """Hello, my dear Caro, and welcome to your personal Telegram Bot! 🥰❤️😍
	
	Please choose a command from the list below:
	-------------------------------------------
	/help - show this help message

	/cats_every_min - send a cat photo every 1 minute
	/cats_every_hour - send a cat photo every 1 hour
	/stop - stop regularly sending cat photos (until you resume)

	/send_cats - immediately send 3 cat photos

	/send_cat_text - send one cat photo with the text you write
	
	/quote - send a memorable quote""")

@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(message.chat.id, """A list of commands:
	-------------------------------------------
	/help - show this help message

	/cats_every_min - send a cat photo every 1 minute
	/cats_every_hour - send a cat photo every 1 hour
	/stop - stop regularly sending cat photos (until you resume)

	/send_cats - immediately send 3 cat photos

	/send_cat_text - send one cat photo with the text you write
	
	/quote - send a memorable quote""")

def get_random_quote() -> str:
	df = pd.read_csv("https://raw.githubusercontent.com/EvgeniiZorin/FILES_DATABASE/main/quotes_for_carolina.csv")
	quote = df.sample(1)
	quote_author, quote_text = list(quote['Author'])[0], list(quote['Quote'])[0]
	return f'"{quote_text}"\n - {quote_author}'


@bot.message_handler(commands=['quote'])
def send_quote(message):
	full_quote = get_random_quote()
	bot.send_message(message.chat.id, "Let me send you a quote:")
	bot.send_message(message.chat.id, full_quote)


def send_cat_photo(chat_id) -> None:
	bot.send_message(chat_id, "Here's a photo of a cat and a quote!")
	full_quote2 = get_random_quote()
	bot.send_message(chat_id, full_quote2)
	r = requests.get('https://cataas.com/cat')
	img = Image.open(BytesIO(r.content))
	# img
	bot.send_photo(chat_id, img)

@bot.message_handler(commands=[
	'cats_every_sec',
	'cats_every_min', 'cats_every_hour'
])
def cats_every_min(message):
	print(f' - start "{message.text}"')
	dict1 = {
		'/cats_every_sec':  5, 
		'/cats_every_min':  60, 
		'/cats_every_hour': 3600
		}
	dict1_str = {
		'/cats_every_sec':   '5 seconds', 
		'/cats_every_min':  '1 minute', 
		'/cats_every_hour': '1 hour'
	}
	# clear schedule first
	schedule.clear(message.chat.id)
	# first one message straight away
	send_cat_photo(message.chat.id)
	# restart the schedule
	print(message.text)
	schedule.every(dict1[message.text]).seconds.do(send_cat_photo, message.chat.id).tag(message.chat.id)



@bot.message_handler(commands=['send_cats'])
def send_cats(message):
	full_quote2 = get_random_quote()
	bot.send_message(message.chat.id, full_quote2)
	for i in range(3):
		r = requests.get('https://cataas.com/cat')
		img = Image.open(BytesIO(r.content))
		# img
		bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['send_cat_text'])
def send_cat_text(message):
	message1 = bot.send_message(message.chat.id, "Please enter text :)")
	bot.register_next_step_handler(message1, process_name_step)
def process_name_step(message):
	r = requests.get(f'https://cataas.com//cat/says/{message.text}')
	img = Image.open(BytesIO(r.content))
	bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['stop'])
def stop(message):
	schedule.clear(message.chat.id)

#################################################################################################

def beep(chat_id) -> None:
	"""Send the beep message."""
	bot.send_message(chat_id, text='Beep!')


@bot.message_handler(commands=['set'])
def set_timer(message):
	args = message.text.split()
	if len(args) > 1 and args[1].isdigit():
		sec = int(args[1])
		schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
	else:
		bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
	schedule.clear(message.chat.id)

#################################################################################################

def run():
	bot.polling(non_stop=True)
	# bot.infinity_polling()

# To run the program
if __name__ == '__main__':
	print('Start the bot!')
	# run()
	threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
	while True:
		schedule.run_pending()
		time.sleep(1)

