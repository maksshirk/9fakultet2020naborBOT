import requests, telebot, os, telegram
from bs4 import BeautifulSoup
from telegram import KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, Updater, CallbackContext
from glob import glob
from random import choice
from utility import get_keyboard
from emoji import emojize
import datetime
import os
from settings import YANDEX_TOKEN
import folium

from mongodb import *

def sms(bot, update):
    search_or_save_user(mdb, bot.effective_user, bot.message)
    check_user = check_point(mdb, bot.effective_user)
    print(check_user)
    #    print(user)
    #    smile = emojize(choice(SMILE), use_aliases=True)
    bot.message.reply_text('Добрый день, {}!\nНачните работу с АСУ'.format(bot.message.chat.first_name), reply_markup=get_keyboard(check_user))


def parrot(bot, update):
    print('Кто-то отправил команду /start, что делать?')
    bot.message.reply_text(bot.message.text)


def get_contact(bot, update):
    print(bot.message.contact)
    bot.message.reply_text('{}, Мы получили ваш номер телефона'.format(bot.message.chat.first_name))

def facts_start(bot, update):
    check_user = check_point(mdb, bot.effective_user)
    if check_user == 1:
        bot.message.reply_text('Сначала введите данные для экстренной связи!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    time = datetime.datetime.now()
    hour = time.hour
    print(hour)
    minutes = time.strftime("%M")
    date = time.strftime("%d.%m.%Y")
    minutes = int(minutes) + 0
    print(minutes)
    if ((8 <= hour < 11) or (hour >= 19 and minutes >= 30 and hour <= 22)) == False:
        check_user = check_point(mdb, bot.effective_user)
        text = "Доклад осуществляется утром <b>с 8.00</b>\nи вечером <b>с 19:30</b>. Не раньше!!!\n<b>Московское время: </b>" + str(hour) + ":" + str(minutes) + "\n<b>Сегодня: </b>" + date
        bot.message.reply_text(text, reply_markup=get_keyboard(check_user), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    location_button = KeyboardButton('Здоров. Без происшествий и проблем, требующих вмешательств.', request_location=True)
    reply_keyboard = [['Здоров. Без происшествий и проблем, требующих вмешательств.'],
                      ["Имеются проблемы со здоровьем или другого характера"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите тип доклада',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "facts_choice"

def facts_choice(bot, update):
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Здоров. Без происшествий и проблем, требующих вмешательств.":
        update.user_data["problems"] = "Здоров. Без происшествий и проблем, требующих вмешательств."
        print(update.user_data["problems"])
        location_button = KeyboardButton('Отправить доклад!', request_location=True)
        reply_keyboard = [[location_button], ["Вернуться в меню!"]]
        bot.message.reply_text('Отправьте доклад',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "facts_ok"

    reply_keyboard = [["Вернуться в меню!"]]

    bot.message.reply_text('Напишите о своей проблеме и отправьте сообщение', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "facts_problems"

def facts_problems(bot, update):
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data["problems"] = bot.message.text
    location_button = KeyboardButton('Отправить доклад', request_location=True)
    reply_keyboard = [[location_button], ["Вернуться в меню!"]]
    bot.message.reply_text('Отправьте доклад!', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "facts_ok"

def facts_ok(bot, update):
    problems = update.user_data["problems"]
    print(update.user_data)
    get_location(bot, problems)
    print("Мы вернулись")
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def get_location(bot, problems):
    location = bot.message.location
    print(location)
    print(problems)
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    b = datetime.datetime.now()
    b = b.strftime("%d-%m-%Y")
    time = datetime.datetime.now()
    print(b)
    print(user)
    save_user_location(mdb, user, b, location, time, problems)
    print(user)
    return user


def get_anecdote(bot, update):
    receive = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(receive.text, "html.parser")
    find = page.select('.anekdot_text')
    for text in find:
        page = (text.getText().strip())
    bot.message.reply_text(page)


def quest_start(bot, update):
    reply_keyboard = [["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "quest_category"


def quest_category(bot, update):
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_category'] = bot.message.text
    if bot.message.text == "Кинофильмы":
        reply_keyboard = [["Чапаев (1934)"],
                          ["Повесть о настоящем человеке (1948)"],
                          ["Добровольцы (1958)"],
                          ["Обыкновенный фашизм (1965)"],
                          ["Офицеры (1972)"],
                          ["В бой идут одни старики (1973)"],
                          ["Они сражались за Родину (1975)"],
                          ["Брестская крепость (2010)"],
                          ["Легенда 17 (2013)"],
                          ["28 панфиловцев (2016)"],
                          ["Движение вверх (2017)"],
                          ["Время первых (2017)"],
                          ["Сто шагов (2019)"],
                          ["Ржев (2019)"],
                          ["Балканский рублеж (2019)"],
                          ["Лев Яшин. Вратарь моей мечты (2019)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите кинофильм',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    else:
        reply_keyboard = [["Русский характер. Толстой А.Н."],
                          ["Волоколамское шоссе. Бек А.А."],
                          ["Взять живым! Карпов В.В."],
                          ["Горячий снег. Бондарев Ю.В."],
                          ["В окопах Сталинграда. Некрасов В.П."],
                          ["Генералиссимус Суворов. Раковский Л.И."],
                          ["Василий Теркин. Твардовский А.Т."],
                          ["Навеки девятнадцатилетник. Бакланов Г.Я."],
                          ["Героев славных имена. Сборник очерков"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите книгу',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))

    return "quest_choice"

def quest_choice(bot, update):
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_title'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text('Загрузите фото! \nВнимание! Фото разрешено загружать только по 1 (одной) штуке. Если хотите несколько загрузить, проделайте процедуру несколько раз.',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "quest_download_photo"

def quest_download_photo(bot, update):
    print (bot.effective_user.id)

    user_id = bot.effective_user.id
    kursant_lastname = lastname(mdb, bot.effective_user)
    time = datetime.datetime.now()
    time = time.strftime("%d.%m.%Y %H-%M-%S")
    file = bot.message.photo[-1].get_file()
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    file = file.download(kursant_lastname + " " + update.user_data['quest_title'] + " " + time + " " + file_name[1])
    print(file)
    group = get_group(mdb, bot.effective_user)
    try:
        os.replace(file, "Report/" + update.user_data['quest_category'] + '/' + update.user_data['quest_title'] + "/" + group + "/" + file)
    except FileNotFoundError:
        os.makedirs("Report/" + update.user_data['quest_category'] + '/' + update.user_data['quest_title'] + "/" + group)
        os.replace(file, "Report/" + update.user_data['quest_category'] + '/' + update.user_data['quest_title'] + "/" + group + "/" + file)
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    report_category = update.user_data['quest_category']
    time = datetime.datetime.now()
    time = time.strftime("%d-%m-%Y %H-%M-%S")
    unit_report = update.user_data['quest_title']
    save_user_report(mdb, user, report_category, unit_report, time)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def quest_download_document(bot, update):
    print(update.user_data['title'])
    user = bot.message.from_user
    print(user.last_name)
    file = bot.message.document.get_file()
    print(file.file_path)
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    print(file_name[1])
    print(file_extension[1])
    file = file.download(update.user_data['user_lastname'] + " " + update.user_data['title'] + file_name[1])
    print(file)
    try:
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ update.user_data['group'] + "/"+ file)
    except FileNotFoundError:
        os.makedirs("Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/" + update.user_data['group'])
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/" + update.user_data['group'] + "/" + file)

    bot.message.reply_text('Great!')
    print("Круто")

def user_start(bot, update):
    print(bot._effective_message.bot.get_chat_member(chat_id='-1001371757648', user_id=bot.message.from_user.id).status)
    print("Он представился")
    check_user = check_point(mdb, bot.effective_user)
    if bot._effective_message.bot.get_chat_member(chat_id='-1001371757648', user_id=bot.message.from_user.id).status != "left":
       print("Все норм")
    else:
        bot.message.reply_text(
            "Вам для начала необходимо присоединиться к каналу, ссылку которого получите от командира",
            reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    reply_keyboard = [["Курсовое звено"],
                      ["901", "903"],
                      ["904", "905-1"],
                      ["905-2", "906"]]
    bot.message.reply_text('Ваше подразделение?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "user_group"

def user_get_group(bot, update):
    update.user_data['user_group'] = bot.message.text
    if bot.message.text == "Курсовое звено":
        reply_keyboard = [["Начальник курса"],
                          ["Курсовой офицер"],
                          ["Старшина курса"]]
        bot.message.reply_text('Ваша должность?',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "user_unit_officer"
    else:
        print("Я тут")
        reply_keyboard = [["Командир учебной группы"],
                      ["Командир 1 отделения","Командир 2 отделения","Командир 3 отделения"],
                      ["Курсант 1-го отделения", "Курсант 2-го отделения", "Курсант 3-го отделения"]]
        bot.message.reply_text('Ваша должность?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
        return "user_unit"

def user_get_unit(bot, update):
    update.user_data['user_unit'] = bot.message.text
    bot.message.reply_text("Ваша фамилия?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname"

def user_get_unit_officer(bot, update):
    print("Я тут")
    update.user_data['user_unit'] = bot.message.text
    bot.message.reply_text("Ваша фамилия?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname"

def user_get_lastname(bot, update):
    update.user_data['user_lastname'] = bot.message.text
    bot.message.reply_text("Ваше имя?", reply_markup=ReplyKeyboardRemove())
    return "user_name"


def user_get_name(bot, update):
    update.user_data['user_name'] = bot.message.text
    bot.message.reply_text("Ваше отчество?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename"

def user_get_middlename(bot, update):
    update.user_data['user_middlename'] = bot.message.text
    button_phone = KeyboardButton('Отправить номер телефона', request_contact=True)
    reply_keyboard = [button_phone]
    bot.message.reply_text("Ваш номер телефона? Внимание, телефон отправляется автоматически после нажатия кнопки!",
                           reply_markup=ReplyKeyboardMarkup([reply_keyboard], resize_keyboard=True,
                                                                one_time_keyboard=True))
    print("Тут норм")
    return "user_phone"

def user_get_phone(bot, update):

    update.user_data['user_phone'] = bot.message.contact.phone_number
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    print(update.user_data)
    save_kursant_anketa(mdb, user, update.user_data)
    print(bot.message.contact)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Приветствую, {}!\nТеперь Ваши данные на проверке!\nНо Вы уже можете приступить к выполнению служебных заданий.".format(bot.message.chat.first_name), reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def report_start(bot, update):
    check_user = check_point(mdb, bot.effective_user)
    if bot._effective_message.bot.get_chat_member(chat_id='-1001371757648', user_id=bot.message.from_user.id).status != "left":
        print("Все норм")
    else:
        bot.message.reply_text(
            "Вы не состоите в канале",
            reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    reply_keyboard = [["1. Отпускной билет (постановка на учет)"],
                      ["2. Бланк инструктажа (подпись родителей на обратной стороне)"],
                      ["3. Письмо родителям (подпись родителей на обратной стороне)"],
                      ["4. Служебное задания (проагитированные курсанты)"],
                      ["5. Отпускной билет (снятие с учета)"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите документ!',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))

    return "report_get"

def report_get(bot, update):
    print(bot.message.text == "Вернуться в меню!")
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    else:
        reply_keyboard = [["Вернуться в меню!"]]
        bot.message.reply_text('Загрузите фото! \nВнимание! Фото разрешено загружать только по 1 (одной) штуке. Если хотите несколько загрузить, проделайте процедуру несколько раз.',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        update.user_data['report_group'] = bot.message.text
    return "report_group"

def report_menu(bot, update):
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Вы вернулись в меню!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def report_photo(bot, update):

    print(bot.message.chat.id)
    user_id = str(bot.message.chat.id)
    print(type(user_id))
    file = bot.message.photo[-1].get_file()
    print(file.file_path)
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    print(file_name[1])
    print(file_extension[1])
    print(lastname(mdb, bot.effective_user))
    kursant_lastname = lastname(mdb, bot.effective_user)
    time = datetime.datetime.now()
    time = time.strftime("%d.%m.%Y %H-%M-%S")
    print(time)
    update.user_data['report_group'] = update.user_data['report_group'].replace('+', '')
    file = file.download(kursant_lastname + " " + user_id + " " + update.user_data['report_group'] + " " + time + " " + file_name[1])
    print(file)
    print(update.user_data['report_group'])
    group = get_group(mdb, bot.effective_user)
    print(update.user_data['report_group'])
    try:
        print("здесь")
        print("Report/" + update.user_data['report_group'] + "/" + group + "/" + file)
        os.replace(file, "Report/" + update.user_data['report_group'] + "/" + group + "/" + file)
    except FileNotFoundError:
        print("а не здесь")
        os.makedirs("Report/" + update.user_data['report_group'] + "/" + group)
        try: os.replace(file, "Report/" + update.user_data['report_group'] + "/" + group + "/" + file)
        except Exception as ex:
            print(ex)
    user = search_or_save_user(mdb, bot.effective_user, bot.message)

    report_category = "Отчеты"

    print("Тут ошибка")
    unit_report = update.user_data['report_group']
    save_user_report(mdb, user, report_category, unit_report, time)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def anketa_start(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    reply_keyboard = [["Пропустить ввод данных матери (мачехи, опекуншы)"],["Вернуться в меню!"]]
    bot.message.reply_text('Введите фамилию матери (мачехи, опекуншы) либо перейдите к вводу данных отца (отчима, опекуна)', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_mother"

def anketa_get_lastname_mother(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Пропустить ввод данных матери (мачехи, опекуншы)":
        reply_keyboard = [["Пропустить ввод данных отца (отчима, опекуна)"], ["Вернуться в меню!"]]
        bot.message.reply_text(
            'Введите фамилию отца (отчима, опекуна) либо перейдите к вводу данных друга (брата, сестры, подруги, девушки)', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
        update.user_data['user_lastname_mother'] = "Отсутствует"
        update.user_data['user_name_mother'] = "Отсутствует"
        update.user_data['user_middlename_mother'] = "Отсутствует"
        update.user_data['user_address_mother'] = "Отсутствует"
        update.user_data['user_phone_mother'] = "Отсутствует"
        return "user_lastname_father"
    update.user_data['user_lastname_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Имя Вашей матери (мачехи, опекуншы)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_name_mother"


def anketa_get_name_mother(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашей матери (мачехи, опекуншы)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_mother"


def anketa_get_middlename_mother(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашей матери (мачехи, опекуншы)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_mother"


def anketa_get_phone_mother(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашей матери (мачехи, опекуншы)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_mother"


def anketa_get_address_mother(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_address_mother'] = bot.message.text
    reply_keyboard = [["Пропустить ввод данных отца (отчима, опекуна)"], ["Вернуться в меню!"]]
    bot.message.reply_text('Введите фамилию отца (отчима, опекуна) либо перейдите к вводу данных друга (брата, сестры, подруги, девушки)', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_father"


def anketa_get_lastname_father(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    if bot.message.text == "Пропустить ввод данных отца (отчима, опекуна)":
        reply_keyboard = [["Вернуться в меню!"]]
        bot.message.reply_text("Фамилия Вашего друга (брата, сестры, подруги, девушки)?",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        update.user_data['user_lastname_father'] = "Отсутствует"
        update.user_data['user_name_father'] = "Отсутствует"
        update.user_data['user_middlename_father'] = "Отсутствует"
        update.user_data['user_address_father'] = "Отсутствует"
        update.user_data['user_phone_father'] = "Отсутствует"
        return "user_lastname_other"
    update.user_data['user_lastname_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Имя Вашего отца (отчима, опекуна)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_name_father"


def anketa_get_name_father(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашего отца (отчима, опекуна)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_father"


def anketa_get_middlename_father(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашего отца (отчима, опекуна)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_father"


def anketa_get_phone_father(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашего отца (отчима, опекуна)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_father"


def anketa_get_address_father(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_address_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Фамилия Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_other"


def anketa_get_lastname_other(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_lastname_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Имя Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_name_other"


def anketa_get_name_other(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_other"


def anketa_get_middlename_other(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_other"


def anketa_get_phone_other(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашего друга (брата, сестры, подруги, девушки)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_other"


def anketa_get_address_other(bot, update):
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_address_other'] = bot.message.text
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    anketa = save_user_anketa(mdb, user, update.user_data)
    print("почти конец")
    print(anketa)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text('Введенные данные отправлены на проверку!', reply_markup=get_keyboard(check_user))
    return ConversationHandler.END


def anketa_comment(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    anketa = save_user_anketa(mdb, user, update.user_data)
    print(anketa)

    update.user_data['comment'] = bot.message.text
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}
    <b>Комментарий:</b> {comment}
    """.format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)
    bot.message.reply_text("Спасибо Вам за комментарий!", reply_markup=get_keyboard())
    return ConversationHandler.END


def anketa_exit_comment(bot, update):
    update.user_data['comment'] = None
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    save_user_anketa(mdb, user, update.user_data)

    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}
    """.format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)
    bot.message.reply_text("Спасибо!", reply_markup=get_keyboard())
    return ConversationHandler.END


def dontknow(bot, update):
    bot.message.reply_text("Я Вас не понимаю, выберите оценку на клавиатуре!")


def send_meme(bot, update):
    lists = glob('images/*')
    picture = choice(lists)
    inl_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton('👍', callback_data="1"),
        InlineKeyboardButton('👎', callback_data="-1")
    ]])
    update.bot.send_photo(
        chat_id=bot.message.chat.id,
        photo=open(picture, 'rb'),
        reply_markup=inl_keyboard)


def inline_button_pressed(bot, update):
    print(bot.callback_query)
    query = bot.callback_query
    update.bot.edit_message_caption(
        caption='Спасибо Вам за выбор!',
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)

def test_bd(bot, update):
    print("Запуск")
    d = check_point(mdb, bot.effective_user)
    print(d['Present']['check_present'])
    return 0

def report(bot, update):
    user_group = check_group(mdb, bot.effective_user)
    user_unit = check_unit(mdb, bot.effective_user)
    user_lastname = lastname(mdb, bot.effective_user)
    if user_unit == "Начальник курса":
        user_group = "91 курс"
        kursant_unit = "Все"
    if user_unit == "Старшина курса":
        user_group = "91 курс"
        kursant_unit = "Все"
    if user_lastname == "Широкопетлев":
        user_group = "91 курс"
        kursant_unit = "Все"
    if user_lastname == "Кольцов":
        user_group = "91 курс"
        kursant_unit = "Все"
    if user_unit == "Командир 1 отделения":
        kursant_unit = "Курсант 1-го отделения"
    if user_unit == "Командир 2 отделения":
        kursant_unit = "Курсант 2-го отделения"
    if user_unit == "Командир 3 отделения":
        kursant_unit = "Курсант 3-го отделения"
    print("На этом пока всё!")
    print(user_group)
    print(kursant_unit)
    find_report(bot, mdb, user_group, kursant_unit)
    print("На этом пока всё!")






def get_address_from_coords(coords):
    #заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    print("тут")
    PARAMS = {
        "apikey": YANDEX_TOKEN,
        "format":"json",
        "lang":"ru_RU",
        "kind":"house",
        "geocode": coords
    }

    #отправляем запрос по адресу геокодера.
    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        #получаем данные
        json_data = r.json()
        #вытаскиваем из всего пришедшего json именно строку с полным адресом.
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        #возвращаем полученный адрес
        return address_str
    except Exception as e:
        #если не смогли, то возвращаем ошибку
        return "error"


