from enum import Enum

# Command class
class Command():
    global_id = 0
    def __init__(self, name, action = None):
        self.name = name
        self.commands = []
        Command.global_id += 1
        self.id = Command.global_id
        self.action = action

    # Add child command to this command
    def addCommand(self, command):
        # если добавляемая команда что-то выполняет, то у нее нет back-команды
        if not command.action:
            command.makeBackCmd(self)
        self.commands.append(command)

    # Get all child commands
    def getCommands(self):
        return self.commands

    # Get string list by commands names
    @property
    def CommandsNames(self):
        return list(c.name for c in self.getCommands())

    # Get child command by id
    def getCommand(self, idx):
        return next((c for c in self.commands if c.id == idx), None)

    # Does command has child commands
    def hasCommands(self):
        return bool(self.commands)

    # Execute command. Returns False if action was not set
    def getAction(self):
        if not self.action:
            return False
        return self.action

    #
    def makeBackCmd(self, parentCmd):
        backCommand = Command('Назад')
        backCommand.id = -1
        backCommand.commands = parentCmd.commands
        self.commands.append(backCommand)

# Action class
class Action:
    def __init__(self, action, args):
        self.action = action
        self.args = args

    def execute(self):
        return self.action(**self.args)

# Send action class
class SendFileAction(Action):
    def __init__(self, action, args, filename):
        super(SendFileAction, self).__init__(action, args)
        self.filename = filename


# User story class
class UserStory():
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.indices = []

class DocumentFile():
    def __init__(self, filename):
        self.filename = filename
