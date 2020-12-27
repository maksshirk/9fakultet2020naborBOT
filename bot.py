from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import  ReplyKeyboardMarkup
from settings import TG_TOKEN
from bs4 import BeautifulSoup
import requests

def sms(bot, update):
    print('Кто то отправил команду')

    my_keyboard = ReplyKeyboardMarkup([['Анекдот'],['Начать']], resize_keyboard=True)
    bot.message.reply_text('Привет, {}'.format(bot.message.chat.first_name), reply_markup=my_keyboard)
    print(bot.message)

def parrot(bot, update):
    print('Кто-то отправил команду /start, что делать?')
    bot.message.reply_text(bot.message.text)

def get_anecdote(bot, update):
    receive = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(receive.text, "html.parser")
    find = page.select('.anekdot_text')
    for text in find:
        page = (text.getText().strip())
    bot.message.reply_text(page)

def main():
    my_bot = Updater(TG_TOKEN)

    my_bot.dispatcher.add_handler(CommandHandler('start', sms))

    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Начать'), sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Анекдот'),get_anecdote))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text,parrot))
    my_bot.start_polling()
    my_bot.idle()

main()