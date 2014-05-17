#!/usr/bin/python

import wx
from wx.lib.buttons import GenBitmapTextButton
import StringIO

from command import CommandParser

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title, commandParser):
        wx.Frame.__init__(self, parent, id, title, size=(500, 550))

        wx.InitAllImageHandlers()
        #wx.Image.AddHandler(wx.PNGHandler()) 

        self.closeInProgress = False
        self.commandParser   = commandParser

        handlers = {
            CommandParser.OnUpdate: self.bitmapUpdated,
            CommandParser.OnCommandResponse: self.commandResponse,
            CommandParser.OnCommandError: self.commandError,
            CommandParser.OnExit: self.onQuit,
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
        dc.SetBackground(wx.Brush("white")) # or some other color
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

        self.textOutput = wx.TextCtrl(parent=self.panel, style=wx.TE_PROCESS_ENTER)
        hbox3.Add(self.textOutput, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.panel.SetSizer(vbox)

        # React to key presses and when enter is pressed.
        #self.textInput.Bind(wx.EVT_TEXT, self.onKeyPress)
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

    def commandResponse(self, responseStr):
        #print("response: %s" % response)
        self.textOutput.SetValue(responseStr)

    def commandError(self, errorStr):
        #print("response: %s" % response)
        self.textOutput.SetValue("ERROR: " + errorStr)

    # Command parser calls this method in order to signal that the UI should close.
    def onQuit(self):
        if not self.closeInProgress:
            self.closeInProgress = True
            self.Destroy()

    def updateImageImpl(self, buffer):
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

    def updateImage(self, buffer):
        #print ("Updating image..")
        wx.CallAfter(self.updateImageImpl, buffer)

    # This method gets called when the UI received a signal to close itself.
    def onCloseFromUI(self, event):
        if not self.closeInProgress:
            # ask the command parser to stop:
            print("UI: exit triggered")
            self.commandParser.stop()
            self.Destroy()

#app = wx.App(0)
#MainWindow(None, -1, 'RapidBreeze', None)
#app.MainLoop()
