#!/usr/bin/env python
import sys, os, pprint, traceback
import wx, wx.stc, keyword
import cPickle

# STC
#http://www.yellowbrain.com/stc/index.html
#http://wxpython.org/docs/api/wx.stc.StyledTextCtrl-class.html
#http://www.yellowbrain.com/stc/margins.html
#http://wxruby.rubyforge.org/doc/styledtextctrl.html

class MyFrame(wx.Frame):
    def __init__(self, parent, title):

        self.epnameold = ''
        self.newname = ''
        self.eprepeat = 2
        self.browsefile = ''

        wx.Frame.__init__(self, parent, title=title)
        if os.path.splitext(sys.argv[0])[1] == ".exe":
            icon = wx.Icon(sys.argv[0], wx.BITMAP_TYPE_ICO)
        else:
            icon = wx.Icon(os.path.splitext(sys.argv[0])[0] + ".ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.SetMinSize((900,500))
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([30,-1,-2])

        self.inputLabel = wx.StaticText(self.panel, wx.ID_ANY, 'File:')
        self.inputText = wx.TextCtrl(self.panel, wx.ID_ANY)
        self.inputText.SetEditable(False)
        self.inputButton = wx.Button(self.panel, wx.ID_ANY, 'Browse...')

        self.seriesLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Series:')
        self.seriesText = wx.TextCtrl(self.panel, wx.ID_ANY)
        self.seriesText.SetValue("None")
        #self.seriesText.Enable(False)
        #self.paramCheck = wx.CheckBox(self.panel, wx.ID_ANY, 'Test')
        #self.paramCheck.SetValue(True)
        self.paramSeasonLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Season:')
        self.paramSeason = wx.SpinCtrl(self.panel, wx.ID_ANY, size=(50,-1) )
        self.paramSeason.SetRange(0, 999)
        self.paramSeason.SetValue(1)
        self.paramEpisodeLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Episode:')
        self.paramEpisode = wx.SpinCtrl(self.panel, wx.ID_ANY, size=(50,-1) )
        self.paramEpisode.SetRange(0, 999)
        self.paramEpisode.SetValue(1)
        self.paramStripLabel = wx.StaticText(self.panel, wx.ID_ANY, 'LStrip:')
        self.paramStrip = wx.SpinCtrl(self.panel, wx.ID_ANY, size=(50,-1) )
        self.paramStrip.SetRange(0, 999)
        self.paramStrip.SetValue(0)
        self.paramSortLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Sort:')
        self.paramSort = wx.SpinCtrl(self.panel, wx.ID_ANY, size=(50,-1) )
        self.paramSort.SetRange(0, 999)
        self.paramSort.SetValue(0)
        self.refreshButton = wx.Button(self.panel, wx.ID_ANY, 'Refresh')

        self.leftBox = wx.StaticBox(self.panel, wx.ID_ANY, 'Selection')
        self.upButton = wx.Button(self.panel, wx.ID_ANY, 'Up')
        self.downButton = wx.Button(self.panel, wx.ID_ANY, 'Down')
        self.allButton = wx.Button(self.panel, wx.ID_ANY, 'All')
        self.noneButton = wx.Button(self.panel, wx.ID_ANY, 'None')
        self.rightBox = wx.StaticBox(self.panel, wx.ID_ANY, 'Controls')
        self.goButton = wx.Button(self.panel, wx.ID_ANY, 'Go!')
        self.goButton.Enable(False)
        self.exitButton = wx.Button(self.panel, wx.ID_EXIT, 'Exit')
        self.advancedButton = wx.Button(self.panel, wx.ID_ANY, 'Advanced')
        
        self.outputText = wx.stc.StyledTextCtrl(self.panel, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_PROCESS_TAB ) # wx.TE_NO_VSCROLL
        self.outputText.SetReadOnly(True)
        #self.outputText.SetEditable(False)
        self.outputText.SetMargins(1,1)
        self.outputText.SetMarginWidth(0,16)
        self.outputText.SetMarginWidth(1,16)
        self.outputText.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
        self.outputText.SetMarginSensitive(1, True) 
        self.outputText.SetMarginWidth(2,0)
        self.outputText.SetMarginMask(0,0)
        self.outputText.MarkerDefine(0, wx.stc.STC_MARK_MINUS, "blue", "black")
        self.outputText.MarkerDefine(1, wx.stc.STC_MARK_SHORTARROW, "blue", "blue")
        self.outputText.MarkerDefine(2, wx.stc.STC_MARK_ARROW, "#00FF00", "#00FF00")
        self.outputText.MarkerDefine(3, wx.stc.STC_MARK_CIRCLE, "#CCFF00", "RED")
        #self.outputText.MarkerDefine(3, wx.stc.STC_MARK_ARROWS, "#00FF00", "#00FF00")


        self.inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.paramSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonLeftSizer = wx.StaticBoxSizer(self.leftBox, wx.HORIZONTAL)
        self.buttonRightSizer = wx.StaticBoxSizer(self.rightBox,  wx.HORIZONTAL)
        self.buttonSizer.Add(self.buttonLeftSizer, 0, wx.ALL | wx.LEFT, 5)
        self.buttonSizer.Add(self.buttonRightSizer, 1, wx.ALL | wx.EXPAND | wx.RIGHT, 5)
        self.textSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)

        self.inputSizer.Add(self.inputLabel, 0, wx.ALL, 5)
        self.inputSizer.Add(self.inputText, 1, wx.ALL | wx.EXPAND, 5)
        self.inputSizer.Add(self.inputButton, 0, wx.ALL, 5)

        self.paramSizer.Add(self.seriesLabel, 0, wx.ALL, 5)
        self.paramSizer.Add(self.seriesText, 1, wx.ALL | wx.EXPAND, 5)
        self.paramSizer.Add(self.paramSeasonLabel, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramSeason, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramEpisodeLabel, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramEpisode, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramStripLabel, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramStrip, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramSortLabel, 0, wx.ALL, 5)
        self.paramSizer.Add(self.paramSort, 0, wx.ALL, 5)
        #self.paramSizer.Add(self.paramCheck, 0, wx.ALL, 5)
        self.paramSizer.Add(self.refreshButton, 0, wx.ALL, 5)
        
        self.buttonLeftSizer.Add(self.upButton, 0, wx.ALL, 5)
        self.buttonLeftSizer.Add(self.downButton, 0, wx.ALL, 5)
        self.buttonLeftSizer.Add(self.allButton, 0, wx.ALL, 5)
        self.buttonLeftSizer.Add(self.noneButton, 0, wx.ALL, 5)
        self.buttonRightSizer.Add(self.goButton, 1, wx.ALL, 5)
        self.buttonRightSizer.Add(self.advancedButton, 0, wx.ALL, 5)
        self.buttonRightSizer.Add(self.exitButton, 0, wx.ALL, 5)
        
        self.textSizer.Add(self.outputText, 1, wx.EXPAND|wx.LEFT|wx.RIGHT,5)
        
        self.rootSizer.Add(self.inputSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.rootSizer.Add(self.paramSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.rootSizer.Add(self.buttonSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.rootSizer.Add(self.textSizer, 1, wx.EXPAND|wx.TOP|wx.BOTTOM,5)

        self.Bind(wx.EVT_BUTTON, self.onInBrowse, self.inputButton)
        self.Bind(wx.EVT_TEXT, self.onSpin, self.seriesText)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.paramSeason)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.paramEpisode)
        self.Bind(wx.EVT_SPINCTRL, self.onSpin, self.paramStrip)
        self.Bind(wx.EVT_BUTTON, self.onRefresh, self.refreshButton)
        
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        
        self.Bind(wx.EVT_BUTTON, self.onAll, self.allButton)
        self.Bind(wx.EVT_BUTTON, self.onNone, self.noneButton)
        self.Bind(wx.EVT_BUTTON, self.onGo, self.goButton)
        self.Bind(wx.EVT_BUTTON, self.onAdv, self.advancedButton)
        self.Bind(wx.EVT_BUTTON, self.onExit, self.exitButton)


        self.panel.SetSizer(self.rootSizer)
        self.rootSizer.Fit(self)
        
        try:
            self.dirname = cPickle.load(open(os.path.splitext(sys.argv[0])[0] + ".pkd", 'rb')) 
        except IOError:
            self.dirname = sys.path[0]
        
        try:
            advLoad = cPickle.load(open(os.path.splitext(sys.argv[0])[0] + ".pkl", 'rb'))
            self.advRules = compile(advLoad, '<string>', 'exec')
        except SyntaxError:
            self.onError("Syntax Error!\n")
            self.onAdv(self)
        except IOError:
            self.onError("Missing Rules, Save the Defauls.")
            self.onAdv(self)

        self.Show()
        
    def OnMarginClick(self, e):
        # fold and unfold as needed
        if e.GetMargin() == 1:
            lineClicked = self.outputText.LineFromPosition(e.GetPosition())
            lineMarker = self.outputText.MarkerGet(lineClicked)
            print "line: %d marker: %d" % (lineClicked, lineMarker)
            if lineMarker == 1:
                self.outputText.MarkerDelete(lineClicked, -1)
                self.outputText.MarkerAdd(lineClicked,1)
            elif lineMarker == 2:
                self.outputText.MarkerDelete(lineClicked, -1)
                self.outputText.MarkerAdd(lineClicked,0)

    def onAll(self, e):
        for line in range(self.outputText.GetLineCount()):
            if self.outputText.MarkerGet(line) == 1:
                self.outputText.MarkerDelete(line, 0)
                self.outputText.MarkerAdd(line,1)
    
    def onNone(self, e):
        for line in range(self.outputText.GetLineCount()):
            if self.outputText.MarkerGet(line) == 2:
                self.outputText.MarkerDelete(line, 1)
                self.outputText.MarkerAdd(line,0)

    def onExit(self, e):
        self.Close(True)

    def onError(self, message):
        dlg = wx.MessageDialog(self, message="Line: " + str(sys.exc_info()[2].tb_lineno) + " - " + message + "\n\n" + traceback.format_exc(0), caption='Error', style=wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
        result = dlg.ShowModal()
        dlg.Destroy()
        return(result)

    def onRemove(self, message):
        dlg = wx.MessageDialog(self, message=message, caption='Remove File', style=wx.YES_NO|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        return(result)

    def onInBrowse(self, e):
        fileDialog = wx.FileDialog (self, "Input File", self.dirname, "", "Video files (*.mkv;*.avi;*.mpg;*.divx)|*.mkv;*.avi;*.mpg;*.divx|All files (*.*)|*.*", wx.CHANGE_DIR )
        if fileDialog.ShowModal() == wx.ID_OK:
            self.browsefile = fileDialog.GetFilename()
            self.dirname = fileDialog.GetDirectory()
            self.inputText.SetValue(os.path.join(self.dirname, self.browsefile))
        fileDialog.Destroy()
        try:
            cPickle.dump(self.dirname, open(os.path.splitext(sys.argv[0])[0] + ".pkd", 'wb')) 
        except IOError:
            pass
        self.onSpin(self)
        self.goButton.Enable(True)
        self.processFiles(False)
        self.seriesText.SetFocus()
        self.seriesText.SetSelection(0,self.seriesText.GetLastPosition())

    def epiName(self, series, season, episode, file):
        try:
            eval(self.advRules)
        except:
            self.onError("Syntax Error!\n" + file)
            self.onAdv(None)
            return
        self.statusBar.SetStatusText(str(episode))
        self.statusBar.SetStatusText(file, 1)
        self.statusBar.SetStatusText(self.newname, 2)
        return(self.newname)
    
    def onAdv(self, e):
        adv = AdvancedRules(None, wx.ID_ANY, 'Advanced Rules')
        adv.ShowModal()
        adv.Destroy()
        try:
            advLoad = cPickle.load(open(os.path.splitext(sys.argv[0])[0] + ".pkl", 'rb'))
            self.advRules = compile(advLoad, '<string>', 'exec')
            if len(self.browsefile):
                self.eprepeat = 2
                self.epnameold = ''
                self.statusBar.SetStatusText(self.epiName(self.seriesText.GetValue(), self.paramSeason.GetValue(), self.paramEpisode.GetValue(), self.browsefile), 2)
                self.processFiles(False)
        except SyntaxError:
            self.onError("Syntax Error!")
            self.onAdv(self)

    def onGo(self, e):
        self.processFiles(True)
        
    def onRefresh(self, e):
        if len(self.inputText.GetValue()):
            self.processFiles(False)

    def processFiles(self, update):
        if not update:
            self.outputText.SetReadOnly(False)
            self.outputText.ClearAll()
            self.outputText.SetReadOnly(True)
            
        filelist = [f for f in os.listdir(".")
                    if os.path.isfile(os.path.join(".", f))]

        # may need to check the float is working correctly, seems to give invalid literal error on strings
        filelist.sort(key=lambda item: (int(item.split(' ')[self.paramSort.GetValue()])
                               if item[self.paramSort.GetValue()].isdigit() else float('inf'), item))
        initEpisode = self.paramEpisode.GetValue()
        for file in filelist:
            fileext = os.path.splitext(file)[1].lower()
            if fileext == ".txt" or fileext == '.jpg':
                if self.onRemove("Remove extra file: " + file) == wx.ID_YES:
                    os.remove(file)
                continue
            filerename = self.epiName(self.seriesText.GetValue(), self.paramSeason.GetValue(), self.paramEpisode.GetValue(), file)
            self.outputText.SetReadOnly(False)
            self.outputText.AppendText(file + "\t\t->\t\t" + filerename + '\n')
            self.outputText.SetReadOnly(True)
            (basedir, topdir) = os.path.split(self.dirname)
            seasondir = os.path.join(basedir,self.seriesText.GetValue() + " - Season " + str(self.paramSeason.GetValue()))
            if update == True and len(filerename):
                if not os.access(seasondir, os.F_OK):
                    os.mkdir(seasondir)
                if os.access(filerename, os.F_OK):
                    self.onError("File " + filerename + "\n\nAlready Exists!")
                else:
                    #print "rename: %s -> %s" % (file, filerename)
                    os.rename(os.path.join(self.dirname,file), os.path.join(seasondir, filerename))
                    self.outputText.MarkerAdd(self.outputText.GetLineCount()-2,2)
            else:
                self.outputText.MarkerAdd(self.outputText.GetLineCount()-2,1)
                if update == True:
                    if self.onError("Series: " + self.seriesText.GetValue() + "\nFile: " + filerename + "\n\nTest Rename.") == wx.ID_CANCEL:
                        self.paramEpisode.SetValue(initEpisode)
                        return
            self.paramEpisode.SetValue(self.paramEpisode.GetValue()+1)
            
        if update == True:
            os.chdir(basedir)
            try:
                os.rmdir(self.dirname)
            except:
                pass
            self.dirname=basedir
            try:
                cPickle.dump(self.dirname, open(os.path.splitext(sys.argv[0])[0] + ".pkd", 'wb')) 
            except IOError:
                pass
            self.goButton.Enable(False)
        else:
            self.paramEpisode.SetValue(initEpisode)
            
        # Add line numbers using STC
        lines = self.outputText.GetLineCount() #get # of lines, ensure text is loaded first!
        width = self.outputText.TextWidth(wx.stc.STC_STYLE_LINENUMBER,str(lines) + "  ")
        self.outputText.SetMarginWidth(0,width)

    def onSpin(self, e):
        if e.GetId() == self.paramSeason.GetId():
            self.paramEpisode.SetValue(1)
        if len(self.browsefile):
            self.statusBar.SetStatusText(self.epiName(self.seriesText.GetValue(), self.paramSeason.GetValue(), self.paramEpisode.GetValue(), self.browsefile), 2)
        self.eprepeat = 2
        self.epnameold = ''
      
class AdvancedRules(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(800,400))
        
        advVars = 'file, self.paramStrip, self.newname, self.eprepeat, self.epnameold, series, season, episode'
        
        self.panel = wx.Panel(self, wx.ID_ANY, size=(800,400))
        self.labelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.varLabel = wx.StaticText(self.panel, wx.ID_ANY, "Var's: " + advVars)
        self.advText = wx.stc.StyledTextCtrl(self.panel, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_PROCESS_TAB )
        self.advText.SetTabWidth(4)
        self.advText.SetUseTabs(0)
        self.advText.SetTabIndents(1)
        self.advText.SetIndentationGuides(1)
        self.advText.SetEOLMode(wx.stc.STC_EOL_LF)
        self.buttonSave = wx.Button(self.panel, wx.ID_ANY, 'Save')
        self.buttonCancel = wx.Button(self.panel, wx.ID_ANY, 'Cancel')
        self.buttonDefaults = wx.Button(self.panel, wx.ID_ANY, 'Defaults')

        self.labelSizer.Add(self.varLabel, 0)
        self.inputSizer.Add(self.advText, 1, wx.EXPAND|wx.LEFT|wx.RIGHT,5)
        self.buttonSizer.Add(self.buttonSave, 0, wx.ALIGN_CENTER)
        self.buttonSizer.Add(self.buttonCancel, 0, wx.ALIGN_CENTER)
        self.buttonSizer.Add(self.buttonDefaults, 0, wx.ALIGN_CENTER)  
        self.rootSizer.Add(self.labelSizer, 0, wx.LEFT, 5)
        self.rootSizer.Add(self.inputSizer, 1, wx.EXPAND|wx.BOTTOM|wx.TOP, 5)
        self.rootSizer.Add(self.buttonSizer, 0, wx.ALL | wx.CENTER, 5)
        
        self.Bind(wx.EVT_BUTTON, self.onSave, self.buttonSave)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.buttonCancel)
        self.Bind(wx.EVT_BUTTON, self.onDefaults, self.buttonDefaults)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.rootSizer)
        self.Centre()
        self.advText.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.advText.SetKeyWords(0, " ".join(keyword.kwlist))


        if not os.access(os.path.splitext(sys.argv[0])[0] + ".pkl", os.F_OK):
            cPickle.dump(self.onDefaults(self), open(os.path.splitext(sys.argv[0])[0] + ".pkl", 'wb'))
        self.advText.SetText(cPickle.load(open(os.path.splitext(sys.argv[0])[0] + ".pkl", 'rb')))

        # Add line numbers using STC
        self.advText.SetMargins(0,0)
        lines = self.advText.GetLineCount() #get # of lines, ensure text is loaded first!
        width = self.advText.TextWidth(wx.stc.STC_STYLE_LINENUMBER,str(lines) + "  ")
        self.advText.SetMarginWidth(0,width)
        self.advText.SetMarginWidth(1,0)
        self.advText.SetMarginWidth(2,0)

    def onError(self, message):
        dlg = wx.MessageDialog(self, message="Line: " + str(sys.exc_info()[2].tb_lineno) + "\n" + message + "\n\n" + traceback.format_exc(0), caption='Error', style=wx.OK|wx.ICON_EXCLAMATION)
        result = dlg.ShowModal()
        dlg.Destroy()
        return(result)

    def onSave(self, e):
        # We need a \n at the end so the compile works
        if self.advText.GetText()[len(self.advText.GetText())-1] != "\n":
            self.advText.AppendText('\n')
        try:
            test = compile(self.advText.GetText(), '<string>', 'exec')            
            if os.access(os.path.splitext(sys.argv[0])[0] + ".pkl", os.W_OK):
                cPickle.dump(self.advText.GetText(), open(os.path.splitext(sys.argv[0])[0] + ".pkl", 'wb'))
                self.Close(True)
            else:
                self.onError("Error Writing Config!")
        except SyntaxError:
            pprint.pprint(self.advText.GetText())
            self.onError("Syntax Error!")
        
        
    def onCancel(self, e):
        self.Close(True)
    
    def onDefaults(self, e):
         # If there are no default rules, create them
        advRules="""file = os.path.splitext(file.replace("_", " "))
filebase = file[0].replace(".", " ")
fileext = file[1]
filename = filebase.split()

try:
    if len(filename) > 1:
        if self.paramStrip.GetValue():
            for strip in range(self.paramStrip.GetValue()):
                filename.pop(0)
        else:
            while "-" in filename:
                filename.pop(0)

        if len(filename) and filename[0] == "-":
            filename.pop(0)
        elif len(filename) and filename[0].startswith("-"):
            filename[0] = filename[0].lstrip("-")

    epname = " ".join(filename).strip()
    if epname != '' and epname == self.epnameold:
        self.epnameold=epname
        epname=epname + " (" + str(self.eprepeat) + ")"
        self.eprepeat+=1
    else:
        self.epnameold=epname
        self.eprepeat=2

    if len(epname):
        epname = " - " + epname

    self.newname = "%s S%02dE%02d%s%s" % (series, season, episode, epname, fileext )

except:
    file = "".join(file)
    self.onError("Syntax Error!\\n" + file)
    self.newname = file
    self.onAdv(self)
"""
        self.advText.SetText(advRules)
        return(advRules)


if __name__ == '__main__':
    try:
        application = wx.PySimpleApp()
        frame = MyFrame(None, "EpiRen")
        application.MainLoop()
    finally:
        del application
