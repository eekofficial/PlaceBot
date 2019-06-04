import telebot

BOT_TOKEN = '813654692:AAHieCj0WbO2-xq6viWNeustBK6W94g77eM'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['add'])
def handle_add(message):
    print(message)
    bot.send_message(message.chat.id, 'Вы хотите добавить новое место')

@bot.message_handler(commands=['list'])
def handle_list(message):
    print(message)
    bot.send_message(message.chat.id, 'Вы захотели посмотреть список мест')

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    print(message)
    bot.send_message(message.chat.id, 'Вы захотели удалить все добавленные места')

bot.polling()

