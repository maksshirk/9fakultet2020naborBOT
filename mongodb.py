from pymongo import MongoClient
from settings import MONGO_DB
from settings import MONGODB_LINK
import datetime

mdb = MongoClient(MONGODB_LINK)[MONGO_DB]


def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({"user_id": effective_user.id})
    if not user:
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.chat.id
        }
        mdb.users.insert_one(user)
    return user


def save_user_location(mdb, user, b, location, time):
    if 0 <= time.hour <= 12:
        r = "morning"
    else:
        r = "evening"
    b = b + " " + r
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {b: {'latitude': location.latitude,
                      'longitude': location.longitude}}})
    return user


def save_user_anketa(mdb, user, user_data):
    time = datetime.datetime.now()
    anketa = "anketa " + time
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'anketa': {'group': user_data['group'],
                             'position': user_data['position'],
                             'lastname': user_data['lastname'],
                             'name': user_data['name'],
                             'middlename': user_data['middlename'],
                             'phone': user_data['phone'],
                             'address': user_data['address'],
                             'lastname_mother': user_data['lastname_mother'],
                             'name_mother': user_data['name_mother'],
                             'middlename_mother': user_data['middlename_mother'],
                             'phone_mother': user_data['phone_mother'],
                             'address_mother': user_data['address_mother'],
                             'lastname_father': user_data['lastname_father'],
                             'name_father': user_data['name_father'],
                             'middlename_father': user_data['middlename_father'],
                             'phone_father': user_data['phone_father'],
                             'address_father': user_data['address_father'],
                             'lastname_other': user_data['lastname_other'],
                             'name_other': user_data['name_other'],
                             'middlename_other': user_data['middlename_other'],
                             'phone_other': user_data['phone_other'],
                             'address_other': user_data['address_other'],
                             }
                  }
         }
    )
    return user
