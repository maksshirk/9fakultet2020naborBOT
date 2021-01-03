from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import  ReplyKeyboardMarkup, KeyboardButton
from handlers import get_contact, get_anecdote, sms, parrot, get_location
from settings import TG_TOKEN
from handlers import *
from bs4 import BeautifulSoup
from utility import get_keyboard
import requests
import logging
import telebot, telepot
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )



def main():

    my_bot = Updater(TG_TOKEN)
    logging.info('Start_bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.location, get_location))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Отчеты по И.З.'), quest_start)],
                            states={
                                # Фамилия курсанта
                                "quest_category": [MessageHandler(Filters.text, quest_category)],
                                # Имя курсанта
                                "quest_choice": [MessageHandler(Filters.text, quest_choice)],
                                # Фамилия курсанта
                                "quest_select": [MessageHandler(Filters.text, quest_select)],
                                # Имя курсанта
                                "quest_download_photo": [MessageHandler(Filters.photo, quest_download_photo)],
                                # Имя курсанта
                                "quest_download_document": [MessageHandler(Filters.document, quest_download_document)]
                                # Имя курсанта
                            },
                            fallbacks=[])
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Регистрация'), anketa_start)],
                            states={
                                # Фамилия курсанта
                                "user_group": [MessageHandler(Filters.text, anketa_get_group)],
                                # Имя курсанта
                                "user_position": [MessageHandler(Filters.text, anketa_get_position)],
                                # Фамилия курсанта
                                "user_lastname":    [MessageHandler(Filters.text, anketa_get_lastname)],
                                # Имя курсанта
                                "user_name":     [MessageHandler(Filters.text, anketa_get_name)],
                                # Отчество курсанта
                                "user_middlename":     [MessageHandler(Filters.text, anketa_get_middlename)],
                                # Телефон курсанта
                                "user_phone": [MessageHandler(Filters.text, anketa_get_phone)],
                                # Адрес проведения отпуска курсанта
                                "user_address": [MessageHandler(Filters.text, anketa_get_address)],
                                #Фамилия матери курсанта
                                "user_lastname_mother": [MessageHandler(Filters.text, anketa_get_lastname_mother)],
                                # Имя матери курсанта
                                "user_name_mother": [MessageHandler(Filters.text, anketa_get_name_mother)],
                                # Отчество матери курсанта
                                "user_middlename_mother": [MessageHandler(Filters.text, anketa_get_middlename_mother)],
                                # Телефон матери курсанта
                                "user_phone_mother": [MessageHandler(Filters.text, anketa_get_phone_mother)],
                                # Адрес матери
                                "user_address_mother": [MessageHandler(Filters.text, anketa_get_address_mother)],
                                # Фамилия отца курсанта
                                "user_lastname_father": [MessageHandler(Filters.text, anketa_get_lastname_father)],
                                # Имя отца курсанта
                                "user_name_father": [MessageHandler(Filters.text, anketa_get_name_father)],
                                # Отчество отца курсанта
                                "user_middlename_father": [MessageHandler(Filters.text, anketa_get_middlename_father)],
                                # Телефон отца курсанта
                                "user_phone_father": [MessageHandler(Filters.text, anketa_get_phone_father)],
                                # Адрес отца
                                "user_address_father": [MessageHandler(Filters.text, anketa_get_address_father)],
                                # Фамилия друга (брата, сестры) курсанта
                                "user_lastname_other": [MessageHandler(Filters.text, anketa_get_lastname_other)],
                                # Имя друга (брата, сестры) курсанта
                                "user_name_other": [MessageHandler(Filters.text, anketa_get_name_other)],
                                # Отчество друга (брата, сестры) курсанта
                                "user_middlename_other": [MessageHandler(Filters.text, anketa_get_middlename_other)],
                                # Телефон друга (брата, сестры) курсанта
                                "user_phone_other": [MessageHandler(Filters.text, anketa_get_phone_other)],
                                # Адрес друга (брата, сестры)
                                "user_address_other": [MessageHandler(Filters.text, anketa_get_address_other)]
                                     },
                                     fallbacks=[MessageHandler(
                                            Filters.text | Filters.video | Filters.photo | Filters.document, dontknow)]
                            )

                            )
    my_bot.start_polling()
    my_bot.idle()

if __name__=="__main__":
    main()