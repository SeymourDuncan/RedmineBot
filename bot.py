import config
import telebot
from telebot import types
from mytypes import Command, UserStory, Action, SendFileAction
from consts import Messages, RedmineConsts, Reports, Paths
from redmineWrapper import RedmineWrapper
import logging
import sys
import os

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
        # пока что однопоточный режим
        self.bot = telebot.TeleBot(config.tebot_token, threaded=False)
        # список активных диалогов
        self.user_stories = []
        # команда самого вернхего уровня
        self.root_cmd = None
        self.redmine = RedmineWrapper()
        logging.basicConfig(filename=Paths.log_file, format='%(asctime)s %(message)s', datefmt='%d.%m.%Y %I:%M:%S %p')

    def remove_userstory(self, chat_id):
        '''Удаление userstory по id chat id'''

        # делаем новый список
        new_us = [us for us in self.user_stories if us.chat_id != chat_id]
        self.user_stories = new_us

    def start(self):
        self.buildCommands()

        @self.bot.message_handler(commands=['start'])
        def handle_start_help(message):
            self.remove_userstory(message.chat.id)
            self.bot.send_message(message.chat.id, Messages.help_msg.format(message.chat.first_name), reply_markup=makeKeyBoard(self.root_cmd))

        # обработка запросов
        @self.bot.message_handler(content_types=["text"])
        def repeat_all_messages(message):
            try:
                res = self.processMessage(message.chat.id, message.text)
                if type(res) is Command:  # если Команда - вернем новые кнопки
                    logging.error("Command {0}".format(res.name))
                    self.bot.send_message(message.chat.id, Messages.select_command, reply_markup=makeKeyBoard(res))
                elif type(res) is str: # Если строка то просто выводим как сообщение
                    self.bot.send_message(message.chat.id, res)
                elif type(res) is SendFileAction: # Может что-то выполнять.
                    # показываем что занимается отправкой
                    self.bot.send_message(message.chat.id, Messages.prepare_file.format(res.filename))
                    logging.error("Executing")
                    result = res.execute()
                    self.bot.send_chat_action(message.chat.id, 'upload_document')
                    logging.info("File path {0}".format(result.filename))
                    self.bot.send_document(message.chat.id, data=open(result.filename , mode="rb"), caption=res.filename)
                else:
                    self.bot.send_message(message.chat.id, Messages.bad_commad_msg)
            except:
                logging.error("{0} {1}".format(sys.exc_info()[0], sys.exc_info()[1]))

        self.bot.polling(none_stop=True)

    def stop(self):
        self.bot.stop_polling()

    # построение дерева команд
    def buildCommands(self):
        self.root_cmd = Command('Root')
        report_cmd = Command('Отчеты')

        protocoltest_cmd = Command('Протокол тестирования')

        fn_tmp = 'Протокол тестирования {}.docx'

        for version in RedmineConsts.versions:
            cmd_ver = Command(version)
            for customer in RedmineConsts.customers:
                cmd_cstm = Command(customer, SendFileAction(self.redmine.getTestProtocol,
                                                           {'version': version, 'customer': customer},
                                                           fn_tmp.format(version)))
                cmd_ver.addCommand(cmd_cstm)
            protocoltest_cmd.addCommand(cmd_ver)

        whatsnew_cmd = Command('What\'s new')
        report_cmd.addCommand(protocoltest_cmd)
        report_cmd.addCommand(whatsnew_cmd)

        self.root_cmd.addCommand(report_cmd)

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
        return cmd.getAction()




