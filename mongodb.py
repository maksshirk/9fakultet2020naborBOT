from pymongo import MongoClient
from settings import MONGO_DB
from settings import MONGODB_LINK
from yandex_geocoder import Client
import datetime, telegram
from geopy import GoogleV3
from settings import YANDEX_TOKEN
mdb = MongoClient(MONGODB_LINK)[MONGO_DB]
import folium
from utility import get_keyboard
from geopy.distance import geodesic
import numpy as np
from telegram.ext import ConversationHandler
import haversine

def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.chat.id,
            "Present": {"check_present": 0}
        }
        mdb.users.insert_one(user)
    return user


def save_user_location(mdb, user, b, location, time, problems):
    if 0 <= time.hour <= 12:
        r = "morning"
    else:
        r = "evening"
    s = time.strftime("%H-%M-%S")
    number = number_Facts(mdb, user, b, r)
    number = int(number) + 1
    print (number)
    print (r)
    time_of_day = "number " + str(r)
    Facts_number = "Facts." + b + "." + time_of_day
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Facts_number:
            {
                'number': number}
        }
        })
    r = str(number) + " " + r
    Facts = "Facts." + b + "." + r
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Facts:
                      {
                      'time': s,
                      'latitude': location.latitude,
                      'longitude': location.longitude,
                      'problems': problems,
                      'number': number}
                  }
         })
    return user

def check_point(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['check_present']

def check_group(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_group']

def check_unit(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_unit']

def number_Facts(mdb, user, b, r):
    print(user['user_id'])
    check = mdb.users.find_one({"user_id": user['user_id']})
    r = str(r) + " number"
    print("тут")
    try:
        print(check['Facts'][b][r]["number"])
        print("Все круто")
        number = check['Facts'][b][r]["number"]
    except Exception as ex:
        print("Сейчас буду здесь")
        print(ex)
        print("Все плохо")
        number = 0
    return number

def number_Report(mdb, user, b, r):
    print(user['user_id'])
    check = mdb.users.find_one({"user_id": user['user_id']})
    a = "number " + str(r)
    try:
        print(check['Report'][b][r][a]["number"])
        print("Все круто")
        number = check['Report'][b][r][a]["number"]
    except Exception as ex:
        print("Сейчас буду здесь")
        print(ex)
        print("Все плохо")
        number = 0
    return number

def lastname(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_lastname']

def get_group(mdb, effective_user):
    check = mdb.users.find_one({"user_id": effective_user.id})
    return check['Present']['user_group']

def save_user_report(mdb, user, report_category, unit_report, time):
    report_category = report_category.replace('.', ' ')
    report_category = report_category.replace('+', ' ')
    unit_report = unit_report.replace('.', ' ')
    unit_report = unit_report.replace('+', ' ')
    time = time.replace('.', ' ')
    time = time.replace('+', ' ')
    TIME = datetime.datetime.now()
    TIME = TIME.strftime("%d-%m-%Y")
    b = report_category
    r = unit_report
    number = number_Report(mdb, user, b, r)
    number = int(number) + 1
    r = "number " + str(r)
    Report_number = "Report." + report_category + "." + unit_report + "." + r
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Report_number:
                        {'number': number}
                            }
                  }
        ,
        True
    )
    unit_report_number = str(number) + " " + unit_report
    Report = "Report." + report_category + "." + unit_report + "." + unit_report_number
    TIME_HMS = datetime.datetime.now()
    TIME_HMS = TIME_HMS.strftime("%H-%M-%S")
    print(Report)
    mdb.users.update(
        {'_id': user['_id']},
        {'$set': {Report:
                        {'date': TIME,
                         'time': TIME_HMS,
                         'check': '0',
                         'number': number}
                            }
                  }
        ,
        True
    )
    return user

def save_kursant_anketa(mdb, user, user_data):
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'Present': {'user_group': user_data['user_group'],
                             'user_unit': user_data['user_unit'],
                             'user_lastname': user_data['user_lastname'],
                             'user_name': user_data['user_name'],
                             'user_middlename': user_data['user_middlename'],
                             'user_phone': user_data['user_phone'],
                             'check_present': 1
                             }
                  }
         }
    )
    return user

def save_user_anketa(mdb, user, user_data):
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'SOS':     {'user_lastname_mother': user_data['user_lastname_mother'],
                              'user_name_mother': user_data['user_name_mother'],
                              'user_middlename_mother': user_data['user_middlename_mother'],
                              'user_phone_mother': user_data['user_phone_mother'],
                              'user_address_mother': user_data['user_address_mother'],
                              'user_lastname_father': user_data['user_lastname_father'],
                              'user_name_father': user_data['user_name_father'],
                              'user_middlename_father': user_data['user_middlename_father'],
                              'user_phone_father': user_data['user_phone_father'],
                              'user_address_father': user_data['user_address_father'],
                              'user_lastname_other': user_data['user_lastname_other'],
                              'user_name_other': user_data['user_name_other'],
                              'user_middlename_other': user_data['user_middlename_other'],
                              'user_phone_other': user_data['user_phone_other'],
                              'user_address_other': user_data['user_address_other'],
                              'check_SOS': 0
                             }
                  }
         }
    )
    mdb.users.update_one({'_id': user['_id']},
                         {'$set': {'Present.check_present': 3}})
    return user

def check_address(doc):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    try:
        doc["Facts"][day][number]["address"]
        status = "OK"
        return status
    except Exception as ex:
        print(ex)
        status = "not OK"
        return status

def put_address(doc, address):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    user_id = doc["user_id"]
    Facts = "Facts." + day + "." + number + ".address"
    mdb.users.update({"user_id": user_id},
                     {'$set': {Facts: address}})
    return user_id

def find_report(bot, mdb, user_group, kursant_unit):
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    all_ok = "<b>Курсанты не имеющие проблем на данный момент:</b>"
    problems = "<b>Курсанты, имеющие проблемы:</b>"
    not_ok = "<b>Курсанты, не совершившие доклад:</b>"
    score_all_ok = 0
    score_problems = 0
    score_not_ok = 0
    if user_group == "91 курс":
        all_ok = "<b>901 учебная группа:</b>"
        problems = "<b>901 учебная группа:</b>"
        not_ok = "<b>901 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 901 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"

        print(not_ok)
        print(not_ok[1])
        cur = mdb.users.find({'Present.user_group': "901"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print (doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]), str(doc["Facts"][day][number]["longitude"]), doc)
                    home = (float(doc["Present"]["address"]["latitude"]), float(doc["Present"]["address"]["longitude"]))
                    point = (float(doc["Facts"][day][number]["latitude"]), float(doc["Facts"][day][number]["longitude"]))
                    distance = geodesic(point, home).m
                    print(str(round(distance)))
                    if doc["Facts"][day][number]["problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nРасстояние до места проведения отпуска: " + str(round(distance))\
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
        all_ok = "<b>903 учебная группа:</b>"
        problems = "<b>903 учебная группа:</b>"
        not_ok = "<b>903 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 903 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "903"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]),
                                                      str(doc["Facts"][day][number]["longitude"]), doc)
                    if doc["Facts"][day][number][
                        "problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                     "user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                       "user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
        all_ok = "<b>904 учебная группа:</b>"
        problems = "<b>904 учебная группа:</b>"
        not_ok = "<b>904 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        #904 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "904"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]),
                                                      str(doc["Facts"][day][number]["longitude"]), doc)
                    if doc["Facts"][day][number][
                        "problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                     "user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                       "user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
        all_ok = "<b>905-1 учебная группа:</b>"
        problems = "<b>905-1 учебная группа:</b>"
        not_ok = "<b>905-1 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 905-1
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "905-1"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]),
                                                      str(doc["Facts"][day][number]["longitude"]), doc)
                    if doc["Facts"][day][number][
                        "problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                     "user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                       "user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
        all_ok = "<b>905-2 учебная группа:</b>"
        problems = "<b>905-2 учебная группа:</b>"
        not_ok = "<b>905-2 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        # 905-2
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "905-2"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]),
                                                      str(doc["Facts"][day][number]["longitude"]), doc)
                    if doc["Facts"][day][number][
                        "problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                     "user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                       "user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
        all_ok = "<b>906 учебная группа:</b>"
        problems = "<b>906 учебная группа:</b>"
        not_ok = "<b>906 учебная группа:</b>"
        score_all_ok = 0
        score_problems = 0
        score_not_ok = 0
        #906 группа
        all_ok = all_ok + "\n<b>Курсанты не имеющие проблем на данный момент:</b>"
        problems = problems + "\n<b>Курсанты, имеющие проблемы:</b>"
        not_ok = not_ok + "\n<b>Курсанты, не совершившие доклад:</b>"
        cur = mdb.users.find({'Present.user_group': "906"})
        cur = cur.sort("Present.user_lastname", 1)
        for doc in cur:
            print(doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                "user_middlename"])
            number = "number " + time_of_day
            try:
                number = doc["Facts"][day][number]["number"]
                number = str(number) + " " + time_of_day
                try:
                    address = get_address_from_coords(str(doc["Facts"][day][number]["latitude"]),
                                                      str(doc["Facts"][day][number]["longitude"]), doc)

                    if doc["Facts"][day][number][
                        "problems"] == "Здоров. Без происшествий и проблем, требующих вмешательств.":
                        score_all_ok = score_all_ok + 1
                        all_ok = all_ok + "\n<b>" + str(score_all_ok) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                     "user_middlename"] \
                                 + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                 + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                 + "\nАдрес: " + str(address)
                    else:
                        score_problems = score_problems + 1
                        problems = problems + "\n<b>" + str(score_problems) + ".</b> " + doc["Present"][
                            "user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"][
                                       "user_middlename"] \
                                   + "\nВремя отметки: " + doc["Facts"][day][number]["time"] \
                                   + "\nМестонахождение: " + str(doc["Facts"][day][number]["latitude"]) + " " + str(
                            doc["Facts"][day][number]["longitude"]) \
                                   + "\nАдрес: " + str(address) \
                                   + "\nПроблемы: " + doc["Facts"][day][number]["problems"]
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print(ex)
                score_not_ok = score_not_ok + 1
                if doc["Present"]["check_present"] == 3:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"] \
                         + "\n<b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"]["user_name_mother"] + " " + doc["SOS"]["user_middlename_mother"] \
                         + "\n<b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                         + "\n<b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                         + "\n<b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"]["user_name_father"] + " " + doc["SOS"]["user_middlename_father"] \
                         + "\n<b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                         + "\n<b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                         + "\n<b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + doc["SOS"]["user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                         + "\n<b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                         + "\n<b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                else:
                    not_ok = not_ok + "\n<b>" + str(score_not_ok) + ".</b> " + doc["Present"]["user_lastname"] + " " + \
                         doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + "\n<b>Номер телефона для связи: </b>" + doc["Present"]["user_phone"]
        bot.message.reply_text(all_ok, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + problems, parse_mode=telegram.ParseMode.HTML)
        bot.message.reply_text("\n" + not_ok, parse_mode=telegram.ParseMode.HTML)
    print(all_ok)
    print(problems)
    print(not_ok)

    print("На этом пока всё!")

def get_address_from_coords(latitude, longitude, doc):
    #заполняем параметры, которые описывались выже. Впиши в поле apikey свой токен!
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    number = "number " + time_of_day
    number = doc["Facts"][day][number]["number"]
    number = str(number) + " " + time_of_day
    if check_address(doc) == "not OK":
        client = Client(YANDEX_TOKEN)
        try:
            address = client.address(longitude,latitude)
            put_address(doc, address)
            return address
        except Exception as e:
            #если не смогли, то возвращаем ошибку
            return "error"
    else:
        return doc["Facts"][day][number]["address"]

def create_map(bot, update):
    print("Я тут")
    time = datetime.datetime.now()
    if 0 <= time.hour <= 12:
        time_of_day = "morning"
    else:
        time_of_day = "evening"
    day = time.strftime("%d-%m-%Y")
    hour = time.strftime("%H-%M-%S")
    map = folium.Map(location=[59.812019, 30.378742], zoom_start = 8)
    cur = mdb.users.find()
    for doc in cur:
        number = "number " + time_of_day
        try:
            number = doc["Facts"][day][number]["number"]
            number = str(number) + " " + time_of_day
            try:
                try:
                    Family = "<p><b>Мать: </b>" + doc["SOS"]["user_lastname_mother"] + " " + doc["SOS"][
                        "user_name_mother"] + " " + \
                             doc["SOS"]["user_middlename_mother"] \
                             + "<p><b>Телефон матери: </b>" + doc["SOS"]["user_phone_mother"] \
                             + "<p><b>Адрес матери: </b>" + doc["SOS"]["user_address_mother"] \
                             + "<p><b>Отец: </b>" + doc["SOS"]["user_lastname_father"] + " " + doc["SOS"][
                                 "user_name_father"] + " " + \
                             doc["SOS"]["user_middlename_father"] \
                             + "<p><b>Телефон отца: </b>" + doc["SOS"]["user_phone_father"] \
                             + "<p><b>Адрес отца: </b>" + doc["SOS"]["user_address_father"] \
                             + "<p><b>Друг (подруга и т.д.): </b>" + doc["SOS"]["user_lastname_other"] + " " + \
                             doc["SOS"][
                                 "user_name_other"] + " " + doc["SOS"]["user_middlename_other"] \
                             + "<p><b>Телефон друга: </b>" + doc["SOS"]["user_phone_other"] \
                             + "<p><b>Адрес друга: </b>" + doc["SOS"]["user_address_other"]
                except Exception as ex:
                    print(ex)
                    Family = "<p>Данных о семье нет"
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + Family
                print(user_name)
                latitude = str(doc["Facts"][day][number]["latitude"])
                longitude = str(doc["Facts"][day][number]["longitude"])
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[latitude, longitude], popup= popup, icon=folium.Icon(color = 'gray')).add_to(map)
                latitude = str(doc["Present"]["address"]["latitude"])
                longitude = str(doc["Present"]["address"]["longitude"])
                user_name = doc["Present"]["user_lastname"] + " " + doc["Present"]["user_name"] + " " + doc["Present"]["user_middlename"] + " <p>+" + doc["Present"]["user_phone"] + " <p>" + doc["Present"]["address"]["address"]
                popuptext = user_name
                iframe = folium.Html(popuptext, script=True)
                popup = folium.Popup(iframe, max_width=300, min_width=300)
                folium.Marker(location=[latitude, longitude], popup=popup, icon=folium.Icon(color= 'red', icon='home')).add_to(map)
            except Exception as ex:
                print(ex)
        except Exception as ex:
            print(ex)
    if 0 <= time.hour <= 12:
        time_of_day = "утро"
    else:
        time_of_day = "вечер"
    day = time.strftime("%d.%m.%Y")
    title = "Карты/Обстановка на " + time_of_day + " " + day + " " + hour + ".html"
    map.save(title)
    with open(title, "rb") as file:
        update.bot.send_document(chat_id=bot.message.chat.id, document=file,
                                  filename=title)
    print(bot)


def lets_go(bot, update):
    user = mdb.users.find_one({"Present.check_present":1})
    user_id = user["user_id"]
    update.user_data['find_user_id'] = user_id
    name = 'Введите адрес:' + user["Present"]["user_lastname"] + " " + user["Present"]["user_name"] + " " + user["Present"]["user_middlename"]
    bot.message.reply_text(name)
    return "put_address_from_coords"

def put_address_from_coords(bot, update):
    print("тут")
    user_id = update.user_data['find_user_id']
    print(user_id)
    address = bot.message.text
    print(address)
    try:
        client = Client(YANDEX_TOKEN)
        print("вот тут")
        coordinates = client.coordinates(address)
        print(coordinates[1])
        print(coordinates[0])
        mdb.users.update_one ({"user_id":user_id},
                              {"$set": {"Present.address":
                                            {"latitude": str(coordinates[1]),
                                             "longitude": str(coordinates[0]),
                                             "address":address
                                            }}})
        mdb.users.update_one({"user_id": user_id},
                             {"$set": {"Present.check_present": 4
                                           }})
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text('Введенные данные отправлены на проверку!', reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
    except Exception as e:
        check_user = check_point(mdb, bot.effective_user)
        bot.message.reply_text(e, reply_markup=get_keyboard(check_user))
        return ConversationHandler.END
