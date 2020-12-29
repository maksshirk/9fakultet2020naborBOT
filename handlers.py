import requests
from bs4 import BeautifulSoup
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler
from glob import glob
from random import choice
from utility import get_keyboard
from emoji import emojize
from utility import SMILE
from mongodb import mdb, search_or_save_user, save_user_anketa

def sms(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    print(user)
    smile = emojize(choice(SMILE), use_aliases=True)
    bot.message.reply_text('Привет, {} \nПоговори со мной {}'.format(bot.message.chat.first_name, smile), reply_markup=get_keyboard())


def parrot(bot, update):
    print('Кто-то отправил команду /start, что делать?')
    bot.message.reply_text(bot.message.text)

def get_contact(bot, update):
    print(bot.message.contact)
    bot.message.reply_text('{}, Мы получили ваш номер телефона'.format(bot.message.chat.first_name))

def get_location(bot, update):
    print(bot.message.location)
    bot.message.reply_text('{}, Мы получили ваше местоположение'.format(bot.message.chat.first_name))

def get_anecdote(bot, update):
    receive = requests.get('http://anekdotme.ru/random')
    page = BeautifulSoup(receive.text, "html.parser")
    find = page.select('.anekdot_text')
    for text in find:
        page = (text.getText().strip())
    bot.message.reply_text(page)

def anketa_start(bot, update):
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    if 'anketa' in user:
        text = """Ваш предыдущий результат:
        <b>Имя:</b> {name}
        <b>Возраст:</b> {age}
        <b>Оценка:</b> {evaluation}
        <b>Комментарий:</b> {comment}
Данные будут обновлены!
        Как Вас зовут?""".format(**user['anketa'])
        bot.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        return "user_name"
    else:
        bot.message.reply_text('Как Вас зовут?', reply_markup=ReplyKeyboardRemove())
        return "user_name"

def anketa_get_name(bot, update):
    update.user_data['name'] = bot.message.text
    bot.message.reply_text("Сколько Вам лет?")
    return "user_age"

def anketa_get_age(bot, update):
    update.user_data['age'] = bot.message.text
    reply_keyboard = [["1", "2", "3", "4", "5"]]
    bot.message.reply_text("Оцените статью от 1 до 5",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return "evaluation"

def anketa_get_evaluation(bot, update):
    update.user_data['evaluation'] = bot.message.text
    reply_keyboard = [["Пропустить"]]
    bot.message.reply_text("Напишите отзыв или нажмите кнопку пропустить этот шаг.",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True, one_time_keyboard=True))
    return "comment"

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
