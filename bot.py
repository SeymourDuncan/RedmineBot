import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.tebot_token)

# commands =\
#     {'Отчеты': {
#         'Протокол тестирования':{
#             'Ngt-Smart 4.1.9':{},
#             'Ngt-Smart 4.2.0':{}
#         },
#         'What''s new':{
#             'Ngt-Smart 4.1.9':{},
#             'Ngt-Smart 4.2.0':{}
#         }
#     },
#     'Справка' : {}
#     }

commands =\
    [
        ('Отчеты', [
            ('Протокол тестирования',[
                ('Ngt-Smart 4.1.9', []),
                ('Ngt-Smart 4.2.0', [])
            ]),
            ('What''s new', [
                ('Ngt-Smart 4.1.9', []),
                ('Ngt-Smart 4.2.0', [])
            ])
        ]),
        ('Справка', [])
    ]

class UserStory():
    def __init__(self, chat_id):
        self.chat_id = 0
        self.indices = []

# список активных диалогов
user_stories = []

def MakeKeyBoard(lst = []):
    markup = types.ReplyKeyboardMarkup()
    l = []
    if not lst:
        lst = commands
    for k in lst:
        markup.row(k[0])

def ProcessMessage(chat_id, msg):
    # ищем юзерстори
    ustories = next(a for a in user_stories if a.chat_id == chat_id)

    # не нашли
    if ustories == None:
        ad = UserStory(chat_id)
        # idx_tpl - (индекс выбранной команды, список следующих команд в виде таплов)
        idx_tpl = next(((i, c[1]) for i, c in enumerate(commands) if c[0] == msg), None)
        if idx_tpl == None:
            return None
        ad.indices.append(idx_tpl[0])
        return idx_tpl[1]

    # нашли
    for story in ustories:


# начало работы
@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Выберите одну из команд", reply_markup=MakeKeyBoard())

# обработка запросов
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    res = ProcessMessage(message.chat.id, message.text)
    if type() is list:
        bot.send_message(message.chat.id, "Выберите одну из команд", reply_markup=MakeKeyBoard(res))
    else:
        return

    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
     bot.polling(none_stop=True)