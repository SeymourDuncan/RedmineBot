import config
import telebot
from telebot import types
from mytypes import Command, UserStory, DocumentFile
from consts import Messages, Reports
from redmineWrapper import RedmineWrapper

# создание клавиатуры
def makeKeyBoard(cmd):
    markup = types.ReplyKeyboardMarkup()
    for k in cmd.CommandsNames:
        markup.row(k)
    return markup

# поиск в глубину по id
def findCommandById(cmdlist, id):
    for cmd in cmdlist:
        if cmd.id == id:
            return cmd
        elif cmd.hasCommands() and cmd.id > 0: # нельзя заходить в back-команду, т.к. зациклимся
            res = findCommandById(cmd.getCommands(), id)
            if res:
                return res

# простой поиск по name команды
def findCommandByName(cmdlist, name):
    return next((c for c in cmdlist if c.name == name), None)

class RedmineBot():
    def __init__(self):
        self.bot = telebot.TeleBot(config.tebot_token)
        # список активных диалогов
        self.user_stories = []
        # команда самого вернхего уровня
        self.root_cmd = None
        self.redmine = RedmineWrapper()

    def start(self):
        self.buildCommands()

        @self.bot.message_handler(commands=['start'])
        def handle_start_help(message):
            self.bot.send_message(message.chat.id, Messages.help_msg.format(message.chat.first_name), reply_markup=makeKeyBoard(self.root_cmd))

        # обработка запросов
        @self.bot.message_handler(content_types=["text"])
        def repeat_all_messages(message):
            res = self.processMessage(message.chat.id, message.text)
            if type(res) is Command:  # если Команда - вернем новые кнопки
                self.bot.send_message(message.chat.id, "Выберите одну из команд", reply_markup=makeKeyBoard(res))
            elif type(res) is str:
                self.bot.send_message(message.chat.id, res)
            elif type(res) is DocumentFile:
                self.bot.send_chat_action(message.chat.id, 'upload_document')
                self.bot.send_document(message.chat.id, data=open(Reports.tp_filen, mode="rb"), caption='Протокол тестирования {}.docx'.format(message.text))
            else:
                self.bot.send_message(message.chat.id, Messages.bad_commad_msg)

        self.bot.polling(none_stop=True)

    def stop(self):
        self.bot.stop_polling()

    # построение дерева команд
    def buildCommands(self):
        self.root_cmd = Command('Root')
        report_cmd = Command('Отчеты')

        protocoltest_cmd = Command('Протокол тестирования')
        protocoltest_cmd.addCommand(Command('NGT-Smart Версия 4.1.9', self.redmine.getTestProtocol, {'version' : 'NGT-Smart Версия 4.1.9'}))
        protocoltest_cmd.addCommand(Command('NGT-Smart Версия 4.2.0', self.redmine.getTestProtocol, {'version' : 'NGT-Smart Версия 4.2.0'}))

        whatsnew_cmd = Command('What''s new')
        whatsnew_cmd.addCommand(Command('Ngt-Smart 4.1.9'))
        whatsnew_cmd.addCommand(Command('Ngt-Smart 4.2.0'))

        report_cmd.addCommand(protocoltest_cmd)
        report_cmd.addCommand(whatsnew_cmd)

        # help_cmd = Command('Справка', lambda: Messages.help_msg)

        self.root_cmd.addCommand(report_cmd)
        # self.root_cmd.addCommand(help_cmd)

    # Обработка действия пользователя
    def processMessage(self, chat_id, msg):
        # ищем юзерстори
        ustory = next((a for a in self.user_stories if a.chat_id == chat_id), None)
        # вызываемая команда
        cmd = None
        # не нашли юзерстори. Создадим
        if not ustory:
            ustory = UserStory(chat_id)
            self.user_stories.append(ustory)

        # если пользователь до этого еще ничего не делал
        if not ustory.indices:
            # узнаем что он вызвал сейчас
            cmd = findCommandByName(self.root_cmd.getCommands(), msg)
        # если уже что-то делал
        else:
            # узнаем какую предыдущую команду запускал пользователь
            # она нужна чтобы найти вызванную команду
            last_cmd = findCommandById(self.root_cmd.getCommands(), ustory.indices[-1])
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




