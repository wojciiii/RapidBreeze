from command import Command

from core.cmodel import ClassEntity
#from core.cmodel import ClassConnection
#from core.cmodel import Member
import core.constants as constants

class CreateCommand(Command):
    def __init__(self, context):
        self.createClass     = False
        self.createInterface = False
        self.name            = ""
        self.context         = context
        self.redraw          = False

    def execute(self):

        if self.createClass:
            c = ClassEntity(entity_name=self.name)
            self.context.add(c)
        elif self.createInterface:
            c = ClassEntity(entity_name=self.name, entity_type=constants.INTERFACE)
            self.context.add(c)

        self.context.dump()

        # Updated mode, needs redrawing.
        self.redraw = True

        return "Created"

    def cancel(self):
        pass

    def redrawRequired(self):
        return self.redraw

    @staticmethod
    def name():
        return "create"

    def expectsArguments(self):
        return True

    def parseArguments(self, arg):
        print ("Parsing arguments %s" % arg)
        if len(arg) < 2:
            raise ValueError("Unexpected number of arguments")

        if arg[0] == "class":
            self.createClass = True

        if arg[0] == "interface":
            self.createInterface = True

        if self.createInterface == False and self.createClass == False:
            raise ValueError("Don't know how to create %s" % arg[0])

        self.name = arg[1]

        if len(self.name) == 0:
            raise ValueError("Class or interface name missing.")
