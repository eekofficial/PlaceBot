import telebot
import sqlite3
from collections import defaultdict
import os

BOT_TOKEN = '813654692:AAHieCj0WbO2-xq6viWNeustBK6W94g77eM'

bot = telebot.TeleBot(BOT_TOKEN)

START, TITLE, ADDRESS, PHOTO, LOCATION = range(5)

USER_STATE = defaultdict(lambda: START)

place_dict = dict()

def update_state(message, state):
    USER_STATE[message.chat.id] = state

def get_state(message):
    return USER_STATE[message.chat.id]

def save_place(message, place_dict):
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    cursor.execute("""
            insert into places values ('{}', '{}', '{}', '{}', '{}', '{}')
        """.format(message.chat.id, place_dict['title'], place_dict['address'], place_dict['photo'], place_dict['location'].longitude, place_dict['location'].latitude))
    conn.commit()
    conn.close()

def get_places(message):
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    cursor.execute("""
        select * from places where user_id='{}'
    """.format(message.chat.id))
    data = cursor.fetchall()
    cursor.close()
    return data

def delete_places(message):
    places = get_places(message)
    for place in places:
        os.remove(place[3])
    conn = sqlite3.connect('places.db')
    cursor = conn.cursor()
    cursor.execute("""
        delete from places where user_id='{}'
    """.format(message.chat.id))
    conn.commit()
    cursor.close()

def put_photo(message):
    photo_id = message.photo[2].file_id
    name = photo_id + '.jpg'
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('place_photo/{}'.format(name), 'wb') as f:
        f.write(downloaded_file)
    return 'place_photo/{}'.format(name)

@bot.message_handler(commands=['start'])
def handle_start(message):
    print(message)
    bot.send_message(message.chat.id, 'Привет, меня зовут PlaceBot!\nЯ умею сохранять места для будущего посещения.')
    bot.send_message(message.chat.id, 'Для навигации используй /help')

@bot.message_handler(commands=['help'])
def handle_help(message):
    print(message)
    bot.send_message(message.chat.id, 'Доступные команды:\n/add – добавление нового места\n/list – отображение добавленных мест\n/reset - удаление всех добавленных локаций')

@bot.message_handler(commands=['add'])
def handle_add(message):
    print(message)
    update_state(message, TITLE)
    bot.send_message(message.chat.id, 'Введите название места:')

@bot.message_handler(commands=['list'])
def handle_list(message):
    print(message)
    if get_places(message):
        bot.send_message(message.chat.id, 'Список сохраненных мест:')
        for place in get_places(message):
            if get_places(message).index(place) == 10:
                break
            bot.send_message(message.chat.id, 'Место {}:'.format(get_places(message).index(place) + 1))
            img = open(place[3], 'rb')
            bot.send_photo(message.chat.id, img)
            bot.send_message(message.chat.id, '{}\n{}'.format(place[1], place[2]))
            bot.send_location(message.chat.id, place[5], place[4])
    else:
        bot.send_message(message.chat.id, 'Список сохраненных мест пуст')

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    print(message)
    delete_places(message)
    bot.send_message(message.chat.id, 'Все ваши места удалены')

@bot.message_handler(func=lambda message: get_state(message) == TITLE)
def handle_title(message):
    print(message)
    place_dict.update({'title': message.text})
    bot.send_message(message.chat.id, 'Введите адрес:')
    update_state(message, ADDRESS)

@bot.message_handler(func=lambda message: get_state(message) == ADDRESS)
def handle_address(message):
    print(message)
    place_dict.update({'address': message.text})
    bot.send_message(message.chat.id, 'Пришлите фотографию места:')
    update_state(message, PHOTO)

@bot.message_handler(func=lambda message: get_state(message) == PHOTO)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print(message)
    place_dict.update({'photo': put_photo(message)})
    bot.send_message(message.chat.id, 'Пришлите локацию:')
    update_state(message, LOCATION)

@bot.message_handler(func=lambda message: get_state(message) == LOCATION)
@bot.message_handler(content_types=['location'])
def handle_location(message):
    print(message)
    place_dict.update({'location': message.location})
    # Сохранение места в базе данных
    save_place(message, place_dict)
    bot.send_message(message.chat.id, 'Место успешно сохранено')
    update_state(message, START)

bot.polling()


