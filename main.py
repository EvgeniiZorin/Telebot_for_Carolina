import telebot
import time
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



@bot.message_handler(commands=[
	'cats_every_sec',
	'cats_every_min', 'cats_every_hour'
])
def cats_every_min(message):
	print(' - start "cats_every_min"')
	dict1 = {
		'/cats_every_sec': 5, 
		'/cats_every_min':60, 
		'/cats_every_hour':3600
		}
	dict1_str = {
		'/cats_every_sec':   '5 seconds', 
		'/cats_every_min':  '1 minute', 
		'/cats_every_hour': '1 hour'
	}
	a = read_file()
	if a == 'running':
		stop(message)
		bot.send_message(message.chat.id, """To restart the regular photo sending, please enter the command again!""")
	else:
		bot.send_message(message.chat.id, f"Cat photos will be sent every {dict1_str[message.text]}!")
		write_to_file(1)
	a = read_file()
	while a == 'running':
		bot.send_message(message.chat.id, "Here's a photo of a cat and a quote!")
		full_quote2 = get_random_quote()
		bot.send_message(message.chat.id, full_quote2)
		r = requests.get('https://cataas.com/cat')
		img = Image.open(BytesIO(r.content))
		# img
		bot.send_photo(message.chat.id, img)
		time.sleep(dict1[message.text])
		a = read_file()
		if a == 'not_running':
			break


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
	a = read_file()
	write_to_file(0)
	if a == 'not_running':
		bot.send_message(message.chat.id, "No regular photo messaging is active.")
	else:
		bot.send_message(message.chat.id, "The regular photo sending has been stopped.")



def run():
	bot.polling(non_stop=True)
	# bot.infinity_polling()
# To run the program
if __name__ == '__main__':
	print('Start the bot!')
	run()

