#!/usr/bin/python

import sys
import getopt
import wx
from command import CommandParser
from ui.ui import MainWindow
import core
import uml
from core.model import Database

# from misc import parseParameters
from misc import *

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

paramDescriptor = parseParameters(sys.argv[0], sys.argv[1:])

print ("File set %d: %s" % (paramDescriptor[PARAM_INPUTFILESET], paramDescriptor[PARAM_INPUTFILENAME]))

#loadCommandsFromFile = False

# Command line arguments:

db = Database()

commandsToExecute = []
if paramDescriptor[PARAM_INPUTFILESET]:
    print ("Loading input file %s." % paramDescriptor[PARAM_INPUTFILENAME])
    commandsToExecute = loadCommandsFromFile(paramDescriptor[PARAM_INPUTFILENAME])

cp = CommandParser(db, commandsToExecute)

app = wx.App(0)
MainWindow(None, -1, 'RapidBreeze', cp)
app.MainLoop()

# Finished

cp.stop()
