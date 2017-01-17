# Command class
class Command():
    global_id = 0
    def __init__(self, name, action = None):
        self.name = name
        self.commands = []
        self.id = Command.global_id
        self.action = action
        Command.global_id+=1

    # Add child command to this command
    def addCommand(self, command):
        self.commands.append(command)

    # Get all child commands
    def getCommands(self):
        return self.commands

    # Get string list by commands names
    def getCommandsNames(self):
        return list(c.name for c in self.commands)

    # Get child command by id
    def getCommand(self, idx):
        return next((c for c in self.commands if c.id == idx), None)

    # Does command has child commands
    def hasCommands(self):
        return bool(self.commands)

    # Execute command. Returns False if action was not set
    def execute(self):
        if not self.action:
            return False

        return self.action()

# User story class
class UserStory():
    def __init__(self, chat_id):
        self.chat_id = 0
        self.indices = []