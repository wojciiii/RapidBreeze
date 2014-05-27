#!/usr/bin/python

import wx
from wx.lib.buttons import GenBitmapTextButton
import StringIO
from functools import wraps

from command import CommandParser

def CallAfterDecorator(func):
    def wrapper(*args, **kwargs):
        wx.CallAfter(func, *args, **kwargs)
    return wrapper

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title, commandParser):
        wx.Frame.__init__(self, parent, id, title, size=(800, 600))

        wx.InitAllImageHandlers()

        self.responseNum     = 0
        self.closeInProgress = False
        self.commandParser   = commandParser

        # Notice that wx.CallAfter is used to call these functions, as
        # they can be called from another thread than the main UI
        # thread.
        handlers = {
            CommandParser.OnUpdate: self.bitmapUpdated,
            CommandParser.OnCommandResponse: self.commandResponse,
            CommandParser.OnCommandError: self.commandError,
            CommandParser.OnExit: self.onExit,
            CommandParser.OnUpdateImage: self.updateImage
        }
        self.commandParser.registerHandlers(handlers)

        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour('WHITE')

        #
        # Menubar:
        #
        menubar = wx.MenuBar()
        file = wx.Menu()
        file.Append(1, '&Quit', '')
        edit = wx.Menu()
        view = wx.Menu()
        go = wx.Menu()
        bookmarks = wx.Menu()
        tools = wx.Menu()
        help = wx.Menu()

        menubar.Append(file, '&File')
        menubar.Append(edit, '&Edit')
        menubar.Append(view, '&View')
        menubar.Append(go, '&Go')
        menubar.Append(bookmarks, '&Bookmarks')
        menubar.Append(tools, '&Tools')
        menubar.Append(help, '&Help')

        self.SetMenuBar(menubar)

        #
        # Layout:
        #

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)

        # First:
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        
        self.MaxImageSize = 400

        bmp = wx.EmptyBitmap(self.MaxImageSize, self.MaxImageSize)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush("white"))
        dc.Clear()
        del dc

        self.imageCtrl = wx.StaticBitmap(self.panel, bitmap=bmp)

        hbox1.Add((1,1),1) 
        hbox1.Add(self.imageCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10) 
        hbox1.Add((1,1),1) 

        # Second:

        # Command input:
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self.panel, label='Command')
        st1.SetFont(font)
        hbox2.Add(st1, flag=wx.RIGHT, border=8)

        self.textInput = wx.TextCtrl(parent=self.panel, style=wx.TE_PROCESS_ENTER)
        hbox2.Add(self.textInput, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.textInput.SetValue("create class Shape")

        # Response output:
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self.panel, label='Response')
        st2.SetFont(font)
        hbox3.Add(st2, flag=wx.RIGHT, border=8)

        self.textOutput = wx.TextCtrl(self.panel, -1, "",size=(200, 75), style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY)

        hbox3.Add(self.textOutput, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        #self.textOutput.AppendText("Test0\n")
        #self.textOutput.AppendText("Test1\n")

        for i in range(10):
            self.commandResponse("Test0")
            self.commandError("Test1")

        self.panel.SetSizer(vbox)

        # React to key presses and when enter is pressed.
        self.textInput.Bind(wx.EVT_TEXT_ENTER, self.onEnterPressed)

        self.CreateStatusBar()
        self.Centre()
        self.Show(True)

        self.Bind(wx.EVT_CLOSE, self.onCloseFromUI)

        # Execute saved commands, if any.
        self.commandParser.executeSavedCommands()

    def onEnterPressed(self, ev):
        print ("Enter pressed.")
        text = self.textInput.GetValue()
        self.textInput.SetValue("")

        # Send command to the component parsing them.
        self.commandParser.sendCommand(text)

    def bitmapUpdated(self, bitmap):
        print("bitmapUpdated!")

    @CallAfterDecorator
    def commandResponse(self, responseStr):
        self.textOutput.SetInsertionPoint(0)
        self.textOutput.AppendText("(%d) %s\n" % (self.responseNum, responseStr))
        self.textOutput.ScrollPages(1)
        self.responseNum += 1

    @CallAfterDecorator
    def commandError(self, errorStr):
        self.textOutput.SetInsertionPoint(0)
        self.textOutput.AppendText("(%d) error: %s\n" % (self.responseNum, errorStr))
        self.textOutput.ScrollLines(0)
        self.responseNum += 1

    # Command parser calls this method in order to signal that the UI should close.
    @CallAfterDecorator
    def onExit(self):
        if not self.closeInProgress:
            self.closeInProgress = True
            self.Destroy()

    @CallAfterDecorator
    def updateImage(self, buffer):
        sbuf = StringIO.StringIO(buffer)

        img = wx.ImageFromStream(sbuf)

        H = img.GetWidth()
        W = img.GetHeight()

        if W > H:
            NewW = self.MaxImageSize
            NewH = self.MaxImageSize * H / W
        else:
            NewH = self.MaxImageSize
            NewW = self.MaxImageSize * W / H

        #img = img.Scale(NewW, NewH)
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))

        self.Refresh()
        print ("Image updated %d bytes.." % len(buffer))

    # This method gets called when the UI received a signal to close itself.
    def onCloseFromUI(self, event):
        if not self.closeInProgress:
            # ask the command parser to stop:
            print("UI: exit triggered")
            self.commandParser.stop()
            self.Destroy()

