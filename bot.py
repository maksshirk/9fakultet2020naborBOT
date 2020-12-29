from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from telegram import  ReplyKeyboardMarkup, KeyboardButton
from handlers import get_contact, get_anecdote, sms, parrot, get_location
from settings import TG_TOKEN
from handlers import *
from bs4 import BeautifulSoup
from utility import get_keyboard
import requests
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def main():
    my_bot = Updater(TG_TOKEN)
    logging.info('Start_bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Анекдот'), get_anecdote))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.location, get_location))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Картинка'), send_meme))
    my_bot.dispatcher.add_handler(CallbackQueryHandler(inline_button_pressed))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Заполнить анкету'), anketa_start)],
                            states={
                                "user_name":    [MessageHandler(Filters.text, anketa_get_name)],
                                "user_age":     [MessageHandler(Filters.text, anketa_get_age)],
                                "evaluation":   [MessageHandler(Filters.regex('1|2|3|4|5'), anketa_get_evaluation)],
                                "comment":      [MessageHandler(Filters.regex('Пропустить'), anketa_exit_comment),
                                                 MessageHandler(Filters.text, anketa_comment)],
                                     },
                                     fallbacks=[MessageHandler(
                                            Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
                            )

                            )

    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling()
    my_bot.idle()

if __name__=="__main__":
    main()