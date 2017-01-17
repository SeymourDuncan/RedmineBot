import config
import telebot
from telebot import types
from mytypes import Command, UserStory
from consts import Messages

bot = telebot.TeleBot(config.tebot_token)

# список активных диалогов
user_stories = []

def MakeKeyBoard(cmd):
    markup = types.ReplyKeyboardMarkup()
    for k in cmd.CommandsNames:
        markup.row(k)
    return markup

root_cmd = None

# простой поиск по name команды
def findCommandByName(cmdlist, name):
    return next((c for c in cmdlist if c.name == name), None)

# поиск в глубину по id
def findCommandById(cmdlist, id):
    for cmd in cmdlist:
        if cmd.id == id:
            return cmd
        elif cmd.hasCommands() and cmd.id > 0: # нельзя заходить в back-команду, т.к. зациклимся
            res = findCommandById(cmd.getCommands(), id)
            if res:
                return res

def buildCommands():
    root = Command('Root')

    report_cmd = Command('Отчеты')

    protocoltest_cmd = Command('Протокол тестирования')
    protocoltest_cmd.addCommand(Command('Ngt-Smart 4.1.9'))
    protocoltest_cmd.addCommand(Command('Ngt-Smart 4.2.0'))

    whatsnew_cmd = Command('What''s new')
    whatsnew_cmd.addCommand(Command('Ngt-Smart 4.1.9'))
    whatsnew_cmd.addCommand(Command('Ngt-Smart 4.2.0'))

    report_cmd.addCommand(protocoltest_cmd)
    report_cmd.addCommand(whatsnew_cmd)

    help_cmd = Command('Справка', lambda: 2**2)

    root.addCommand(report_cmd)
    root.addCommand(help_cmd)

    return root
# Обработка действия пользователя
def ProcessMessage(chat_id, msg):
    # ищем юзерстори
    ustory = next((a for a in user_stories if a.chat_id == chat_id), None)
    # вызываемая команда
    cmd = None
    # не нашли юзерстори. Создадим
    if not ustory:
        ustory = UserStory(chat_id)
        user_stories.append(ustory)

    # если пользователь до этого еще ничего не делал
    if not ustory.indices:
        # узнаем что он вызвал сейчас
        cmd = findCommandByName(root_cmd.getCommands(), msg)
    # если уже что-то делал
    else:
        # узнаем какую предыдущую команду запускал пользователь
        # она нужна чтобы найти вызванную команду
        last_cmd = findCommandById(root_cmd.getCommands(), ustory.indices[-1])
        cmd = findCommandByName(last_cmd.getCommands(), msg)

    # если вызвал не то, что положено, например вручную вбил команду - то ничего не делаем
    if not cmd:
        return None
    # итак, нашли вызванную команду
    # решаем что делать с вызванной командой
    if cmd.hasCommands():
        # добавяем в юзерстори только если есть внутренние команды,
        # т.к. юзерстори нужна для навигации по командам, а команда, у которой нет подкоманд - не меняет положение юзера в дереве
        if cmd.id < 0: # специальная команда "Назад"
            ustory.indices.pop(-1)
        else:
            ustory.indices.append(cmd.id)
        return cmd

    # выполняем
    return cmd.execute()

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, Messages.help_msg.format(message.chat.first_name))

# обработка запросов
@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    res = ProcessMessage(message.chat.id, message.text)
    if type(res) is Command: # если Команда - вернем новые кнопки
        bot.send_message(message.chat.id, "Выберите одну из команд", reply_markup=MakeKeyBoard(res))
    else:
        bot.send_message(message.chat.id, Messages.bad_commad_msg)

if __name__ == '__main__':
    root_cmd = buildCommands()
    bot.polling(none_stop=True)