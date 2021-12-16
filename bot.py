from telebot import TeleBot ,types,util
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import os


from telebot import TeleBot, types, util

stat_dict = dict()

TOKEN = '2100684897:AAHtiSM6TdaeuxvGSX-0Bz4e0-WyDwQLwRQ'

bot = TeleBot(TOKEN)

mongodb_host = os.environ.get('MONGO_HOST', 'mongo')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)
db = client['todo']


@bot.message_handler(commands=['help'])
def help(update):
    bot.send_message(update.chat.id,
                     'На данный момент я знаю следующие команды \n /help - справка о командах \n /stat - статистика по пользователям',
                     reply_to_message_id=update.message_id)


@bot.message_handler(commands=['publish'])
def publish(update):
    print("Message from tlg: ", update.text.replace('/publish ', ''))


@bot.message_handler(commands=['stat'])
def stat(update):
    if update.chat.type == 'supergroup':
        chat_name = update.chat.title
        rez = chat_name + '\n'
        for d in sorted(loads(dumps(db[chat_name].find())), key=lambda p: (-p['counter'], p['name'])):
            rez += d["name"] + ': ' + str(d["counter"]) + '\n'

    elif update.chat.type == 'private':
        rez = ''
        for group in sorted(db.list_collection_names()):
            rez += group + ':\n'
            for d in sorted(loads(dumps(db[group].find())), key=lambda p: (-p['counter'], p['name'])):
                rez += d["name"] + ': ' + str(d["counter"]) + '\n'

    try:
        bot.send_message(update.chat.id, rez, reply_to_message_id=update.message_id)
    except:
        bot.send_message(update.chat.id, 'Статистика пока отсутствует', reply_to_message_id=update.message_id)


@bot.my_chat_member_handler()
def run(message):
    global stat_dict
    if message.new_chat_member.status == 'left' or message.new_chat_member.status == 'kicked':
        if message.chat.title in db.list_collection_names():
            db.drop_collection(message.chat.title)


@bot.message_handler(content_types='text')
def echo(update):
    parazid = ['ковид', "коронавирус", "вакцина", "вакцинация", "covid"]
    if update.chat.type == 'supergroup':
        chat_id = update.chat.title
    else:
        chat_id = update.chat.username
    user_name = update.json['from']['username']
    for i in parazid:
        if i in update.text.lower():
            a = db[chat_id]
            # print(a)
            if a.find_one({'name': user_name}) is None:
                user_data = {
                    "name": user_name,
                    "counter": 1,
                }
                a.insert_one(user_data)
            else:
                tmp = a.find_one({'name': user_name})['counter']
                current_name = {'name': user_name}
                current_cnt = {"$set": {'counter': tmp + 1}}
                a.update_one(current_name, current_cnt)

            bot.send_message(update.chat.id, 'Данная информация может содержать информацию о Короновирусно инфекции',
                             reply_to_message_id=update.message_id)


if __name__ == "__main__":
    bot.infinity_polling(allowed_updates=util.update_types)