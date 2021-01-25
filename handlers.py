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
import uuid
from mongodb import *
from array import *

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
    SOS(bot)
    print(bot.message.contact)
    bot.message.reply_text('{}, Мы получили ваш номер телефона'.format(bot.message.chat.first_name))

def SOS(bot):
    if bot.message.text == "/sos":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END

def facts_start(bot, update):
    SOS(bot)
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
    if ((7 <= hour < 11) or  (18 <= hour <= 22)) == False:
        check_user = check_point(mdb, bot.effective_user)
        text = "Доклад осуществляется утром <b>с 7.00</b>\nи вечером <b>с 18:00</b>. Не раньше!!!\n<b>Московское время: </b>" + str(hour) + ":" + str(minutes) + "\n<b>Сегодня: </b>" + date
        bot.message.reply_text(text, reply_markup=get_keyboard(check_user), parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    reply_keyboard = [['Здоров. Без происшествий и проблем, требующих вмешательств.'],
                      ["Имеются проблемы со здоровьем или другого характера"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите тип доклада',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "facts_choice"

def facts_choice(bot, update):
    SOS(bot)
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
        bot.message.reply_text('Отправьте доклад. Внимание внизу имеется кнопку. Нажмите на неё, иначе ничего не получится',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "facts_ok"

    reply_keyboard = [["Вернуться в меню!"]]

    bot.message.reply_text('Напишите о своей проблеме и отправьте сообщение', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "facts_problems"

def facts_problems(bot, update):
    SOS(bot)
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
    SOS(bot)
    problems = update.user_data["problems"]
    print(update.user_data)
    get_location(bot, problems)
    print("Мы вернулись")
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def get_location(bot, problems):
    SOS(bot)
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
    SOS(bot)
    receive = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(receive.text, "html.parser")
    find = page.select('.anekdot_text')
    for text in find:
        page = (text.getText().strip())
    bot.message.reply_text(page)


def quest_start(bot, update):
    SOS(bot)
    reply_keyboard = [["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "quest_category"


def quest_category(bot, update):
    SOS(bot)
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
                          ["Жила-была девочка (1944)"],
                          ["Мы смерти смотрели в лицо (1980)"],
                          ["Порох (1985)"],
                          ["Зимнее утро (1966)"],
                          ["Блокада (1973-1977)"],
                          ["Коридор бессмертия (2019)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите кинофильм',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Математический анализ":
        reply_keyboard = [["Задание 1 Область определения функции и логарифма"],
                          ["Задание 2, 3, 4 Построение графика функции"],
                          ["Задание 5 Четность и нечетность функции"],
                          ["Задание 6 Экстремумы функции без использования производной"],
                          ["Задание 7 Периодические функции"],
                          ["Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя"],
                          ["Задания 14 15 Непрерывность функции и точки разрыва"],
                          ["Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций"],
                          ["Задание 18 Значение производной в данной точке"],
                          ["Задание 23 Приближенные вычисления с помощью производной"],
                          ["Задание 24 Производная функции, заданной параметрическим способом"],
                          ["Задания 25, 28 Производная неявной функции"],
                          ["Задание 26 Уравнение касательной и нормали к графику функции"],
                          ["Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба"],
                          ["Задание 29 Правило Лопиталя"],
                          ["Задание 30 Нахождение асимптот графиков функций"],
                          ["Задание 31 Нахождение интервалов монотонности"],
                          ["Задание 32 Экстремумы фнукций"],
                          ["Задание 34,34 Исследование функции, применение производной к построению графиков функций"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Аналитическая геометрия и линейная алгебра":
        reply_keyboard = [["Задание 1-4 Задача 1-1 Комплексные числа"],
                          ["Задание 1-4 Задача 1-2 Разложение на множители"],
                          ["Задание 3-5 Задача 3-1 Векторы, их произведения"],
                          ["Задание 3-5 Задача 3-2 Длина и угол между векторами"],
                          ["Задание 4-2 Задача 4-1 Уравнение прямой"],
                          ["Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки"],
                          ["Задание 6-2 Задача 6-2 Уравнение параллельной прямой"],
                          ["Задание 6-2 Задача 6-3 Уравнение плоскости"],
                          ["Задание 6-2 Задача 6-7 Проекция точки на плоскость"],
                          ["Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка"],
                          ["Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы"],
                          ["Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите индивидуальное задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    else:
        reply_keyboard = [["Русский характер. Толстой А.Н."],
                          ["Волоколамское шоссе. Бек А.А."],
                          ["Взять живым! Карпов В.В."],
                          ["Горячий снег. Бондарев Ю.В."],
                          ["Генералиссимус Суворов. Раковский Л.И."],
                          ["Василий Теркин. Твардовский А.Т."],
                          ["Навеки девятнадцатилетник. Бакланов Г.Я."],
                          ["Героев славных имена. Сборник очерков"],
                          ["Доклад начальника академии об образовании академии"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите книгу',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))

    return "quest_choice"

def quest_choice(bot, update):
    SOS(bot)
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
    SOS(bot)
    print (bot.effective_user.id)
    uid = str(uuid.uuid4())
    user_id = bot.effective_user.id
    kursant_lastname = lastname(mdb, bot.effective_user)
    time = datetime.datetime.now()
    time = time.strftime("%d.%m.%Y %H-%M-%S")
    file = bot.message.photo[-1].get_file()
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    file = file.download(kursant_lastname + " " + uid + " " + file_name[1])
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
    save_user_report(mdb, user, report_category, unit_report, time, uid)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку! \nУникальный номер данного доклада :\n<b>" + uid + "</b>\nПригодится в случае технических неполадок. Запишите его!", reply_markup=get_keyboard(check_user), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def quest_download_document(bot, update):
    SOS(bot)
    print(update.user_data['title'])
    uid = uuid.uuid4()
    user = bot.message.from_user
    print(user.last_name)
    file = bot.message.document.get_file()
    print(file.file_path)
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    print(file_name[1])
    print(file_extension[1])
    file = file.download(update.user_data['user_lastname'] + " " + str(uid) + " " + file_name[1])
    print(file)
    try:
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ update.user_data['group'] + "/"+ file)
    except FileNotFoundError:
        os.makedirs("Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/" + update.user_data['group'])
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/" + update.user_data['group'] + "/" + file)

    bot.message.reply_text('Great!')
    print("Круто")

def user_start(bot, update):
    SOS(bot)
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
                      ["Комиссия"],
                      ["901", "903"],
                      ["904", "905-1"],
                      ["905-2", "906"]]
    bot.message.reply_text('Ваше подразделение?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "user_group"

def user_get_group(bot, update):
    SOS(bot)
    update.user_data['user_group'] = bot.message.text
    if bot.message.text == "Комиссия":
        reply_keyboard = [["Курсант 95 курса"]]
        bot.message.reply_text('Ваша должность?',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
        return "user_unit_officer"
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
    SOS(bot)
    update.user_data['user_unit'] = bot.message.text
    bot.message.reply_text("Ваша фамилия?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname"

def user_get_unit_officer(bot, update):
    SOS(bot)
    print("Я тут")
    update.user_data['user_unit'] = bot.message.text
    bot.message.reply_text("Ваша фамилия?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname"

def user_get_lastname(bot, update):
    SOS(bot)
    update.user_data['user_lastname'] = bot.message.text
    bot.message.reply_text("Ваше имя?", reply_markup=ReplyKeyboardRemove())
    return "user_name"


def user_get_name(bot, update):
    SOS(bot)
    update.user_data['user_name'] = bot.message.text
    bot.message.reply_text("Ваше отчество?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename"

def user_get_middlename(bot, update):
    SOS(bot)
    update.user_data['user_middlename'] = bot.message.text
    button_phone = KeyboardButton('Отправить номер телефона', request_contact=True)
    reply_keyboard = [button_phone]
    bot.message.reply_text("Ваш номер телефона? Внимание, телефон отправляется автоматически после нажатия кнопки!",
                           reply_markup=ReplyKeyboardMarkup([reply_keyboard], resize_keyboard=True,
                                                                one_time_keyboard=True))
    print("Тут норм")
    return "user_phone"

def user_get_phone(bot, update):
    SOS(bot)
    update.user_data['user_phone'] = bot.message.contact.phone_number
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    print(update.user_data)
    save_kursant_anketa(mdb, user, update.user_data, update)
    print(bot.message.contact)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Приветствую, {}!\nТеперь Ваши данные на проверке!\nНо Вы уже можете приступить к выполнению служебных заданий.".format(bot.message.chat.first_name), reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def report_start(bot, update):
    SOS(bot)
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
    SOS(bot)
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
    SOS(bot)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Вы вернулись в меню!", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def report_photo(bot, update):
    SOS(bot)
    uid = str(uuid.uuid4())
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
    print(update.user_data['report_group'])
    print(uid)
    file = file.download(kursant_lastname + " " + uid + " " + file_name[1])

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
    save_user_report(mdb, user, report_category, unit_report, time, uid)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Ваш доклад принят в обработку! \nУникальный номер данного доклада :\n<b>" + uid + "</b>\nПригодится в случае технических неполадок. Запишите его!", reply_markup=get_keyboard(check_user), parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def anketa_start(bot, update):
    SOS(bot)
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    reply_keyboard = [["Пропустить ввод данных матери (мачехи, опекуншы)"],["Вернуться в меню!"]]
    bot.message.reply_text('Введите фамилию матери (мачехи, опекуншы) либо перейдите к вводу данных отца (отчима, опекуна)', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_mother"

def anketa_get_lastname_mother(bot, update):
    SOS(bot)
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
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашей матери (мачехи, опекуншы)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_mother"


def anketa_get_middlename_mother(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашей матери (мачехи, опекуншы)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_mother"


def anketa_get_phone_mother(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_mother'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашей матери (мачехи, опекуншы)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_mother"


def anketa_get_address_mother(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_address_mother'] = bot.message.text
    reply_keyboard = [["Пропустить ввод данных отца (отчима, опекуна)"], ["Вернуться в меню!"]]
    bot.message.reply_text('Введите фамилию отца (отчима, опекуна) либо перейдите к вводу данных друга (брата, сестры, подруги, девушки)', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_father"


def anketa_get_lastname_father(bot, update):
    SOS(bot)
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
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашего отца (отчима, опекуна)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_father"


def anketa_get_middlename_father(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашего отца (отчима, опекуна)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_father"


def anketa_get_phone_father(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашего отца (отчима, опекуна)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_father"


def anketa_get_address_father(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_address_father'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Фамилия Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_lastname_other"


def anketa_get_lastname_other(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_lastname_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Имя Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_name_other"


def anketa_get_name_other(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_name_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Отчество Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_middlename_other"


def anketa_get_middlename_other(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_middlename_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Телефон Вашего друга (брата, сестры, подруги, девушки)?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_phone_other"


def anketa_get_phone_other(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['user_phone_other'] = bot.message.text
    reply_keyboard = [["Вернуться в меню!"]]
    bot.message.reply_text("Адрес Вашего друга (брата, сестры, подруги, девушки)? Например: Республика Алтай, г.Барнаул, ул.Советская, д.3, к.1, кв.123", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "user_address_other"


def anketa_get_address_other(bot, update):
    SOS(bot)
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
    SOS(bot)
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
    SOS(bot)
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
    SOS(bot)
    bot.message.reply_text("Я Вас не понимаю, выберите оценку на клавиатуре!")


def send_meme(bot, update):
    SOS(bot)
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
    SOS(bot)
    print(bot.callback_query)
    query = bot.callback_query
    update.bot.edit_message_caption(
        caption='Спасибо Вам за выбор!',
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)

def test_bd(bot, update):
    SOS(bot)
    print("Запуск")
    d = check_point(mdb, bot.effective_user)
    print(d['Present']['check_present'])
    return 0

def report(bot, update):
    SOS(bot)
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

def report_group(bot, update):
    SOS(bot)
    user_group = check_group(mdb, bot.effective_user)
    find_report_group(bot, mdb, user_group)





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

def get_rock(bot, update):
    SOS(bot)
    print("вот тут")
    reply_keyboard = [["Отчеты"],
                      ["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "get_report"
def get_report(bot, update):
    SOS(bot)
    #заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    print(get_group(mdb, bot.effective_user) + " " + lastname(mdb, bot.effective_user) + " запросил статус докладов! Он молодец")
    type = bot.message.text
    films = {1:"Чапаев (1934)",
             2:"Повесть о настоящем человеке (1948)",
             3:"Добровольцы (1958)",
             4:"Обыкновенный фашизм (1965)",
             5:"Офицеры (1972)",
             6:"В бой идут одни старики (1973)",
             7:"Они сражались за Родину (1975)",
             8:"Брестская крепость (2010)",
             9:"Легенда 17 (2013)",
             10:"28 панфиловцев (2016)",
             11:"Движение вверх (2017)",
             12:"Время первых (2017)",
             13:"Сто шагов (2019)",
             14:"Ржев (2019)",
             15:"Балканский рублеж (2019)",
             16:"Лев Яшин  Вратарь моей мечты (2019)",
             17:"Жила-была девочка (1944)",
             18:"Мы смерти смотрели в лицо (1980)",
             19:"Порох (1985)",
             20:"Зимнее утро (1966)",
             21:"Блокада (1973-1977)",
             22:"Коридор бессмертия (2019)"}
    books = {1:"Русский характер  Толстой А Н ",
             2:"Волоколамское шоссе  Бек А А ",
             3:"Взять живым! Карпов В В ",
             4:"Горячий снег  Бондарев Ю В ",
             5:"Генералиссимус Суворов  Раковский Л И ",
             6:"Василий Теркин  Твардовский А Т ",
             7:"Навеки девятнадцатилетник  Бакланов Г Я ",
             8:"Героев славных имена  Сборник очерков",
             9:"Доклад начальника академии об образовании академии"}
    math = {1:"Задание 1 Область определения функции и логарифма",
            2:"Задание 2, 3, 4 Построение графика функции",
            3:"Задание 5 Четность и нечетность функции",
            4:"Задание 6 Экстремумы функции без использования производной",
            5:"Задание 7 Периодические функции",
            6:"Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя",
            7:"Задания 14 15 Непрерывность функции и точки разрыва",
            8:"Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций",
            9:"Задание 18 Значение производной в данной точке",
            10:"Задание 23 Приближенные вычисления с помощью производной",
            11:"Задание 24 Производная функции, заданной параметрическим способом",
            12:"Задания 25, 28 Производная неявной функции",
            13:"Задание 26 Уравнение касательной и нормали к графику функции",
            14:"Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба",
            15:"Задание 29 Правило Лопиталя",
            16:"Задание 30 Нахождение асимптот графиков функций",
            17:"Задание 31 Нахождение интервалов монотонности",
            18:"Задание 32 Экстремумы фнукций",
            19:"Задание 34,34 Исследование функции, применение производной к построению графиков функций"}
    analit = {1:"Задание 1-4 Задача 1-1 Комплексные числа",
              2:"Задание 1-4 Задача 1-2 Разложение на множители",
              3:"Задание 3-5 Задача 3-1 Векторы, их произведения",
              4:"Задание 3-5 Задача 3-2 Длина и угол между векторами",
              5:"Задание 4-2 Задача 4-1 Уравнение прямой",
              6:"Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки",
              7:"Задание 6-2 Задача 6-2 Уравнение параллельной прямой",
              8:"Задание 6-2 Задача 6-3 Уравнение плоскости",
              9:"Задание 6-2 Задача 6-7 Проекция точки на плоскость",
              10:"Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка",
              11:"Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы",
              12:"Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"}
    reports = {1:"1  Отпускной билет (постановка на учет)",
            2:"2  Бланк инструктажа (подпись родителей на обратной стороне)",
            3:"3  Письмо родителям (подпись родителей на обратной стороне)",
            4:"4  Служебное задания (проагитированные курсанты)",
            5:"5  Отпускной билет (снятие с учета)"}
    if type == "Кинофильмы":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nКинофильмы:\n"
        while count <= 22:
            film = films[count]
            film = "<b>" + film + ":</b> " + get_status_film(film, bot, update) + "\n"
            doklad = doklad + film
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Отчеты":
        count = 1
        doklad = "<b>Ваши отчеты:</b> \n"
        while count <= 5:
            reps = reports[count]
            reps = "<b>" + reps + ":</b> " + get_status_reps(reps, bot, update) + "\n"
            doklad = doklad + reps
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Литературные произведения":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nЛитературные произведения:\n"
        while count <= 9:
            book = books[count]
            book = "<b>" + book + ":</b> " + get_status_books(book, bot, update) + "\n"
            doklad = doklad + book
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Математический анализ":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nИндивидуальные задания по МА:\n"
        while count <= 19:
            mathematic = math[count]
            mathematic = "<b>" + mathematic + ":</b> " + get_status_mathematic(mathematic, bot, update) + "\n"
            doklad = doklad + mathematic
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Аналитическая геометрия и линейная алгебра":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nИндивидуальные задания по АГЛА:\n"
        while count <= 12:
            analitic = analit[count]
            analitic = "<b>" + analitic + ":</b> " + get_status_analitic(analitic, bot, update) + "\n"
            doklad = doklad + analitic
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Если есть какие-то вопросы, обратитесь к лейтенанту Широкопетлеву (8-911-170-18-75)", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END


def get_count_rock(bot, update):
    SOS(bot)
    print("вот тут")
    reply_keyboard = [["Отчеты"],
                      ["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "get_count_report"

def get_count_report(bot, update):
    SOS(bot)
    #заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    print(get_group(mdb, bot.effective_user) + " " + lastname(mdb, bot.effective_user) + " запросил сколько еще работать")
    type = bot.message.text
    films = {1:"Чапаев (1934)",
             2:"Повесть о настоящем человеке (1948)",
             3:"Добровольцы (1958)",
             4:"Обыкновенный фашизм (1965)",
             5:"Офицеры (1972)",
             6:"В бой идут одни старики (1973)",
             7:"Они сражались за Родину (1975)",
             8:"Брестская крепость (2010)",
             9:"Легенда 17 (2013)",
             10:"28 панфиловцев (2016)",
             11:"Движение вверх (2017)",
             12:"Время первых (2017)",
             13:"Сто шагов (2019)",
             14:"Ржев (2019)",
             15:"Балканский рублеж (2019)",
             16:"Лев Яшин  Вратарь моей мечты (2019)",
             17:"Жила-была девочка (1944)",
             18:"Мы смерти смотрели в лицо (1980)",
             19:"Порох (1985)",
             20:"Зимнее утро (1966)",
             21:"Блокада (1973-1977)",
             22:"Коридор бессмертия (2019)"}
    books = {1:"Русский характер  Толстой А Н ",
             2:"Волоколамское шоссе  Бек А А ",
             3:"Взять живым! Карпов В В ",
             4:"Горячий снег  Бондарев Ю В ",
             5:"Генералиссимус Суворов  Раковский Л И ",
             6:"Василий Теркин  Твардовский А Т ",
             7:"Навеки девятнадцатилетник  Бакланов Г Я ",
             8:"Героев славных имена  Сборник очерков",
             9:"Доклад начальника академии об образовании академии"}
    math = {1:"Задание 1 Область определения функции и логарифма",
            2:"Задание 2, 3, 4 Построение графика функции",
            3:"Задание 5 Четность и нечетность функции",
            4:"Задание 6 Экстремумы функции без использования производной",
            5:"Задание 7 Периодические функции",
            6:"Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя",
            7:"Задания 14 15 Непрерывность функции и точки разрыва",
            8:"Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций",
            9:"Задание 18 Значение производной в данной точке",
            10:"Задание 23 Приближенные вычисления с помощью производной",
            11:"Задание 24 Производная функции, заданной параметрическим способом",
            12:"Задания 25, 28 Производная неявной функции",
            13:"Задание 26 Уравнение касательной и нормали к графику функции",
            14:"Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба",
            15:"Задание 29 Правило Лопиталя",
            16:"Задание 30 Нахождение асимптот графиков функций",
            17:"Задание 31 Нахождение интервалов монотонности",
            18:"Задание 32 Экстремумы фнукций",
            19:"Задание 34,34 Исследование функции, применение производной к построению графиков функций"}
    analit = {1:"Задание 1-4 Задача 1-1 Комплексные числа",
              2:"Задание 1-4 Задача 1-2 Разложение на множители",
              3:"Задание 3-5 Задача 3-1 Векторы, их произведения",
              4:"Задание 3-5 Задача 3-2 Длина и угол между векторами",
              5:"Задание 4-2 Задача 4-1 Уравнение прямой",
              6:"Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки",
              7:"Задание 6-2 Задача 6-2 Уравнение параллельной прямой",
              8:"Задание 6-2 Задача 6-3 Уравнение плоскости",
              9:"Задание 6-2 Задача 6-7 Проекция точки на плоскость",
              10:"Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка",
              11:"Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы",
              12:"Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"}
    reports = {1:"1  Отпускной билет (постановка на учет)",
            2:"2  Бланк инструктажа (подпись родителей на обратной стороне)",
            3:"3  Письмо родителям (подпись родителей на обратной стороне)",
            4:"4  Служебное задания (проагитированные курсанты)",
            5:"5  Отпускной билет (снятие с учета)"}
    if type == "Кинофильмы":
        text = "Кинофильмы:\n"
        cur = mdb.users.find({})
        for doc in cur:
            bot = doc["user_id"]
            count = 1
            doklad = "<b>Ваши доклады:</b> \nКинофильмы:\n"
            while count <= 22:
                film = films[count]
                film = "<b>" + film + ":</b> " + get_count_film(film, bot, update) + "\n"
                doklad = doklad + film
                count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Отчеты":
        count = 1
        doklad = "<b>Ваши отчеты:</b> \n"
        while count <= 5:
            reps = reports[count]
            reps = "<b>" + reps + ":</b> " + get_count_reps(reps, bot, update) + "\n"
            doklad = doklad + reps
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Литературные произведения":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nЛитературные произведения:\n"
        while count <= 9:
            book = books[count]
            book = "<b>" + book + ":</b> " + get_count_books(book, bot, update) + "\n"
            doklad = doklad + book
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Математический анализ":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nИндивидуальные задания по МА:\n"
        while count <= 19:
            mathematic = math[count]
            mathematic = "<b>" + mathematic + ":</b> " + get_count_mathematic(mathematic, bot, update) + "\n"
            doklad = doklad + mathematic
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    if type == "Аналитическая геометрия и линейная алгебра":
        count = 1
        doklad = "<b>Ваши доклады:</b> \nИндивидуальные задания по АГЛА:\n"
        while count <= 12:
            analitic = analit[count]
            analitic = "<b>" + analitic + ":</b> " + get_count_analitic(analitic, bot, update) + "\n"
            doklad = doklad + analitic
            count = count + 1
        bot.message.reply_text(doklad, parse_mode=telegram.ParseMode.HTML)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text("Если есть какие-то вопросы, обратитесь к лейтенанту Широкопетлеву (8-911-170-18-75)", reply_markup=get_keyboard(check_user))
    return ConversationHandler.END


def get_help(bot, update):
    SOS(bot)
    print("вот тут")
    #["Руководящие документы"],
    #["Отчеты"],
    reply_keyboard = [["РУКОВОДЯЩИЕ ДОКУМЕНТЫ"],
                      ["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "get_type_help"


def get_type_help(bot, update):
    SOS(bot)
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_category'] = bot.message.text
    print(bot.message.text)
    if bot.message.text == "РУКОВОДЯЩИЕ ДОКУМЕНТЫ":
        reply_keyboard = [["Общевоинские уставы ВС РФ"],
                          ["Уголовный кодекс"],
                          ["Вопросы прохождения службы"],
                          ["О статусе военнослужащих"],
                          ["Военная доктрина"],
                          ["Инструктаж в отпуск"],
                          ["КоАП РФ"],
                          ["О вещевом обеспечении"],
                          ["О воинской обязанности и военной службе"],
                          ["О государственной тайне"],
                          ["О продовольственном обеспечении"],
                          ["О финансовом обеспечении"],
                          ["Об обороне"],
                          ["Памятка БДД"],
                          ["Перечни рекомендуемых и обязательных книг и фильмов"],
                          ["Пособие для ВВУЗОВ по COVID-19"],
                          ["Приказ МО РФ 2017 по ВПД"],
                          ["Проверка и оценка ФП"],
                          ["Трудовой кодекс"],
                          ["Пособие для ВВУЗОВ по COVID-19"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите документ!',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Отчеты":
        reply_keyboard = [["1. Отпускной билет (постановка на учет)"],
                          ["2. Бланк инструктажа (подпись родителей на обратной стороне)"],
                          ["3. Письмо родителям (подпись родителей на обратной стороне)"],
                          ["4. Служебное задания (проагитированные курсанты)"],
                          ["5. Отпускной билет (снятие с учета)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите документ!',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Кинофильмы":
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
                          ["Жила-была девочка (1944)"],
                          ["Мы смерти смотрели в лицо (1980)"],
                          ["Порох (1985)"],
                          ["Зимнее утро (1966)"],
                          ["Блокада (1973-1977)"],
                          ["Коридор бессмертия (2019)"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите кинофильм',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Математический анализ":
        reply_keyboard = [["Задание 1 Область определения функции и логарифма"],
                          ["Задание 2, 3, 4 Построение графика функции"],
                          ["Задание 5 Четность и нечетность функции"],
                          ["Задание 6 Экстремумы функции без использования производной"],
                          ["Задание 7 Периодические функции"],
                          ["Задания 8, 9, 10, 11, 12, 13 Вычисление пределов и правило Лопиталя"],
                          ["Задания 14 15 Непрерывность функции и точки разрыва"],
                          ["Задания 16, 17, 19, 20, 21, 22 Дифференцирование сложных функций"],
                          ["Задание 18 Значение производной в данной точке"],
                          ["Задание 23 Приближенные вычисления с помощью производной"],
                          ["Задание 24 Производная функции, заданной параметрическим способом"],
                          ["Задания 25, 28 Производная неявной функции"],
                          ["Задание 26 Уравнение касательной и нормали к графику функции"],
                          ["Задание 27, 33 Производная второго порядка, выпуклости и точки перегиба"],
                          ["Задание 29 Правило Лопиталя"],
                          ["Задание 30 Нахождение асимптот графиков функций"],
                          ["Задание 31 Нахождение интервалов монотонности"],
                          ["Задание 32 Экстремумы фнукций"],
                          ["Задание 34,34 Исследование функции, применение производной к построению графиков функций"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    elif bot.message.text == "Аналитическая геометрия и линейная алгебра":
        reply_keyboard = [["Задание 1-4 Задача 1-1 Комплексные числа"],
                          ["Задание 1-4 Задача 1-2 Разложение на множители"],
                          ["Задание 3-5 Задача 3-1 Векторы, их произведения"],
                          ["Задание 3-5 Задача 3-2 Длина и угол между векторами"],
                          ["Задание 4-2 Задача 4-1 Уравнение прямой"],
                          ["Задание 6-2 Задача 6-1 Уравнение прямой проходящей через 2 точки"],
                          ["Задание 6-2 Задача 6-2 Уравнение параллельной прямой"],
                          ["Задание 6-2 Задача 6-3 Уравнение плоскости"],
                          ["Задание 6-2 Задача 6-7 Проекция точки на плоскость"],
                          ["Задание 7-2 Задачи 7-1,7-2 Поверхности второго порядка"],
                          ["Задание 9-5 Задача 9-1 Собственные числа и векторы матрицы"],
                          ["Задание 9-5 Задача 9-2 Собственные значения и векторы линейного оператора"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите индивидуальное задание',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    else:
        reply_keyboard = [["Русский характер. Толстой А.Н."],
                          ["Волоколамское шоссе. Бек А.А."],
                          ["Взять живым! Карпов В.В."],
                          ["Горячий снег. Бондарев Ю.В."],
                          ["Генералиссимус Суворов. Раковский Л.И."],
                          ["Василий Теркин. Твардовский А.Т."],
                          ["Навеки девятнадцатилетник. Бакланов Г.Я."],
                          ["Героев славных имена. Сборник очерков"],
                          ["Доклад начальника академии об образовании академии"],
                          ["Вернуться в меню!"]]
        bot.message.reply_text('Выберите книгу',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    print("123")
    return "get_choice_help"

def get_choice_help(bot, update):
    SOS(bot)
    bot.message.reply_text('Материал может загружаться какое-то время!')
    print("Я оказался тут")
    if bot.message.text == "Вернуться в меню!":
        print("Вы здесь")
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    update.user_data['quest_title'] = bot.message.text
    type = update.user_data['quest_category']
    title = update.user_data['quest_title']
    report_category = type.replace('.', ' ')
    unit_report = title.replace('.', ' ')
    title = title + ".zip"
    path = "Справочник/" + type + "/" + title
    try:
        with open(path, "rb") as file:
            update.bot.send_document(chat_id=bot.message.chat.id, document=file, filename=title)
    except FileNotFoundError:
        os.makedirs("Справочник/" + type + "/")
        bot.message.reply_text("Загрузите файл в папку:" + " Справочник/" + type + "/" + "\n и назовите его: " + title)
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text('Если вы хотите добавить дополнительный материал, мы будем очень рады! Либо если хотите получить какие-то материалы в доступ напишите лейтенанту Широкопетлеву (8-911-170-18-75)')
    bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def sos(bot, update):
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def exit(bot, update):
    check_user = check_point(mdb, bot.effective_user)
    bot.message.reply_text('Вы вернулись в меню!', reply_markup=get_keyboard(check_user))
    return ConversationHandler.END

def get_rating_category(bot, update):
    SOS(bot)
    print("вот тут")
    #["Руководящие документы"],
    #["Отчеты"],
    reply_keyboard = [["Кинофильмы"],
                      ["Литературные произведения"],
                      ["Математический анализ"],
                      ["Аналитическая геометрия и линейная алгебра"],
                      ["Вернуться в меню!"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "get_type_rating"