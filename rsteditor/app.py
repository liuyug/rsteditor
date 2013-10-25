#!/usr/bin/env python
# -*- coding: utf-8 -*-

# for python library
import os.path
import shutil

# for wxPython library
import wx
import wx.aui
import wx.stc
# for MacOS
#import wx.webkit
# for my python module
from rsteditor import htmlviewer
from rsteditor import utils
from rsteditor import editor
from rsteditor import explorer
from rsteditor.output import rst2html
from rsteditor import APPNAME
from rsteditor import VERSION
from rsteditor import AUTHORS
from rsteditor import DATA_PATH
from rsteditor import HOME_PATH
from rsteditor import CONFIG_PATH
from rsteditor import TEMPLATE_PATH
from rsteditor import CONFIG_FILE
from rsteditor import FILENAME
from rsteditor import ALLOWED_LOADS
from rsteditor import config
from rsteditor import _



ID_RSTEDITOR_BASE = wx.ID_HIGHEST + 1
ID_HTML_VIEWER = ID_RSTEDITOR_BASE + 1
ID_CODE_VIEWER = ID_RSTEDITOR_BASE + 2
ID_FILE_EXPLORER = ID_RSTEDITOR_BASE + 3
ID_FIND_PREV = ID_RSTEDITOR_BASE + 4
ID_FIND_NEXT = ID_RSTEDITOR_BASE + 5
ID_PREVIEW = ID_RSTEDITOR_BASE + 6
ID_PREVIEW_ONSAVE = ID_RSTEDITOR_BASE + 7
ID_PREVIEW_ONINPUT = ID_RSTEDITOR_BASE + 8
ID_PREVIEW_SCROLLSYNC = ID_RSTEDITOR_BASE + 9

class RSTEditorFrame(wx.Frame):
    """ RSTEditor Main Frame """
    def __init__(self, parent):
        super(RSTEditorFrame, self).__init__(parent, title=APPNAME, size=(800, 600))
        self.m_mgr = wx.aui.AuiManager(self)
        # menu
        menuBar = wx.MenuBar()
        filemenu = wx.Menu()
        filemenu.Append(wx.ID_NEW, _('&New\tCtrl+N'))
        filemenu.Append(wx.ID_OPEN, _('&Open\tCtrl+O'))
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_SAVE, _('&Save\tCtrl+S'))
        filemenu.Append(wx.ID_SAVEAS, _('Save as ...'))
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, _('E&xit'))
        self.Bind(wx.EVT_MENU, self.OnNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        menuBar.Append(filemenu, _('&File'))
        editmenu = wx.Menu()
        editmenu.Append(wx.ID_UNDO, _('&Undo\tCtrl+Z'))
        editmenu.Append(wx.ID_REDO, _('&Redo\tShift+Ctrl+Z'))
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_CUT, _('Cu&t\tCtrl+X'))
        editmenu.Append(wx.ID_COPY, _('&Copy\tCtrl+C'))
        editmenu.Append(wx.ID_PASTE, _('&Paste\tCtrl+V'))
        editmenu.Append(wx.ID_DELETE, _('&Delete\tDel'))
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_SELECTALL, _('Select &All\tCtrl+A'))
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_FIND, _('Find...\tCtrl+F'))
        editmenu.Append(ID_FIND_NEXT, _('Find &next\tF3'))
        editmenu.Append(ID_FIND_PREV, _('Find previous\tShift+F3'))
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnEdit, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.OnFind, id=ID_FIND_PREV)
        self.Bind(wx.EVT_MENU, self.OnFind, id=ID_FIND_NEXT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_PASTE)
        menuBar.Append(editmenu, _('&Edit'))
        viewmenu = wx.Menu()
        viewmenu.AppendCheckItem(ID_FILE_EXPLORER, _('File Explorer'))
        viewmenu.AppendCheckItem(ID_HTML_VIEWER, _('reStructuredText Preview'))
        viewmenu.AppendCheckItem(ID_CODE_VIEWER, _('Code Viewer'))
        self.Bind(wx.EVT_MENU, self.OnShowAuiPanel, id=ID_HTML_VIEWER)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_HTML_VIEWER)
        self.Bind(wx.EVT_MENU, self.OnShowAuiPanel, id=ID_CODE_VIEWER)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_CODE_VIEWER)
        self.Bind(wx.EVT_MENU, self.OnShowAuiPanel, id=ID_FILE_EXPLORER)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_FILE_EXPLORER)
        menuBar.Append(viewmenu, _('&View'))
        preview_menu = wx.Menu()
        preview_menu.Append(ID_PREVIEW, _('&Preview\tCtrl+P'))
        preview_menu.AppendCheckItem(ID_PREVIEW_ONSAVE, _('Preview on &save'))
        preview_menu.AppendCheckItem(ID_PREVIEW_ONINPUT, _('Preview on &input'))
        preview_menu.AppendCheckItem(ID_PREVIEW_SCROLLSYNC, _('&Scroll synchronize'))
        self.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW)
        self.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW_ONSAVE)
        self.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW_ONINPUT)
        self.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW_SCROLLSYNC)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_PREVIEW_ONSAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_PREVIEW_ONINPUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_PREVIEW_SCROLLSYNC)
        menuBar.Append(preview_menu, _('&Preview'))
        helpmenu = wx.Menu()
        helpmenu.Append(wx.ID_ABOUT, _('&About'))
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        menuBar.Append(helpmenu, _('&Help'))
        self.SetMenuBar(menuBar)

        # for webkit_gtk
        self.Show()
        self.Hide()
        # client window
        self.editor = editor.EditorWindow(self)
        self.explorer = explorer.ExplorerWindow(self)
        self.htmlviewer = htmlviewer.GetWebViewer(self)
        self.codeviewer = editor.CodeViewer(self)
        self.m_mgr.AddPane(self.explorer, wx.aui.AuiPaneInfo().
                           Name('explorer').Left().
                           Caption('File Explorer'))
        self.m_mgr.AddPane(self.editor, wx.aui.AuiPaneInfo().
                           Name('editor').CentrePane().
                           Caption('Editor'))
        self.m_mgr.AddPane(self.htmlviewer, wx.aui.AuiPaneInfo().
                           Name('htmlviewer').Right().Position(0).
                           Caption('HTML Preview'))
        self.m_mgr.AddPane(self.codeviewer, wx.aui.AuiPaneInfo().
                           Name('codeviewer').Right().Position(1).
                           Caption('Code Viewer'))

        # status bar
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -3])
        self.statusbar.SetStatusText(_('Ready'), 0)
        self.statusbar.SetStatusText(_('Welcome To RSTEditor'), 1)
        # other event
        self.Bind(explorer.EVT_LOAD_FILE, self.OnLoadFile, id=wx.ID_ANY)
        self.Bind(editor.EVT_REQ_PREVIEW, self.OnReqPreview, id=wx.ID_ANY)
        self.Bind(editor.EVT_SCROLL_WIN, self.OnScrollWin, id=wx.ID_ANY)
        # init
        self.filename = FILENAME
        self.UpdateTitle(self.filename)
        path = config.get('main', 'path')
        if not os.path.exists(path):
            path = HOME_PATH
        self.explorer.SetRootDir(path)
        size = utils.strsize2intlist(config.get('window', 'size'), (800, 600))
        self.SetSize(size)
        self.Center()
        try:
            aui_cfg = config.get('window', 'auiconfig')
            self.m_mgr.LoadPerspective(aui_cfg)
        except:
            self.m_mgr.GetPane('editor').Show().BestSize((300,600))
            self.m_mgr.GetPane('htmlviewer').Show().BestSize((300,300))
            self.m_mgr.GetPane('codeviewer').Hide().BestSize((300,300))
            self.m_mgr.GetPane('explorer').Show().BestSize((200,600))
            self.m_mgr.Update()
        self.editor.SetFocus()

    def OnExit(self, event):
        self.Close(True)

    def OnClose(self, event):
        self.NeedSaveFirstly()
        aui_cfg = self.m_mgr.SavePerspective()
        config.set('window', 'auiconfig', aui_cfg)
        size = self.GetSize()
        config.set('window', 'size', '%dx%d'% tuple(size))
        config.set('main', 'path', self.explorer.rootdir)
        event.Skip()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = APPNAME
        info.Version = VERSION
        info.Copyright = '(C) 2013'
        desc = APPNAME + ' is the editor for writing ReStructedText.\n'
        desc += 'wxWidgets %s'% wx.version()
        info.Description = desc
        info.Developers = AUTHORS
        wx.AboutBox(info)

    def OnNew(self, event):
        self.NeedSaveFirstly()
        self.filename = FILENAME
        self.UpdateTitle(self.filename)
        ext = os.path.splitext(self.filename)[1].lower()
        text = ''
        skeleton = os.path.join(TEMPLATE_PATH, 'skeleton%s'% ext)
        if os.path.exists(skeleton):
            with open(skeleton, 'r') as f:
                text = f.read()
        self.editor.SetValue(text)
        self.editor.SetSavePoint()
        self.PreviewRST('', ext)

    def OnOpen(self, event):
        self.NeedSaveFirstly()
        dlg = wx.FileDialog(self,
                            'Choose a file',
                            os.getcwd(),
                            '',
                            '*.*',
                            wx.OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            evt = explorer.LoadFileEvent(filename=path, id=self.GetId())
            wx.PostEvent(self, evt)
        dlg.Destroy()

    def OnSave(self, event):
        text = self.editor.GetValue()
        if self.filename == FILENAME:
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, wx.ID_SAVEAS)
            self.GetEventHandler().ProcessEvent(evt)
        else:
            with open(self.filename, 'w') as f:
                f.write(text)
            self.editor.SetSavePoint()
            if config.getboolean('preview', 'onsave'):
                ext = os.path.splitext(self.filename)[1].lower()
                self.PreviewRST(text, ext)
        return

    def OnSaveAs(self, event):
        dlg = wx.FileDialog(self,
                            'Save file as ...',
                            os.getcwd(),
                            '',
                            '*.*',
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.UpdateTitle(self.filename)
            text = self.editor.GetValue()
            with open(self.filename, 'w') as f:
                    f.write(text)
            self.editor.SetSavePoint()
            evt = explorer.SetRootEvent(id=self.GetId(), path=os.path.dirname(self.filename), refresh=True)
            wx.PostEvent(self.explorer, evt)
            ext = os.path.splitext(self.filename)[1].lower()
            self.PreviewRST(text, ext)
        dlg.Destroy()

    def OnEdit(self, event):
        id = event.GetId()
        if id == wx.ID_UNDO:
            if self.editor.CanUndo():
                self.editor.Undo()
        elif id == wx.ID_REDO:
            if self.editor.CanRedo():
                self.editor.Redo()
        elif id == wx.ID_CUT:
            self.editor.Cut()
        elif id == wx.ID_COPY:
            self.editor.Copy()
        elif id == wx.ID_PASTE:
            if self.editor.CanPaste():
                self.editor.Paste()
        elif id == wx.ID_DELETE:
            self.editor.Clear()
        elif id == wx.ID_SELECTALL:
            self.editor.SelectAll()
        elif id == wx.ID_FIND:
            self.editor.ShowFindWindow()

    def OnFind(self, event):
        id = event.GetId()
        if id == ID_FIND_PREV:
            self.editor.FindPrev()
        elif id == ID_FIND_NEXT:
            self.editor.FindNext()
        return

    def OnPreview(self, event):
        id = event.GetId()
        if id == ID_PREVIEW:
            value = self.editor.GetValue()
            ext = os.path.splitext(self.filename)[1]
            self.PreviewRST(value, ext)
        elif id == ID_PREVIEW_ONSAVE:
            if event.IsChecked():
                config.set('preview', 'onsave', 'yes')
            else:
                config.set('preview', 'onsave', 'no')
        elif id == ID_PREVIEW_ONINPUT:
            if event.IsChecked():
                config.set('preview', 'oninput', 'yes')
            else:
                config.set('preview', 'oninput', 'no')
        elif id == ID_PREVIEW_SCROLLSYNC:
            if event.IsChecked():
                config.set('preview', 'synchronize', 'yes')
            else:
                config.set('preview', 'synchronize', 'no')
        return

    def OnUpdateUI(self, event):
        evtId = event.GetId()
        if evtId == ID_HTML_VIEWER:
            event.Check(self.m_mgr.GetPane('htmlviewer').IsShown())
        elif evtId == ID_CODE_VIEWER:
            event.Check(self.m_mgr.GetPane('codeviewer').IsShown())
        elif evtId == ID_FILE_EXPLORER:
            event.Check(self.m_mgr.GetPane('explorer').IsShown())
        elif evtId == wx.ID_UNDO:
            event.Enable(self.editor.CanUndo())
        elif evtId == wx.ID_REDO:
            event.Enable(self.editor.CanRedo())
        elif evtId == wx.ID_PASTE:
            event.Enable(self.editor.CanPaste())
        elif evtId == ID_PREVIEW_ONSAVE:
            event.Check(config.getboolean('preview', 'onsave'))
        elif evtId == ID_PREVIEW_ONINPUT:
            event.Check(config.getboolean('preview', 'oninput'))
        elif evtId == ID_PREVIEW_SCROLLSYNC:
            if wx.Platform == '__WXMSW__':
                event.Check(False)
                event.Enable(False)
            else:
                event.Check(config.getboolean('preview', 'synchronize'))
        return

    def OnShowAuiPanel(self, event):
        evtId = event.GetId()
        if evtId == ID_HTML_VIEWER:
            self.m_mgr.GetPane('htmlviewer').Show(event.IsChecked())
        elif evtId == ID_CODE_VIEWER:
            self.m_mgr.GetPane('codeviewer').Show(event.IsChecked())
        elif evtId == ID_FILE_EXPLORER:
            self.m_mgr.GetPane('explorer').Show(event.IsChecked())
        self.m_mgr.Update()

    def OnLoadFile(self, event):
        self.NeedSaveFirstly()
        path = event.filename
        ext = os.path.splitext(path)[1].lower()
        if ext in ALLOWED_LOADS:
            with open(path, 'r') as f:
                text = f.read()
            self.filename = path
            self.UpdateTitle(self.filename)
            self.statusbar.SetStatusText(_('Load %s')% self.filename, 0)
            self.editor.SetValue(text)
            self.editor.SetSavePoint()
            self.editor.SetStyle(ext)
            evt = explorer.SetRootEvent(id=self.GetId(), path=os.path.dirname(self.filename), refresh=False)
            wx.PostEvent(self.explorer, evt)
            self.PreviewRST(text, ext)
        return

    def OnReqPreview(self, event):
        if config.getboolean('preview', 'oninput'):
            value = self.editor.GetValue()
            ext = os.path.splitext(self.filename)[1]
            self.PreviewRST(value, ext, True)
        return

    def OnScrollWin(self, event):
        if config.getboolean('preview', 'synchronize'):
            dy = event.pos
            editor_range = self.editor.GetScrollRange(wx.VERTICAL)
            htmlviewer_range = self.htmlviewer.GetScrollRange(wx.VERTICAL)
            unit = htmlviewer_range / editor_range
            delay = False
            evt = htmlviewer.ReqScrollEvent(dx=0, dy=dy*unit, delay=delay, id=self.htmlviewer.GetId())
            wx.PostEvent(self.htmlviewer, evt)

    def PreviewRST(self, text, type='.rst', delay=False):
        dy = self.editor.GetScrollPos(wx.VERTICAL)
        editor_range = self.editor.GetScrollRange(wx.VERTICAL)
        htmlviewer_range = self.htmlviewer.GetScrollRange(wx.VERTICAL)
        unit = htmlviewer_range / editor_range
        if type in ['.rst', '.rest']:
            html = rst2html(text)
            url = 'file:///%s'% self.filename
            self.codeviewer.SetValue(html)
            self.htmlviewer.SetPage(html, url)
            evt = htmlviewer.ReqScrollEvent(dx=0, dy=dy*unit, delay=delay, id=self.htmlviewer.GetId())
            wx.PostEvent(self.htmlviewer, evt)
        else:
            self.htmlviewer.SetPage('')
            self.codeviewer.SetValue('')
        self.editor.SetFocus()
        return

    def UpdateTitle(self, name):
        title = '%s - %s'% (APPNAME, name)
        self.SetTitle(title)

    def NeedSaveFirstly(self):
        if self.editor.GetModify():
            answer = wx.MessageBox(
                    _('Current file has been modified. Do you want to save it firstly?'),
                    _('File Modified'),
                    wx.YES_NO, self)
            if answer == wx.YES:
                evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, wx.ID_SAVE)
                self.GetEventHandler().ProcessEvent(evt)
            return True
        return False


def main():
    if not os.path.exists(CONFIG_PATH):
        shutil.copytree(os.path.join(DATA_PATH, 'config'), CONFIG_PATH)
    if not os.path.exists(TEMPLATE_PATH):
        os.makedirs(TEMPLATE_PATH)
    config_file = os.path.join(CONFIG_PATH, CONFIG_FILE)
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        # default config
        config.add_section('main')
        config.set('main', 'path', HOME_PATH)
        config.add_section('window')
        config.set('window', 'size', '800x600')
        config.add_section('preview')
        config.set('preview', 'onsave', 'no')
        config.set('preview', 'oninput', 'yes')
        config.set('preview', 'synchronize', 'yes')
    app = wx.App(redirect=False)
    frame = RSTEditorFrame(None)
    frame.Show(True)
    app.MainLoop()
    with open(config_file, 'w') as f:
        config.write(f)
    return


if __name__ == '__main__':
    main()
