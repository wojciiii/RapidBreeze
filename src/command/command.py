class Command(object):

    def execute(self):
        raise NotImplementedError()

    def cancel(self):
        raise NotImplementedError()

    def parseArguments(self, arg):
        print("Warning: this parseArguments does nothing.")

    def expectsArguments(self):
        return False

    # Indicates if re-generation is required.
    def redrawRequired(self):
        return False

    @staticmethod
    def name():
        raise NotImplementedError()

class HelpCommand(Command):
    def execute(self):
        print ("Help command executed")
        helpStr = """Help: The following commands are supported:
        ...
        """
        return helpStr

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "help"

class QuitCommand(Command):
    def __init__(self, context):
        self.context = context

    def execute(self):
        #self.context.commandResponseFnct("OK")
        self.context.signalStop()
        self.context.quitFnct()
        return "OK"

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "quit"

class UndoCommand(Command):
    def execute(self):
        pass

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "undo"

class RedoCommand(Command):
    def execute(self):
        pass

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "redo"

class HistoryCommand(Command):
    def execute(self):
        pass

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "history"

class EmptyCommand(Command):
    def execute(self):
        pass

    def cancel(self):
        pass

    @staticmethod
    def name():
        return "empty"

class SetOptionCommand(Command):
    def __init__(self, context):
        self.context = context
        self.name    = ""
        self.value   = ""

    def execute(self):
        self.context.setOption(self.name, self.value)
        return "OK"

    @staticmethod
    def createInstance(name, value):
        return SetOptionCommand.name() + " " + name + " " + value

    def parseArguments(self, arg):
        self.name = arg[0]
        self.value = arg[1]

    def expectsArguments(self):
        return True

    def cancel(self):
        # No cancel.
        pass

    @staticmethod
    def name():
        return "SetOption"

class ForceUpdateCommand(Command):
    def __init__(self, context):
        self.context = context

    def execute(self):
        self.context.forceUpdate()
        return "OK"

    @staticmethod
    def createInstance():
        return ForceUpdateCommand.name()

    def expectsArguments(self):
        return False

    def cancel(self):
        # No cancel.
        pass

    @staticmethod
    def name():
        return "ForceUpdateCommand"
