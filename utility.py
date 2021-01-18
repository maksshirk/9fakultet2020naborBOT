from telegram import KeyboardButton, ReplyKeyboardMarkup

#SMILE = ['😂', '💥', '😍']
CALLBACK_BUTTON_PICTURE = "Картинка🖼"
CALLBACK_BUTTON_PEN = "Представиться👨‍✈️"
CALLBACK_BUTTON_START = "Начать▶"
CALLBACK_BUTTON_JOKE = "Анекдот😁"

def get_keyboard(check_user):
#    contact_button = KeyboardButton('Отправить контакты', request_contact = True,)
    # my_keyboard = ReplyKeyboardMarkup([[CALLBACK_BUTTON_PEN], [location_button], ["Отчеты по И.З."]], resize_keyboard=True)
    location_button = KeyboardButton('Доклад о состоянии дел', request_location=True)
    print(check_user)
    if check_user == 0:
        my_keyboard = ReplyKeyboardMarkup([[CALLBACK_BUTTON_PEN]], resize_keyboard=True)
    elif check_user == 1:
        my_keyboard = ReplyKeyboardMarkup([["Ввести данные для связи в случае отсутствия доклада"]], resize_keyboard=True)
    elif check_user == 5:
        my_keyboard = ReplyKeyboardMarkup([['Ввести адреса проведения отпуска'],["Принять доклад о состоянии дел"], ["Показать обстановку на карте"], ["1. Отчеты"], ["2. Индивидуальные задания"]], resize_keyboard=True)
    elif check_user == 3:
        my_keyboard = ReplyKeyboardMarkup([["Доклад о состоянии дел"], ["1. Отчеты"], ["2. Индивидуальные задания"], ["Изменить данные для связи в случае отсутствия доклада"]], resize_keyboard=True)
    else:
        my_keyboard = ReplyKeyboardMarkup([["Доклад о состоянии дел"], ["1. Отчеты"], ["2. Индивидуальные задания"]], resize_keyboard=True)
    return my_keyboard