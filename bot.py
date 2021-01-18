import logging

from telegram.ext import CommandHandler, MessageHandler, Filters

from handlers import *
from mongodb import *
from settings import TG_TOKEN

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )



def main():
    my_bot = Updater(TG_TOKEN)
    logging.info('Start_bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Принять доклад о состоянии дел'), report))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Показать обстановку на карте'), create_map))
    my_bot.dispatcher.add_handler(CommandHandler('test_bd', test_bd))
    my_bot.dispatcher.add_handler(
            ConversationHandler(entry_points=[MessageHandler(Filters.regex('Представиться'), user_start)],
                                states={
                                    # Фамилия курсанта
                                    "user_group": [MessageHandler(Filters.text, user_get_group)],
                                    # Фамилия курсанта
                                    "user_unit": [MessageHandler(Filters.text, user_get_unit)],
                                    "user_unit_officer": [MessageHandler(Filters.text, user_get_unit_officer)],
                                    "user_lastname":    [MessageHandler(Filters.text, user_get_lastname)],
                                    # Имя курсанта
                                    "user_name":     [MessageHandler(Filters.text, user_get_name)],
                                    # Отчество курсанта
                                    "user_middlename":     [MessageHandler(Filters.text, user_get_middlename)],
                                    "user_phone": [MessageHandler(Filters.contact, user_get_phone)]
                                         },
                                         fallbacks=[]
                                )

                                )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Изменить ранее введенные данные (в случае ошибки)'), user_start)],
                            states={
                                # Фамилия курсанта
                                "user_group": [MessageHandler(Filters.text, user_get_group)],
                                # Фамилия курсанта
                                "user_unit": [MessageHandler(Filters.text, user_get_unit)],
                                "user_unit_officer": [MessageHandler(Filters.text, user_get_unit_officer)],
                                "user_lastname": [MessageHandler(Filters.text, user_get_lastname)],
                                # Имя курсанта
                                "user_name": [MessageHandler(Filters.text, user_get_name)],
                                # Отчество курсанта
                                "user_middlename": [MessageHandler(Filters.text, user_get_middlename)],
                                "user_phone": [MessageHandler(Filters.contact, user_get_phone)]
                            },
                            fallbacks=[CommandHandler('start', report_menu)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('1. Отчеты'), report_start)],
                            states={
                                # Фамилия курсанта
                                "report_get": [MessageHandler(Filters.text, report_get)],
                                "report_group": [MessageHandler(Filters.photo, report_photo)]
                            },
                            fallbacks=[CommandHandler('start', report_menu)]
                            )
    )

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('2. Индивидуальные задания'), quest_start)],
                            states={
                                "quest_category": [MessageHandler(Filters.text, quest_category)],
                                "quest_choice": [MessageHandler(Filters.text, quest_choice)],
                                "quest_download_photo": [MessageHandler(Filters.photo, quest_download_photo)],
                                # Имя курсанта
                                "quest_download_document": [MessageHandler(Filters.document, quest_download_document)]
                                # Имя курсанта
                            },
                            fallbacks=[CommandHandler('start', report_menu)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Доклад о состоянии дел'), facts_start)],
                            states={
                                "facts_choice": [MessageHandler(Filters.text, facts_choice)],
                                "facts_ok": [MessageHandler(Filters.location, facts_ok)],
                                "facts_problems": [MessageHandler(Filters.text, facts_problems)]
                            },
                            fallbacks=[CommandHandler('start', report_menu)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Ввести адреса проведения отпуска'), lets_go)],
                            states={
                                "put_address_from_coords": [MessageHandler(Filters.text, put_address_from_coords)]
                            },
                            fallbacks=[CommandHandler('start', report_menu)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Ввести данные для связи в случае отсутствия доклада'), anketa_start)],
                            states={
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
                                     fallbacks=[CommandHandler('start', report_menu)]
                            )

                            )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[
            MessageHandler(Filters.regex('Изменить данные для связи в случае отсутствия доклада'), anketa_start)],
                            states={
                                # Фамилия матери курсанта
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
                            fallbacks=[CommandHandler('start', report_menu)]
                            )

    )
    my_bot.start_polling()
    my_bot.idle()

if __name__=="__main__":
    main()