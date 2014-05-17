import threading
import Queue
import hashlib

from command import *
from model import *

from uml.plantumlgenerator import PlantUmlGenerator
from uml import plantuml as puml

class CommandParser(object):
    """
    Parse textual commands and converts them into objects.
    """

    # Indices into a dict used to describe the functions 
    # which are used by the spawned threads.
    OnUpdate          = 0
    OnCommandResponse = 1
    OnCommandError    = 2
    OnExit            = 3
    OnUpdateImage     = 4

    def __init__(self, context, cmds):
        self.commandQueue    = Queue.Queue()
        self.processingQueue = Queue.Queue()

        self.savedCommands   = cmds

        self.cpt = CommandParserThread(self.commandQueue, self.processingQueue, context)
        self.cpt.start()

        self.gt = GeneratorThread(self.processingQueue, context)
        self.gt.start()

    def registerHandlers(self, handlers):
        self.cpt.registerHandlers(handlers)
        self.gt.registerHandlers(handlers)

    def setOnUpdate(self, updateFnct):
        self.cpt.setOnUpdate(updateFnct)

    def setOnCommandResponse(self, commandResponseFnct):
        self.cpt.setOnCommandResponse(commandResponseFnct)

    def setOnCommandError(self, commandErrorFnct):
        self.cpt.setOnCommandError(commandErrorFnct)

    def sendCommand(self, text):
        print ("Sending command: %s" % text)
        self.commandQueue.put(text)

    def executeSavedCommands(self):
        self.disableDrawing()
        try:
            for cmd in self.savedCommands:
                self.sendCommand(cmd)
        finally:
            self.enableDrawing()
            self.forceUpdate()

    def disableDrawing(self):
        cmd = SetOptionCommand.createInstance("drawingEnabled", "False")
        self.sendCommand(cmd)

    def enableDrawing(self):
        cmd = SetOptionCommand.createInstance("drawingEnabled", "True")
        self.sendCommand(cmd)

    def forceUpdate(self):
        cmd = ForceUpdateCommand.createInstance()
        self.sendCommand(cmd)

    def stop(self):
        # Send empty command to unblock the event loop.
        self.cpt.signalStop()
        self.commandQueue.put(EmptyCommand().name())

        self.gt.signalStop()
        self.processingQueue.put(EmptyCommand().name())

class CommandParserThread(threading.Thread):
    """
    Thread used for parsing commands.
    """
    def __init__(self, srcQueue, dstQueue, context):
        threading.Thread.__init__(self)
        self.srcQueue = srcQueue
        self.dstQueue = dstQueue
        self.runFlag  = True

        self.drawingEnabled      = True

        self.updateFnct          = None
        self.commandResponseFnct = None
        self.commandErrorFnct    = None
        self.quitFnct            = None

        self.context             = context

        self.COMMANDS = {
            # class diagram commands:
            CreateCommand.name(): CreateCommand(self.context), 
            # Generic commands:
            HelpCommand.name(): HelpCommand(),
            QuitCommand.name(): QuitCommand(self), 
            UndoCommand.name(): UndoCommand(), 
            RedoCommand.name(): RedoCommand(), 
            HistoryCommand.name(): HistoryCommand(),
            SetOptionCommand.name(): SetOptionCommand(self),
            ForceUpdateCommand.name(): ForceUpdateCommand(self),
            # Special command for unblocking event loop.
            EmptyCommand.name(): EmptyCommand()
        }

    def signalStop(self):
        self.runFlag = False
        print("runFlag = %d" % self.runFlag)

    def registerHandlers(self, handlers):
        self.updateFnct          = handlers[CommandParser.OnUpdate]
        self.commandResponseFnct = handlers[CommandParser.OnCommandResponse]
        self.commandErrorFnct    = handlers[CommandParser.OnCommandError]
        self.quitFnct            = handlers[CommandParser.OnExit]

    def parseCommand(self, cmd):
        print("Thread parsing command: %s" % cmd)

        whitespaceSeparatedList = cmd.split()

        command = EmptyCommand()

        if len(whitespaceSeparatedList) == 0:
            self.commandErrorFnct("Command not understod")
        try:
            command = self.COMMANDS[whitespaceSeparatedList[0]]
        except KeyError:
            self.commandErrorFnct("Command not understod")
            return

        hasArguments = False
        if len(whitespaceSeparatedList) > 1:
            del whitespaceSeparatedList[0]
            hasArguments = True

        if command.expectsArguments() == True and hasArguments == False:
            self.commandErrorFnct("No arguments provided")
            return

        if command.expectsArguments():
            try:
                command.parseArguments(whitespaceSeparatedList)
            except Exception as e:
                print "parseArguments failed: %s." % str(e)

        try:
            ret = command.execute()
            self.commandResponseFnct(ret)
        except Exception as e:
            print "Command execute failed: %s." % str(e)

        if self.drawingEnabled:
            if command.redrawRequired():
                print ("Redrawing.")
                self.dstQueue.put(GeneratorThread.UPDATECMD)
            else:
                print ("NOT Redrawing.")
        else:
            print ("Drawing is disabled..")

    def forceUpdate(self):
        print ("Forced to redraw.")
        self.dstQueue.put(GeneratorThread.UPDATECMD)

    def setOption(self, name, value):
        print ("Setting option %s to %s." % (name, value))
        if (value == "True"):
            vars(self)[name] = True
        elif (value == "False"):
            vars(self)[name] = False
        else:
            vars(self)[name] = value

    def run(self):
        while self.runFlag:
            try:
                cmd = self.srcQueue.get(block=True, timeout=1)
                self.parseCommand(cmd)
                self.srcQueue.task_done()
            except Queue.Empty:
                # This is expected, used for blocking until an event is received.
                #print("Queue.Empty")
                pass
        print("Exit from run().")

class GeneratorThread(threading.Thread):
    """
    Thread used for generating UML diagrams.
    """
    UPDATECMD = "UPDATECMD"

    def __init__(self, srcQueue, context):
        threading.Thread.__init__(self)
        self.srcQueue = srcQueue
        self.runFlag  = True
        self.context  = context
        self.generator = PlantUmlGenerator()
        self.plantUML  = puml.PlantUML(jarFile="./uml/plantuml.jar")
        self.updateImageFnct = None

    def registerHandlers(self, handlers):
        self.updateImageFnct = handlers[CommandParser.OnUpdateImage]

    def signalStop(self):
        self.runFlag = False
#       print("runFlag = %d" % self.runFlag)

    def generate(self):
        self.context.generate(self.generator)
        t = self.generator.getText()
        ret = self.plantUML.convert(t)
        if ret == 0:
            o = self.plantUML.getOutput()
            self.updateImageFnct(o)
        else:
            print("plantUML.convert returned error, code %d." % ret)

    def run(self):
        while self.runFlag:
            try:
                updateCmd = self.srcQueue.get(block=True, timeout=1)
                if updateCmd == GeneratorThread.UPDATECMD:
                    self.generate()
                else:
                    pass
                self.srcQueue.task_done()
            except Queue.Empty:
                # This is expected, used for blocking until an event is received.
                pass
#        print("Exit from run().")
