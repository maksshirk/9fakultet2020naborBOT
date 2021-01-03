import requests, telebot, os, telegram
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, Updater, CallbackContext
from glob import glob
from random import choice
from utility import get_keyboard
from emoji import emojize
import datetime
import os
from settings import TG_TOKEN

from mongodb import mdb, search_or_save_user, save_user_anketa, save_user_location


def sms(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    #    print(user)
    #    smile = emojize(choice(SMILE), use_aliases=True)
    bot.message.reply_text('Добрый день!\nВнесите свои данные в АСУ', reply_markup=get_keyboard())


def parrot(bot, update):
    print('Кто-то отправил команду /start, что делать?')
    bot.message.reply_text(bot.message.text)


def get_contact(bot, update):
    print(bot.message.contact)
    bot.message.reply_text('{}, Мы получили ваш номер телефона'.format(bot.message.chat.first_name))


def get_location(bot, update):
    location = bot.message.location
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    b = datetime.datetime.now()
    b = b.strftime("%m/%d/%Y")
    time = datetime.datetime.now()
    print(b)
    print(user)
    save_user_location(mdb, user, b, location, time)
    bot.message.reply_text('{}, Мы получили ваше местоположение'.format(bot.message.chat.first_name))


def get_anecdote(bot, update):
    receive = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(receive.text, "html.parser")
    find = page.select('.anekdot_text')
    for text in find:
        page = (text.getText().strip())
    bot.message.reply_text(page)


def quest_start(bot, update):
    reply_keyboard = [["Кинофильмы"],
                      ["Литературные произведения"]]
    bot.message.reply_text('Выберите категорию',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "quest_category"


def quest_category(bot, update):
    update.user_data['category'] = bot.message.text
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
                          ["Лев Яшин. Вратарь моей мечты (2019)"]]
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
                          ["Героев славных имена. Сборник очерков"]]
        bot.message.reply_text('Выберите книгу',
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))

    return "quest_choice"

def quest_choice(bot, update):
    update.user_data['title'] = bot.message.text
    reply_keyboard = [["Загрузить фото"],
                      ["Загрузить документ (PDF, zip и другие"]]
    bot.message.reply_text('Выберите вид доклада',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                one_time_keyboard=True))
    return "quest_select"


def quest_select(bot, update):
    update.user_data['choice'] = bot.message.text
    if bot.message.text == "Загрузить фото":
        return "quest_download_photo"
    else: return "quest_download_document"

def quest_download_photo(bot, update):
    print(update.user_data['title'])
    user = bot.message.from_user
    print(user.last_name)
    file = bot.message.photo[-1].get_file()
    print(file.file_path)
    file_extension = os.path.splitext(file.file_path)
    file_name = os.path.split(file.file_path)
    print(file_name[1])
    print(file_extension[1])
    file = file.download(user.last_name + " " + update.user_data['title'] + " " + file_name[1])
    print(file)
    try:
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ file)
    except FileNotFoundError:
        os.makedirs("Report/" + update.user_data['category'] + '/' + update.user_data['title'])
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ file)

    bot.message.reply_text('Great!')
    print("Круто")

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
    file = file.download(user.last_name + file_name[1])
    print(file)
    try:
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ file)
    except FileNotFoundError:
        os.makedirs("Report/" + update.user_data['category'] + '/' + update.user_data['title'])
        os.replace(file, "Report/" + update.user_data['category'] + '/' + update.user_data['title'] + "/"+ file)

    bot.message.reply_text('Great!')
    print("Круто")

def anketa_start(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    reply_keyboard = [["Управление"],
                      ["901", "903"],
                      ["904", "905/1"],
                      ["905/2", "906"]]
    bot.message.reply_text('Ваша учебная группа?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "user_group"


def anketa_get_group(bot, update):
    update.user_data['group'] = bot.message.text
    if bot.message.text == "Управление":
        reply_keyboard = [["Начальник курса", "Курсовой офицер"],
                          ["Старшина"]]
    else:
        reply_keyboard = [["Командир группы", "Командир отделения"],
                          ["Курсант"]]
    bot.message.reply_text('Ваша должность?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                            one_time_keyboard=True))
    return "user_position"


def anketa_get_position(bot, update):
    update.user_data['position'] = bot.message.text
    bot.message.reply_text("Ваша фамилия?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname"


def anketa_get_lastname(bot, update):
    update.user_data['lastname'] = bot.message.text
    bot.message.reply_text("Ваше имя?", reply_markup=ReplyKeyboardRemove())
    return "user_name"


def anketa_get_name(bot, update):
    update.user_data['name'] = bot.message.text
    bot.message.reply_text("Ваше отчество?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename"


def anketa_get_middlename(bot, update):
    update.user_data['middlename'] = bot.message.text
    bot.message.reply_text("Номер Вашего телефона?", reply_markup=ReplyKeyboardRemove())
    return "user_phone"


def anketa_get_phone(bot, update):
    update.user_data['phone'] = bot.message.text
    if update.user_data['position'] == "Начальник курса" or "Курсовой офицер":
        user = search_or_save_user(mdb, bot.effective_user, bot.message)
        update.user_data['address'] = "Не требуется"
        update.user_data['lastname_mother'] = "Не требуется"
        update.user_data['name_mother'] = "Не требуется"
        update.user_data['middlename_mother'] = "Не требуется"
        update.user_data['phone_mother'] = "Не требуется"
        update.user_data['address_mother'] = "Не требуется"
        update.user_data['lastname_father'] = "Не требуется"
        update.user_data['name_father'] = "Не требуется"
        update.user_data['middlename_father'] = "Не требуется"
        update.user_data['phone_father'] = "Не требуется"
        update.user_data['address_father'] = "Не требуется"
        update.user_data['lastname_other'] = "Не требуется"
        update.user_data['name_other'] = "Не требуется"
        update.user_data['middlename_other'] = "Не требуется"
        update.user_data['phone_other'] = "Не требуется"
        update.user_data['address_other'] = "Не требуется"
        anketa = save_user_anketa(mdb, user, update.user_data)
        print(anketa)
        bot.message.reply_text("Вы зарегистрированы", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    bot.message.reply_text("Адрес проведения отпуска?", reply_markup=ReplyKeyboardRemove())
    return "user_address"


def anketa_get_address(bot, update):
    update.user_data['address'] = bot.message.text
    bot.message.reply_text("Фамилия Вашей матери?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname_mother"


def anketa_get_lastname_mother(bot, update):
    update.user_data['lastname_mother'] = bot.message.text
    bot.message.reply_text("Имя Вашей матери?", reply_markup=ReplyKeyboardRemove())
    return "user_name_mother"


def anketa_get_name_mother(bot, update):
    update.user_data['name_mother'] = bot.message.text
    bot.message.reply_text("Отчество Вашей матери?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename_mother"


def anketa_get_middlename_mother(bot, update):
    update.user_data['middlename_mother'] = bot.message.text
    bot.message.reply_text("Телефон Вашей матери?", reply_markup=ReplyKeyboardRemove())
    return "user_phone_mother"


def anketa_get_phone_mother(bot, update):
    update.user_data['phone_mother'] = bot.message.text
    bot.message.reply_text("Адрес Вашей матери?", reply_markup=ReplyKeyboardRemove())
    return "user_address_mother"


def anketa_get_address_mother(bot, update):
    update.user_data['address_mother'] = bot.message.text
    bot.message.reply_text("Фамилия Вашего отца?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname_father"


def anketa_get_lastname_father(bot, update):
    update.user_data['lastname_father'] = bot.message.text
    bot.message.reply_text("Имя Вашего отца?", reply_markup=ReplyKeyboardRemove())
    return "user_name_father"


def anketa_get_name_father(bot, update):
    update.user_data['name_father'] = bot.message.text
    bot.message.reply_text("Отчество Вашего отца?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename_father"


def anketa_get_middlename_father(bot, update):
    update.user_data['middlename_father'] = bot.message.text
    bot.message.reply_text("Телефон Вашего отца?", reply_markup=ReplyKeyboardRemove())
    return "user_phone_father"


def anketa_get_phone_father(bot, update):
    update.user_data['phone_father'] = bot.message.text
    bot.message.reply_text("Адрес Вашего отца?", reply_markup=ReplyKeyboardRemove())
    return "user_address_father"


def anketa_get_address_father(bot, update):
    update.user_data['address_father'] = bot.message.text
    bot.message.reply_text("Фамилия Вашего друга (брата, сестры)?", reply_markup=ReplyKeyboardRemove())
    return "user_lastname_other"


def anketa_get_lastname_other(bot, update):
    update.user_data['lastname_other'] = bot.message.text
    bot.message.reply_text("Имя Вашего друга (брата, сестры)?", reply_markup=ReplyKeyboardRemove())
    return "user_name_other"


def anketa_get_name_other(bot, update):
    update.user_data['name_other'] = bot.message.text
    bot.message.reply_text("Отчество Вашего друга (брата, сестры)?", reply_markup=ReplyKeyboardRemove())
    return "user_middlename_other"


def anketa_get_middlename_other(bot, update):
    update.user_data['middlename_other'] = bot.message.text
    bot.message.reply_text("Телефон Вашего друга (брата, сестры)?", reply_markup=ReplyKeyboardRemove())
    return "user_phone_other"


def anketa_get_phone_other(bot, update):
    update.user_data['phone_other'] = bot.message.text
    bot.message.reply_text("Адрес Вашего друга (брата, сестры)?", reply_markup=ReplyKeyboardRemove())

    return "user_address_other"


def anketa_get_address_other(bot, update):
    update.user_data['address_other'] = bot.message.text
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    anketa = save_user_anketa(mdb, user, update.user_data)
    print("почти конец")
    print(anketa)
    bot.message.reply_text("Вы зарегистрированы", reply_markup=ReplyKeyboardRemove())
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
