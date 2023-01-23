import telebot
import time
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import os

telebot_token = os.environ.get('TELEBOT_API_CARO')
bot = telebot.TeleBot(telebot_token)

a = 0

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, """Hello, my dear Caro, and welcome to your personal Telegram Bot! 🥰❤️😍
	
	Please choose a command from the list below:
	-------------------------------------------
	/help - show this help message

	/cats_every_min - send a cat photo every 1 minute
	/cats_every_hour - send a cat photo every 1 hour
	/stop - stop regularly sending cat photos (until you resume)

	/send_cats - immediately send 5 cat photos

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

	/send_cats - immediately send 5 cat photos

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



@bot.message_handler(commands=['cats_every_min', 'cats_every_hour'])
def cats_every_min(message):
	dict1 = {
		# 'cats_every_sec': 1, 
		'/cats_every_min':60, 
		'/cats_every_hour':3600
		}
	global a
	if a == 1:
		a = 0
		bot.send_message(message.chat.id, "Frequency of cat photos has been changed.")
	if a == 0:
		bot.send_message(message.chat.id, "Starting...")
		a = 1
		while a == 1:
			bot.send_message(message.chat.id, "Here's a photo of a cat and a quote!")
			full_quote2 = get_random_quote()
			bot.send_message(message.chat.id, full_quote2)
			r = requests.get('https://cataas.com/cat')
			img = Image.open(BytesIO(r.content))
			# img
			bot.send_photo(message.chat.id, img)
			time.sleep(dict1[message.text])
	# else:
	# 	bot.send_message(message.chat.id, "Already on!")

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
	global a
	if a == 1:
		bot.send_message(message.chat.id, "Stopping...")
		a = 0
	else:
		bot.send_message(message.chat.id, "Not running.")



def run():
	bot.polling(none_stop=True)
	# bot.infinity_polling()
# To run the program
if __name__ == '__main__':
	run()

