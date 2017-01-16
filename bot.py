import config
import telebot
from telebot import types as teletypes
from types import Command, UserStory

bot = telebot.TeleBot(config.tebot_token)

commands = []
def BuildCommands():
    report_cmd = Command('Отчеты')

    protocoltest_cmd = Command('Протокол тестирования')
    protocoltest_cmd.addCommand(Command('Ngt-Smart 4.1.9'))
    protocoltest_cmd.addCommand(Command('Ngt-Smart 4.2.0'))

    whatsnew_cmd = Command('What''s new')
    whatsnew_cmd.addCommand(Command('Ngt-Smart 4.1.9'))
    whatsnew_cmd.addCommand(Command('Ngt-Smart 4.2.0'))

    report_cmd.addCommand(protocoltest_cmd)
    report_cmd.addCommand(whatsnew_cmd)

    help_cmd = Command('Справка')

    commands.append(report_cmd)
    commands.append(help_cmd)


# список активных диалогов
user_stories = []

def MakeKeyBoard(lst = []):
    markup = teletypes.ReplyKeyboardMarkup()
    l = None
    if not lst:
        lst = list(c.name for c in commands)
    for k in l:
        markup.row(k)

def findCommandById(cmdlist, id):
    for cmd in cmdlist:
        if cmd.id == id:
            return cmd
        elif cmd.hasCommands:
            res = findCommandById(cmd.getCommands, id)
            if res:
                return res

def ProcessMessage(chat_id, msg):
    # ищем юзерстори
    ustory = next(a for a in user_stories if a.chat_id == chat_id)

    # вызываемая команда
    cmd = None
    # не нашли
    if ustory == None:
        cmd = next((c for c in commands if c.name == msg), None)
        if not cmd:
            return None
        ustory = UserStory(chat_id)
        user_stories.append(ustory)
    else:
        # узнаем какую предыдущую команду запускал пользователь
        last_cmd = findCommandById(commands, ustory.indices[-1])
        # теоретически не должно быть
        if last_cmd or not last_cmd.hasCommands:
            return None
        cmd = next((c for c in last_cmd.getCommands if c.name == msg), None)

    # итак, нашли вызванную команду
    # добавяем в юзерстори
    ustory.indices.append(cmd.id)
    # решаем что делать с вызванной командой
    if cmd.hasCommands:
        return cmd.getCommandsNames

    return cmd.execute;

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