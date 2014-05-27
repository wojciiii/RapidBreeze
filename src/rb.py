#!/usr/bin/python

import sys
import getopt
import wx
from command import CommandParser
from ui.ui import MainWindow
import core
import uml
from core.model import Database
from misc import *

# Command line arguments:
paramDescriptor = parseParameters(sys.argv[0], sys.argv[1:])
db = Database()
commandsToExecute = []
if paramDescriptor[PARAM_INPUTFILESET]:
    print ("Loading input file %s." % paramDescriptor[PARAM_INPUTFILENAME])
    commandsToExecute = loadCommandsFromFile(paramDescriptor[PARAM_INPUTFILENAME])

cp = CommandParser(db, commandsToExecute)
app = wx.App(0)
MainWindow(None, -1, 'RapidBreeze', cp)
app.MainLoop()
cp.stop()
