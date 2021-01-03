from telegram import KeyboardButton, ReplyKeyboardMarkup

#SMILE = ['😂', '💥', '😍']
CALLBACK_BUTTON_PICTURE = "Картинка🖼"
CALLBACK_BUTTON_PEN = "Регистрация🖋"
CALLBACK_BUTTON_START = "Начать▶"
CALLBACK_BUTTON_JOKE = "Анекдот😁"

def get_keyboard():
#    contact_button = KeyboardButton('Отправить контакты', request_contact = True,)
    location_button = KeyboardButton('Жив. Здоров.', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([[CALLBACK_BUTTON_PEN], [location_button], ["Отчеты по И.З."]], resize_keyboard=True)

    return my_keyboard