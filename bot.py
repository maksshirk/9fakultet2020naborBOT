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
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Рейтинг курса по индивидуальным заданиям'), get_user_rating))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Обновить рейтинг И.З. Отключает бот на 30 минут'), get_rating))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Обновить рейтинг докладов. Отключает бот на 1 минуту'), get_rating_facts))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Рейтинг курса по представлению докладов о состоянии дел'), get_user_rating_facts))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Принять доклад о состоянии дел'), report))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Принять доклад у курсантов о состоянии дел'), report_group))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Показать обстановку на карте'), create_map))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Учет проверенных работ офицерами/курсантами 5 курса'), check_officer))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Учет проверенных работ курсантами'), check_kursants))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Проверить доклад'), check_doklad)],
                            states={
                                # Фамилия курсанта
                                "type_doklad": [MessageHandler(Filters.text, type_doklad)],
                                "choice_doklad": [MessageHandler(Filters.text, choice_doklad)],
                                "zagruzka_v_bd": [MessageHandler(Filters.text, zagruzka_v_bd)],
                                "zagruzka_v_bd_problem": [MessageHandler(Filters.text, zagruzka_v_bd_problem)],
                                "poehali": [MessageHandler(Filters.text, poehali)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Проверить работы'), check_doklad_kursant)],
                            states={
                                # Фамилия курсанта
                                "type_doklad_kursant": [MessageHandler(Filters.text, type_doklad_kursant)],
                                "choice_doklad_kursant": [MessageHandler(Filters.text, choice_doklad_kursant)],
                                "zagruzka_v_bd_kursant": [MessageHandler(Filters.text, zagruzka_v_bd_kursant)],
                                "zagruzka_v_bd_problem_kursant": [MessageHandler(Filters.text, zagruzka_v_bd_problem_kursant)],
                                "poehali_kursant": [MessageHandler(Filters.text, poehali_kursant)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Проверить статус докладов'), get_rock)],
                            states={
                                # Фамилия курсанта
                                "get_report": [MessageHandler(Filters.regex("Отчеты|Кинофильмы|Литературные произведени|Математический анализ|Аналитическая геометрия и линейная алгебра|Вернуться в меню!"), get_report)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Руководящие документы, ссылки, материалы и виды отчетов'), get_help)],
                            states={
                                # Фамилия курсанта
                                "get_type_help": [MessageHandler(Filters.text, get_type_help)],
                                "get_choice_help": [MessageHandler(Filters.text, get_choice_help)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Рейтинги по категориям'), get_rating_category)],
                            states={
                                # Фамилия курсанта
                                "get_type_rating": [MessageHandler(Filters.text, get_choice_rating)],
                                "get_choice_rating": [MessageHandler(Filters.text, get_choice_rating)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
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
                                    "user_phone": [MessageHandler(Filters.contact, user_get_phone)],
                                    "exit": [MessageHandler(Filters.text, exit)]
                                         },
                                         fallbacks=[CommandHandler('sos', sos)]
                                )

                                )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Изменить данные о себе (в случае ошибки)'), user_start)],
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
                                "user_phone": [MessageHandler(Filters.contact, user_get_phone)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )
    )

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('1. Отчеты'), report_start)],
                            states={
                                # Фамилия курсанта
                                "report_get": [MessageHandler(Filters.text, report_get)],
                                "report_group": [MessageHandler(Filters.photo, report_photo)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )
    )

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('2. Индивидуальные задания'), quest_start)],
                            states={
                                "quest_category": [MessageHandler(Filters.text, quest_category)],
                                "quest_choice": [MessageHandler(Filters.text, quest_choice)],
                                "quest_download_photo": [MessageHandler(Filters.photo, quest_download_photo)],
                                # Имя курсанта
                                "quest_download_document": [MessageHandler(Filters.document, quest_download_document)],
                                "exit": [MessageHandler(Filters.text, exit)]
                                # Имя курсанта
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Тест'), test_start)],
                            states={
                                "facts_choice": [MessageHandler(Filters.text, facts_choice)],
                                "facts_ok": [MessageHandler(Filters.location, facts_ok)],
                                "facts_problems": [MessageHandler(Filters.text, facts_problems)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            ))
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[CommandHandler('report', facts_start)],
                            states={
                                "facts_choice": [MessageHandler(Filters.text, facts_choice)],
                                "facts_ok": [MessageHandler(Filters.location, facts_ok)],
                                "facts_problems": [MessageHandler(Filters.text, facts_problems)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Доклад о состоянии дел'), facts_start)],
                            states={
                                "facts_choice": [MessageHandler(Filters.text, facts_choice)],
                                "facts_ok": [MessageHandler(Filters.location, facts_ok)],
                                "facts_problems": [MessageHandler(Filters.text, facts_problems)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )
    )
    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex('Ввести адреса проведения отпуска'), lets_go)],
                            states={
                                "put_address_from_coords": [MessageHandler(Filters.text, put_address_from_coords)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
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
                                "user_address_other": [MessageHandler(Filters.text, anketa_get_address_other)],
                                "exit": [MessageHandler(Filters.text, exit)]
                                     },
                                     fallbacks=[CommandHandler('sos', sos)]
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
                                "user_address_other": [MessageHandler(Filters.text, anketa_get_address_other)],
                                "exit": [MessageHandler(Filters.text, exit)]
                            },
                            fallbacks=[CommandHandler('sos', sos)]
                            )

    )

    my_bot.start_polling()
    my_bot.idle()

if __name__=="__main__":
    main()

def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"', update, error)

